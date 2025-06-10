from flask import Flask, request, jsonify, render_template
from generate_description import generate_description
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    topic = data.get("topic", "").strip()
    length = data.get("length", "medium")
    max_words_raw = data.get("max_words", "").strip()
    max_words = int(max_words_raw) if max_words_raw else 1300

    logging.info(f"[INPUT] Topic: {topic}")
    logging.info(f"[INPUT] Length: {length} | Max Words: {max_words}")

    try:
        logging.info("[PROCESS] Starting generation...")
        result = generate_description(topic, length, max_words)
        logging.info("[SUCCESS] Description generated.")
        return jsonify({"result": result})
    except Exception as e:
        logging.error(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
