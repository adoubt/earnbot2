import aiosqlite
from typing import Any

class UsersDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(
                    f'''CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY,
                                                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                        watching TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                        balance REAL DEFAULT 0.00,
                                                        referr INTEGER DEFAULT NULL,
                                                        referrals INTEGER DEFAULT 0,
                                                        rereferrals INTEGER DEFAULT 0,
                                                        username STRING DEFAULT NULL,
                                                        today_left INTEGER DEFAULT 20,
                                                        update_limit TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                        is_admin INTEGER DEFAULT 0,
                                                        watched_videos INTEGER DEFAULT 0,
                                                        queue INTEGER DEFAULT 1,
                                                        is_member INTEGER DEFAULT 0,
                                                        multiply INTEGER DEFAULT 1,
                                                        requested INTEGER DEFAULT 0,
                                                        language TEXT DEFAULT NULL,
                                                        requested_time INTEGER DEFAULT 0)''') as cursor:
                pass

    @classmethod
    async def get_all(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result

    @classmethod
    async def get_all_banned(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users WHERE is_banned=1') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result

    @classmethod
    async def get_user(cls, user_id: int):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result

    @classmethod
    async def create_user( 
        cls,
        user_id: int,
        username:str|None = None,
        is_admin:int|None = 0,
        referr:int|None = None,
        language:str|None = None
    ):
        async with aiosqlite.connect("src/databases/users.db") as db:
            query = '''
            INSERT INTO users(
                "user_id", "username","is_admin","referr","language"
            ) 
            VALUES (?, ?, ?, ?, ?)
            '''
            await db.execute(
                query,
                (user_id, username, is_admin,
                referr,language)
            )
            await db.commit()


    @classmethod
    async def get_value(cls, user_id: int, key: Any):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT {key} FROM users WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod
    async def set_value(cls, user_id: int, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/users.db") as db:
            if type(key) is int:
                await db.execute(f'UPDATE users SET {key}={new_value} WHERE user_id={user_id}')
            else:
                await db.execute(f'UPDATE users SET {key}=? WHERE user_id={user_id}',(new_value,))
            await db.commit()


    @classmethod        
    async def del_users(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            
            await db.execute(f'DELETE from users')
            await db.commit()

    @classmethod
    async def add_points(cls, user_id: int, points: int):
        await cls.set_value(user_id, 'balance', (await cls.get_value(user_id, 'balance')) + points)
    

    @classmethod
    async def is_admin(cls, user_id: int):
        return (await cls.get_value(user_id, 'is_admin')) == 1
    
    @classmethod
    async def refer(cls, user_id: int, amount: float, referrals: int = 0, rereferrals: int = 0) -> None:
        """Прибавка бенефитов реферерру"""
        async with aiosqlite.connect("src/databases/users.db") as db:
            await db.execute(
                "UPDATE users SET balance = balance + ?, referrals = referrals + ?, rereferrals = rereferrals + ? WHERE user_id = ?",
                (amount, referrals, rereferrals, user_id),
            )
            await db.commit()
