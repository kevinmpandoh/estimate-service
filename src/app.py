from flask import Flask, request, jsonify
from flask_cors import CORS
from services.train_service import train_model_service
from services.estimate_service import estimate_service

app = Flask(__name__)
CORS(app)

@app.route("/estimate", methods=["POST"])
def estimate():
    try:
        data = request.json
        result = estimate_service(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/train", methods=["POST"])
def train_model():
    try:
        result = train_model_service()
        return jsonify({
            "success": True,
            "message": "Model trained successfully",
            **result
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
