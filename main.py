import os  # စာလုံးအသေးဖြင့် ပြင်ထားသည်
import json
import fastapi_poe as fp
import google.generativeai as genai

# Render ထဲက Environment Variable နာမည်ကိုသာ ခေါ်ယူရပါမည်
# Key အစစ်ကို Render Dashboard > Environment ထဲမှာ GEMINI_API_KEY ဆိုတဲ့ နာမည်နဲ့ ထည့်ပေးပါ
RAW_API_KEY = os.environ.get("GEMINI_API_KEY")

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        
        # ၁။ API Key ရှိမရှိ အရင်စစ်ဆေးခြင်း
        if not RAW_API_KEY:
            yield fp.PartialResponse(text="❌ Error: Render Settings ထဲမှာ GEMINI_API_KEY ကို ရှာမတွေ့ပါ။ Variable နာမည် မှန်မမှန် ပြန်စစ်ပေးပါ။")
            return

        # ၂။ AI Models List
        models = ["gemini-2.0-flash", "gemini-1.5-flash-latest"]
        
        # ၃။ Voice DNA Style ဖတ်ခြင်း
        try:
            with open('voice_map_summary.json', 'r') as f:
                voice_dna = json.load(f)
            dna_style = json.dumps(voice_dna)
        except:
            dna_style = "Natural Human-like"

        prompt = f"Using Style DNA: {dna_style}, answer this naturally: {user_message}"

        # ၄။ Multi-Engine Logic
        success = False
        for m_name in models:
            try:
                genai.configure(api_key=RAW_API_KEY)
                model = genai.GenerativeModel(m_name)
                
                # Safety Settings လျှော့ချခြင်း
                safety = [
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]

                response = model.generate_content(prompt, safety_settings=safety)
                if response.text:
                    yield fp.PartialResponse(text=response.text)
                    success = True
                    break
            except Exception as e:
                # Error ဖြစ်လျှင် နောက် Model တစ်ခုသို့ ဆက်သွားမည်
                continue

        if not success:
            yield fp.PartialResponse(text="⚠️ အခုလောလောဆယ် AI Engines အားလုံး Limit ပြည့်နေပါသည်။ ခဏအကြာမှ ပြန်စမ်းပေးပါ။")

bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
