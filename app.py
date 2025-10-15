from datetime import datetime
import pytz
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Webhook funcionando! Acesse /get-datetime para ver a data e hora."

@app.route("/get-datetime", methods=["GET"])
def get_datetime():
    tz = pytz.timezone("America/Sao_Paulo")
    now = datetime.now(tz)
    formatted_now = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    return jsonify({
        "datetime": formatted_now,
        "formatted": now.strftime("%d/%m/%Y %H:%M:%S"),
        "timezone": "America/Sao_Paulo",
        "status": "success"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
