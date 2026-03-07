import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=key)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello")
    print("SUCCESS")
    print(response.text)
except Exception as e:
    print("FAILURE")
    print(e)
