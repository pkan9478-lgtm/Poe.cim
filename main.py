import os
import json
import asyncio
import fastapi_poe as fp
import google.generativeai as genai

# Render Environment မှ Key ကို ယူခြင်း
API_KEY = os.environ.get("GEMINI_API_KEY")

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        # နောက်ဆုံး Message ကို ယူသည်
        user_message = request.query[-1].content
        
        if not API_KEY:
            yield fp.PartialResponse(text="❌ Error: GEMINI_API_KEY is missing.")
            return

        try:
            # AI Engine အား Configure လုပ်ခြင်း
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Voice DNA Context
            try:
                with open('voice_map_summary.json', 'r') as f:
                    voice_dna = json.load(f)
                dna_context = f"Voice DNA Context: {json.dumps(voice_dna)}"
            except:
                dna_context = "Style: Natural Human-like"

            # Prompt တည်ဆောက်ခြင်း
            prompt = f"{dna_context}\nAnswer this user message naturally: {user_message}"
            
            # AI ထံမှ အဖြေတောင်းခြင်း
            response = model.generate_content(prompt)
            
            if response and response.text:
                # Poe သို့ အဖြေ ပေးပို့ခြင်း
                yield fp.PartialResponse(text=response.text)
            else:
                yield fp.PartialResponse(text="⚠️ AI returned an empty response.")

        except Exception as e:
            # Error ဖြစ်လျှင်လည်း စနစ်တကျ ပြန်ကြားပေးခြင်းဖြင့် Exit မဖြစ်အောင် လုပ်ဆောင်သည်
            yield fp.PartialResponse(text=f"⚠️ System Error: {str(e)}")
        
        # ဤနေရာတွင် Poe protocol က လိုအပ်သော 'done' အခြေအနေကို အလိုအလျောက် ပို့ဆောင်ပေးမည်

# App တည်ဆောက်ခြင်း
bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
