from flask import Flask
import requests

app = Flask(__name__)

@app.route("/", methods=["GET"])
def main_page():
    return "Flask is working and correctly set up", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
