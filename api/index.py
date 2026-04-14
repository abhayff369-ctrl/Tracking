from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# 🔐 API Key (env se lega, default bhi diya hai)
API_KEY = os.getenv("API_KEY", "ABHAY123API")


def lookup_phone_number(phone_number):
    url = "https://calltracer.in"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "country": "IN",
        "q": phone_number
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        def get_value(label):
            cell = soup.find(string=lambda t: t and label in t)
            if cell:
                tr = cell.find_parent("tr")
                if tr:
                    tds = tr.find_all("td")
                    if len(tds) > 1:
                        return tds[1].get_text(strip=True)
            return "N/A"

        data = {
            "Number": phone_number,
            "Owner Name": get_value("Owner Name"),
            "Mobile State": get_value("Mobile State"),
            "SIM Card": get_value("SIM card"),
            "Connection": get_value("Connection"),
            "Country": get_value("Country"),
        }

        return data

    except Exception as e:
        return {"error": str(e)}


@app.route("/")
def home():
    return jsonify({
        "status": "API Running",
        "developer": "Abhay Singh",
        "usage": "/api?number=XXXXXXXXXX&key=YOUR_KEY"
    })


@app.route("/api")
def lookup():
    phone_number = request.args.get("number")
    user_key = request.args.get("key")

    # ❌ Key check
    if user_key != API_KEY:
        return jsonify({
            "success": False,
            "developer": "Abhay Singh",
            "message": "Invalid API Key"
        }), 403

    if not phone_number:
        return jsonify({
            "success": False,
            "developer": "Abhay Singh",
            "message": "Number required"
        }), 400

    result = lookup_phone_number(phone_number)

    return jsonify({
        "success": True,
        "developer": "Abhay Singh",
        "data": result
    })


# 🔥 Vercel handler (IMPORTANT)
def handler(request, context):
    return app(request.environ, lambda *args: None)
