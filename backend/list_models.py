import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Models available for your API key:\n")

for model in client.models.list():
    methods = getattr(model, "supported_actions", None)
    if methods is None:
        methods = getattr(model, "supported_generation_methods", [])

    print(f"{model.name}")
    print(f"  Methods: {methods}")
    print()
    