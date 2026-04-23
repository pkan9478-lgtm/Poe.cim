import os
import json
import httpx
import fastapi_poe as fp
import google.generativeai as genai

# Render Environment Variable မှ Key ကိုယူခြင်း
API_KEY = os.environ.get("GEMINI_API_KEY")

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        attachments = request.query[-1].attachments
        
        if not API_KEY:
            yield fp.PartialResponse(text="❌ Error: GEMINI_API_KEY is missing in Render settings.")
            return

        try:
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # ၁။ အခုတင်လိုက်တဲ့ voice_map_summary.json ဖိုင်ကို ဖတ်ခြင်း
            try:
                with open('voice_map_summary.json', 'r') as f:
                    voice_dna = json.load(f)
                dna_context = f"You must use this Voice Style DNA to respond: {json.dumps(voice_dna)}"
            except Exception as dna_error:
                dna_context = "Style Context: Natural, human-like Burmese/English conversationalist."

            # ၂။ Prompt အား စာသားနှင့် ဖိုင်များ ပေါင်းစပ်တည်ဆောက်ခြင်း
            prompt_parts = [f"{dna_context}\n\nUser Message: {user_message}"]
            
            # ဓာတ်ပုံ သို့မဟုတ် ဖိုင်များပါလာပါက Vision စနစ်ဖြင့် ဖတ်ခြင်း
            if attachments:
                async with httpx.AsyncClient() as client:
                    for attachment in attachments:
                        resp = await client.get(attachment.url)
                        if resp.status_code == 200:
                            prompt_parts.append({
                                "mime_type": attachment.content_type,
                                "data": resp.content
                            })

            # ၃။ AI မှ အဖြေထုတ်ပေးခြင်း
            # Safety ပိတ်ထားပြီး တိုက်ရိုက်အဖြေထုတ်ပေးမည့် Full System
            safety_settings = [
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]

            response = model.generate_content(prompt_parts, safety_settings=safety_settings)
            
            if response and response.text:
                yield fp.PartialResponse(text=response.text)
            else:
                yield fp.PartialResponse(text="⚠️ AI သည် အကြောင်းအရာကို နားလည်သော်လည်း အဖြေထုတ်ရန် ငြင်းဆိုထားပါသည်။")

        except Exception as e:
            yield fp.PartialResponse(text=f"⚠️ System Error: {str(e)}")

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(server_bot_dependencies={})

bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)
