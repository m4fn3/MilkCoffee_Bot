import dataclasses


@dataclasses.dataclass(frozen=True)
class Menu:
    usage = "menu^menu^menu^menu"
    brief = "装飾設定メニューを表示^Show simulator menu^의상 시뮬레이터 메뉴 표시^Mostrar el menú del simulador"
    description = "装飾シミュレータのメニューを表示します^Show costume simulator menu^의상 시뮬레이터 메뉴 표시^Mostrar el menú del simulador de vestuario"

@dataclasses.dataclass(frozen=True)
class Set:
    usage = "set [装飾コード]^set [CostumeCode]^set [장식 코드]^set [código de decoración]"
    brief = "装飾コードで設定^Set the costume code^의상 코드로 설정^Establecer el código"
    description = "装飾コードでアイテムを設定します^Set items with costume code^의상 코드로 설정^Conjunto con código de vestuario"
    help = "他の人の装飾をコピーする際に使用できます^It can be used to copy other people's costume^다른 사람의 의상을 복사하는 데 사용할 수 있습니다^Se puede usar para copiar el disfraz de otras personas"


@dataclasses.dataclass(frozen=True)
class My:
    usage = "my^my^my^my"
    brief = "保存済み作品一覧を表示^list of saved works^저장된 작업 목록보기^lista de obras guardadas"
    description = "保存した作品の一覧を表示します^Show a list of saved works^저장된 작업 목록을 표시 할 수 있어^Mostrar una lista de trabajos guardados"


@dataclasses.dataclass(frozen=True)
class Delete:
    usage = "delete [保存番号|保存名称]^delete [save number | save name]^delete 저장 번호 | 저장 명칭]^delete [guardar número | guardar nombre]"
    brief = "保存済み作品の削除^Remove the saved work^저장된 작업을 삭제합니다^Eliminar el guardado obras"
    description = "保存済みの作品を削除します^Remove the saved work^저장된 작업을 삭제합니다^Eliminar el trabajo guardado"


@dataclasses.dataclass(frozen=True)
class Random:
    usage = "random^random^random^random"
    brief = "ランダム装飾を作成^Make random costume^무작위 의상 만들기^Hacer un disfraz al azar"
    description = "ランダムな装飾を作成します^Make random costume^무작위 의상을 만들 수 있습니다^puede hacer un disfraz al azar"

@dataclasses.dataclass(frozen=True)
class Invite:
    usage = "invite^invite^invite^invite"
    brief = "BOTのリンク集の表示^Send bot links^봇 링크 보내기^Enviar enlaces de bot"
    description = "招待リンクを表示します^Send invitation link^초대 링크 보내기^Enviar enlace de invitación"

@dataclasses.dataclass(frozen=True)
class Lang:
    usage = "lang (言語)^lang (language)^lang (언어)^lang (idioma)"
    brief = "言語の設定^Setup language^설정 언어^Configurar idioma"
    description = "言語を設定します^Set up language^언어를 설정합니다^Configurar idioma"

@dataclasses.dataclass(frozen=True)
class Follow:
    usage = "follow (チャンネル)^follow (channel)^follow (채널)^follow (canal)"
    brief = "BOTの更新情報通知^Receive bot's updates^봇의 업데이트 받기^Recibe actualice de bot"
    description = "BOTの更新情報を受け取ります^Receive BOT's updates^BOT의 업데이트를받습니다^Reciba las actualizaciones de BOT"

@dataclasses.dataclass(frozen=True)
class Notice:
    usage = "notice (チャンネル)^notice (channel)^notice (채널)^notice (canal)"
    brief = "運営の更新情報受け取り^Receive MilkChoco updates^밀크초코 업데이트 받기^Recibe actualice de MilkChoco"
    description = "MilkChoco運営の更新情報を受け取ります^Receive MilkChoco updates^MilkChoco 업데이트 받기^Reciba actualizaciones de MilkChoco"

@dataclasses.dataclass(frozen=True)
class Ads:
    usage = "ads^ads^ads^ads"
    brief = "10分のタイマーを設定^Set 10 minutes timer^10 분 타이머 설정^aviso después de 10 minutos"
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
    language = Lang()
    # Notify
    follow = Follow()
    notice = Notice()
    ads = Ads()
