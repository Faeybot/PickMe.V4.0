from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import reset_quotas

def setup_scheduler():
    scheduler = AsyncIOScheduler()
    # Menjalankan fungsi reset_quotas setiap hari pukul 00:00
    scheduler.add_job(reset_quotas, 'cron', hour=0, minute=0)
    scheduler.start()
    print("⏰ Scheduler aktif: Kuota akan direset setiap tengah malam.")
  
