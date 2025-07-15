from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow access from mobile apps

# Simulated database (use MySQL later if needed)
clients = {
    "001": {
        "name": "Ali",
        "plot_no": "21A",
        "block": "C",
        "pin": "1234",
        "total_price": "5000000",
        "paid_amount": "3000000",
        "registry_status": "Not Registered"
    }
}

# ------------------ API: Get client info ------------------
@app.route("/client/<client_id>", methods=["GET"])
def get_client(client_id):
    pin = request.args.get("pin")
    client = clients.get(client_id)
    if client and client["pin"] == pin:
        return jsonify({"status": "success", "data": client})
    return jsonify({"status": "error", "message": "Client not found or wrong PIN"}), 404

# ------------------ API: Create/Update client ------------------
@app.route("/client", methods=["POST"])
def add_or_update_client():
    data = request.json
    if not data or "id" not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400
    clients[data["id"]] = data
    return jsonify({"status": "success", "message": "Client saved"}), 201

# ------------------ Health Check ------------------
@app.route("/", methods=["GET"])
def index():
    return "✅ API is running"

# ✅ Corrected entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)