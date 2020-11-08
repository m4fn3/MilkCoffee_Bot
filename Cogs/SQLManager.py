import json
from typing import Optional, List, Set

import asyncpg


class SQLManager:
    def __init__(self, database_url: str, bot_loop):
        self.loop = bot_loop
        self.con = None
        self.database_url = database_url

    # Connection
    async def connect(self) -> asyncpg.connection:
        """データベースに接続"""
        self.con = await asyncpg.create_pool(self.database_url, loop=self.loop)

    def is_connected(self) -> bool:
        """データベースに接続しているか確認"""
        if self.con is None:
            return False
        else:
            return True

    def register_new_user(self, user_id: int) -> None:
        await self.con.execute("")
