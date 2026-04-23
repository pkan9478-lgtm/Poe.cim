import os
import json
import fastapi_poe as fp
import google.generativeai as genai

# Render Environment ထဲက Key ကို တိုက်ရိုက်ယူခြင်း
api_key = os.environ.get("AIzaSyBzxxQRB9lTRuN_XOOFAQQhXVKXroVWwlY")

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        
        # Key မရှိလျှင် သတိပေးရန်
        if not api_key:
            yield fp.PartialResponse(text="⚠️ Render Environment ထဲမှာ GEMINI_API_KEY ကို ရှာမတွေ့သေးပါ။ ကျေးဇူးပြု၍ Key ပြန်ထည့်ပေးပါ။")
            return

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Voice DNA ဖတ်ရန် ကြိုးစားခြင်း
            try:
                with open('voice_map_summary.json', 'r') as f:
                    voice_dna = json.load(f)
                dna_text = json.dumps(voice_dna)
            except:
                dna_text = "Natural and helpful"

            prompt = f"Using Style DNA: {dna_text}, answer naturally: {user_message}"
            response = model.generate_content(prompt)
            yield fp.PartialResponse(text=response.text)
            
        except Exception as e:
            yield fp.PartialResponse(text=f"⚠️ AI Engine Error: {str(e)}")

bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
