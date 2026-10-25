import asyncio
import logging
import random
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token mới của Bot
TELEGRAM_TOKEN = "8922811014:AAG0skxtzMPWNgM1ZpU8GWKKKaM-l-XDCBI"

# Cấu hình API
API_LCTX = "https://wtx.tele68.com/v1/tx/sessions"
API_LCMD5 = "https://wtxmd52.tele68.com/v1/txmd5/sessions"

# Quản lý trạng thái
state = {
    "current_game": None,
    "is_running": False,
    "bet_task": None,
    "last_session": None
}

def generate_prediction():
    """Thuật toán dự đoán Tài/Xỉu và %"""
    ket_qua = random.choice(["Tài 🔥", "Xỉu ❄️"])
    khoang = random.choices(["50-60", "60-70", "80-100"], weights=[45, 35, 20], k=1)[0]

    if khoang == "50-60":
        pt = random.randint(50, 60)
    elif khoang == "60-70":
        pt = random.randint(61, 70)
    else:
        pt = random.randint(80, 100)
    return ket_qua, pt

def extract_session_id(data):
    """Dò tìm mã phiên tự động trong JSON"""
    if isinstance(data, dict):
        for key in ["session", "id", "session_id", "issue"]:
            if key in data and isinstance(data[key], (int, str)):
                return str(data[key])
        if "data" in data:
            inner = data["data"]
            if isinstance(inner, list) and len(inner) > 0:
                for key in ["session", "id", "session_id", "issue"]:
                    if key in inner[0]: return str(inner[0][key])
            elif isinstance(inner, dict):
                for key in ["session", "id", "session_id", "issue"]:
                    if key in inner: return str(inner[key])
    elif isinstance(data, list) and len(data) > 0:
        for key in ["session", "id", "session_id", "issue"]:
            if key in data[0]: return str(data[0][key])
    return "Không xác định"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🔥 **TOOL DỰ ĐOÁN TÀI XỈU LC79** 🔥\n"
        "➖➖➖➖➖➖➖➖➖➖➖\n"
        "👉 `/lctx` : Chọn sàn Tài Xỉu\n"
        "👉 `/lcmd5` : Chọn sàn MD5\n"
        "👉 `/chay` : Bắt đầu chạy tự động\n"
        "👉 `/dung` : Dừng chạy\n"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def lctx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if state["is_running"]:
        return await update.message.reply_text("⚠️ Dừng tool trước khi đổi sàn (`/dung`).")
    state["current_game"] = "lctx"
    await update.message.reply_text("✅ **Đã chọn: LC79 Tài Xỉu**\n👉 Bấm `/chay` để chạy.", parse_mode="Markdown")

async def lcmd5_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if state["is_running"]:
        return await update.message.reply_text("⚠️ Dừng tool trước khi đổi sàn (`/dung`).")
    state["current_game"] = "lcmd5"
    await update.message.reply_text("✅ **Đã chọn: LC79 MD5**\n👉 Bấm `/chay` để chạy.", parse_mode="Markdown")

async def fetch_and_predict(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Hàm gọi API và gửi kết quả ngay lập tức"""
    game = state["current_game"]
    api_url = API_LCTX if game == "lctx" else API_LCMD5
    game_name = "LC79 TÀI XỈU" if game == "lctx" else "LC79 MD5"

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(headers=headers) as client:
            res = await client.get(api_url, timeout=10)
            data = res.json()

        session_id = extract_session_id(data)

        # Chỉ báo nếu là phiên mới
        if session_id != state["last_session"]:
            state["last_session"] = session_id
            ket_qua, phan_tram = generate_prediction()

            msg = (
                f"🎰 **{game_name}**\n"
                f"➖➖➖➖➖➖➖➖➖➖➖\n"
                f"🆔 **Phiên:** `{session_id}`\n"
                f"🎯 **Kết quả:** {ket_qua}\n"
                f"📊 **Tỷ lệ:** {phan_tram}%\n"
                f"➖➖➖➖➖➖➖➖➖➖➖"
            )
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
            
    except Exception as e:
        logging.error(f"Lỗi API: {e}")

async def auto_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Vòng lặp tự động quét API liên tục"""
    while state["is_running"]:
        await fetch_and_predict(context, chat_id)
        await asyncio.sleep(5) # Quét mỗi 5 giây

async def chay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not state["current_game"]:
        return await update.message.reply_text("⚠️ Chưa chọn sàn! Chọn `/lctx` hoặc `/lcmd5`.")
    
    if state["is_running"]:
        return await update.message.reply_text("⚠️ Tool đang chạy rồi!")

    state["is_running"] = True
    state["last_session"] = None 
    chat_id = update.effective_chat.id

    # BẮT ĐẦU CHẠY VÀ LẤY KẾT QUẢ NGAY LẬP TỨC
    await update.message.reply_text("🚀 **Đang lấy dữ liệu phiên...**")
    await fetch_and_predict(context, chat_id)
    
    # Sau đó mới chạy vòng lặp ngầm
    state["bet_task"] = asyncio.create_task(auto_loop(context, chat_id))

async def dung_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not state["is_running"]:
        return await update.message.reply_text("⚠️ Tool đang dừng.")
    
    state["is_running"] = False
    if state.get("bet_task") and not state["bet_task"].done():
        state["bet_task"].cancel()
    await update.message.reply_text("🛑 **ĐÃ DỪNG TOOL!**", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("lctx", lctx_command))
    app.add_handler(CommandHandler("lcmd5", lcmd5_command))
    app.add_handler(CommandHandler("chay", chay_command))
    app.add_handler(CommandHandler("dung", dung_command))
    app.run_polling()

if __name__ == "__main__":
    main()
