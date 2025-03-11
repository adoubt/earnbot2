import asyncio

from src.methods.database.users_manager import UsersDatabase
from src.methods.database.videos_manager import VideosDatabase

async def init_databases() -> None:
    
    await UsersDatabase.create_table()
    await VideosDatabase.create_table()

# # Пример вызова
# if __name__ == '__main__':
#     asyncio.run(init_databases())
