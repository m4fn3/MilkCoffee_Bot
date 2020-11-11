import json
from typing import Optional, List

import asyncpg

from .utils.multilingual import get_lg


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

    # User
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

    # Costume
    async def get_canvas(self, user_id: int) -> str:
        """作業中の装飾データを取得"""
        res = await self.con.fetchrow("SELECT canvas FROM user_data WHERE id = $1", user_id)
        if res is None or res["canvas"] is None:
            return "1aecsirk"
        else:
            return res["canvas"]

    async def set_canvas(self, user_id: int, code: str) -> None:
        """作業中の装飾データを設定"""
        await self.con.execute("UPDATE user_data SET canvas = $1 WHERE id = $2", code, user_id)

    async def get_save_work(self, user_id: int) -> list:
        """保存された作品のデータを取得"""
        res = await self.con.fetchrow("SELECT save FROM user_data WHERE id = $1", user_id)
        if res is None or res["save"] is None:
            return []
        else:
            return json.loads(res["save"])

    async def update_save_work(self, user_id: int, new_data: list) -> None:
        """保存された作品のデータを更新"""
        await self.con.execute("UPDATE user_data SET save = $1 WHERE id = $2", json.dumps(new_data), user_id)

    # Notify
    async def get_notify_data(self, guild_id: int) -> Optional[dict]:
        """通知設定データを取得"""
        res = await self.con.fetchrow("SELECT * FROM notify WHERE id = $1", guild_id)
        if res is None:
            return None
        else:
            return dict(res)

    async def update_notify_data(self, guild_id: int, new_data: dict) -> None:
        """通知設定データを更新"""
        await self.con.execute(
            "UPDATE notify SET twitter = $1, facebook_jp = $2, facebook_en = $3, facebook_kr = $4, facebook_es = $5, youtube = $6 WHERE id = $7",
            new_data["twitter"], new_data["facebook_jp"], new_data["facebook_en"], new_data["facebook_kr"], new_data["facebook_es"], new_data["youtube"], guild_id
        )

    async def set_notify_data(self, guild_id: int, new_data: dict) -> None:
        """通知設定データを追加"""
        await self.con.execute(
            "INSERT INTO notify values($1, $2, $3, $4, $5, $6, $7)",
            guild_id, new_data["twitter"], new_data["facebook_jp"], new_data["facebook_en"], new_data["facebook_kr"], new_data["facebook_es"], new_data["youtube"]
        )

    async def get_notify_channels(self, notify_type: str) -> List[int]:
        """通知チャンネルのリストを取得"""
        res = await self.con.execute("SELECT array_agg($1) FROM notify", notify_type)
        if res is None or res["array_agg"] is None:
            return []
        else:
            return [ch for ch in res["array_agg"] if ch is not None]
