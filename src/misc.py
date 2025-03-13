from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN=os.getenv('BOT_TOKEN')
SUPER_ADMIN = os.getenv('SUPER_ADMIN')
PASSWORD = os.getenv('PASSWORD') # /set_admin{PASSWORD}
LOG_CHANNEL_LINK = 'https://t.me/+hDKuiFhOBOc4YmQ1'
LOG_CHANNEL_ID = -1001971599660
CHANNEL_ID = '-1001971599660'
CHANNEL_LINK = 'https://t.me/+hDKuiFhOBOc4YmQ1'
TIME_REQUEST = 60*60*48
WATCHED_VIDEOS_THRESHOLD = 5
AD_MSG_WITHDRAW = '''Para enviar una solicitud de eliminación, debe estar suscrito al canal de nuestro patrocinador.

Este chico es un joven millonario de Perú, a la edad de 26 años ha logrado un éxito increíble en su trabajo y ahora ayuda a las personas a ganar dinero en línea y comparte esta información en su canal.


Suscríbete a tu canal ahora mismo, mira de 5 a 10 publicaciones y haz clic para confirmar la suscripción✅'''

bot_id = BOT_TOKEN.split(":",1)[0]
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
