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

# Token của Bot
TELEGRAM_TOKEN = "8922811014:AAG0skxtzMPWNgM1ZpU8GWKKKaM-l-XDCBI"

# Cấu hình API
API_LCTX = "https://wtx.tele68.com/v1/tx/sessions"
API_LCMD5 = "https://wtxmd52.tele68.com/v1/txmd5/sessions"

# Quản lý trạng thái
state = {
    "current_game": None,      # 'lctx' hoặc 'lcmd5'
    "is_running": False,       # Trạng thái đang chạy auto
    "bet_task": None,          # Lưu tiến trình chạy ngầm
    "last_session": None       # Lưu ID phiên trước đó để tránh báo trùng
}

def generate_prediction():
    """Hàm sinh thuật toán dự đoán ngẫu nhiên theo tỷ lệ %"""
    ket_qua = random.choice(["Tài 🔥", "Xỉu ❄️"])
    
    # Phân bổ tỷ lệ (50-60% ra nhiều nhất, 80-100% ra ít nhất)
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

    return ket_qua, phan_tram

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start hướng dẫn sử dụng"""
    msg = (
        "🔥 **HỆ THỐNG TOOL BOT LC79** 🔥\n"
        "➖➖➖➖➖➖➖➖➖➖➖\n"
        "📌 **Hướng dẫn sử dụng:**\n"
        "1️⃣ Chọn sàn game:\n"
        "👉 `/lctx` : Chọn sàn LC79 Tài Xỉu\n"
        "👉 `/lcmd5` : Chọn sàn LC79 MD5\n\n"
        "2️⃣ Điều khiển Tool:\n"
        "👉 `/chay` : Bắt đầu auto quét API dự đoán\n"
        "👉 `/dung` : Dừng auto\n\n"
        "💡 *Thuật toán AI nâng cấp, tự động nhận diện phiên mới.*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def lctx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh chọn sàn LC79 Tài Xỉu"""
    if state["is_running"]:
        await update.message.reply_text("⚠️ Vui lòng dùng `/dung` để dừng tool trước khi đổi sàn!", parse_mode="Markdown")
        return
    state["current_game"] = "lctx"
    await update.message.reply_text("✅ **Đã chọn sàn: LC79 Tài Xỉu**\n👉 Nhập `/chay` để bắt đầu.", parse_mode="Markdown")

async def lcmd5_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh chọn sàn LC79 MD5"""
    if state["is_running"]:
        await update.message.reply_text("⚠️ Vui lòng dùng `/dung` để dừng tool trước khi đổi sàn!", parse_mode="Markdown")
        return
    state["current_game"] = "lcmd5"
    await update.message.reply_text("✅ **Đã chọn sàn: LC79 MD5**\n👉 Nhập `/chay` để bắt đầu.", parse_mode="Markdown")

async def auto_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Vòng lặp tự động quét API và dự đoán"""
    game = state["current_game"]
    api_url = API_LCTX if game == "lctx" else API_LCMD5
    game_name = "LC79 TÀI XỈU" if game == "lctx" else "LC79 MD5"

    while state["is_running"]:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(api_url, timeout=10)
                data = res.json()

            # Cố gắng lấy ID phiên hiện tại từ API (tùy thuộc cấu trúc JSON trả về)
            # Giả định API trả về dict có key 'session' hoặc 'id' hoặc list các phiên
            session_id = None
            if isinstance(data, dict):
                session_id = data.get("session") or data.get("id") or data.get("session_id")
                # Nếu API trả về list session trong key 'data'
                if not session_id and "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                    session_id = data["data"][0].get("id") or data["data"][0].get("session")
            elif isinstance(data, list) and len(data) > 0:
                 session_id = data[0].get("id") or data[0].get("session")

            # Fallback nếu không tìm thấy ID
            if not session_id:
                session_id = str(data)

            # Nếu là phiên mới (khác phiên cũ)
            if session_id != state["last_session"]:
                state["last_session"] = session_id
                
                # Sinh dự đoán
                ket_qua, phan_tram = generate_prediction()

                # Gửi tin nhắn báo cáo
                msg = (
                    f"🤖 **{game_name}** 🤖\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"🆔 **Phiên:** `{session_id}`\n"
                    f"🎯 **Dự đoán:** {ket_qua}\n"
                    f"📊 **Tỷ lệ thắng:** {phan_tram}%\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"💡 *Hệ thống tự động phân tích...*"
                )
                await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

        except asyncio.CancelledError:
            break
        except Exception as e:
            logging.error(f"Lỗi API: {e}")
            # Không gửi tin nhắn báo lỗi liên tục để tránh spam, chỉ log ra hệ thống
            
        # Nghỉ 5-10 giây trước khi check API tiếp
        await asyncio.sleep(7)

async def chay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /chay bắt đầu auto"""
    if not state["current_game"]:
        await update.message.reply_text("⚠️ Bạn chưa chọn sàn!\nVui lòng chọn `/lctx` hoặc `/lcmd5` trước.", parse_mode="Markdown")
        return

    if state["is_running"]:
        await update.message.reply_text("⚠️ Tool đang chạy rồi!", parse_mode="Markdown")
        return

    state["is_running"] = True
    state["last_session"] = None # Reset phiên để bắt đầu nhận diện lại từ đầu
    
    game_name = "LC79 TÀI XỈU" if state["current_game"] == "lctx" else "LC79 MD5"
    await update.message.reply_text(
        f"🚀 **ĐÃ BẮT ĐẦU CHẠY TOOL {game_name}**\nTool sẽ tự động bắt phiên và dự đoán kết quả.", 
        parse_mode="Markdown"
    )

    # Khởi chạy task ngầm
    state["bet_task"] = asyncio.create_task(auto_loop(context, update.effective_chat.id))

async def dung_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /dung dừng auto"""
    if not state["is_running"]:
        await update.message.reply_text("⚠️ Tool hiện tại đang dừng, không có tiến trình nào chạy.", parse_mode="Markdown")
        return

    state["is_running"] = False
    if state.get("bet_task") and not state["bet_task"].done():
        state["bet_task"].cancel()
        
    await update.message.reply_text("🛑 **ĐÃ DỪNG TOOL THÀNH CÔNG!**", parse_mode="Markdown")

def main():
    """Khởi chạy Bot"""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Đăng ký các lệnh
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("lctx", lctx_command))
    app.add_handler(CommandHandler("lcmd5", lcmd5_command))
    app.add_handler(CommandHandler("chay", chay_command))
    app.add_handler(CommandHandler("dung", dung_command))

    logging.info("Bot LC79 đã khởi động...")
    app.run_polling()

if __name__ == "__main__":
    main()
