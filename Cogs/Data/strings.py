import dataclasses


@dataclasses.dataclass(frozen=True)
class Strings:
    """テキストを置き換えます"""
    # main.py
    prefix_of_the_bot = ["このBOTのprefixは`{}`です!\n`{}help`で詳しい使い方を確認できます。", "The prefix for this bot is `{}`! \n`{}help` for more details on how to use it.", "이 봇의 접두사는`{}`입니다! 사용 방법에 대한 자세한 내용은 \n` {} 도움말`을 참조하세요.", "¡El prefijo de este bot es `{}`! \n`{}help` para obtener más detalles sobre cómo usarlo."]





