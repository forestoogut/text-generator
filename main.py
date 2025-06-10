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
    max_words = int(data.get('max_words', 120))  # default max ~120 words

    try:
        result = generate_description(topic, length_category=length, max_words=max_words)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
