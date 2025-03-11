from src.methods.database.users_manager import UsersDatabase
from aiogram.types import Message, CallbackQuery

from loguru import logger
from src.misc import bot_id, CHANNEL_LINK
from src.methods.utils import process_referral, is_user_subscribed
from src.keyboards import user_keyboards
# def new_seller_handler(function):
#     async def _new_seller_handler(*args, **kwargs):
#         message: Message = args[0]
#         user_id = message.from_user.id
#         if (await UsersDatabase.get_value(user_id, 'is_seller')) == 0:
#             await UsersDatabase.set_value(user_id, 'is_seller', 1)
#             await LicensesDatabase.set_default(user_id)
#         return await function(*args, **kwargs)

#     return _new_seller_handler


def new_user_handler(function):
    async def _new_user_handler(*args, **kwargs):
        message: Message = args[0]
        user_id = message.from_user.id
        
        # username = message.
        if (await UsersDatabase.get_user(user_id)) == -1:
            username =message.from_user.username
            language = message.from_user.language_code
            referr = message.text.split()[1] if len(message.text.split()) > 1 else None

            
            await UsersDatabase.create_user(user_id=user_id,username=username,language=language,referr=referr)
            if referr: await process_referral(referr)

            logger.success(f"Новый пользователь (ID: {user_id} username {username})")
            if user_id == int(bot_id):

                await UsersDatabase.set_value(user_id,'is_admin',1)
                #назначение бота админом для кнопок в админке(костыль, вроде пофикшен)
                logger.info(f'[Admin] {user_id} получил права админа')
            # else:
                # await message.answer(
                # "👋 Привет, вижу ты новенький. Будем знакомы, чтобы получить список моих команд напиши <code>/help</code>",
                # parse_mode="HTML")


        return await function(*args, **kwargs)

    return _new_user_handler


def pursue_subscription(function):
    async def _pursue_subscription(*args, **kwargs):
        msg = args[0]
        if msg is None:
            return

        if (await is_user_subscribed(msg.from_user.id)) or (
                type(msg) is CallbackQuery and (await is_user_subscribed(msg.message.from_user.id))):
            return await function(*args, **kwargs)
        msg_text = f'Для использования бота необходимо подписаться на канал.\n<a href="{CHANNEL_LINK}">Подписаться (кликабельно)</a>'
       
        

        await msg.answer(text=msg_text, parse_mode ="HTML",reply_markup=user_keyboards.get_subscription_kb(CHANNEL_LINK))
        return

    return _pursue_subscription