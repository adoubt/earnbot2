import aiosqlite

class ConfigDatabase:
    @classmethod
    async def create_table(cls):
        """Создает таблицу, если её нет"""
        async with aiosqlite.connect("src/databases/config.db") as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            await db.commit()

    @classmethod
    async def get_value(cls, key: str):
        """Получает значение по ключу"""
        async with aiosqlite.connect("src/databases/config.db") as db:
            async with db.execute('SELECT value FROM config WHERE key = ?', (key,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None  # Возвращает None, если ключа нет

    @classmethod
    async def set_value(cls, key: str, value: str):
        """Обновляет или вставляет значение по ключу"""
        async with aiosqlite.connect("src/databases/config.db") as db:
            await db.execute('''
                INSERT INTO config (key, value) 
                VALUES (?, ?) 
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            ''', (key, value))
            await db.commit()

    @classmethod
    async def get_all(cls):
        """Получает все ключи и значения"""
        async with aiosqlite.connect("src/databases/config.db") as db:
            async with db.execute('SELECT key, value FROM config') as cursor:
                return {key: value for key, value in await cursor.fetchall()}

    @classmethod
    async def delete_value(cls, key: str):
        """Удаляет ключ из таблицы"""
        async with aiosqlite.connect("src/databases/config.db") as db:
            await db.execute('DELETE FROM config WHERE key = ?', (key,))
            await db.commit()

