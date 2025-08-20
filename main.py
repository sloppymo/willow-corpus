from fastapi import FastAPI, Request
import openai, os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
def home():
    return {"status": "Willow API running!"}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # or whichever model you use
        messages=[{"role": "user", "content": user_message}]
    )
    return {"reply": response["choices"][0]["message"]["content"]}
