import json
import re
import requests
import os
from dotenv import load_dotenv
from NetHyTech_Pyttsx3_Speak import speak

# Load environment variables
load_dotenv()

# Constants
API_URL = "https://pi.ai/api/chat"
HEADERS_TEMPLATE = {
    "Accept": "text/event-stream",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Content-Type": "application/json",
    "Dnt": "1",
    "Origin": "https://pi.ai",
    "Priority": "u=1, i",
    "Referer": "https://pi.ai/talk",
    "Sec-Ch-Ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "X-Api-Version": "3"
}

session_id = os.getenv("HOSTSESSION")
conversation_id = os.getenv("conv_id")

def get_new_session_cookie():
    response = requests.get("https://pi.ai")
    return list(response.cookies)[0].value if response.cookies else None

def generate_response(user_query, session_cookie="NetHyTech", print_output=True):
    headers = HEADERS_TEMPLATE.copy()
    headers["Cookie"] = f"__Host-session={session_id}; __cf_bm={session_cookie}"
    
    payload = {
        "text": user_query,
        "conversation": conversation_id
    }

    with requests.Session() as session:
        response = session.post(API_URL, json=payload, headers=headers, stream=True)
        
        if response.status_code in (401, 403):
            print("Session cookie expired. Generating a new one...")
            new_session_cookie = get_new_session_cookie()
            return generate_response(user_query, new_session_cookie, print_output)

        complete_response = ""
        if response.status_code == 200:
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    try:
                        json_data = json.loads(line.lstrip("data:"))
                        content = json_data.get("text", "")
                        with_emoji = content.encode("latin1").decode("utf-8")
                        # if print_output:
                        #     print(with_emoji, end="", flush=True)
                        complete_response += with_emoji
                    except json.JSONDecodeError:
                        continue

    return complete_response

if __name__ == "__main__":
    while True:
        user_query = input("\033[0;31m\nUser: \033[0m")
        complete_response = generate_response(user_query)
        speak(complete_response, 2)
