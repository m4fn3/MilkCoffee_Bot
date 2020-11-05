from .part.emoji_data import *
from .part.name_data import *
from .part.regex_data import *


@dataclasses.dataclass(frozen=True)
class Base:
    emoji = BaseEmoji()
    name = BaseName()
    regex = BaseRegex()
    min = 0
    max = 1
    len = 2
    icon = "<:base:773913727678021672>"


@dataclasses.dataclass(frozen=True)
class Character:
    emoji = CharacterEmoji()
    name = CharacterName()
    regex = CharacterRegex()
    min = 0
    max = 20
    len = 21
    icon = "<:char:773913711093350430>"


@dataclasses.dataclass(frozen=True)
class Weapon:
    emoji = WeaponEmoji()
    name = WeaponName()
    regex = WeaponRegex()
    min = 1
    max = 34
    len = 34
    icon = "<:weapon:773910067954057269>"


@dataclasses.dataclass(frozen=True)
class Head:
    emoji = HeadEmoji()
    name = HeadName()
    regex = HeadRegex()
    min = 0
    max = 74
    len = 75
    icon = "<:head:773910068256440380>"


@dataclasses.dataclass(frozen=True)
class Body:
    emoji = BodyEmoji()
    name = BodyName()
    regex = BodyRegex()
    min = 0
    max = 87
    len = 88
    icon = "<:body:773910068118814720>"


@dataclasses.dataclass(frozen=True)
class Back:
    emoji = BackEmoji()
    name = BackName()
    regex = BackRegex()
    min = 0
    max = 79
    len = 80
    icon = "<:back:773910068097712149>"


@dataclasses.dataclass(frozen=True)
class ItemData:
    base = Base()
    character = Character()
    weapon = Weapon()
    head = Head()
    body = Body()
    back = Back()
