from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6952136450"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002845832658"))
GROUP_ID = int(os.getenv("GROUP_ID", "-1002493478840"))

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Helper: send message
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# Helper: forward message
def forward_message(from_chat_id, message_id, to_chat_id):
    url = f"{BASE_URL}/forwardMessage"
    requests.post(url, json={
        "chat_id": to_chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    })

# Command handlers
def handle_start(chat_id, user_id):
    if user_id == ADMIN_ID:
        send_message(chat_id, "✅ Welcome Admin! You have full access.")
    else:
        send_message(chat_id, "Hello! This is my bot running on Render.")

def handle_ban(chat_id, user_id, target_id):
    if user_id == ADMIN_ID:
        url = f"{BASE_URL}/banChatMember"
        requests.post(url, json={"chat_id": chat_id, "user_id": target_id})
        send_message(chat_id, f"🚫 User {target_id} banned.")
    else:
        send_message(chat_id, "❌ You are not authorized.")

def handle_kick(chat_id, user_id, target_id):
    if user_id == ADMIN_ID:
        url = f"{BASE_URL}/kickChatMember"
        requests.post(url, json={"chat_id": chat_id, "user_id": target_id})
        send_message(chat_id, f"👢 User {target_id} kicked.")
    else:
        send_message(chat_id, "❌ You are not authorized.")

def handle_mute(chat_id, user_id, target_id):
    if user_id == ADMIN_ID:
        url = f"{BASE_URL}/restrictChatMember"
        requests.post(url, json={
            "chat_id": chat_id,
            "user_id": target_id,
            "permissions": {"can_send_messages": False}
        })
        send_message(chat_id, f"🔇 User {target_id} muted.")
    else:
        send_message(chat_id, "❌ You are not authorized.")

# === Health Check Route ===
@app.route("/", methods=["GET"])
def health_check():
    return {"status": "ok", "message": "Bot server is running ✅"}

# === Webhook route ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        text = msg.get("text", "")
        message_id = msg["message_id"]

        # Debug log
        print("Incoming message:", msg)

        # === Forward non-command messages ===
        if text and not text.startswith("/"):
            forward_message(chat_id, message_id, GROUP_ID)
            forward_message(chat_id, message_id, CHANNEL_ID)

        # === Handle commands ===
        if text.startswith("/start"):
            handle_start(chat_id, user_id)

        elif text.startswith("/ban") and user_id == ADMIN_ID:
            try:
                target_id = int(text.split()[1])
                handle_ban(chat_id, user_id, target_id)
            except:
                send_message(chat_id, "Usage: /ban <user_id>")

        elif text.startswith("/kick") and user_id == ADMIN_ID:
            try:
                target_id = int(text.split()[1])
                handle_kick(chat_id, user_id, target_id)
            except:
                send_message(chat_id, "Usage: /kick <user_id>")

        elif text.startswith("/mute") and user_id == ADMIN_ID:
            try:
                target_id = int(text.split()[1])
                handle_mute(chat_id, user_id, target_id)
            except:
                send_message(chat_id, "Usage: /mute <user_id>")

    return {"ok": True}

# Auto-set webhook on startup
if TOKEN:
    APP_URL = os.getenv("RENDER_EXTERNAL_URL", "https://telegram-bot-h9su.onrender.com")
    if APP_URL:
        webhook_url = f"{APP_URL}/webhook"
        set_webhook = f"{BASE_URL}/setWebhook?url={webhook_url}"
        try:
            r = requests.get(set_webhook)
            print("Webhook set:", r.json())
        except Exception as e:
            print("Error setting webhook:", e)