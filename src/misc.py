from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN=os.getenv('BOT_TOKEN')
SUPER_ADMIN = os.getenv('SUPER_ADMIN')
PASSWORD = os.getenv('PASSWORD') # /set_admin{PASSWORD}
CHANNEL = 0
CHANNEL_LINK = ''

bot_id = BOT_TOKEN.split(":",1)[0]
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
