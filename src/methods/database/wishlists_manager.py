import aiosqlite
from typing import Any

DB_PATH = "src/databases/wishlists.db"
class WishlistsDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS wishlists(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    user_id INTEGER,
                                    product_id INTEGER,
                                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    UNIQUE(user_id, product_id)
                                    )'''
                                  ) as cursor:
                pass

    @classmethod
    async def get_value(cls, key: Any, user_id:int):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f'SELECT {key} FROM wishlists WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
            
    @classmethod
    async def get_wishlist_count(cls, user_id:int):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f'SELECT COUNT(*) FROM wishlists WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod        
    async def del_from_wishlist(cls,user_id:int,product_id:int):        
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f'DELETE FROM wishlists WHERE user_id = {user_id} and product_id = {product_id}')
            await db.commit()
    
    @classmethod
    async def empty_wishlist(cls, user_id):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f'DELETE FROM wishlists WHERE user_id = {user_id}')
            await db.commit()
    
    @classmethod # When the beat was sold exclusively
    async def del_product_from_wishlists(cls, product_id):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f'DELETE FROM wishlists WHERE product_id = {product_id}')
            await db.commit()

    @classmethod
    async def add_to_wishlist(cls, 
                            user_id: int,
                            product_id: int
                            ):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f'INSERT OR IGNORE INTO wishlists ("user_id", "product_id") VALUES (?,?)',
                             (user_id,product_id))
            await db.commit()
    
    @classmethod    
    async def get_wishlist_by_user(cls, user_id:int):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f'SELECT * FROM wishlists WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result
    
    @classmethod
    async def is_product_in_wishlist(cls, user_id: int, product_id: int) -> bool:
        query = '''SELECT 1 FROM wishlists WHERE user_id = ? AND product_id = ? LIMIT 1'''
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(query, (user_id, product_id)) as cursor:
                result = await cursor.fetchone()
                # Если результат не None, значит продукт есть в вишлисте
                return result is not None