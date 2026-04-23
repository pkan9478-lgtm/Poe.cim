import os
import json
import httpx
import fastapi_poe as fp
import google.generativeai as genai
from fastapi import Request, Response

# Render Environment Variable
API_KEY = os.environ.get("GEMINI_API_KEY")

class TwinVoiceBot(fp.PoeBot):
    async def get_response(self, request: fp.QueryRequest):
        user_message = request.query[-1].content
        attachments = request.query[-1].attachments
        
        if not API_KEY:
            yield fp.PartialResponse(text="❌ Error: GEMINI_API_KEY Missing.")
            return

        try:
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # DNA File ကို ဖတ်ခြင်း
            dna_context = ""
            if os.path.exists('voice_map_summary.json'):
                with open('voice_map_summary.json', 'r') as f:
                    voice_dna = json.load(f)
                dna_context = f"Voice DNA Info: {json.dumps(voice_dna)}\n"

            prompt_parts = [f"{dna_context}Respond naturally to: {user_message}"]
            
            # File Attachments စနစ်
            if attachments:
                async with httpx.AsyncClient() as client:
                    for attachment in attachments:
                        resp = await client.get(attachment.url)
                        if resp.status_code == 200:
                            prompt_parts.append({
                                "mime_type": attachment.content_type,
                                "data": resp.content
                            })

            # AI မှ အဖြေတောင်းခြင်း
            response = model.generate_content(prompt_parts)
            
            if response and response.text:
                yield fp.PartialResponse(text=response.text)
            else:
                yield fp.PartialResponse(text="⚠️ AI returned no content.")

        except Exception as e:
            # Error တက်ရင်တောင် 'done' event မပျောက်အောင် စာသားပြန်ပို့ပေးသည်
            yield fp.PartialResponse(text=f"⚠️ System Error: {str(e)}")

# HEAD request (405 Error) ကို ဖြေရှင်းရန် Custom Handler
bot = TwinVoiceBot()
app = fp.make_app(bot, allow_without_key=True)

@app.head("/")
@app.get("/")
async def index_handler():
    return Response("Bot is running", status_code=200)
