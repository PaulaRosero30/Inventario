from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

DATA_FILE = "inventory.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "products": [],
        "categories": ["Electrónica", "Ropa", "Alimentos", "Hogar", "Herramientas", "Otro"],
        "movements": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Initialize with sample data
def init_sample_data():
    if not os.path.exists(DATA_FILE):
        sample = {
            "products": [
                {"id": str(uuid.uuid4()), "name": "Laptop Dell XPS", "sku": "DELL-XPS-001", "category": "Electrónica", "price": 1200.00, "stock": 15, "min_stock": 5, "supplier": "Tech Corp", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": "Teclado Mecánico", "sku": "KB-MECH-002", "category": "Electrónica", "price": 85.00, "stock": 3, "min_stock": 10, "supplier": "Periféricos S.A.", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": "Mouse Inalámbrico", "sku": "MOUSE-WL-003", "category": "Electrónica", "price": 35.00, "stock": 42, "min_stock": 15, "supplier": "Periféricos S.A.", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": "Silla Ergonómica", "sku": "CHAIR-ERG-004", "category": "Hogar", "price": 320.00, "stock": 8, "min_stock": 3, "supplier": "MobiliarioPlus", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": "Camisa Oxford", "sku": "SHIRT-OXF-005", "category": "Ropa", "price": 45.00, "stock": 0, "min_stock": 20, "supplier": "Textiles MX", "created_at": datetime.now().isoformat()},
            ],
            "categories": ["Electrónica", "Ropa", "Alimentos", "Hogar", "Herramientas", "Otro"],
            "movements": []
        }
        save_data(sample)

init_sample_data()

# --- PRODUCTS ---
@app.route("/api/products", methods=["GET"])
def get_products():
    data = load_data()
    category = request.args.get("category")
    search = request.args.get("search", "").lower()
    products = data["products"]
    if category:
        products = [p for p in products if p["category"] == category]
    if search:
        products = [p for p in products if search in p["name"].lower() or search in p["sku"].lower()]
    return jsonify(products)

@app.route("/api/products", methods=["POST"])
def create_product():
    data = load_data()
    product = request.json
    product["id"] = str(uuid.uuid4())
    product["created_at"] = datetime.now().isoformat()
    product["stock"] = int(product.get("stock", 0))
    product["min_stock"] = int(product.get("min_stock", 5))
    product["price"] = float(product.get("price", 0))
    data["products"].append(product)
    # Log movement
    if product["stock"] > 0:
        data["movements"].append({
            "id": str(uuid.uuid4()),
            "product_id": product["id"],
            "product_name": product["name"],
            "type": "entrada",
            "quantity": product["stock"],
            "date": datetime.now().isoformat(),
            "note": "Stock inicial"
        })
    save_data(data)
    return jsonify(product), 201

@app.route("/api/products/<product_id>", methods=["PUT"])
def update_product(product_id):
    data = load_data()
    for i, p in enumerate(data["products"]):
        if p["id"] == product_id:
            old_stock = p["stock"]
            updated = {**p, **request.json}
            updated["id"] = product_id
            updated["stock"] = int(updated.get("stock", 0))
            updated["min_stock"] = int(updated.get("min_stock", 5))
            updated["price"] = float(updated.get("price", 0))
            data["products"][i] = updated
            # Log stock change
            new_stock = updated["stock"]
            if new_stock != old_stock:
                diff = new_stock - old_stock
                data["movements"].append({
                    "id": str(uuid.uuid4()),
                    "product_id": product_id,
                    "product_name": updated["name"],
                    "type": "entrada" if diff > 0 else "salida",
                    "quantity": abs(diff),
                    "date": datetime.now().isoformat(),
                    "note": "Ajuste de inventario"
                })
            save_data(data)
            return jsonify(updated)
    return jsonify({"error": "Producto no encontrado"}), 404

@app.route("/api/products/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    data = load_data()
    data["products"] = [p for p in data["products"] if p["id"] != product_id]
    save_data(data)
    return jsonify({"message": "Eliminado"})

# --- STOCK MOVEMENT ---
@app.route("/api/products/<product_id>/movement", methods=["POST"])
def stock_movement(product_id):
    data = load_data()
    body = request.json
    for i, p in enumerate(data["products"]):
        if p["id"] == product_id:
            qty = int(body["quantity"])
            move_type = body["type"]  # "entrada" or "salida"
            if move_type == "salida" and p["stock"] < qty:
                return jsonify({"error": "Stock insuficiente"}), 400
            data["products"][i]["stock"] += qty if move_type == "entrada" else -qty
            data["movements"].append({
                "id": str(uuid.uuid4()),
                "product_id": product_id,
                "product_name": p["name"],
                "type": move_type,
                "quantity": qty,
                "date": datetime.now().isoformat(),
                "note": body.get("note", "")
            })
            save_data(data)
            return jsonify(data["products"][i])
    return jsonify({"error": "Producto no encontrado"}), 404

# --- STATS ---
@app.route("/api/stats", methods=["GET"])
def get_stats():
    data = load_data()
    products = data["products"]
    total_products = len(products)
    total_value = sum(p["price"] * p["stock"] for p in products)
    low_stock = [p for p in products if p["stock"] <= p["min_stock"] and p["stock"] > 0]
    out_of_stock = [p for p in products if p["stock"] == 0]
    return jsonify({
        "total_products": total_products,
        "total_value": round(total_value, 2),
        "low_stock_count": len(low_stock),
        "out_of_stock_count": len(out_of_stock),
        "low_stock_items": low_stock,
        "out_of_stock_items": out_of_stock
    })

# --- MOVEMENTS ---
@app.route("/api/movements", methods=["GET"])
def get_movements():
    data = load_data()
    movements = sorted(data["movements"], key=lambda x: x["date"], reverse=True)
    return jsonify(movements[:50])

# --- CATEGORIES ---
@app.route("/api/categories", methods=["GET"])
def get_categories():
    data = load_data()
    return jsonify(data["categories"])

if __name__ == "__main__":
    app.run(debug=True, port=5000)
