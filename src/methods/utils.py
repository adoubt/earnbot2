import urllib.parse
import re
from aiogram.types import Message
from src.misc import bot,CHANNEL
from src.methods.database.users_manager import UsersDatabase
from loguru import logger

def get_file_id(message: Message, file_type: str) -> str:
    """Проверка основного сообщения"""
    if message.audio and file_type in ['mp3', 'preview']:
        return message.audio.file_id
    elif message.document and file_type in ['wav', 'stems']:
        return message.document.file_id
    #Проверка вложенного сообщения
    elif message.reply_to_message:
        if message.reply_to_message.audio and file_type in ['mp3', 'preview']:
            return message.reply_to_message.audio.file_id
        elif message.reply_to_message.document and file_type in ['wav', 'stems']:
            return message.reply_to_message.document.file_id
    return None

def parse_callback_data(data: str) -> dict:
    """Удаляем префикс и парсим параметры"""
    query_string = data.split(':', 1)[1]
    return dict(urllib.parse.parse_qsl(query_string))

def is_valid_email(email):
    """Определение шаблона для валидации email-адреса"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

async def process_referral(user_id: int, level: int = 1):
    """Обрабатывает рефералку на любом уровне"""
    bonus_levels = {1: 5.0, 2: 2.5}  # Можно добавить больше уровней
    referral_field = "referrals" if level == 1 else "rereferrals"
    amount = bonus_levels.get(level, 0)  # Если уровень больше 2, начисления нет

    if amount > 0:
        await UsersDatabase.refer(user_id=user_id, amount=amount, **{referral_field: 1})

    # Получаем данные о пользователе
    data = await UsersDatabase.get_user(user_id)
    balance, referrals, rereferrals, username, referrer = data[3], data[5], data[6], data[7], data[4]

    # Формируем сообщение
    message = f"""🎉 {"Alguien se registró en el bot usando su enlace" if level == 1 else "Alguien se registró en el bot utilizando el enlace de tu amigo"} 🎉

<b>+ {amount:.1f} Sol</b> 💰 

📢 Has invitado a: <b>{referrals} usuarios</b>
📣 Tus amigos han invitado a: <b>{rereferrals} usuarios</b>
💸 Su saldo: <b>{balance} Sol</b>"""

    # Отправляем сообщение пользователю
    try:
        await bot.send_message(user_id, message, parse_mode="HTML")
    except:
        logger.error(f'@{username}({user_id}) didn\'t receive the message')

    # Рекурсивно начисляем бонусы рефереру
    if referrer and level < len(bonus_levels):
        await process_referral(referrer, level + 1)


    


async def is_user_subscribed(user_id: int, **kwargs):

    member = await bot.get_chat_member(CHANNEL, user_id)
    if member.status in ["member", "creator", "administrator"]:
        return True
    else:
        return False