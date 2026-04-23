import os
import json
import fastapi_poe as fp
import google.generativeai as genai

# ၁။ API Key ချိတ်ဆက်ခြင်း (Environment Variable မှ အလိုအလျောက် ရယူသည်)
GEMINI_API_KEY = os.environ.get("AIzaSyARef_w8xOClcWb85nB4A67PyuMAzkaH3U")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ၂။ Voice DNA ကို ဖတ်ခြင်း
try:
    with open('voice_map_summary.json', 'r') as f:
        voice_dna = json.load(f)
except Exception:
    voice_dna = {"traits": "Natural, human-like, flowing text"}

# ၃။ Poe Chatbot အဖြစ် တည်ဆောက်ခြင်း
class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        try:
            # ပင်မ အင်ဂျင်အဖြစ် အသစ်ဆုံး Gemini 2.0 Flash ကို သုံးပါမည်
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # (အရေးကြီးဆုံးအပိုင်း) Rewriter အစား အမေးအဖြေ Assistant အဖြစ် ပြောင်းလဲထားသော အမိန့်
            prompt = f"""
            You are a highly intelligent and authentic AI assistant. 
            Using the following Voice Style DNA: {json.dumps(voice_dna)}, 
            answer the user's input directly, naturally, and helpfully. 
            Do NOT just rewrite the text. Provide a real, conversational response to their statement or question.
            
            User input: {user_message}
            """
            
            response = model.generate_content(prompt)
            yield fp.PartialResponse(text=response.text)
            
        except Exception as e:
            # Quota ပြည့်သွားပါက သို့မဟုတ် Error တက်ပါက အရန်အင်ဂျင် (1.5 Flash) ဖြင့် အလိုအလျောက် ပြန်ဖြေပေးမည်
            try:
                model_fallback = genai.GenerativeModel('gemini-1.5-flash')
                response_fallback = model_fallback.generate_content(prompt)
                yield fp.PartialResponse(text=response_fallback.text)
            except Exception as inner_e:
                yield fp.PartialResponse(text=f"System Notification - AI Engine Error: {str(inner_e)}")

# ၄။ ဆာဗာ အသက်သွင်းခြင်း
bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
