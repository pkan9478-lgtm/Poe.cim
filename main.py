import os
import json
import fastapi_poe as fp
import google.generativeai as genai

# API Key ကို Render Environment မှသာ ယူပါမည်
GEMINI_API_KEY = os.environ.get("AIzaSyBzxxQRB9lTRuN_XOOFAQQhXVKXroVWwlY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

try:
    with open('voice_map_summary.json', 'r') as f:
        voice_dna = json.load(f)
except:
    voice_dna = {"traits": "Natural, human-like, flowing text"}

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        try:
            # Model အမည်ကို နောက်ဆုံးဗားရှင်း သုံးထားပါသည်
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            prompt = f"Using Style DNA: {json.dumps(voice_dna)}, answer naturally: {user_message}"
            
            response = model.generate_content(prompt, safety_settings=[
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ])
            yield fp.PartialResponse(text=response.text)
        except Exception as e:
            yield fp.PartialResponse(text=f"⚠️ စနစ်က ခေတ္တအဆင်မပြေဖြစ်နေပါသည်။ Key အသစ်ကို Render တွင် ပြန်ထည့်ပေးပါ။")

bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
