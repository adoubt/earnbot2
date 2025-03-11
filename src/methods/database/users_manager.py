import aiosqlite
from typing import Any

class UsersDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(
                    f'''CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY,
                                                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                                        watching TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                        balance REAL 0.00,
                                                        referr TEXT DEFAULT NULL,
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
                return result[0]

    @classmethod
    async def create_user(
        cls,
        user_id: int,
        is_seller: int = 0,
        is_banned: int = 0,
        is_admin: int = 0,
        balance: float = 0.0,
        username: str= None,
        artist_name:str = None,
        email: str = None,
        insta: str = None,
        subscription: int = 0,
        wallet_id: int = None,
        language: str = "en",
        channel: str = None,
        default_payment_method: str = "CryptoBot"
    ):
        async with aiosqlite.connect("src/databases/users.db") as db:
            query = '''
            INSERT INTO users(
                "user_id", "is_seller", "is_banned", "is_admin", "balance",
                "username", "artist_name", "email", "insta", "subscription",
                "wallet_id", "language", "channel","default_payment_method"
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            await db.execute(
                query,
                (user_id, is_seller, is_banned, is_admin, balance,
                username, artist_name, email, insta, subscription,
                wallet_id, language, channel, default_payment_method)
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

    # @classmethod        
    # async def clear_all_context(cls):
    #     async with aiosqlite.connect("src/databases/users.db") as db:
            
    #         await db.execute(f'UPDATE users SET context=""')
    #         await db.commit()
    # @classmethod        
    # async def clear_context(cls,user_id:int):
    #     async with aiosqlite.connect("src/databases/users.db") as db:
            
    #         await db.execute(f'UPDATE users SET context="" WHERE user_id ={user_id}')
    #         await db.commit()


    @classmethod        
    async def del_users(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            
            await db.execute(f'DELETE from users')
            await db.commit()

    @classmethod
    async def add_points(cls, user_id: int, points: int):
        await cls.set_value(user_id, 'balance', (await cls.get_value(user_id, 'balance')) + points)
    
    # @classmethod
    # async def add_requets(cls, user_id: int, requests: int):
    #     await cls.set_value(user_id, 'requests_left', (await cls.get_value(user_id, 'requests_left')) + requests)
    
    @classmethod
    async def is_banned(cls, user_id: int):
        return await cls.get_value(user_id, 'is_banned')

    @classmethod
    async def is_admin(cls, user_id: int):
        return (await cls.get_value(user_id, 'is_admin')) == 1
    
    
# INSERT INTO users("user_id", "balance", "is_banned", "status", "context") VALUES ({user_id}, 0, 0, 0, "")'
# 'CREATE TABLE prompts(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT, body TEXT)')