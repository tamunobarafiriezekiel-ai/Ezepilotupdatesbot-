import os
import asyncio
from telegram import Bot

TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # Example: https://your-app.onrender.com

async def set_webhook():
    bot = Bot(token=TOKEN)
    webhook_url = f"{APP_URL}/webhook"

    # Remove old webhook first (if any)
    await bot.delete_webhook()

    # Set new webhook
    success = await bot.set_webhook(url=webhook_url)
    if success:
        print(f"Webhook set to {webhook_url}")
    else:
        print("Failed to set webhook.")

if __name__ == "__main__":
    asyncio.run(set_webhook())
