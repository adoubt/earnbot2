from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN=os.getenv('BOT_TOKEN')
SUPER_ADMIN = os.getenv('SUPER_ADMIN')
PASSWORD = os.getenv('PASSWORD') 
LOG_CHANNEL_LINK = os.getenv('LOG_CHANNEL_LINK')
LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHANNEL_LINK = os.getenv('CHANNEL_LINK')
TIME_REQUEST = 60*60*48
WATCHED_VIDEOS_THRESHOLD = 5
BALANCE_THRESHOLD = 75000
REFERR_REWARD_RARE = 1500
REREFERR_REWARD_RATE = 750
AD_MSG_WITHDRAW = '''Para enviar una solicitud de retirada, debe estar suscrito al canal de nuestro patrocinador. 

Este chico es un joven millonario de Chile , a los 36 años tuvo un éxito increíble en su trabajo y ahora ayuda a la gente a ganar dinero por internet y comparte esta información en su canal


Suscríbase a su canal ahora mismo, vea de 5 a 10 publicaciones y haga clic para confirmar su suscripción✅'''
REWARD_RATE = 750
bot_id = BOT_TOKEN.split(":",1)[0]
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
