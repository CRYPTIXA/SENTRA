import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config_loader import telegram_token, whale_threshold
from database.nhost_db import NhostDB

# Initialize database connection
nhost_db = NhostDB()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = str(update.effective_user.id)
    # Add user to database with default threshold
    try:
        nhost_db.add_user(user_id, whale_threshold)
        await update.message.reply_text(
            "Welcome to SENTRA Whale Tracker! You're now subscribed to whale transaction alerts."
        )
    except Exception as e:
        # If user already exists, update their threshold
        nhost_db.update_threshold(user_id, whale_threshold)
        await update.message.reply_text(
            "Welcome back to SENTRA Whale Tracker! Your settings have been updated."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "SENTRA Whale Tracker Bot\n\n"
        "Commands:\n"
        "/start - Subscribe to whale alerts\n"
        "/help - Show this help message\n"
        "/track <wallet_address> - Track a specific wallet\n"
        "/threshold <amount> - Set your custom whale threshold (in USD)\n"
    )
    await update.message.reply_text(help_text)

async def track_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a wallet to track."""
    user_id = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("Please provide a wallet address to track.")
        return
    
    wallet_address = context.args[0]
    try:
        nhost_db.add_tracked_wallet(user_id, wallet_address)
        await update.message.reply_text(f"Now tracking wallet: {wallet_address}")
    except Exception as e:
        await update.message.reply_text(f"Error tracking wallet: {str(e)}")

async def set_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set custom whale threshold."""
    user_id = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("Please provide a threshold amount in USD.")
        return
    
    try:
        threshold = int(context.args[0])
        nhost_db.update_threshold(user_id, threshold)
        await update.message.reply_text(f"Whale threshold updated to ${threshold:,} USD")
    except ValueError:
        await update.message.reply_text("Please provide a valid number for the threshold.")
    except Exception as e:
        await update.message.reply_text(f"Error updating threshold: {str(e)}")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(telegram_token).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("track", track_wallet))
    application.add_handler(CommandHandler("threshold", set_threshold))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()