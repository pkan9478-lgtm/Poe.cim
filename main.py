import os
import json
import asyncio
import fastapi_poe as fp
import google.generativeai as genai

# ၁။ လုံခြုံရေးအပြည့်ဖြင့် API Key ကို ဆွဲယူခြင်း
API_KEY = os.environ.get("AIzaSyBzxxQRB9lTRuN_XOOFAQQhXVKXroVWwlY")

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        
        if not API_KEY:
            yield fp.PartialResponse(text="❌ System Error: API Key is missing in Render settings.")
            return

        # ၂။ AI Engines List (တစ်ခုမရလျှင် နောက်တစ်ခုကို Auto သုံးရန်)
        # အစီအစဉ်: 2.0 Flash -> 1.5 Flash Latest -> 1.5 Pro
        models_to_try = [
            "gemini-2.0-flash", 
            "gemini-1.5-flash-latest", 
            "gemini-1.5-pro-latest"
        ]

        # ၃။ Voice DNA ကို စနစ်တကျ ဖတ်ခြင်း
        try:
            with open('voice_map_summary.json', 'r') as f:
                voice_dna = json.load(f)
            style_context = f"Apply this Voice DNA Style: {json.dumps(voice_dna)}"
        except:
            style_context = "Tone: Natural and Human-like"

        prompt = f"""
        {style_context}
        Instruction: Answer the user's question naturally in the identified style.
        User Input: {user_message}
        """

        # ၄။ Multi-Engine Logic (စစ်မှန်သော Full System)
        success = False
        for model_name in models_to_try:
            try:
                genai.configure(api_key=API_KEY)
                model = genai.GenerativeModel(model_name)
                
                # Safety Settings ကို အပွင့်ဆုံးထားခြင်း (Error နည်းစေရန်)
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
                    break # တစ်ခု အောင်မြင်လျှင် ရပ်မည်
            except Exception as e:
                print(f"Model {model_name} failed: {str(e)}")
                continue # နောက် Model တစ်ခုကို ထပ်စမ်းမည်

        if not success:
            yield fp.PartialResponse(text="⚠️ AI Engines အားလုံး၏ Quota ပြည့်နေပါသည်။ (၁) မိနစ်ခန့် စောင့်ပြီးမှ ပြန်လည်မေးမြန်းပေးပါ။")

# ၅။ ဆာဗာကို Production Mode ဖြင့် လွှင့်တင်ခြင်း
bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
