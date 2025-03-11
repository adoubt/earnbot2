import aiosqlite
from typing import List, Tuple, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Cart:
    cart_id: int
    user_id: int
    status: str
    created_at :datetime
    updated_at:datetime


@dataclass
class CartItem:
    item_id: int
    cart_id: int
    product_id: int
    quantity: int
    license_id: int
    added_at:datetime
    is_reserved:int
    reserved_at:datetime
@dataclass
class AppliedCoupon:
    cart_id: int
    coupon_id:int
    applied_at:datetime

class Database:
    """Асинхронный класс для работы с базой данных."""

    def __init__(self, db_path: str = "src/databases/carts.db"):
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
    async def create_tables(self): 
        """Создать таблицы, если они не существуют.""" 
        async with self.get_db_connection() as db: 
            await db.execute(''' CREATE TABLE IF NOT EXISTS carts ( 
                             cart_id INTEGER PRIMARY KEY, 
                             user_id INTEGER NOT NULL, 
                             status TEXT NOT NULL DEFAULT "active", 
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ''') 
            
            await db.execute(''' CREATE TABLE IF NOT EXISTS items (
                              item_id INTEGER PRIMARY KEY, 
                             cart_id INTEGER NOT NULL, 
                             product_id INTEGER NOT NULL, 
                             quantity INTEGER NOT NULL DEFAULT 1, 
                             license_id INTEGER NOT NULL, 
                             added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                             is_reserved INTEGER DEFAULT 0,
                             reserved_at TIMESTAMP DEFAULT NULL
                             UNIQUE(product_id,cart_id)
                             FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ) ''') 
            
            await db.execute(''' CREATE TABLE IF NOT EXISTS applied_coupons (
                             id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                             cart_id INTEGER NOT NULL, 
                             coupon_id iNTEGER ,
                             applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                             UNIQUE(cart_id,coupon_id)
                             FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ) ''') 

            await db.commit()

class CartManager:
    """Менеджер для работы с корзинами."""

    def __init__(self, db: Database):
        self.db = db
    
    async def get_cart_by_user_id(self, user_id: int, status: str = 'active') -> Optional[Cart]:
        """Получить корзину по user_id и статусу."""
        result = await self.db.fetch_one(
            'SELECT * FROM carts WHERE user_id = ? AND status = ?', 
            (user_id, status)
        )
        return Cart(*result) if result else None

    async def create_cart(self, user_id: int) -> Cart:
        """Создать корзину для пользователя."""
        await self.db.execute(
            'INSERT INTO carts (user_id) VALUES (?)', 
            (user_id,)
        )
        return await self.get_cart_by_user_id(user_id, 'active')

    async def update_cart_status(self, cart: Cart, status: str) -> None:
        """Обновить статус корзины."""
        cart.status = status
        await self.db.execute(
            'UPDATE carts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE cart_id = ?', 
            (status,  cart.cart_id)
        ) 
    async def update_cart(self,cart:Cart)->None:
        """Зафиксировать время изменения корзины"""
        await self.db.execute(
            'UPDATE carts SET updated_at = CURRENT_TIMESTAMP WHERE cart_id = ?',
            (cart.cart_id,)
        )

class CartItemManager:
    """Менеджер для работы с товарами в корзине."""

    def __init__(self, db: Database):
        self.db = db
  
  
    async def add_item_to_cart(self, cart: Cart, product_id: int, license_id: int, quantity: int = 1) -> None:
        """Добавить товар в корзину."""
        await self.db.execute(
            'REPLACE INTO items (cart_id, product_id, quantity, license_id) VALUES (?, ?, ?, ?)', 
            (cart.cart_id, product_id, quantity, license_id)
        )


    async def remove_item_from_cart(self, cart: Cart, product_id: int) -> None:
        """Удалить товар из корзины."""
        await self.db.execute(
            'DELETE FROM items WHERE cart_id = ? AND product_id = ?', 
            (cart.cart_id, product_id)
        )

    async def get_items_from_cart(self, cart: Cart) -> List[CartItem]:
        """Получить все товары из корзины."""
        rows = await self.db.fetch_all( 
            'SELECT * FROM items WHERE cart_id = ?', 
            (cart.cart_id,)
        )
        return [CartItem(*row) for row in rows]

    async def clear_cart(self, cart: Cart) -> None:
        """Очистить корзину."""
        await self.db.execute(
            'DELETE FROM items WHERE cart_id = ?', 
            (cart.cart_id,)
        )

    async def count_items_in_cart(self, cart: Cart) -> int: 
        """Посчитать количество товаров в корзине.""" 
        result = await self.db.fetch_one(
             'SELECT COUNT(*) FROM items WHERE cart_id = ?', 
             (cart.cart_id,) ) 
        return result[0] if result else 0

    async  def check_item_in_cart(self, cart:Cart, product_id: int)-> CartItem:
        """Найти совпадение по product_id"""
        cart_item = await self.db.fetch_all(
            'SELECT * FROM items WHERE product_id = ? AND cart_id = ?',
            (product_id,cart.cart_id,)
        )
        return cart_item if cart_item else None
    ##################################
    ##                              ##
    ##     ОТРЕФАКТОРИ ЭТО БОЖЕ     ##
    ##                              ##
    ##################################
    async def is_item_reserved(self, cart: Cart, product_id: int, time_limit: int) -> bool:
        """Проверить, зарезервирован ли товар и не истек ли срок резервирования."""
        result = await self.db.fetch_one(
            '''
            SELECT is_reserved, reserved_at
            FROM items 
            WHERE cart_id = ? 
            AND product_id = ?
            ''',
            (cart.cart_id, product_id)
        )

        if result:
            is_reserved, reserved_at = result
            if reserved_at:
                # Если reserved_at не NULL, проверяем срок резервирования
                time_diff = await self.db.fetch_val(
                    '''
                    SELECT strftime('%s', 'now') - strftime('%s', reserved_at)
                    '''
                )
                if time_diff > time_limit:
                    # Время резервирования истекло, разрезервируем товар
                    await self.db.execute(
                        '''
                        UPDATE items 
                        SET is_reserved = 0, reserved_at = NULL
                        WHERE cart_id = ? 
                        AND product_id = ?
                        ''',
                        (cart.cart_id, product_id)
                    )
                
                    return False  # Товар больше не зарезервирован
            return is_reserved == 1
        return False

    
    async def reserve_item(self, cart: Cart, product_id: int) -> None:
        """Установить резерв для товара."""
        await self.db.execute(
            'UPDATE items SET is_reserved = 1, reserved_at = CURRENT_TIMESTAMP WHERE cart_id = ? AND product_id = ?',
            (cart.cart_id, product_id)
        )

    async def unreserve_item(self, cart: Cart, product_id: int) -> None:
        """Снять резерв с товара."""
        await self.db.execute(
            'UPDATE items SET is_reserved = 0, reserved_at = NULL WHERE cart_id = ? AND product_id = ?',
            (cart.cart_id, product_id)
        )
    
