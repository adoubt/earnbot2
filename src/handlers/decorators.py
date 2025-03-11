from src.methods.database.users_manager import UsersDatabase
from src.methods.database.licenses_manager import LicensesDatabase
from aiogram.types import Message

from loguru import logger
from src.misc import bot_id

def new_seller_handler(function):
    async def _new_seller_handler(*args, **kwargs):
        message: Message = args[0]
        user_id = message.from_user.id
        if (await UsersDatabase.get_value(user_id, 'is_seller')) == 0:
            await UsersDatabase.set_value(user_id, 'is_seller', 1)
            await LicensesDatabase.set_default(user_id)
        return await function(*args, **kwargs)

    return _new_seller_handler


def new_user_handler(function):
    async def _new_user_handler(*args, **kwargs):
        message: Message = args[0]
        user_id = message.from_user.id
        username =message.from_user.username
        language = message.from_user.language_code
        # username = message.
        if (await UsersDatabase.get_user(user_id)) == -1:
            await UsersDatabase.create_user(user_id=user_id,username = username,language = language)
            
            logger.success(f"Новый пользователь (ID: {user_id})")
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