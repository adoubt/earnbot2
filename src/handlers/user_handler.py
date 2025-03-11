import asyncio
from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command,StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.keyboards import user_keyboards

from src.methods.database.users_manager import UsersDatabase
from src.methods.database.videos_manager import VideosDatabase

router =  Router()

from src.misc import bot, SUPER_ADMIN
from src.handlers.decorators import new_user_handler

from src.methods.utils import parse_callback_data, is_valid_email, get_file_id

@router.message(Command("start"))
@new_user_handler
async def start_handler(message: Message, is_clb=False,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    requested = await UsersDatabase.get_value(user_id,'requested')
    await message.answer("""Nuestra empresa tiene un acuerdo con una agencia de publicidad para promocionar un vídeo en TikTok 📈
 
Por lo tanto, estamos dispuestos a pagar a cada usuario por ver vídeos cortos subidos por este bot.
 
⚠️ Tienes que ver los vídeos para ser recompensado. Los vídeos duran entre 10 y 15 segundos
 
💰 Puedes ganar hasta <b>50 Sol</b> diariamente viendo vídeos
 
Para empezar, pulse el botón "<b>Ver vídeos y ganar dinero 📺</b>".""",parse_mode="HTML",reply_markup=user_keyboards.get_start_kb(requested))
    


































@router.callback_query(lambda clb: clb.data.startswith(""))

async def showcase_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    pass


@router.message(F.text == "⚙️")
async def settings_handler(message: Message, is_clb=False, **kwargs):
    pass

@router.message(F.text.startswith("🤍 W"))
async def wishlist_handler(message: Message, is_clb=False,current_page:int|None = 0,**kwargs):
    pass

@router.callback_query(lambda clb: clb.data == 'w')
async def wishlist_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    pass

class EditFile(StatesGroup):
    file_ask = State()

@router.callback_query(lambda clb: clb.data.startswith('editfile_'))
@new_user_handler
async def editfile_clb_handler(clb: CallbackQuery, state = FSMContext, is_clb=False, **kwargs):
    data = clb.data.split('_',2)
    product_id = int(data[2])
    await state.set_data([product_id,data[1]])
    file_type = data[1]
    if file_type == 'mp3':
        text = 'Upload or forward .MP3'
    elif file_type == 'wav':
        text = 'Upload or forward .WAV'
    elif file_type == 'stems':
        text = 'Upload or forward .ZIP (or other archive)'
    elif file_type == 'preview':
        text = 'Upload or forward preview .MP3 '
    await state.set_state(EditFile.file_ask)
    
    await clb.message.edit_text(text=text,reply_markup =user_keyboards.get_edit_file_kb(product_id,file_type))



@router.message(EditFile.file_ask)
async def file_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    data = await state.get_data()
    product_id = data[0]
    file_type = data[1]
    link = get_file_id(message, file_type)
    await state.clear()
        

@router.callback_query(lambda clb: clb.data == 'hide_file')
async def hide_file_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await clb.message.delete()
