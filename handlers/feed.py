from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.filters import clean_text
import os

router = Router()

@router.message(F.text == "📢 Tulis Feed")
async def write_feed(message: types.Message):
    await message.answer("Kirim Teks untuk Feed (Auto-Post) atau Kirim Foto (Butuh Approval Admin).")

@router.message(F.text)
async def process_text_feed(message: types.Message):
    if not clean_text(message.text):
        return await message.answer("⚠️ Pesanmu mengandung kata kasar!")
    
    # Kirim langsung ke Channel Publik
    caption = f"👤 [FEED]\n\"{message.text}\"\n\n💌 Chat via @{os.getenv('BOT_USERNAME')}"
    await message.bot.send_message(os.getenv("FEED_CHANNEL_ID"), caption)
    await message.answer("✅ Teks kamu sudah tayang di Channel Feed!")

@router.message(F.photo)
async def feed_photo_req(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✅ Approve", callback_data=f"app_{message.from_user.id}"))
    
    # Kirim ke Grup Admin Privat untuk disetujui
    await message.bot.send_photo(
        os.getenv("ADMIN_GROUP_ID"), 
        message.photo[-1].file_id, 
        f"📩 REQUEST FEED FOTO\nUser: {message.from_user.id}", 
        reply_markup=builder.as_markup()
    )
    await message.answer("⏳ Fotomu sedang ditinjau Admin. Akan muncul di channel jika disetujui.")

@router.callback_query(F.data.startswith("app_"))
async def approve_callback(call: types.CallbackQuery):
    # Kirim foto yang disetujui ke Channel Publik
    await call.bot.send_photo(
        os.getenv("FEED_CHANNEL_ID"), 
        call.message.photo[-1].file_id, 
        f"📸 [NEW FEED FOTO]\n💌 Chat via @{os.getenv('BOT_USERNAME')}"
    )
    await call.message.edit_caption(caption="✅ TELAH DISETUJUI & TAYANG")
    await call.answer("Berhasil diposting!")
  
