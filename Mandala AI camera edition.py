import os
import sys
import time
import json
import requests
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION ---
API_KEY = "AIzaSyAWbI5O6-n_sXI3QB-Rk4EsMgq-rwnNH-s"
# We try your current IP first, then the local internal address
URLS = [
    "http://192.0.0.4:8080/shot.jpg", 
    "http://127.0.0.1:8080/shot.jpg"
]
HISTORY_FILE = "mandala_memory.json"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            saved_h = json.load(f)
    else: saved_h = []
    chat = model.start_chat(history=saved_h)
except Exception as e:
    print(f"Startup Error: {e}")

# --- 2. THE VISION ENGINE ---
def capture_vision():
    """Tries to grab a photo from the IP Webcam server"""
    for url in URLS:
        try:
            # We wait up to 5 seconds for a connection
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img_path = "vision_input.jpg"
                with open(img_path, "wb") as f:
                    f.write(response.content)
                return img_path
        except:
            continue
    return None

# --- 3. MAIN INTERFACE ---
os.system('clear')
print("   " + "="*40)
print("   MANDALA AI: STABLE VISION SYSTEM")
print("   " + "="*40)
print("   -> Type 'camera' to start the lens.")
print("   -> Type 'exit' to save memory.\n")

while True:
    user_input = input(f"   Hritabrata: ").strip().lower()
    
    if user_input == 'camera':
        path = capture_vision()
        if path:
            print("   [SUCCESS] Image Received!")
            task = input("   AI: What should I solve or explain in this photo? ")
            try:
                img = Image.open(path)
                print("   [ANALYZING] Using Transformer brain...")
                response = model.generate_content([f"System: You are Mandala AI. Task: {task}", img])
                print(f"\n   Mandala AI: {response.text}\n")
            except Exception as e:
                if "429" in str(e):
                    print("\n   [!] QUOTA FULL: Waiting 20 seconds...")
                    time.sleep(20)
                else: print(f"\n   Vision Error: {e}")
        else:
            print("   [!] ERROR: Connection Refused. Start the server in IP Webcam!")
        continue

    if user_input in ['exit', 'quit']:
        print("   AI: Memory saved. Goodbye!")
        break

    # Standard Chat
    try:
        response = chat.send_message(user_input)
        print(f"\n   Mandala AI: {response.text}\n")
        
        with open(HISTORY_FILE, "w") as f:
            json.dump([{"role": m.role, "parts": [{"text": m.parts[0].text}]} for m in chat.history], f)
    except Exception as e:
        if "429" in str(e):
            print("\n   [!] Quota full. Retrying in 15 seconds...")
            time.sleep(15)
        else: print(f"\n   Error: {e}")
