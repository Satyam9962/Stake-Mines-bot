import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from PIL import Image, ImageDraw
import random
import io

# --- Configuration ---
BOT_TOKEN = "7490545740:AAEcbWJN2nXrj1cdK6GCsRXkk_EQ5XkReNc"
PASSKEY = "AWsTYje72VvBbhuinkj"  # Only you will have this

# --- Conversation states ---
ASK_PASSKEY, ASK_CLIENT_SEED = range(2)

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Image Generator ---
def generate_prediction_image(seed: str):
    random.seed(seed)
    tile_size = 80
    grid_size = 5
    safe_tiles = random.sample(range(25), 5)

    img = Image.new("RGB", (tile_size * grid_size, tile_size * grid_size + 60), color=(25, 25, 35))
    draw = ImageDraw.Draw(img)

    for i in range(25):
        row, col = divmod(i, 5)
        x, y = col * tile_size, row * tile_size
        if i in safe_tiles:
            # Draw 3D green diamond
            draw.rectangle([x + 10, y + 10, x + tile_size - 10, y + tile_size - 10], fill=(0, 255, 0))
            draw.polygon([  # diamond corners
                (x + tile_size // 2, y),
                (x + tile_size - 10, y + tile_size // 2),
                (x + tile_size // 2, y + tile_size - 10),
                (x + 10, y + tile_size // 2)
            ], fill=(0, 200, 0))
        else:
            draw.rectangle([x + 15, y + 15, x + tile_size - 15, y + tile_size - 15], fill=(100, 100, 120))

    # Footer Box
    draw.rectangle([0, tile_size * 5 + 10, tile_size * 5, tile_size * 5 + 60], fill=(40, 150, 80))
    draw.text((tile_size * 5 // 2 - 80, tile_size * 5 + 25), "✅ Ready for next signal", fill=(255, 255, 255))

    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return output

# --- Bot Logic ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Hello {name}!\n\n✨ Aapka swagat hai hamare *Stake Mines Bot* me!\n\n"
        "Aage badhne ke liye kripya ek *passkey* dein, jo sirf aapke paas hona chahiye.",
        parse_mode="Markdown"
    )
    return ASK_PASSKEY

async def check_passkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == PASSKEY:
        await update.message.reply_text(
            "✅ Thank you! Access granted.\n\n⚠️ Sirf *3 mines* ke sath khelen.\nAb apna *client seed* bhejein:",
            parse_mode="Markdown"
        )
        return ASK_CLIENT_SEED
    else:
        await update.message.reply_text("❌ Galat passkey. Kripya sahi passkey dein.")
        return ASK_PASSKEY

async def handle_client_seed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    seed = update.message.text.strip()
    image_stream = generate_prediction_image(seed)
    await update.message.reply_photo(photo=image_stream, caption="🎯 Yahan hai aapka prediction!")
    return ASK_CLIENT_SEED

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Conversation cancelled.")
    return ConversationHandler.END

# --- Main ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PASSKEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_passkey)],
            ASK_CLIENT_SEED: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_client_seed)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("✅ Bot is running...")
    app.run_polling()
