import aiosqlite
from typing import Any

class VideosDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/videos.db") as db:
            async with db.execute(f'''CREATE TABLE IF NOT EXISTS videos(video_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                        file_id TEXT UNIQUE NOT NULL,
                                                                        duration REAL,
                                                                        file_name TEXT,
                                                                        queue INTEGER
                                                                        )''') as cursor:
                pass

    @classmethod
    async def get_all(cls):
        async with aiosqlite.connect("src/databases/videos.db") as db:
            async with db.execute(f'SELECT * FROM videos') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result
    
    @classmethod
    async def get_all_offset(cls, offset:int, limit:int):
        async with aiosqlite.connect("src/databases/videos.db") as db:
            async with db.execute(f'SELECT * FROM videos LIMIT {limit} OFFSET {offset}') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result


    @classmethod
    async def get_video(cls,
                        video_id : int
                        ):      
        async with aiosqlite.connect("src/databases/videos.db") as db:
            async with db.execute(f'SELECT * FROM videos WHERE video_id = {video_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod
    async def get_video_by_queue(cls,
                        queue : int
                        ):      
        async with aiosqlite.connect("src/databases/videos.db") as db:
            async with db.execute(f'SELECT * FROM videos WHERE queue = {queue}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result
        
  
    @classmethod
    async def create_video(cls, file_id: str, file_name: str, duration: float, queue: int):
        async with aiosqlite.connect("src/databases/videos.db") as db:
            query = '''
            INSERT OR IGNORE INTO videos ("file_id", "file_name", "duration", "queue") 
            VALUES (?, ?, ?, ?)
            '''
            cursor = await db.execute(query, (file_id, file_name, duration, queue))
            await db.commit()

            if cursor.rowcount > 0:
                await cls.set_queue()  # Выполняем только если была вставка
                return True  # Видео добавлено
            return False  # Видео уже было в БД


    @classmethod        
    async def del_video(cls,video_id:str):
        async with aiosqlite.connect("src/databases/videos.db") as db:
            
            await db.execute(f'DELETE from videos WHERE video_id = {video_id}')
            await db.commit()
            await cls.set_queue()

    @classmethod
    async def get_value(cls, video_id: int, key: Any):
        async with aiosqlite.connect("src/databases/videos.db") as db:
            async with db.execute(f'SELECT {key} FROM videos WHERE video_id = {video_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod
    async def set_value(cls, video_id: int, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/videos.db") as db:
            if type(key) is int:
                await db.execute(f'UPDATE videos SET {key}={new_value} WHERE video_id = {video_id}')
            else:
                await db.execute(f'UPDATE videos SET {key}=? WHERE video_id = {video_id}',(new_value,))
            await db.commit()

    @classmethod        
    async def del_videos(cls):
        async with aiosqlite.connect("src/databases/videos.db") as db:
            
            await db.execute(f'DELETE from videos')
            await db.commit()

    @classmethod
    async def set_queue(cls):
        all_videos = await cls.get_all()
        i=0
        for video in all_videos:
            i+=1
            await cls.set_value(video[0], 'queue', i)
    
    @classmethod
    async def get_count(cls):
        async with aiosqlite.connect("src/databases/videos.db") as db:
            async with db.execute(f'SELECT COUNT(*) FROM videos') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
            

