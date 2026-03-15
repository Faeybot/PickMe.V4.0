from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import FSInputFile
from models import User
from database import async_session
import os

router = Router()

# 1. Definisi State (Tidak berubah, tetap terkoneksi ke alur lama)
class Reg(StatesGroup):
    name = State()
    age = State()
    gender = State()
    interests = State()
    about = State()
    photo = State()
    loc = State()

# 2. Perintah /start dengan LOGO dan TOS
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    logo_path = "logo_pickme.png" # Pastikan file ini ada di root GitHub Anda
    tos_text = (
        "🔥 **Selamat Datang di PickMe!** 🔥\n"
        "Tempat cari jodoh terdekat & seru-seruan di Feed.\n\n"
        "⚖️ **SYARAT & KETENTUAN:**\n"
        "1. Berusia 18 tahun ke atas.\n"
        "2. Dilarang konten ilegal/judi.\n"
        "3. Laporan user lain akan ditinjau Admin.\n\n"
        "Apakah kamu setuju dan ingin mendaftar?"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✅ Setuju & Daftar", callback_data="accept_tos"))
    
    # Cek apakah file logo ada, jika ada kirim foto, jika tidak kirim teks saja
    if os.path.exists(logo_path):
        await message.answer_photo(
            photo=FSInputFile(logo_path),
            caption=tos_text,
            reply_markup=builder.as_markup()
        )
    else:
        await message.answer(tos_text, reply_markup=builder.as_markup())

# 3. Callback saat klik Setuju (Mulai masuk ke State Name)
@router.callback_query(F.data == "accept_tos")
async def start_reg(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Bagus! Mari mulai.\n\nSiapa namamu?")
    await state.set_state(Reg.name)
    await call.answer()

# 4. Alur pendaftaran selanjutnya (Tetap sinkron dengan database)
@router.message(Reg.name)
async def reg_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Berapa umurmu?")
    await state.set_state(Reg.age)

@router.message(Reg.age)
async def reg_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Gunakan angka saja ya (Contoh: 20)")
    await state.update_data(age=int(message.text))
    
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Pria"), KeyboardButton(text="Wanita")]
    ], resize_keyboard=True)
    await message.answer("Apa gender kamu?", reply_markup=kb)
    await state.set_state(Reg.gender)

@router.message(Reg.gender)
async def reg_gender(message: types.Message, state: FSMContext):
    if message.text not in ["Pria", "Wanita"]:
        return await message.answer("Klik tombol di bawah ya!")
    await state.update_data(gender=message.text)
    
    # Daftar Minat (Bisa Anda sesuaikan)
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Flirting"), KeyboardButton(text="DirtyTalk")],
        [KeyboardButton(text="Musik"), KeyboardButton(text="Traveling")]
    ], resize_keyboard=True)
    await message.answer("Pilih Minat / Vibe kamu:", reply_markup=kb)
    await state.set_state(Reg.interests)

@router.message(Reg.interests)
async def reg_int(message: types.Message, state: FSMContext):
    await state.update_data(interests=message.text)
    await message.answer("Tulis sedikit tentang kamu (About Me):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Reg.about)

@router.message(Reg.about)
async def reg_about(message: types.Message, state: FSMContext):
    await state.update_data(about_me=message.text)
    await message.answer("Kirim 1 Foto Profil terbaikmu:")
    await state.set_state(Reg.photo)

@router.message(Reg.photo, F.photo)
async def reg_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📍 Kirim Lokasi", request_location=True)]
    ], resize_keyboard=True)
    await message.answer("Terakhir, bagikan lokasimu untuk mencari jodoh terdekat:", reply_markup=kb)
    await state.set_state(Reg.loc)

@router.message(Reg.loc, F.location)
async def reg_loc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    
    # SIMPAN KE DATABASE (Terkoneksi ke models.py & database.py)
    async with async_session() as session:
        async with session.begin():
            new_u = User(
                id=user_id, 
                full_name=data['name'], 
                age=data['age'],
                gender=data['gender'], 
                interests=data['interests'],
                about_me=data['about_me'], 
                photo_id=data['photo'],
                latitude=message.location.latitude, 
                longitude=message.location.longitude
            )
            session.add(new_u)
    
    # MIRRORING KE ADMIN (Log pendaftaran)
    log_channel = os.getenv("LOG_CHANNEL_ID")
    if log_channel:
        await message.bot.send_photo(
            log_channel, 
            data['photo'], 
            f"🆕 **USER BARU DAFTAR**\n\nNama: {data['name']}\nID: `{user_id}`\nGender: {data['gender']}"
        )
    
    await message.answer("🎉 Akun kamu sudah aktif! Gunakan /menu untuk mulai mencari jodoh.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    
