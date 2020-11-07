from .part.emoji_data import *
from .part.name_data import *
from .part.regex_data import *


@dataclasses.dataclass(frozen=True)
class Base:
    emoji = BaseEmoji()
    name = BaseName()
    min = 0
    max = 1
    len = 2
    index = 0
    page = 1


@dataclasses.dataclass(frozen=True)
class Character:
    emoji = CharacterEmoji()
    name = CharacterName()
    min = 0
    max = 20
    len = 21
    index = 1
    page = 3


@dataclasses.dataclass(frozen=True)
class Weapon:
    emoji = WeaponEmoji()
    name = WeaponName()
    min = 1
    max = 34
    len = 34
    index = 2
    page = 4


@dataclasses.dataclass(frozen=True)
class Head:
    emoji = HeadEmoji()
    name = HeadName()
    min = 0
    max = 75
    len = 76
    index = 3
    page = 8


@dataclasses.dataclass(frozen=True)
class Body:
    emoji = BodyEmoji()
    name = BodyName()
    min = 0
    max = 86
    len = 87
    index = 4
    page = 9


@dataclasses.dataclass(frozen=True)
class Back:
    emoji = BackEmoji()
    name = BackName()
    min = 0
    max = 78
    len = 79
    index = 5
    page = 8

@dataclasses.dataclass(frozen=True)
class Emoji:
    base = "<:base:773913727678021672>"
    char = "<:char:773913711093350430>"
    weapon = "<:weapon:773910067954057269>"
    head = "<:head:773910068256440380>"
    body = "<:body:773910068118814720>"
    back = "<:back:773910068097712149>"
    search = "<:search:774149798102040577>"
    exit = "<:exit:774149798730530826>"
    goback = "<:goback:774149798747963402>"
    limited = "<:limited:774149798286065694>"
    num = "<:num:774426280253718558>"
    right = "<:right:774488678193037342>"
    left = "<:left:774488697537560627>"
    load = "<:load:774498067511771136>"
    save = "<:save:774498016245579807>"
    config = "<:config:774498276492705792>"
    language = "<:language:758954812653305896>"
    region = "<:region:758947780319379486>"
    twitter = "<:twitter:757612992727613460>"
    facebook = "<:facebook:757612955029340190>"
    youtube = "<:youtube:757613031915257926>"

@dataclasses.dataclass(frozen=True)
class ItemData:
    base = Base()
    character = Character()
    weapon = Weapon()
    head = Head()
    body = Body()
    back = Back()
    emoji = Emoji()
    regex = ItemRegex().regex
