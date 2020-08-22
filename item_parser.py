from typing import Any


def check_item_id(item: str) -> (int, Any):
    """ 装飾コードのリストの形式を確認して、装飾コードのリストを返す """
    if int(item[0:1]) not in [0, 1]:
        return 0, "wrong_base_id"
    if not 0 <= int(item[1:3]) <= 20:
        return 0, "wrong_char_id"
    if not 1 <= int(item[3:5]) <= 34:
        return 0, "wrong_weapon_id"
    if not 1 <= int(item[5:7]) <= 55:
        return 0, "wrong_head_id"
    if not 1 <= int(item[7:9]) <= 61:
        return 0, "wrong_body_id"
    if not 1 <= int(item[9:11]) <= 56:
        return 0, "wrong_back_id"
    return 1, [int(item[0:1]), int(item[1:3]), int(item[3:5]), int(item[5:7]), int(item[7:9]), int(item[9:11])]


def check_item_list(item: list) -> (int, Any):
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
    if not (item[4].isdigit() and 1 <= int(item[4]) <= 61):
        return 0, "wrong_body_id"
    if not (item[5].isdigit() and 1 <= int(item[5]) <= 56):
        return 0, "wrong_back_id"
    return 1, [int(item[0]), int(item[1]), int(item[2]), int(item[3]), int(item[4]), int(item[5])]


def parse_item_list_to_code(item: list) -> str:
    return f"{item[0]}{item[1]}{item[2]}{item[3]}{item[4]}{item[5]}"


def parse_item_code_to_list(item: str) -> list:
    return [int(item[0:1]), int(item[1:3]), int(item[3:5]), int(item[5:7]), int(item[7:9]), int(item[9:11])]
