import os
import json
import httpx
import fastapi_poe as fp
import google.generativeai as genai
from fastapi import Response

# Render Settings ထဲက Key ကို တိုက်ရိုက်ယူသည်
API_KEY = os.environ.get("GEMINI_API_KEY")

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        attachments = request.query[-1].attachments
        
        if not API_KEY:
            yield fp.PartialResponse(text="❌ Error: GEMINI_API_KEY Missing in Render Settings.")
            return

        try:
            # ၁။ API Configuration
            genai.configure(api_key=API_KEY)
            
            # ဆရာအလိုရှိသော နောက်ဆုံးပေါ် Gemini 2.0 Flash ကို အသုံးပြုထားပါသည်
            # Model Name ပြောင်းလဲမှုကို ခံနိုင်ရည်ရှိအောင် Stable နာမည်ကို သုံးထားသည်
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # ၂။ Voice DNA (JSON) ကို စနစ်တကျ ဖတ်ခြင်း
            dna_context = ""
            if os.path.exists('voice_map_summary.json'):
                try:
                    with open('voice_map_summary.json', 'r') as f:
                        voice_dna = json.load(f)
                    dna_context = f"Use this Voice DNA Style: {json.dumps(voice_dna)}\n"
                except:
                    pass

            prompt_parts = [f"{dna_context}User Message: {user_message}"]
            
            # ၃။ Vision System (ဓာတ်ပုံနှင့် ဖိုင်ဖတ်ခြင်း)
            if attachments:
                async with httpx.AsyncClient() as client:
                    for attachment in attachments:
                        resp = await client.get(attachment.url)
                        if resp.status_code == 200:
                            prompt_parts.append({
                                "mime_type": attachment.content_type,
                                "data": resp.content
                            })

            # ၄။ AI ထံမှ အဖြေတောင်းယူခြင်း (Safety Settings အပွင့်ဆုံးထားသည်)
            safety = [
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]

            response = model.generate_content(prompt_parts, safety_settings=safety)
            
            if response and response.text:
                yield fp.PartialResponse(text=response.text)
            else:
                yield fp.PartialResponse(text="⚠️ AI Engine မှ အဖြေထုတ်ပေးရန် ငြင်းဆိုထားပါသည်။ (Safety Filter)")

        except Exception as e:
            # ၅၀၂ သို့မဟုတ် 'Done' Event Error မတက်အောင် စာသားဖြင့် ပြန်ပို့ပေးသည်
            yield fp.PartialResponse(text=f"⚠️ System Error: {str(e)}")

# Poe App အသက်သွင်းခြင်း
bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)

# 405 Method Not Allowed ပြဿနာကို ဖြေရှင်းရန် Health Check Handler
@app.head("/")
@app.get("/")
async def health_check():
    return Response("TwinVoice Bot is running on Gemini 2.0 Flash!", status_code=200)
