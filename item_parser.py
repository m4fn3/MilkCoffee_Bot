from typing import Any, List
import string

numbers = "0123456789"
alphabets = string.ascii_letters
characters = numbers + alphabets


def parse_to_36(tmp: int):
    result = ''
    while tmp >= 36:
        idx = tmp % 36
        result = characters[idx] + result
        tmp = int(tmp / 36)
    idx = tmp % 36
    return characters[idx] + result


def parse_from_36(num: str) -> (int, Any):
    """36進数→10進数に変換"""
    try:
        num = int(num, 36)
    except:
        return 0  # 不正な文字が含まれていた場合(0-9a-zA-Z以外)
    else:
        return 1, num


def check_item_id(item: str) -> (int, Any):
    """ 装飾コードのリストの形式を確認して、装飾コードのリストを返す """
    code, result = parse_from_36(item)  # 36進数から10進数に変換
    if code == 0:
        return 0, "wrong_costume_code"
    item = str(result).zfill(11)  # 11桁になるように0埋めする
    if int(item[0:1]) not in [0, 1]:
        return 0, "wrong_base_id"
    if not 0 <= int(item[1:3]) <= 20:
        return 0, "wrong_char_id"
    if not 1 <= int(item[3:5]) <= 34:
        return 0, "wrong_weapon_id"
    if not 1 <= int(item[5:7]) <= 55:
        return 0, "wrong_head_id"
    if not 1 <= int(item[7:9]) <= 62:
        return 0, "wrong_body_id"
    if not 1 <= int(item[9:11]) <= 56:
        return 0, "wrong_back_id"
    return 1, [int(item[0:1]), int(item[1:3]), int(item[3:5]), int(item[5:7]), int(item[7:9]), int(item[9:11])]


def check_item_list(item: List[str]) -> (int, Any):
    """ 装飾コードの形式を確認して、装飾コードのリストに変換 """
    if len(item) != 6:
        return 0, "missing_required_arguments"
    if not (item[0].isdigit() and int(item[0]) in [0, 1]):
        return 0, "wrong_base_id"
    if not (item[1].isdigit() and 0 <= int(item[1]) <= 20):
        return 0, "wrong_char_id"
    if not (item[2].isdigit() and 1 <= int(item[2]) <= 34):
        return 0, "wrong_weapon_id"
    if not (item[3].isdigit() and 1 <= int(item[3]) <= 55):
        return 0, "wrong_head_id"
    if not (item[4].isdigit() and 1 <= int(item[4]) <= 62):
        return 0, "wrong_body_id"
    if not (item[5].isdigit() and 1 <= int(item[5]) <= 56):
        return 0, "wrong_back_id"
    return 1, [int(item[0]), int(item[1]), int(item[2]), int(item[3]), int(item[4]), int(item[5])]


def parse_item_list_to_code(item: List[int]) -> str:
    code = f"{item[0]}{str(item[1]).zfill(2)}{str(item[2]).zfill(2)}{str(item[3]).zfill(2)}{str(item[4]).zfill(2)}{str(item[5]).zfill(2)}"
    return parse_to_36(int(code))


def parse_item_code_to_list(item: str) -> list:
    _, result = parse_from_36(item)  # 36進数から10進数に変換
    item = str(result).zfill(11)  # 11桁になるように0埋めする
    return [int(item[0:1]), int(item[1:3]), int(item[3:5]), int(item[5:7]), int(item[7:9]), int(item[9:11])]
