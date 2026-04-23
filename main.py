import os
import json
import fastapi_poe as fp
import google.generativeai as genai

# ၁။ Gemini API ချိတ်ဆက်ခြင်း
GEMINI_API_KEY = os.environ.get("AIzaSyC4n9LKe84mvm3R-jtYWuXWe_aXNECT5ek")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ၂။ Voice DNA ကို ဖတ်ခြင်း
try:
    with open('voice_map_summary.json', 'r') as f:
        voice_dna = json.load(f)
except Exception:
    voice_dna = {"traits": "Natural, human-like, flowing text"}

# ၃။ Poe ၏ Official Protocol ဖြင့် Bot တည်ဆောက်ခြင်း
class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Using this Voice Style DNA: {json.dumps(voice_dna)}, rewrite this text to be 100% human-like. Only output the rewritten text: {user_message}"
            
            response = model.generate_content(prompt)
            # Poe နားလည်သော Streaming စနစ်ဖြင့် ပြန်ပို့ခြင်း
            yield fp.PartialResponse(text=response.text)
        except Exception as e:
            yield fp.PartialResponse(text=f"Error: {str(e)}")

# ၄။ ဆာဗာ အသက်သွင်းခြင်း
bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
