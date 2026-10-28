import time
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
models = [
    "models/gemini-flash-latest",
    "models/gemini-3.7-flash",
    "models/gemini-3.6-flash",
    "models/gemini-3.5-flash",
    "models/gemini-3.5-flash-lite",
]

for model in models:
    print("=" * 60)
    print(model)

    try:
        start = time.time()

        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly one word: Hello"
        )

        elapsed = time.time() - start

        print(f"Time: {elapsed:.2f} sec")
        print(response.text)

    except Exception as e:
        print(e)