import aiosqlite
from typing import Any



# TESTS 6279510886 436839651
# Update users SET watched_videos = 6 WHERE user_id = 436839651
# Update users SET balance = 251 WHERE user_id = 436839651
# Update users SET requested_time = DATETIME('2025-03-11 12:52:08') WHERE user_id = 436839651
# DELETE from users where user_id = 436839651
#
class UsersDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(
                    f'''CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY,
                                                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                        watching TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                        balance INTEGER DEFAULT 0,
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
                                                        requested_time TIMESTAMP,
                                                        card_number TEXT DEFAULT NULL,
                                                        email TEXT DEFAULT NULL,
                                                        amount_requested REAL DEFAULT NULL)''') as cursor:
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
    async def get_all_admins(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users WHERE is_admin = 1') as cursor:
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
    async def get_user_by_username(cls, username: str):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users WHERE username = "{username}"') as cursor:
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
    @classmethod
    async def get_count(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT COUNT(*) FROM users') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
    
    @classmethod
    async def update_watching(cls, user_id:int, duration: int,queue:int):

        async with aiosqlite.connect("src/databases/users.db") as db: 
            await db.execute(f"UPDATE users SET watching=DATETIME(CURRENT_TIMESTAMP, ?) WHERE user_id=?",
                             (f'+{duration} seconds',user_id))
            await db.commit()
        await cls.set_value(user_id,'queue',queue)

    @classmethod
    async def reward_user(cls, user_id: int, amount: int, hold: int, today_left: int):
        """Начисляет награду пользователю и обновляет лимиты"""
        
        update_limit_clause = ", update_limit = DATETIME(CURRENT_TIMESTAMP, ?)" if today_left == 20 else ""
        params = (amount, f'+{hold} seconds', user_id) if today_left == 20 else (amount, user_id)

        async with aiosqlite.connect("src/databases/users.db") as db:
            await db.execute(f"""
                UPDATE users
                SET balance = balance + ?,
                    today_left = today_left - 1,
                    watched_videos = watched_videos + 1
                    {update_limit_clause}
                WHERE user_id = ?;
            """, params)
            await db.commit()
    
    @classmethod
    async def request(cls, user_id:int, amount_requested :int):

        async with aiosqlite.connect("src/databases/users.db") as db: 
            await db.execute(f"""UPDATE users SET
                            requested_time = DATETIME(CURRENT_TIMESTAMP),
                            amount_requested = ?,
                            requested = 1
                            
                            WHERE user_id=?""",
                            (amount_requested,user_id))
            await db.commit()
        await cls.set_value(user_id,'amount_requested',amount_requested)   
    
    @classmethod
    async def cheat_6(cls, user_id: int):
        """Откатывает время созданной заявки на -48 часов.
        Если время отсутствует (NULL), то берётся текущее время и отнимается 48 часов.
        """
        async with aiosqlite.connect("src/databases/users.db") as db:
            query = """
                UPDATE users 
                SET requested_time = COALESCE(requested_time, DATETIME('now')) -- Если NULL, берём текущее время
                    , requested_time = DATETIME(requested_time, '-48 hours') -- Уменьшаем на 48 часов
                WHERE user_id = ?
            """
            await db.execute(query, (user_id,))
            await db.commit()