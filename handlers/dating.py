import sys
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.dating_service import DatingService
from database import async_session
from models import User
import os

router = Router()

@router.message(F.text == "🔍 Cari Jodoh (Swipe)")
async def swipe_menu(message: types.Message):
    async with async_session() as session:
        # Ambil data user yang sedang mencari (untuk tahu lokasi & preferensi mereka)
        result = await session.get(User, message.from_user.id)
        if not result:
            return await message.answer("Silakan daftar dulu dengan mengetik /start")
        
        # Tentukan preferensi lawan jenis secara otomatis
        pref = "Wanita" if result.gender == "Pria" else "Pria"
        
        # Panggil service untuk cari user terdekat
        match_data = await DatingService.get_nearby_users(
            result.id, pref, result.latitude, result.longitude
        )

    if not match_data:
        return await message.answer("Yah, belum ada user baru di sekitarmu. Coba lagi nanti ya!")

    target, distance = match_data
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="❌ Skip", callback_data=f"skip_{target.id}"),
        types.InlineKeyboardButton(text="❤️ Like", callback_data=f"like_{target.id}")
    )
    builder.row(types.InlineKeyboardButton(text="🚩 Lapor", callback_data=f"rep_{target.id}"))

    caption = (
        f"🔥 **{target.full_name}, {target.age}th**\n"
        f"📍 Jarak: {round(distance, 1)} km dari lokasimu\n\n"
        f"\"{target.about_me}\"\n\n"
        f"✨ Minat: {target.interests}"
    )

    await message.answer_photo(
        photo=target.photo_id, 
        caption=caption, 
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("like_"))
async def handle_like(call: types.CallbackQuery):
    # Logika match bisa dikembangkan di sini (Simpan ke tabel Like)
    await call.answer("Kamu menyukai profil ini! ❤️")
    await call.message.delete()
    # Tampilkan profil selanjutnya otomatis
    await swipe_menu(call.message)

@router.callback_query(F.data.startswith("skip_"))
async def handle_skip(call: types.CallbackQuery):
    await call.answer("Banyak ikan di laut.. 🌊")
    await call.message.delete()
    await swipe_menu(call.message)
  
