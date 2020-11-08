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
class Load:
    usage = "load [保存番号|保存名称]^load [save number | save name]^load [저장 번호 | 저장 명칭]^load [guardar número | guardar nombre]"
    brief = "保存した作品を作業場に読み込むよ!^Load the saved work into the current workshop!^저장된 작업을 현재 작업장에로드하십시오!^¡Carga el trabajo guardado en el taller actual!"
    description = "保存した作品を番号または名称で指定して、現在の作業場に読み込むよ!^Load the saved work  into the current workshop  by number or name!^저장 한 작품을 번호 또는 이름을 지정하여 현재 작업 공간에 불러와요!^Especifique el trabajo guardado por número o nombre y cárguelo en el lugar de trabajo actual."

@dataclasses.dataclass(frozen=True)
class Save:
    usage = "save (保存名称)^save (save name)^save (저장 명칭)^save (guardar nombre)"
    brief = "現在の装飾を保存できるよ!^Save the current decoration!^현재의 장식을 저장 할 수 있어!^¡Puede guardar la decoración actual!"
    description = "現在の装飾を保存できるよ!保存名称を指定しなかったら、'Untitled1'みたいな名前を自動でつけとくね!^Save the current decoration! If you don't specify a save name, I automatically give it a name like 'Untitled 1'!^현재의 장식을 저장 할 수 있어! 저장할 이름을 지정하지 않으면, 'Untitled 1'같은 이름을 자동으로 저장할거야!^¡Puede guardar la decoración actual! Si no especifica un nombre para guardar, puede darle automáticamente un nombre como 'Untitled 1'."

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
    load = Load()
    save = Save()
    # Bot
    invite = Invite()
    language = Lang()
    # Notify
    follow = Follow()
    notice = Notice()
    ads = Ads()
