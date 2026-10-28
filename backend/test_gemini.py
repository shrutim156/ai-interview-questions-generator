import time
from google import genai

import os
from dotenv import load_dotenv


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "models/gemini-3.5-flash-lite"

print(f"Testing {MODEL}")

start = time.time()

try:
    response = client.models.generate_content(
        model=MODEL,
        contents="Say hello in one sentence."
    )

    print(f"Time: {time.time() - start:.2f} seconds")
    print(response.text)

except Exception as e:
    print(type(e).__name__)
    print(e)