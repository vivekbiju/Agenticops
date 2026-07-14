import os
from dotenv import load_dotenv
from google import genai

# Explicitly load the .env file located inside the Backend folder
load_dotenv(dotenv_path=os.path.join("Backend", ".env"))

# Now initialize the client with the successfully loaded key
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

response = client.models.generate_content(
    model='gemini-3.5-flash', 
    contents="Hello"
)
print(response.text)