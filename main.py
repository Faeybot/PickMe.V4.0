import asyncio
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from database import init_db
from handlers import register, feed, dating
from utils.scheduler import setup_scheduler

load_dotenv()

async def main():
    # 1. Inisialisasi Database (Membuat tabel otomatis)
    await init_db()
    
    # 2. Jalankan Penjadwal (Reset kuota jam 00:00)
    setup_scheduler()
    
    # 3. Inisialisasi Bot & Dispatcher
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    
    # 4. Atur Menu Tombol di Pojok Kiri Bawah Telegram
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Daftar / Reset Profil"),
        types.BotCommand(command="menu", description="Buka Menu Utama"),
    ])

    # 5. Daftarkan Semua Handler (Logic)
    dp.include_routers(register.router, feed.router, dating.router)
    
    # 6. Mulai Bot (Menghapus antrean pesan lama agar tidak lag)
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 PickMe Bot siap digunakan!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot Berhenti.")
      
