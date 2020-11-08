import json
from typing import Optional, List, Set
from .utils.multilingual import get_lg

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

    async def get_registered_users(self) -> List[int]:
        """登録済みユーザーのリストを取得"""
        res = await self.con.fetchrow("SELECT array_agg(id) FROM user_data")
        if res is None or res["array_agg"] is None:
            return []
        else:
            return res["array_agg"]

    async def register_new_user(self, user_id: int) -> None:
        """新規ユーザーを追加"""
        await self.con.execute("INSERT INTO user_data(id) VALUES($1)", user_id)

    async def get_lang(self, user_id: int, region) -> int:
        """ユーザーの言語を取得"""
        res = await self.con.fetchrow("SELECT language FROM user_data WHERE id = $1", user_id)
        if res is None or res["language"] is None:
            return 0
        return get_lg(res["language"], region)

    async def set_lang(self, user_id: int, lang: int) -> None:
        """言語を変更"""
        await self.con.execute("UPDATE user_data SET language = $1 WHERE id = $2", lang, user_id)

    async def get_notify_channels(self, notify_type: str) -> List[int]:
        """通知に登録されているチャンネルのリストを取得"""
        res = await self.con.fetchrow("SELECT guild FROM notify where type = $1", notify_type)
        if res is None or res["guild"] is None:
            return []
        else:
            return res["guild"]

    async def add_notify_channel(self, notify_type: str, channel_id: int) -> None:
        """通知に新規登録"""
        await self.con.execute("UPDATE notify SET guild = array_append(guild, $1) where type = $2", channel_id, notify_type)

    async def remove_notify_channel(self, notify_type: str, channel_id: int) -> None:
        """通知登録を解除"""
        await self.con.execute("UPDATE notify SET guild = array_remove(guild, $1) where type = $2", channel_id, notify_type)

