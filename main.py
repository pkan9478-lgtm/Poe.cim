import os
import json
import fastapi_poe as fp
import google.generativeai as genai

# ၁။ လုံခြုံရေးအရ Environment Variable အမည်ကိုသာ အတိအကျ ခေါ်ယူသည်
# Render တွင် Variable အမည်ကို GEMINI_API_KEY ဟု ပေးထားရန် လိုအပ်သည်
API_KEY_NAME = "GEMINI_API_KEY"
raw_key = os.environ.get(API_KEY_NAME)

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        
        # API Key မရှိလျှင် Render Settings စစ်ရန် အကြောင်းကြားမည်
        if not raw_key:
            yield fp.PartialResponse(text="[System Error]: API Key missing in Environment. Please set GEMINI_API_KEY in Render.")
            return

        try:
            # ၂။ AI Engine ကို အသက်သွင်းခြင်း
            genai.configure(api_key=raw_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # ၃။ Voice DNA ကို ချိတ်ဆက်ခြင်း
            try:
                with open('voice_map_summary.json', 'r') as f:
                    voice_dna = json.load(f)
                context_prompt = f"System Context: Use this Voice DNA {json.dumps(voice_dna)} to answer naturally."
            except:
                context_prompt = "System Context: Answer naturally and human-like."

            # ၄။ တိုက်ရိုက် အဖြေထုတ်ပေးခြင်း (No Demo / No Simulation)
            full_prompt = f"{context_prompt}\nUser Message: {user_message}"
            
            # Safety ပိတ်ထားခြင်း (Block None)
            safety = [
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]

            response = model.generate_content(full_prompt, safety_settings=safety)
            
            if response.text:
                yield fp.PartialResponse(text=response.text)
            else:
                yield fp.PartialResponse(text="⚠️ AI response was empty due to internal safety filters.")

        except Exception as e:
            # Error တက်ပါက တိကျသော အကြောင်းရင်းကို ပြပေးမည်
            yield fp.PartialResponse(text=f"⚠️ Engine Error: {str(e)}")

# ၅။ Production Server အသက်သွင်းခြင်း
bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
