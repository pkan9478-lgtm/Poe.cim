import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Render ရဲ့ လုံခြုံသော နေရာမှ API Key ကို ဆွဲယူခြင်း
GEMINI_API_KEY = os.environ.get("AIzaSyC4n9LKe84mvm3R-jtYWuXWe_aXNECT5ek")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# GitHub တွင် တိုက်ရိုက်တင်ထားမည့် Voice DNA ဖိုင်ကို ဖတ်ခြင်း
JSON_PATH = 'voice_map_summary.json'

if os.path.exists(JSON_PATH):
    with open(JSON_PATH, 'r') as f:
        voice_dna = json.load(f)
else:
    voice_dna = {"traits": "Natural, human-like, authentic tone."}

@app.route("/", methods=["POST"])
def poe_handler():
    try:
        data = request.json
        user_message = data['query'][-1]['content']
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Using the following Voice Style DNA:
        {json.dumps(voice_dna)}
        
        Rewrite this text to be 100% human-like. Only output the rewritten text.
        Text to rewrite: {user_message}
        """
        response = model.generate_content(prompt)
        return jsonify({"text": response.text})
    except Exception as e:
        return jsonify({"text": f"Error: {str(e)}"})

# Render အတွက် Port ကို အလိုအလျောက် သတ်မှတ်ခြင်း
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
