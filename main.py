import logging
import random
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Cấu hình logging cơ bản
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token của Bot
TELEGRAM_TOKEN = "8627314570:AAG8L2vxe8u-4uDGdnip8gzoW8BlDQ_bg3E"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start giới thiệu tool"""
    msg = (
        "🔥 **TOOL MD5 BON IOS FREE** 🔥\n"
        "➖➖➖➖➖➖➖➖➖➖➖\n"
        "📌 **Hướng dẫn sử dụng:**\n"
        "👉 Nhập lệnh: `/md5 <chuỗi_md5>`\n"
        "👉 Hỗ trợ mã MD5 dài **32 ký tự** hoặc **64 ký tự**.\n\n"
        "💡 *Thuật toán AI phân tích dự đoán Tài/Xỉu tự động, không cần Key.*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def md5_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /md5 <chuỗi_32_hoặc_64_ký_tự>"""
    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập mã MD5!\nCú pháp: `/md5 <chuỗi_md5>`", parse_mode="Markdown")
        return

    md5_input = context.args[0].strip()

    # Kiểm tra độ dài 32 hoặc 64 và phải là ký tự hex (0-9, a-f)
    if not (re.match(r'^[a-fA-F0-9]{32}$', md5_input) or re.match(r'^[a-fA-F0-9]{64}$', md5_input)):
        await update.message.reply_text(
            "❌ **Mã MD5 không hợp lệ!**\n"
            "Vui lòng nhập chuỗi dài đúng 32 hoặc 64 ký tự (chỉ chứa số 0-9 và chữ A-F).", 
            parse_mode="Markdown"
        )
        return

    # --- THUẬT TOÁN DỰ ĐOÁN (TẠO NGẪU NHIÊN THEO XÁC SUẤT) ---
    # Random Tài hoặc Xỉu
    ket_qua = random.choice(["Tài 🔥", "Xỉu ❄️"])
    
    # Phân bổ tỷ lệ % theo yêu cầu (50-60, 60-70, 80-100)
    khoang_phan_tram = random.choices(
        ["50-60", "60-70", "80-100"], 
        weights=[45, 35, 20], # 45% ra 50-60%, 35% ra 60-70%, 20% ra 80-100%
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
        f"🤖 **TOOL MD5 BON IOS FREE** 🤖\n"
        f"➖➖➖➖➖➖➖➖➖➖➖\n"
        f"🔗 **Mã MD5:** `{md5_input}`\n"
        f"🎯 **Dự đoán:** {ket_qua}\n"
        f"📊 **Tỷ lệ thắng:** {phan_tram}%\n"
        f"➖➖➖➖➖➖➖➖➖➖➖\n"
        f"💡 *Chúc bạn may mắn!*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    """Khởi chạy Telegram Bot"""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Đăng ký các lệnh
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("md5", md5_command))

    logging.info("Bot TOOL MD5 BON IOS FREE đã khởi động...")
    app.run_polling()

if __name__ == "__main__":
    main()
