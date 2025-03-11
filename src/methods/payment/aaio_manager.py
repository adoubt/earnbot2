from src.misc import  MERCHANT_ID, SECRET
from loguru import logger
import aiohttp, random, hashlib
from urllib.parse import urlencode
from typing import Optional, Tuple

async def get_pay_link(amount : float,
                        merchant_id: Optional[str]= MERCHANT_ID,
                        secret:  Optional[str]= SECRET,
                        desc :Optional[str] = '',
                        currency :Optional[str]= 'RUB') -> Tuple[str, str]:
    
    pay_link, order_id = generate_pay_link(merchant_id, amount, currency, secret, desc)
    return pay_link, order_id # Ссылка на оплату


def generate_pay_link(merchant_id_aaio:str,
                        amount_aaio:float,
                        currency_aaio:str,
                        secret_aaio:str,
                        desc_aaio:str) -> Tuple[str, str]:
    """Генерация рандомных чисел для  № заказа"""
    rand = "1234567890"
    number = ''.join(random.choice(list(rand)) for _ in range(10))

    """Язык формы"""
    lang = 'ru'

    sign = f'{merchant_id_aaio}:{amount_aaio}:{currency_aaio}:{secret_aaio}:{number}'
    params = {
        'merchant_id': merchant_id_aaio,
        'amount': amount_aaio,
        'currency': currency_aaio,
        'order_id': number,
        'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
        'desc': desc_aaio,
        'lang': lang
    }

    pay_link = "https://aaio.io/merchant/pay?" + urlencode(params)
    order_id = number
    return pay_link, order_id


async def pending_status(pay_link:str) -> int:
        
        # return 1
        try:
            status = await check_payment(pay_link)
            return status #Если статус 0-2
        except aiohttp.ClientError as e:
            logger.info(f"Не удалось получить ответ от AAIO. pay_link: {pay_link}. E: {e}")
            return 4 #неизвестная ошибка от платежки
        

async def check_payment(pay_link: str) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.get(pay_link) as response:
            content = await response.text()
            if '<span class="mb-2">Заказ просрочен. Оплатить заказ необходимо было' in content:
                return 2
            elif '<span class="mb-2">Заказ успешно был оплачен</span>' in content:
                return 1
            else:
                return 0