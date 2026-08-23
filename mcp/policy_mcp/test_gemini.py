import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


print(
    "API Key exists:",
    bool(os.getenv("GEMINI_API_KEY"))
)


client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


response = client.models.generate_content(
    model=os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    ),
    contents="Say hello in one sentence."
)


print("\nGemini Response:")

print(response.text)