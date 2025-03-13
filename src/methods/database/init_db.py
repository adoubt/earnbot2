import asyncio

from src.methods.database.users_manager import UsersDatabase
from src.methods.database.videos_manager import VideosDatabase
from src.methods.database.config_manager import ConfigDatabase
from src.misc import CHANNEL_LINK, CHANNEL_ID
async def init_databases() -> None:
    await UsersDatabase.create_table()
    await VideosDatabase.create_table()
    await ConfigDatabase.create_table()
    await ConfigDatabase.set_value('link',CHANNEL_LINK)
    await ConfigDatabase.set_value('channel_id',CHANNEL_ID)
    if await ConfigDatabase.get_value('ad_state') is None:
        await ConfigDatabase.set_value('ad_state','off')

# # Пример вызова
# if __name__ == '__main__':
#     asyncio.run(init_databases())
