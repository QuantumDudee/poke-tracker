from curl_cffi import requests
import os

def send_notification(title, message, url=""):
    topic = os.getenv("NTFY_TOPIC", "poke-harshit-test123")
    ntfy_url = f"https://ntfy.sh/{topic}"
    
    headers = {
        "Title": title,
        "Priority": "urgent",
        "Click": url
    }
    
    try:
        response = requests.post(
            ntfy_url, 
            data=message.encode('utf-8'), 
            headers=headers, 
            impersonate="chrome"
        )
        if response.status_code == 200:
            print(f"Notification sent successfully: {title}")
        else:
            print(f"Failed to send notification. Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending notification: {e}")

# Simple test block
if __name__ == "__main__":
    send_notification("TEST RESTOCK", "This is a test from the stock tracker.", "https://google.com")
