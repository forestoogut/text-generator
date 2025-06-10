from flask import Flask, request, render_template, jsonify
from generate_description import generate_description
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    topic = data.get('topic')
    length = data.get('length', 'medium')
    max_words_raw = data.get('max_words', '').strip()
    max_words = int(max_words_raw) if max_words_raw else 120

    try:
        result = generate_description(topic, length_category=length, max_words=max_words)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
