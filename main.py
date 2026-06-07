from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


@app.route('/home', methods=['POST'])
def home():
    data = request.json
    user_query = data['query']

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_query
    )
    return jsonify({'answer': response.text})


if __name__ == '__main__':
    app.run(debug=True)
