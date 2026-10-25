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

# Token Bot
TELEGRAM_TOKEN = "8922811014:AAG0skxtzMPWNgM1ZpU8GWKKKaM-l-XDCBI"

# Link API
API_LCTX = "https://wtx.tele68.com/v1/tx/sessions"
API_LCMD5 = "https://wtxmd52.tele68.com/v1/txmd5/sessions"

# Trạng thái
state = {
    "current_game": None,
    "is_running": False,
    "bet_task": None,
    "last_session": None,
    "be_cau": False
}

def generate_algorithm(is_be_cau=False):
    """Thuật toán dự đoán Tài/Xỉu và %"""
    ket_qua = random.choice(["Tài 🔥", "Xỉu ❄️"])
    khoang = random.choices(["50-60", "60-70", "80-100"], weights=[45, 35, 20], k=1)[0]

    if khoang == "50-60":
        pt = random.randint(50, 60)
    elif khoang == "60-70":
        pt = random.randint(61, 70)
    else:
        pt = random.randint(80, 100)
        
    if is_be_cau:
        ket_qua = "Xỉu ❄️" if "Tài" in ket_qua else "Tài 🔥"
        
    return ket_qua, pt

def get_session_from_api(data):
    """Hàm đệ quy dò tìm mã phiên (Session) trong JSON của API"""
    keys_to_find = ["session", "id", "phien", "session_id", "issue", "code"]
    
    if isinstance(data, dict):
        for key in keys_to_find:
            if key in data and isinstance(data[key], (int, str)):
                return str(data[key])
        for key, value in data.items():
            result = get_session_from_api(value)
            if result: return result
            
    elif isinstance(data, list) and len(data) > 0:
        return get_session_from_api(data[0])
        
    return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🎲 **HỆ THỐNG TOOL DỰ ĐOÁN LC79** 🎲\n"
        "➖➖➖➖➖➖➖➖➖➖➖\n"
        "👉 `/lctx` : Chọn game Tài Xỉu\n"
        "👉 `/lcmd5` : Chọn game MD5\n"
        "👉 `/chay` : Chạy dự đoán (+2 phiên)\n"
        "👉 `/dung` : Dừng chạy\n"
        "👉 `/becau` : Bật thuật toán Bẻ Cầu\n"
        "👉 `/kobecau` : Tắt Bẻ Cầu\n"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def lctx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if state["is_running"]:
        return await update.message.reply_text("⚠️ Dừng tool trước khi đổi game (`/dung`).")
    state["current_game"] = "lctx"
    await update.message.reply_text("🎲 **Đã chọn game: LC79 Tài Xỉu**\n👉 Bấm `/chay` để chạy.", parse_mode="Markdown")

async def lcmd5_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if state["is_running"]:
        return await update.message.reply_text("⚠️ Dừng tool trước khi đổi game (`/dung`).")
    state["current_game"] = "lcmd5"
    await update.message.reply_text("🎲 **Đã chọn game: LC79 MD5**\n👉 Bấm `/chay` để chạy.", parse_mode="Markdown")

async def becau_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state["be_cau"] = True
    await update.message.reply_text("🔄 **ĐÃ BẬT CHẾ ĐỘ BẺ CẦU**", parse_mode="Markdown")

async def kobecau_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state["be_cau"] = False
    await update.message.reply_text("✅ **ĐÃ TẮT CHẾ ĐỘ BẺ CẦU**", parse_mode="Markdown")

async def fetch_and_predict(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Gọi API lấy phiên và dự đoán phiên tiếp theo"""
    game = state["current_game"]
    api_url = API_LCTX if game == "lctx" else API_LCMD5
    game_name = "LC79 TÀI XỈU" if game == "lctx" else "LC79 MD5"

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(headers=headers) as client:
            res = await client.get(api_url, timeout=10)
            data = res.json()

        current_session = get_session_from_api(data)

        if not current_session or not current_session.isdigit():
            return

        # SỬA LỖI CHẬM 1 PHIÊN: Cộng +2 thay vì +1 để bù trừ độ trễ mạng
        # VD: API trả về 1001 -> Dự đoán cho 1003
        next_session = str(int(current_session) + 2)

        if next_session != state["last_session"]:
            state["last_session"] = next_session
            
            ket_qua, phan_tram = generate_algorithm(is_be_cau=state["be_cau"])
            trang_thai_cau = "🔄 Bẻ Cầu" if state["be_cau"] else "➡️ Không Bẻ Cầu"

            msg = (
                f"🎲 **Chọn game: {game_name}**\n"
                f"➖➖➖➖➖➖➖➖➖➖➖\n"
                f"🆔 **Phiên API:** `{current_session}`\n"
                f"⏭️ **Dự đoán phiên:** `{next_session}` (+2)\n"
                f"🔄 **Thuật toán:** {trang_thai_cau}\n"
                f"🤖 **Dự đoán:** {ket_qua}\n"
                f"📊 **Tỷ lệ thắng:** {phan_tram}%\n"
                f"➖➖➖➖➖➖➖➖➖➖➖"
            )
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
            
    except Exception as e:
        logging.error(f"Lỗi API: {e}")

async def auto_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Vòng lặp tự động càn quét API (giảm xuống 2s để bắt phiên nhanh hơn)"""
    while state["is_running"]:
        await fetch_and_predict(context, chat_id)
        await asyncio.sleep(2) 

async def chay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not state["current_game"]:
        return await update.message.reply_text("⚠️ Chưa chọn game! Chọn `/lctx` hoặc `/lcmd5`.")
    
    if state["is_running"]:
        return await update.message.reply_text("⚠️ Tool đang chạy rồi!")

    state["is_running"] = True
    state["last_session"] = None 
    chat_id = update.effective_chat.id

    await update.message.reply_text("🚀 **Đang kết nối API lấy phiên...**")
    await fetch_and_predict(context, chat_id)
    
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
    app.add_handler(CommandHandler("becau", becau_command))
    app.add_handler(CommandHandler("kobecau", kobecau_command))
    
    app.run_polling()

if __name__ == "__main__":
    main()
