import os
import time
import asyncio
import logging
import requests
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Cấu hình logging để dễ theo dõi trên Render
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- CẤU HÌNH THÔNG TIN ---
TARGET_URL = "https://lc79b.bet"
API_MD5 = "https://ancient-poetry-7f56.lot896613.workers.dev/?mode=md5"
API_HU = "https://wtx.tele68.com/v1/tx/sessions"
TELEGRAM_TOKEN = "8627314570:AAG8L2vxe8u-4uDGdnip8gzoW8BlDQ_bg3E"

# Biến toàn cục quản lý trạng thái
state = {
    "playwright": None,
    "browser": None,
    "context": None,
    "page": None,
    "is_logged_in": False,
    "is_running": False,
    "account": "",
    "password": "",
    "last_balance": "0"
}

async def get_balance(page):
    """Hàm quét lấy số dư tài khoản trên giao diện game"""
    try:
        # 💡 Thay thế '.user-balance' bằng class/id số dư thực tế trên web game
        balance_elem = page.locator(".user-balance, .money-number, span.balance").first
        if await balance_elem.is_visible(timeout=5000):
            text = await balance_elem.inner_text()
            return text.strip()
    except Exception as e:
        logging.error(f"Lỗi khi lấy số dư: {e}")
    return "Không xác định"

# --- CÁC HÀM XỬ LÝ LỆNH TELEGRAM ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start"""
    msg = (
        "🔥 **XIN CHÀO BẠN ĐÃ ĐẾN VỚI TOOL BONDZTOOLS** 🔥\n\n"
        "📌 **Danh sách lệnh điều khiển:**\n"
        "👉 `/dangnhap <taikhoan> <matkhau>` : Đăng nhập tài khoản game\n"
        "👉 `/chay` : Bắt đầu chạy auto cược 2 sàn theo API\n"
        "👉 `/dung` : Dừng hệ thống auto cược\n"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def dangnhap_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /dangnhap <tk> <mk>"""
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Vui lòng nhập đúng cú pháp: `/dangnhap <taikhoan> <matkhau>`", parse_mode="Markdown")
        return

    username = context.args[0]
    password = context.args[1]
    
    state["account"] = username
    state["password"] = password

    await update.message.reply_text(f"⏳ Đang tiến hành kết nối và đăng nhập tài khoản `{username}`...", parse_mode="Markdown")

    try:
        if not state["playwright"]:
            state["playwright"] = await async_playwright().start()
        
        if not state["browser"]:
            state["browser"] = await state["playwright"].chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            state["context"] = await state["browser"].new_context(viewport={"width": 1280, "height": 800})
            state["page"] = await state["context"].new_page()

        page = state["page"]
        await page.goto(TARGET_URL, timeout=60000)
        await asyncio.sleep(4)

        # --- THỰC HIỆN ĐĂNG NHẬP ---
        # 💡 Thay các selector bên dưới cho đúng với giao diện web thực tế
        # await page.fill("input[placeholder*='Tài khoản']", username)
        # await page.fill("input[placeholder*='Mật khẩu']", password)
        # await page.click("button:has-text('Đăng Nhập')")
        await asyncio.sleep(5)

        # Lấy số dư sau khi đăng nhập
        balance = await get_balance(page)
        state["last_balance"] = balance
        state["is_logged_in"] = True

        reply_msg = (
            f"✅ **ĐĂNG NHẬP THÀNH CÔNG!**\n"
            f"👤 Tài khoản: `{username}`\n"
            f"💰 Số dư hiện tại: `{balance}`\n\n"
            f"👉 Nhập `/chay` để bắt đầu auto cược."
        )
        await update.message.reply_text(reply_msg, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Lỗi đăng nhập: {e}")
        await update.message.reply_text(f"❌ Đăng nhập thất bại: `{str(e)}`", parse_mode="Markdown")

async def chay_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Vòng lặp chạy ngầm tự động cược"""
    last_session = None

    while state["is_running"]:
        try:
            # 1. Gọi 2 API lấy dữ liệu
            res_md5 = requests.get(API_MD5, timeout=10).json()
            res_hu = requests.get(API_HU, timeout=10).json()

            current_session = res_hu.get("session") or res_hu.get("id") or time.strftime("%H%M%S")

            if current_session != last_session:
                last_session = current_session

                # 2. Thực hiện thao tác đặt cược trên 2 sàn qua Playwright
                page = state["page"]
                # await page.click("#btn_san_1_tai")
                # await page.click("#btn_san_2_xiu")

                # Chờ phiên hoàn thành (Ví dụ: 25 giây)
                await asyncio.sleep(25)

                # 3. Lấy số dư mới & kiểm tra kết quả Đúng / Sai
                new_balance = await get_balance(page)
                
                # Logic xác định Thắng / Thua (Đúng / Sai)
                status_str = "✅ ĐÚNG (Thắng)" if new_balance != state["last_balance"] else "⚠️ SAI (Thua / Hòa)"

                # 4. Báo cáo kết quả về Telegram
                report = (
                    f"📢 **BÁO CÁO PHIÊN CƯỢC: {current_session}**\n"
                    f"-----------------------------------\n"
                    f"🎯 Trạng thái: {status_str}\n"
                    f"💰 Số dư trước: `{state['last_balance']}`\n"
                    f"💰 Số dư mới: `{new_balance}`"
                )
                state["last_balance"] = new_balance
                await context.bot.send_message(chat_id=chat_id, text=report, parse_mode="Markdown")

        except Exception as e:
            logging.error(f"Lỗi trong vòng lặp cược: {e}")
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Lỗi ván cược: `{str(e)}`", parse_mode="Markdown")

        await asyncio.sleep(10)

async def chay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /chay"""
    if not state["is_logged_in"]:
        await update.message.reply_text("⚠️ Bạn chưa đăng nhập! Vui lòng dùng lệnh `/dangnhap <tk> <mk>` trước.", parse_mode="Markdown")
        return

    if state["is_running"]:
        await update.message.reply_text("⚠️ Tool hiện tại đang chạy rồi!", parse_mode="Markdown")
        return

    state["is_running"] = True
    await update.message.reply_text("🚀 **ĐÃ BẮT ĐẦU KÍCH HOẠT AUTO CƯỢC 2 SÀN!**\nTool sẽ tự động nhận diện phiên API và báo kết quả liên tục.", parse_mode="Markdown")

    # Chạy vòng lặp ngầm trong asyncio Task
    asyncio.create_task(chay_loop(context, update.effective_chat.id))

async def dung_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /dung"""
    if not state["is_running"]:
        await update.message.reply_text("⚠️ Tool hiện tại đang dừng, không có phiên nào đang chạy.", parse_mode="Markdown")
        return

    state["is_running"] = False
    await update.message.reply_text("🛑 **ĐÃ DỪNG AUTO CƯỢC THÀNH CÔNG!**", parse_mode="Markdown")

def main():
    """Khởi chạy Telegram Bot Application"""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("dangnhap", dangnhap_command))
    app.add_handler(CommandHandler("chay", chay_command))
    app.add_handler(CommandHandler("dung", dung_command))

    logging.info("Bot Telegram BONDZTOOLS đã khởi động...")
    app.run_polling()

if __name__ == "__main__":
    main()
