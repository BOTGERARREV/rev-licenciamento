
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
    return "Servidor de Licenciamento Online - REV Infinity"

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
    app.run(host="0.0.0.0", port=5000)
