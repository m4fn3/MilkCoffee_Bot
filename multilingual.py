from enum import IntEnum


def get_lang(lang, region):
    if lang == LanguageCode.REGION:
        if str(region) == "japan":
            return LanguageCode.JAPANESE.value - 1
        elif str(region) == "south-korea":
            return LanguageCode.KOREAN.value - 1
        else:
            return LanguageCode.ENGLISH.value - 1
    else:
        return lang.value - 1


class LanguageCode(IntEnum):
    REGION = 0
    JAPANESE = 1
    ENGLISH = 2
    KOREAN = 3
    SPANISH = 4
