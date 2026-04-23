import os
import json
import fastapi_poe as fp
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("AIzaSyC4n9LKe84mvm3R-jtYWuXWe_aXNECT5ek")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

try:
    with open('voice_map_summary.json', 'r') as f:
        voice_dna = json.load(f)
except Exception:
    voice_dna = {"traits": "Natural, human-like, flowing text"}

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        try:
            # ဤနေရာတွင် အသစ်ဆုံးဖြစ်သော Gemini 2.5 Flash သို့ ပြောင်းလဲထားပါသည်
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"Using this Voice Style DNA: {json.dumps(voice_dna)}, rewrite this text to be 100% human-like. Only output the rewritten text: {user_message}"
            
            response = model.generate_content(prompt)
            yield fp.PartialResponse(text=response.text)
        except Exception as e:
            # အကယ်၍ 2.5 flash အလုပ်မလုပ်ပါက 2.0 flash သို့ အရန်အဖြစ် ပြောင်းလဲအသုံးပြုမည်
            try:
                model_fallback = genai.GenerativeModel('gemini-2.0-flash')
                response_fallback = model_fallback.generate_content(prompt)
                yield fp.PartialResponse(text=response_fallback.text)
            except Exception as inner_e:
                yield fp.PartialResponse(text=f"AI Engine Error: {str(inner_e)}")

bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
