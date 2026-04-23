import os
import json
import fastapi_poe as fp
import google.generativeai as genai

# ၁။ လုံခြုံရေးအရ API Key ကို Code ထဲတွင် မရေးဘဲ Environment Variable မှသာ ယူပါမည်
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ၂။ Voice DNA ကို လုံခြုံစွာ ဖတ်ခြင်း
try:
    with open('voice_map_summary.json', 'r') as f:
        voice_dna = json.load(f)
except:
    voice_dna = {"traits": "Natural, human-like, flowing text"}

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        
        # 404 Error ကာကွယ်ရန် Stable ဖြစ်သော Model ကို သုံးပါသည်
        model_name = 'gemini-1.5-flash-latest' 

        try:
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
            Style DNA: {json.dumps(voice_dna)}
            Response Instructions: Answer naturally and helpfully.
            User: {user_message}
            """

            # Safety Settings ကို အကောင်းဆုံး ချိန်ညှိထားပါသည်
            response = model.generate_content(prompt, safety_settings=[
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ])
            
            if response.text:
                yield fp.PartialResponse(text=response.text)
            else:
                yield fp.PartialResponse(text="⚠️ AI က စာသားကို ငြင်းပယ်လိုက်ပါသည်။ အခြားစကားလုံးဖြင့် စမ်းသပ်ကြည့်ပါ။")
                
        except Exception as e:
            yield fp.PartialResponse(text=f"⚠️ ခေတ္တစောင့်ဆိုင်းပေးပါ။ စနစ်က ပြန်လည်ပြင်ဆင်နေပါသည်။")

bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
