import aiosqlite
from typing import Any,Optional,Tuple,List
from contextlib import asynccontextmanager
from src.misc import DB_PATH



class Database:
    """Асинхронный класс для работы с базой данных."""

    def __init__(self, db_path: str ):
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
    async def execute_and_get_id(self, query: str, params: tuple = ()) ->  Optional[int]:
        """Выполнение запроса без возврата значений."""
        async with self.get_db_connection() as db:
            cursor = await db.execute(query, params)
            result = cursor.lastrowid
            return result if result else None

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Tuple]:
        """Получить одну запись."""
        async with self.get_db_connection() as db:
            cursor = await db.execute(query, params)
            result =  await cursor.fetchone()
            return result if result else None

    async def fetch_all(self, query: str, params: tuple = ()) -> List[Tuple]:
        """Получить все записи."""
        async with self.get_db_connection() as db:
            cursor = await db.execute(query, params)
            result =  await cursor.fetchall()
            return result if result else None
        



#Использовать вот так

class TestClassAgaAga:

    def __init__(self,db:Database):
        self.db = db
    pass


orders_service = TestClassAgaAga(Database( db_path=DB_PATH))