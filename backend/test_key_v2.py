from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=key)

try:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents='Hello',
    )
    print("SUCCESS")
    print(response.text)
except Exception as e:
    print("FAILURE")
    print(e)
