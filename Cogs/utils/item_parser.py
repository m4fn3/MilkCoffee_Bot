import string
from typing import List

# 36進数用の文字列
numbers = "0123456789"
alphabets = string.ascii_letters
characters = numbers + alphabets


def code_to_list(code36: str) -> List[int]:
    """装飾コードを番号リストに変換"""
    code10 = int(code36, 36)  # 36進数->10進数に変換
    item = str(code10).zfill(11)  # 11桁になるよう0埋め
    return [int(item[0:1]), int(item[1:3]), int(item[3:5]), int(item[5:8]), int(item[8:11]), int(item[11:14])]


def list_to_code(item: list) -> str:
    """番号リストを装飾コードに変換"""
    code = f"{item[0]}{str(item[1]).zfill(2)}{str(item[2]).zfill(2)}{str(item[3]).zfill(3)}{str(item[4]).zfill(3)}{str(item[5]).zfill(3)}"
    return parse_to_36(int(code))


def parse_to_36(tmp: int):
    """10進数->36進数に変換"""
    result = ''
    while tmp >= 36:
        idx = tmp % 36
        result = characters[idx] + result
        tmp = int(tmp / 36)
    idx = tmp % 36
    return characters[idx] + result



def update_code(code: str):
    """旧形式の装飾コードを新形式に変換"""