class AppliedCouponManager:
    """Сервис для работы с Coupon Codes."""
    
    def __init__(self, db: Database):
        self.db = db

    async def apply_coupon(self, cart: Cart, coupon_id) -> None:
        """Применить Coupon Code к товаром в корзине."""
        await self.db.execute(
            'REPLACE INTO applied_coupons (cart_id, coupon_id) VALUES (?, ?,)', 
            (cart.cart_id, coupon_id)
        )


class ShoppingCartService:
    """Сервис для работы с корзинами и товарами."""

    def __init__(self):
        self.db = Database()
        self.cart_manager = CartManager(self.db)
        self.cart_item_manager = CartItemManager(self.db)
        self.applied_coupon_manager = AppliedCouponManager(self.db)

    async def _initialize_db(self):
        """Инициализация БД асинхронно."""
        # Здесь не нужно использовать loop.run_until_complete, просто используйте await
        await self.db.create_tables()
    

    async def get_or_create_cart(self, user_id: int) -> Cart:
        """Получить корзину или создать новую."""
        cart = await self.cart_manager.get_cart_by_user_id(user_id)
        return cart if cart else await self.cart_manager.create_cart(user_id)

    async def add_item(self, user_id: int, product_id: int, license_id: int, quantity: int = 1) -> None:
        """Добавить товар в корзину."""
        cart = await self.get_or_create_cart(user_id)
        await self.cart_item_manager.add_item_to_cart(cart, product_id, license_id, quantity)
        await self.cart_manager.update_cart(cart)


    async def remove_item(self, user_id: int, product_id: int) -> None:
        """Удалить товар из корзины."""
        cart = await self.get_or_create_cart(user_id)  # Неважно время, просто нужен cart_id
        await self.cart_item_manager.remove_item_from_cart(cart, product_id)
        await self.cart_manager.update_cart(cart)

    async def get_cart_items(self, user_id: int) -> List[CartItem]:
        """Получить все товары в корзине пользователя."""
        cart = await self.get_or_create_cart(user_id)
        return await self.cart_item_manager.get_items_from_cart(cart)

    async def clear_cart(self, user_id: int) -> None:
        """Очистить корзину пользователя."""
        cart = await self.get_or_create_cart(user_id)
        await self.cart_item_manager.clear_cart(cart)
        await self.cart_manager.update_cart(cart)

    async def update_status(self, user_id: int, status: str) -> None:
        """Обновить статус корзины для пользователя."""
        cart = await self.get_or_create_cart(user_id)  # Неважно время, просто нужен cart_id
        await self.cart_manager.update_cart_status(cart, status )

    async def count_items_in_cart(self, user_id: int) -> int: 
        """Посчитать количество товаров в корзине пользователя.""" 
        cart = await self.get_or_create_cart(user_id)
        return await self.cart_item_manager.count_items_in_cart(cart)
    
    async def check_item_in_cart(self,user_id:int,product_id: int) -> CartItem:
        """Найти совпадение по product_id у пользователя"""
        cart = await self.get_or_create_cart(user_id)
        return await self.cart_item_manager.check_item_in_cart(cart,product_id)

    async def apply_coupon(self,user_id:int, coupon_id)-> None:
        """Применить купон"""
        cart = await self.get_or_create_cart(user_id)
        await self.applied_coupon_manager.apply_coupon(cart,coupon_id,)
    
    async def reserve_item(self, user_id: int, product_id: int) -> bool:
        """Зарезервировать товар."""
        cart = await self.get_or_create_cart(user_id)
        if await self.cart_item_manager.is_item_reserved(cart, product_id):
            return False
        await self.cart_item_manager.reserve_item(cart, product_id)
        return True

    async def unreserve_item(self, user_id: int, product_id: int) -> None:
        """Снять резерв с товара."""
        cart = await self.get_or_create_cart(user_id)
        await self.cart_item_manager.unreserve_item(cart, product_id)