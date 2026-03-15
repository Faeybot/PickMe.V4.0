import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from database import init_db
from handlers import register, feed, dating
from utils.scheduler import setup_scheduler

load_dotenv()

async def main():
    # 1. Pastikan tabel database sudah terbuat
    await init_db()
    
    # 2. Aktifkan penjadwal reset kuota
    setup_scheduler()
    
    # 3. Inisialisasi Bot
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    
    # 4. Daftarkan Perintah Menu (Bot Commands)
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Daftar / Reset Profil"),
        types.BotCommand(command="menu", description="Main Menu (Swipe/Feed)"),
    ])

    # 5. Hubungkan semua Handler (Register, Feed, Dating)
    dp.include_routers(register.router, feed.router, dating.router)
    
    # 6. Mulai Bot
    print("🚀 PickMe Bot is LIVE!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot Berhenti.")
    
