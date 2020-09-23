from typing import Any, List
import string, json

numbers = "0123456789"
alphabets = string.ascii_letters
characters = numbers + alphabets
with open('./assets/item_info.json') as f:
    item_info = json.load(f)


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
        return 0, ["装飾コードが間違っています.", "Wrong costume code.", "잘못된 코스튬 코드", "Código de vestuario incorrecto"]
    item = str(result).zfill(11)  # 11桁になるように0埋めする
    if int(item[0:1]) not in [0, 1]:
        return 0, ["色(白か黒)の番号が間違っています.", "Wrong base number.", "잘못된 base 번호", "Número base incorrecto."]
    if not item_info["character"]["min"] <= int(item[1:3]) <= item_info["character"]["max"]:
        return 0, ["キャラの番号が間違っています.", "Wrong character number.", "character 번호가 잘못되었습니다.", "Número de carácter incorrecto."]
    if not item_info["weapon"]["min"] <= int(item[3:5]) <= item_info["weapon"]["max"]:
        return 0, ["武器の番号が間違っています.", "Wrong weapon number", "무기의 번호가 잘못되었습니다.", "Número de arma incorrecto"]
    if not item_info["head"]["min"] <= int(item[5:7]) <= item_info["head"]["max"]:
        return 0, ["頭装飾の番号が間違っています.", "Head decoration number", "머리 코스튬 번호", "Número de decoración de la cabeza"]
    if not item_info["body"]["min"] <= int(item[7:9]) <= item_info["body"]["max"]:
        return 0, ["体装飾の番号が間違っています.", "Body decoration number", "본체 코스튬 번호", "Número de decoración corporal"]
    if not item_info["back"]["min"] <= int(item[9:11]) <= item_info["back"]["max"]:
        return 0, ["背中装飾の番号が間違っています.", "Back decoration number", "뒷면 코스튬 번호", "Número de decoración trasera"]
    return 1, [int(item[0:1]), int(item[1:3]), int(item[3:5]), int(item[5:7]), int(item[7:9]), int(item[9:11])]


def check_item_list(item: List[str]) -> (int, Any):
    """ 装飾コードの形式を確認して、装飾コードのリストに変換 """
    if len(item) != 6:
        return 0, ["引数の数が間違っています.", "Missing required arguments.", "필수 인수가 없습니다.", "Faltan argumentos obligatorios"]
    if not (item[0].isdigit() and int(item[0]) in [0, 1]):
        return 0, ["色(白か黒)の番号が間違っています.", "Wrong base number.", "잘못된 base 번호", "Número base incorrecto."]
    if not (item[1].isdigit() and item_info["character"]["min"] <= int(item[1]) <= item_info["character"]["max"]):
        return 0, ["キャラの番号が間違っています.", "Wrong character number.", "character 번호가 잘못되었습니다.", "Número de carácter incorrecto."]
    if not (item[2].isdigit() and item_info["weapon"]["min"] <= int(item[2]) <= item_info["weapon"]["max"]):
        return 0, ["武器の番号が間違っています.", "Wrong weapon number", "무기의 번호가 잘못되었습니다.", "Número de arma incorrecto"]
    if not (item[3].isdigit() and item_info["head"]["min"] <= int(item[3]) <= item_info["head"]["max"]):
        return 0, ["頭装飾の番号が間違っています.", "Head decoration number", "머리 코스튬 번호", "Número de decoración de la cabeza"]
    if not (item[4].isdigit() and item_info["body"]["min"] <= int(item[4]) <= item_info["body"]["max"]):
        return 0, ["体装飾の番号が間違っています.", "Body decoration number", "본체 코스튬 번호", "Número de decoración corporal"]
    if not (item[5].isdigit() and item_info["back"]["min"] <= int(item[5]) <= item_info["back"]["max"]):
        return 0, ["背中装飾の番号が間違っています.", "Back decoration number", "뒷면 코스튬 번호", "Número de decoración trasera"]
    return 1, [int(item[0]), int(item[1]), int(item[2]), int(item[3]), int(item[4]), int(item[5])]


def parse_item_list_to_code(item: List[int]) -> str:
    code = f"{item[0]}{str(item[1]).zfill(2)}{str(item[2]).zfill(2)}{str(item[3]).zfill(2)}{str(item[4]).zfill(2)}{str(item[5]).zfill(2)}"
    return parse_to_36(int(code))


def parse_item_code_to_list(item: str) -> list:
    _, result = parse_from_36(item)  # 36進数から10進数に変換
    item = str(result).zfill(11)  # 11桁になるように0埋めする
    return [int(item[0:1]), int(item[1:3]), int(item[3:5]), int(item[5:7]), int(item[7:9]), int(item[9:11])]


