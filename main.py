import logging
import random
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token của Bot
TELEGRAM_TOKEN = "8627314570:AAG8L2vxe8u-4uDGdnip8gzoW8BlDQ_bg3E"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start hướng dẫn sử dụng"""
    msg = (
        "🔥 **TOOL MD5 BONDZ WIBU ** 🔥\n"
        "➖➖➖➖➖➖➖➖➖➖➖\n"
        "📌 **Hướng dẫn sử dụng:**\n"
        "🎲 NHẬP ĐỂ DỰ ĐOÁN.\n"
        "🎲  THUẬT TOÁN SEX ANIME\n\n"
        "🎲 *Thuật toán AI phân tích .*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tự động nhận diện tin nhắn chứa mã MD5 32 hoặc 64 ký tự"""
    text = update.message.text.strip()

    # Kiểm tra xem tin nhắn có đúng là mã MD5 không (32 hoặc 64 ký tự hex)
    if re.match(r'^[a-fA-F0-9]{32}$', text) or re.match(r'^[a-fA-F0-9]{64}$', text):
        
        # --- THUẬT TOÁN DỰ ĐOÁN ---
        ket_qua = random.choice(["Tài 🔥", "Xỉu ❄️"])
        
        # Phân bổ tỷ lệ % (50-60, 60-70, 80-100)
        khoang_phan_tram = random.choices(
            ["50-60", "60-70", "80-100"], 
            weights=[45, 35, 20], 
            k=1
        )[0]

        if khoang_phan_tram == "50-60":
            phan_tram = random.randint(50, 60)
        elif khoang_phan_tram == "60-70":
            phan_tram = random.randint(61, 70)
        else:
            phan_tram = random.randint(80, 100)

        # Format tin nhắn trả về
        msg = (
            f"🤖 **TOOL MD5 BON IOS ** \n"
            f"➖➖➖➖➖➖➖➖➖➖➖\n"
            f"🔗 **Mã MD5:** `{text}`\n"
            f"🎯 **Dự đoán:** {ket_qua}\n"
            f"📊 **Tỷ lệ thắng:** {phan_tram}%\n"
            f"➖➖➖➖➖➖➖➖➖➖➖\n"
            f"💡 *Chúc bạn may mắn!*"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    
    # Nếu người dùng nhập chuỗi hex nhưng sai độ dài (ví dụ 31 hoặc 33 ký tự), có thể báo lỗi nhẹ
    elif re.match(r'^[a-fA-F0-9]+$', text) and len(text) in range(25, 70):
        await update.message.reply_text(
            "⚠️ **Sai định dạng!**\nVui lòng gửi mã MD5 có độ dài chính xác là 32 hoặc 64 ký tự.", 
            parse_mode="Markdown"
        )
    # Các tin nhắn chat bình thường khác bot sẽ tự động bỏ qua (không phản hồi)

def main():
    """Khởi chạy Bot"""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Lệnh /start
    app.add_handler(CommandHandler("start", start_command))
    
    # Tự động bắt mọi tin nhắn văn bản (không phải lệnh) để check MD5
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Bot TOOL MD5 BON IOS FREE đã khởi động...")
    app.run_polling()

if __name__ == "__main__":
    main()
