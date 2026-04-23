import os
import json
import fastapi_poe as fp
import google.generativeai as genai

# Render Settings ထဲက Key ကို တိုက်ရိုက်ယူသည်
API_KEY = os.environ.get("GEMINI_API_KEY")

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        # နောက်ဆုံးပို့လိုက်သော Message ကို ယူသည်
        user_message = request.query[-1].content
        
        if not API_KEY:
            yield fp.PartialResponse(text="❌ [Server Error]: GEMINI_API_KEY is missing in Render Environment.")
            return

        try:
            # AI Engine Configuration
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Voice DNA Style ချိတ်ဆက်ခြင်း
            try:
                with open('voice_map_summary.json', 'r') as f:
                    voice_dna = json.load(f)
                dna_context = f"Voice DNA Context: {json.dumps(voice_dna)}"
            except:
                dna_context = "Style: Natural Human-like"

            # အဖြေထုတ်ပေးရန် Prompt
            prompt = f"{dna_context}\nAnswer this user message naturally: {user_message}"
            
            # Safety Settings (အပွင့်ဆုံးထားသည်)
            safety = [
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]

            response = model.generate_content(prompt, safety_settings=safety)
            
            if response and response.text:
                yield fp.PartialResponse(text=response.text)
            else:
                yield fp.PartialResponse(text="⚠️ AI Engine မှ အဖြေထုတ်ပေးနိုင်ခြင်းမရှိပါ။ (Safety Filter ကြောင့် ဖြစ်နိုင်ပါသည်)")

        except Exception as e:
            # ၅၀၂ Error မဖြစ်အောင် Error တက်ရင် စာသားဖြင့် ပြန်ပြပေးမည်
            yield fp.PartialResponse(text=f"⚠️ System Error: {str(e)}")

# Production App အသက်သွင်းခြင်း
bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
