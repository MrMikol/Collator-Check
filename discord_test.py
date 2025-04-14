import requests
import json

WEBHOOK_URL = "https://discord.com/api/webhooks/1361400853830963422/bXFX-EobvkOjqqNWMX4naYQGbTU2Nj9Kp8UlFQELnMB_QBERNIpsn6joSeTlJklOaxEE"  # From your config

def send_test_message():
    payload = {
        "content": "🔔 This is a TEST alert from Collator Monitor",
        "embeds": [{
            "title": "TEST Notification",
            "description": "If you see this, your webhook is working!",
            "color": 65280,  # Green color
            "fields": [
                {
                    "name": "Test Field",
                    "value": "Everything looks good!",
                    "inline": True
                }
            ]
        }]
    }

    try:
        response = requests.post(
            WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        print("✅ Test message sent successfully to Discord!")
    except Exception as e:
        print(f"❌ Failed to send test message: {e}")

if __name__ == "__main__":
    send_test_message()