import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

genai.configure(api_key='AIzaSyBToLypnjRLq96jpgt7Tz7bLVtsWN52tDg')

model = genai.GenerativeModel('gemini-pro')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    context = data.get('context', '')

    try:
        prompt = f"{context}\n\nQuestion: {question}"
        response = model.generate_content(prompt)

        if response and response.text:
            return jsonify({'answer': response.text.strip()})
        else:
            return jsonify({'error': 'No response from Gemini API'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
