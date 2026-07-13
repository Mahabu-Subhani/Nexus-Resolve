import os
from dotenv import load_dotenv
load_dotenv()

def show(name):
    val = os.environ.get(name)
    if val is None:
        print(f"{name}: NOT SET")
    else:
        print(f"{name}: len={len(val)}  starts='{val[:6]}'  ends='{val[-4:]}'")

show("GEMINI_API_KEY")
show("SLACK_BOT_TOKEN")
show("SLACK_APP_TOKEN")
show("GOOGLE_GENAI_USE_VERTEXAI")
show("GOOGLE_APPLICATION_CREDENTIALS")
show("GOOGLE_API_KEY")
print()
print(".env file found at:", os.path.join(os.getcwd(), ".env"), "->", os.path.exists(".env"))
