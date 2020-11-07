import dataclasses


@dataclasses.dataclass(frozen=True)
class Menu:
    usage = "menu^menu^menu^menu"
    description = "装飾シミュレータメニューを表示します^Show costume simulator menu^의상 시뮬레이터 메뉴 표시^Mostrar el menú del simulador de vestuario"


@dataclasses.dataclass(frozen=True)
class Set:
    usage = "set [装飾コード]^set [CostumeCode]^set [장식 코드]^set [código de decoración]"
    description = "装飾コードで設定します^Set with costume code^의상 코드로 설정^Conjunto con código de vestuario"
    help = "他の人の装飾をコピーする際に使用できます^It can be used to copy other people's costume^다른 사람의 의상을 복사하는 데 사용할 수 있습니다^Se puede usar para copiar el disfraz de otras personas"


@dataclasses.dataclass(frozen=True)
class My:
    usage = "my^my^my^my"
    description = "保存した作品の一覧を表示します^Show a list of saved works^저장된 작업 목록을 표시 할 수 있어^Mostrar una lista de trabajos guardados"


@dataclasses.dataclass(frozen=True)
class Delete:
    usage = "delete [保存番号|保存名称]^delete [save number | save name]^delete 저장 번호 | 저장 명칭]^delete [guardar número | guardar nombre]"
    description = "保存済みの作品を削除します^Remove the saved work^저장된 작업을 삭제합니다^Eliminar el trabajo guardado"


@dataclasses.dataclass(frozen=True)
class Random:
    usage = "random^random^random^random"
    description = "ランダムな装飾を作成します^Make random costume^무작위 의상을 만들 수 있습니다^puede hacer un disfraz al azar"

@dataclasses.dataclass(frozen=True)
class Invite:
    usage = "invite^invite^invite^invite"
    description = "招待リンクを表示します^Send invitation link^초대 링크 보내기^Enviar enlace de invitación"

@dataclasses.dataclass(frozen=True)
class Info:
    usage = "info^info^info^info"
    description = "BOTの情報を表示します^Show information about BOT^봇에 대한 정보를 표시합니다!.^Muestra información sobre BOT"

@dataclasses.dataclass(frozen=True)
class Lang:
    usage = "lang (言語)^lang (language)^lang (언어)^lang (idioma)"
    description = "言語を設定します^Set up language^언어를 설정합니다^Configurar idioma"

@dataclasses.dataclass(frozen=True)
class Follow:
    usage = "follow (チャンネル)^follow (channel)^follow (채널)^follow (canal)",
    description = "BOTの更新情報を受け取ります^Receive BOT's updates^BOT의 업데이트를받습니다^Reciba las actualizaciones de BOT"

@dataclasses.dataclass(frozen=True)
class Notice:
    usage = "notice (チャンネル)^notice (channel)^notice (채널)^notice (canal)"
    description = "MilkChoco運営の更新情報を受け取ります^Receive MilkChoco updates^MilkChoco 업데이트 받기^Reciba actualizaciones de MilkChoco"

@dataclasses.dataclass(frozen=True)
class Ads:
    usage = "ads^ads^ads^ads"
    description = "10分間のタイマーを設定します^Set a 10-minute timer^10 분 타이머 설정^Establecer un temporizador de 10 minutos"

@dataclasses.dataclass(frozen=True)
class CmdData:
    # Costume
    set = Set()
    my = My()
    delete = Delete()
    random = Random()
    menu = Menu()
    # Bot
    invite = Invite()
    info = Info()
    language = Lang()
    # Notify
    follow = Follow()
    notice = Notice()
    ads = Ads()
