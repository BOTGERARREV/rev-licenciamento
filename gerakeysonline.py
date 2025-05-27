from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
KEYS_FILE = "keys.json"

def carregar_chaves():
    if not os.path.exists(KEYS_FILE):
        return {}
    with open(KEYS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def salvar_chaves(chaves):
    with open(KEYS_FILE, "w") as f:
        json.dump(chaves, f, indent=4)

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Licenciamento - REV Infinity</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #121212;
                color: #ffffff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                font-family: Arial, sans-serif;
            }
            .card {
                background-color: #1e1e1e;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 0 15px rgba(0,0,0,0.5);
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🔐 Servidor de Licenciamento - REV Infinity</h2>
            <p>API ativa e escutando validações de chave.</p>
            <p style="font-size: 0.9em; color: #aaaaaa;">Use POST /validar para verificar chaves de ativação.</p>
        </div>
    </body>
    </html>
    """

@app.route("/validar", methods=["POST"])
def validar():
    data = request.json
    chave = data.get("key", "").strip()
    maquina = data.get("machine_id", "").strip()

    if not chave or not maquina:
        return jsonify({"status": "fail", "message": "Dados incompletos."})

    chaves = carregar_chaves()

    if chave not in chaves:
        return jsonify({"status": "fail", "message": "Chave inválida."})

    validade = datetime.strptime(chaves[chave]["validade"], "%Y-%m-%d")
    if validade < datetime.now():
        return jsonify({"status": "fail", "message": "Chave expirada."})

    if chaves[chave]["machine"] == "":
        chaves[chave]["machine"] = maquina
        salvar_chaves(chaves)
    elif chaves[chave]["machine"] != maquina:
        return jsonify({"status": "fail", "message": "Chave já usada em outra máquina."})

    return jsonify({"status": "ok", "message": "Licença válida e ativa!"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
