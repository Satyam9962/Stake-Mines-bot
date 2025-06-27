import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from utils import generate_prediction_image
import os
import io

# --- Configuration ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
PASSKEY_BASIC = "AjdJe62BHkaie"
PASSKEY_KING = "Sushru73TyaMisGHn"
CHOOSE_PLAN, ASK_PASSKEY, ASK_SEED = range(3)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🪙 Mines Basic", callback_data="basic")],
        [InlineKeyboardButton("👑 Mines King (Recommended)", callback_data="king")]
    ]
    await update.message.reply_text(
        f"Namaste {user.first_name} 👋

"
        "🤖 Swagat hai aapka *Stake Mines Predictor Bot* mein!

"
        "Kripya ek plan choose kare niche se:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return CHOOSE_PLAN

async def choose_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan = query.data
    context.user_data["plan"] = plan
    await query.message.reply_text("🔐 Apna passkey bheje (sirf approved users ke liye):")
    return ASK_PASSKEY

async def check_passkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    correct = PASSKEY_BASIC if context.user_data["plan"] == "basic" else PASSKEY_KING
    if user_input == correct:
        await update.message.reply_text("✅ Passkey verified! Ab apna client seed bheje:")
        return ASK_SEED
    else:
        await update.message.reply_text("❌ Galat passkey. Dubara try kare:")
        return ASK_PASSKEY

async def receive_seed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    seed = update.message.text.strip()
    image = generate_prediction_image(seed)
    bio = io.BytesIO()
    bio.name = 'prediction.png'
    image.save(bio, 'PNG')
    bio.seek(0)
    await update.message.reply_photo(photo=bio, caption="🟩 Yeh rahe 5 safe tiles!
Type 'Next' for new prediction.")
    return ASK_SEED

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_PLAN: [CallbackQueryHandler(choose_plan)],
            ASK_PASSKEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_passkey)],
            ASK_SEED: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_seed)]
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)
    logger.info("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
