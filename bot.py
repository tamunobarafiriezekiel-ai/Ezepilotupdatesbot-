import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID")
GROUP_ID = os.getenv("GROUP_ID")

# Initialize Flask app
app = Flask(__name__)

# Create Telegram application (no polling)
application = Application.builder().token(TOKEN).build()

# === Commands ===
async def start(update: Update, context):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("Welcome Admin ✅")
    else:
        await update.message.reply_text("Welcome to the bot!")

async def ban(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    user_id = int(context.args[0])
    try:
        await context.bot.ban_chat_member(chat_id=GROUP_ID, user_id=user_id)
        await update.message.reply_text(f"User {user_id} banned.")
    except Exception as e:
        await update.message.reply_text(str(e))

async def kick(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /kick <user_id>")
        return
    user_id = int(context.args[0])
    try:
        await context.bot.ban_chat_member(chat_id=GROUP_ID, user_id=user_id)
        await context.bot.unban_chat_member(chat_id=GROUP_ID, user_id=user_id)
        await update.message.reply_text(f"User {user_id} kicked.")
    except Exception as e:
        await update.message.reply_text(str(e))

async def mute(update: Update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /mute <user_id>")
        return
    user_id = int(context.args[0])
    try:
        await context.bot.restrict_chat_member(
            chat_id=GROUP_ID,
            user_id=user_id,
            permissions={"can_send_messages": False},
        )
        await update.message.reply_text(f"User {user_id} muted.")
    except Exception as e:
        await update.message.reply_text(str(e))

# === Register Handlers ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ban", ban))
application.add_handler(CommandHandler("kick", kick))
application.add_handler(CommandHandler("mute", mute))

# === Webhook route ===
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"
