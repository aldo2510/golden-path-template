import os
from flask import Flask, jsonify

app = Flask(__name__)
APP_NAME = os.getenv("APP_NAME", "Golden Path Demo")

@app.get("/")
def index():
    return jsonify({
        "message": "¡Hola desde el Golden Path!",
        "application": APP_NAME,
        "platform": "Azure Container Apps",
        "deployed_by": "GitHub Actions + Terraform"
    })

@app.get("/health")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
