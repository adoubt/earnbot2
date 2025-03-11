import aiosqlite
from typing import Any, List, Optional, Tuple
from loguru import logger
from typing import List, Tuple, Optional
from contextlib import asynccontextmanager

# Настройка логирования
logger.add("src/logs/orders.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip")
logger.add("src/logs/errors.log", format="{time} {level} {message}", level="ERROR", rotation="5 MB", compression="zip")
DB_PATH = "src/databases/orders.db"

class Database:
    """Асинхронный класс для работы с базой данных."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    @asynccontextmanager
    async def get_db_connection(self):
        """Асинхронный контекстный менеджер для работы с базой данных."""
        db = await aiosqlite.connect(self.db_path)
        try:
            yield db
        finally:
            await db.commit()
            await db.close()

    async def execute(self, query: str, params: tuple = ()) -> None:
        """Выполнение запроса без возврата значений."""
        async with self.get_db_connection() as db:
            await db.execute(query, params)

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Tuple]:
        """Получить одну запись."""
        async with self.get_db_connection() as db:
            cursor = await db.execute(query, params)
            return await cursor.fetchone()

    async def fetch_all(self, query: str, params: tuple = ()) -> List[Tuple]:
        """Получить все записи."""
        async with self.get_db_connection() as db:
            cursor = await db.execute(query, params)
            return await cursor.fetchall()

class OrdersDAL:
    def __init__(self, db: Database):
        self.db = db
    
    # SQL Queries
    CREATE_TABLE_QUERY = '''CREATE TABLE IF NOT EXISTS orders(
                                order_id INTEGER PRIMARY KEY,
                                user_id INTEGER NOT NULL,
                                promo_code_id INTEGER DEFAULT NULL,
                                subtotal_amount REAL NOT NULL,
                                service_fee REAL NOT NULL,
                                status TEXT CHECK(status IN ('pending', 'paid', 'expired', 'failed')) DEFAULT 'pending',
                                total_amount REAL NOT NULL,
                                payment_method TEXT,
                                invoice_id INTEGER NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                paid_at TIMESTAMP DEFAULT NULL)'''

    INSERT_ORDER_QUERY = '''INSERT INTO orders(user_id, promo_code_id,subtotal_amount,service_fee, total_amount, payment_method, cart_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?)'''

    SELECT_ORDER_VALUE_QUERY = '''SELECT {key} FROM orders WHERE order_id = ?'''
    SELECT_ORDERS_BY_STATUS_QUERY = '''SELECT * FROM orders WHERE status = ?'''
    SELECT_ORDERS_BY_USER_QUERY = '''SELECT * FROM orders WHERE user_id = ?{status_clause}'''
    UPDATE_ORDER_VALUE_QUERY = '''UPDATE orders SET {key} = ? WHERE order_id = ?'''
    DELETE_ORDERS_BY_USER_AND_STATUS_QUERY = '''DELETE FROM orders WHERE user_id = ? AND status = ?'''
    SELECT_ORDER_ID_BY_USER_AND_STATUS_QUERY = '''SELECT order_id FROM orders WHERE user_id = ? AND status = ?'''

    async def create_table(self) -> None:
        logger.info("Creating orders table if not exists")
        await self.db.execute(self.CREATE_TABLE_QUERY)

    async def create_order(self, user_id: int, cart_id: int, subtotal_amount: float, service_fee: float, total_amount: float, 
                           payment_method: str = 'CryptoBot', promo_code_id: Optional[int] = None) -> int:
        logger.info(f"Creating order for user_id {user_id} with cart_id {cart_id}")
        await self.db.execute(self.INSERT_ORDER_QUERY, (user_id, promo_code_id, subtotal_amount, service_fee, total_amount, payment_method, cart_id))
        return self.db.lastrowid

    async def get_order_value(self, order_id: int, key: str) -> Optional[Any]:
        query = self.SELECT_ORDER_VALUE_QUERY.format(key=key)
        logger.info(f"Getting {key} value for order_id {order_id}")
        result = await self.db.fetch_one(query, (order_id,))
        return result[0] if result else None
    
    async def get_orders_by_status(self, status: str) -> List[Tuple]:
        logger.info(f"Getting orders with status {status}")
        return await self.db.fetch_all(self.SELECT_ORDERS_BY_STATUS_QUERY, (status,))
    
    async def get_orders_by_user(self, user_id: int, status: Optional[str] = None) -> List[Tuple]:
        status_clause = ' AND status = ?' if status else ''
        query = self.SELECT_ORDERS_BY_USER_QUERY.format(status_clause=status_clause)
        logger.info(f"Getting orders for user_id {user_id} with status {status}")
        return await self.db.fetch_all(query, [user_id, status] if status else [user_id])

    async def update_order_value(self, order_id: int, key: str, value: Any) -> None:
        query = self.UPDATE_ORDER_VALUE_QUERY.format(key=key)
        logger.info(f"Updating {key} value for order_id {order_id}")
        await self.db.execute(query, (value, order_id))

    async def delete_orders_by_user_and_status(self, user_id: int, status: str) -> None:
        logger.info(f"Deleting orders for user_id {user_id} with status {status}")
        await self.db.execute(self.DELETE_ORDERS_BY_USER_AND_STATUS_QUERY, (user_id, status))

    async def get_order_id_by_user_and_status(self, user_id: int, status: str) -> Optional[int]:
        logger.info(f"Getting order_id for user_id {user_id} with status {status}")
        result = await self.db.fetch_one(self.SELECT_ORDER_ID_BY_USER_AND_STATUS_QUERY, (user_id, status))
        return result[0] if result else None

class OrdersService:
    def __init__(self, db: Database):
        self.orders_dal = OrdersDAL(db)

    async def create_table(self) -> None:
        await self.orders_dal.create_table()
        
    async def create_order(self, user_id: int, cart_id: int, subtotal_amount: float, service_fee: float, total_amount: float, 
                           payment_method: str = 'CryptoBot', promo_code_id: Optional[int] = None) -> int:
        return await self.orders_dal.create_order(user_id, cart_id, subtotal_amount, service_fee, total_amount, payment_method, promo_code_id)

    async def get_order_status(self, order_id: int) -> Optional[str]:
        return await self.orders_dal.get_order_value(order_id, 'status')

    async def get_pending_orders(self) -> List[Any]:
        return await self.orders_dal.get_orders_by_status('pending')

    async def get_user_orders(self, user_id: int, status: Optional[str] = None) -> List[Any]:
        return await self.orders_dal.get_orders_by_user(user_id, status)

    async def update_order_status(self, order_id: int, status: str, paid_at: Optional[int] = None) -> None:
        await self.orders_dal.update_order_value(order_id, 'status', status)
        if paid_at:
            await self.orders_dal.update_order_value(order_id, 'paid_at', paid_at)

    async def delete_pending_orders(self, user_id: int) -> None:
        await self.orders_dal.delete_orders_by_user_and_status(user_id, 'pending')

    async def get_pending_order_id(self, user_id: int) -> Optional[int]:
        return await self.orders_dal.get_order_id_by_user_and_status(user_id, 'pending')
