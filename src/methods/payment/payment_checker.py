from methods.database.orders_manager import OrdersDatabase
from src.methods.payment import aaio_manager
from methods.payment.process import ProcessOrder
import asyncio

async def run_order_status_checker():
    # Создается таблица ордеров, если ее нет. 
    await OrdersDatabase.create_table()

    while True:
        pending_orders = await OrdersDatabase.get_pending_orders()
        if pending_orders != -1:
            await asyncio.gather(*[process_pending_order(pending_order) for pending_order in pending_orders])
        
        await asyncio.sleep(5)

async def process_pending_order(pending_order):
    order_id, pending_link, user_id, product_id = pending_order[:4]
    status = await aaio_manager.pending_status(pending_link)
    
    if status == 1: # Если оплата прошла успешно
        await ProcessOrder.success_order(user_id, product_id, order_id) 
    elif status == 2: # Если оплата просрочена
        await ProcessOrder.expired_order(user_id, order_id)