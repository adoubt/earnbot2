import aiosqlite
from typing import List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from contextlib import asynccontextmanager

@dataclass
class Coupon:
    coupon_id: int                       # Уникальный идентификатор
    code: str                            # Код купона
    seller_id: int                       # ID продавца
    discount_value: int                  # Значение скидки (в процентах)
    status: str                          # Состояние купона ('active' или 'archived')
    usage_limit: Optional[int]           # Лимит использования (None, если без ограничений)
    used_cart_count: int                 # Количество применений в корзинах
    start_date: datetime                 # Дата начала действия
    end_date: Optional[datetime]         # Дата окончания действия (может быть None)

@dataclass
class CouponLicenses:
    coupon_id: int
    license_id: int


class Database:
    """Асинхронный класс для работы с базой данных."""

    def __init__(self, db_path: str = "src/databases/coupons.db"):
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
            await db.execute(''' CREATE TABLE IF NOT EXISTS coupon_codes (
    coupon_id INTEGER PRIMARY KEY AUTOINCREMENT,       
    code TEXT NOT NULL CHECK (LENGTH(code) BETWEEN 1 AND 15 AND code NOT LIKE '% %'),
    seller_id INTEGER NOT NULL,                 
    discount_value INTEGER NOT NULL CHECK (discount_value >= 1 AND discount_value <= 90),
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    end_date TIMESTAMP DEFAULT NULL,               
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    usage_limit INTEGER DEFAULT NULL,             
    used_cart_count INTEGER DEFAULT 0,            
    CONSTRAINT unique_code_per_seller UNIQUE (code, seller_id)
    )
 ''') 
            
            await db.execute(''' CREATE TABLE IF NOT EXISTS coupon_licenses (
                             id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             coupon_id INTEGER NOT NULL,
                             license_id INTEGER NOT NULL,
                             UNIQUE(coupon_id,license_id)
                             )''') 

            await db.commit()


class CouponManager:
    """Менеджер для работы с купонами."""

    def __init__(self, db: Database):
        self.db = db

    async def get_coupon(self, coupon_id: int, status: str = 'active') -> Optional[Coupon]:
        """Получить купон по coupon_id либо NONE."""
        result = await self.db.fetch_one(
                'SELECT * FROM coupon_codes WHERE coupon_id = ? AND status = ?', 
                (coupon_id, status)
            )
        return Coupon(*result) if result else None
    
    async def get_coupon_by_code(self, code: str, status: str = 'active') -> Optional[Coupon]:
        """Получить купон по code либо NONE."""
        result = await self.db.fetch_one(
                'SELECT * FROM coupon_codes WHERE code = ? AND status = ?', 
                (code, status)
            )
        return Coupon(*result) if result else None

    async def create_coupon(self, code: str, seller_id: int, discount_value: int, usage_limit: int = None) -> Coupon:
        """Создать купон и вернуть coupon_id."""
        # Валидация кода купона
        if len(code) < 1 or len(code) > 15 or ' ' in code:
            raise ValueError("Invalid coupon code.")
        
        if discount_value < 1 or discount_value > 90:
            raise ValueError("Discount value must be between 1 and 90.")

        await self.db.execute(
            'INSERT INTO coupon_codes (code, seller_id, discount_value, usage_limit) VALUES (?, ?, ?, ?)', 
            (code, seller_id, discount_value, usage_limit)
        )
        return await self.get_coupon_by_code(code, 'active')
    
    async def update_coupon_status(self, coupon: Coupon, status: str) -> None:
        """Обновить статус купона."""
        coupon.status = status
        await self.db.execute(
            'UPDATE coupon_codes SET status = ? WHERE coupon_id = ?', 
            (status, coupon.coupon_id)
        )

    async def archive_expired_coupons(self) -> None:
        """Архивировать просроченные купоны."""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await self.db.execute(
            'UPDATE coupon_codes SET status = "archived" WHERE end_date < ? AND status = "active"',
            (current_time,)
        )

    async def increment_usage(self, coupon: Coupon) -> None:
        """Увеличить счетчик использованных купонов в корзинах."""
        if coupon.usage_limit is not None and coupon.used_cart_count >= coupon.usage_limit:
            raise ValueError("Usage limit exceeded.")
        
        coupon.used_cart_count += 1
        await self.db.execute(
            'UPDATE coupon_codes SET used_cart_count = ? WHERE coupon_id = ?', 
            (coupon.used_cart_count, coupon.coupon_id)
        )
        
        # Архивировать купон, если достигнут лимит использования
        if coupon.usage_limit is not None and coupon.used_cart_count >= coupon.usage_limit:
            await self.update_coupon_status(coupon, 'archived')


class CouponLicensesManager:
    """Менеджер для работы с лицензиями доступными в купоне."""
    def __init__(self, db: Database):
        self.db = db

    async def add_license_to_coupon(self, coupon_id: int, license_id: int) -> None:
        """Добавить лицензию в купон."""
        await self.db.execute(
            'INSERT INTO coupon_licenses (coupon_id, license_id) VALUES (?, ?)', 
            (coupon_id, license_id)
        )

    async def remove_license_from_coupon(self, coupon_id: int, license_id: int) -> None:
        """Удалить лицензию из купона."""
        await self.db.execute(
            'DELETE FROM coupon_licenses WHERE coupon_id = ? AND license_id = ?', 
            (coupon_id, license_id)
        )


class CouponService:

    def __init__(self):
        self.db = Database()
        self.coupon_manager = CouponManager(self.db)
        self.coupon_licenses_manager = CouponLicensesManager(self.db)

    async def _initialize_db(self):
        """Инициализация БД асинхронно."""
        await self.db.create_tables()

    async def deactivate_expired_coupons(self):
        """Деактивировать просроченные купоны."""
        await self.coupon_manager.archive_expired_coupons()

    async def apply_coupon(self, coupon_code: str) -> Coupon:
        """Применить купон."""
        coupon = await self.coupon_manager.get_coupon_by_code(coupon_code)
        if not coupon:
            raise ValueError("Coupon not found or is archived.")
        
        await self.coupon_manager.increment_usage(coupon)
        return coupon

    #тут нужно прописать основную сервис логику, добавление, редактирование промокодов для продавцов, включение выключение лицензий по входному license_id
    # сделать какую-то валидацию на проверку времени, статус,  и наверное стоит сразу архивировать купон если время вышло, сделать методы для каунтеров при применении, так же выключать архивировать если usage_limit ну еще валидацию вводимого code по тем огрничениям которые я описал в создании таблицы