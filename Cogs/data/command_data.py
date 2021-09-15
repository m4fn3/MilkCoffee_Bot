import dataclasses


@dataclasses.dataclass(frozen=True)
class Menu:
    usage = "menu^menu^menu^menu"
    brief = "装飾設定メニューを表示^Show simulator menu^의상 시뮬레이터 메뉴 표시^Mostrar el menú del simulador"
    description = "装飾シミュレータの設定メニューを表示します^Show the costume simulator's setting menu^의상 시뮬레이터 메뉴 표시^Mostrar el menú del simulador de vestuario"


@dataclasses.dataclass(frozen=True)
class Set:
    usage = "set [装飾コード]^set [CostumeCode]^set [장식 코드]^set [código de decoración]"
    brief = "装飾コードで設定^Set with the costume code^의상 코드로 설정^Establecer el código"
    description = "装飾コードでアイテムを設定します^Set item with costume code^의상 코드로 설정^Conjunto con código de vestuario"
    help = "他の人の装飾をコピーする際に使用できます^It can be used to copy other people's costume^다른 사람의 의상을 복사하는 데 사용할 수 있습니다^Se puede usar para copiar el disfraz de otras personas"


@dataclasses.dataclass(frozen=True)
class Show:
    usage = "show (保存番号|保存名称)^show (save number | save name)^show (저장 번호 | 저장 명칭)^show (guardar número | guardar nombre)"
    brief = "現在の装飾の表示^Show the current costume^현재의 장식을 표시 할 수 있어!^¡Puede mostrar la decoración actual!"
    description = "現在の装飾を表示します.^Show the current costume.^현재의 장식을 표시 할  수있어! 저장 번호를 지정한 후 저장 한 작품 중에서 번호에 있던 작품을 보여주지!^¡Puede mostrar la decoración actual! Después de especificar el número de guardado, las obras que coincidan con el número se " \
                  "mostrarán de las obras guardadas. "


@dataclasses.dataclass(frozen=True)
class My:
    usage = "my^my^my^my"
    brief = "保存済み作品一覧を表示^List the saved works^저장된 작업 목록보기^lista de obras guardadas"
    description = "あなたが保存した作品の一覧を表示します^Show the list of your saved works^저장된 작업 목록을 표시 할 수 있어^Mostrar una lista de trabajos guardados"


@dataclasses.dataclass(frozen=True)
class Load:
    usage = "load [保存番号|保存名称]^load [save number | save name]^load [저장 번호 | 저장 명칭]^load [guardar número | guardar nombre]"
    brief = "保存した作品の読み込み^Load the saved works^저장된 작업을 현재 작업장에로드하십시오!^¡Carga el trabajo guardado en el taller actual!"
    description = "保存した作品を番号または名称で指定して、現在の作業場に読み込みます!.^Load the saved works into the current workshop by save number or name.^저장 한 작품을 번호 또는 이름을 지정하여 현재 작업 공간에 불러와요!^Especifique el trabajo guardado por número o nombre y cárguelo en el lugar de trabajo actual."


@dataclasses.dataclass(frozen=True)
class Save:
    usage = "save [保存名称]^save [save name]^save [저장 명칭]^save [guardar nombre]"
    brief = "現在の装飾の保存^Save the current costume^현재의 장식을 저장 할 수 있어!^¡Puede guardar la decoración actual!"
    description = "現在の装飾を保存します.^Save the current costume.^현재의 장식을 저장 할 수 있어! 저장할 이름을 지정하지 않으면, 'Untitled 1'같은 이름을 자동으로 저장할거야!^¡Puede guardar la decoración actual! Si no especifica un nombre para guardar, puede darle automáticamente un nombre como 'Untitled 1'."


@dataclasses.dataclass(frozen=True)
class Delete:
    usage = "delete [保存番号|保存名称]^delete [save number | save name]^delete 저장 번호 | 저장 명칭]^delete [guardar número | guardar nombre]"
    brief = "保存済み作品の削除^Remove the saved work^저장된 작업을 삭제합니다^Eliminar el guardado obras"
    description = "保存済みの作品を削除します.^Remove the your saved work.^저장된 작업을 삭제합니다^Eliminar el trabajo guardado"


@dataclasses.dataclass(frozen=True)
class Random:
    usage = "random^random^random^random"
    brief = "ランダム装飾を作成^Make random costume^무작위 의상 만들기^Hacer un disfraz al azar"
    description = "ランダムな装飾を作成します.^Make the random costume.^무작위 의상을 만들 수 있습니다^puede hacer un disfraz al azar"


@dataclasses.dataclass(frozen=True)
class Invite:
    usage = "invite^invite^invite^invite"
    brief = "BOTのリンク集の表示^Send bot links^봇 링크 보내기^Enviar enlaces de bot"
    description = "招待リンクを表示します.^Send invitation link.^초대 링크 보내기^Enviar enlace de invitación"


@dataclasses.dataclass(frozen=True)
class Lang:
    usage = "lang (言語)^lang (language)^lang (언어)^lang (idioma)"
    brief = "言語の設定^Setup language^설정 언어^Configurar idioma"
    description = "言語を設定します.^Setup your language.^언어를 설정합니다^Configurar idioma"


@dataclasses.dataclass(frozen=True)
class Follow:
    usage = "follow (チャンネル)^follow (channel)^follow (채널)^follow (canal)"
    brief = "BOTの更新情報通知^Receive bot's updates^봇의 업데이트 받기^Recibe actualice de bot"
    description = "BOTの更新情報を受け取るよう設定します.^Receive BOT's updates.^BOT의 업데이트를받습니다^Reciba las actualizaciones de BOT"


@dataclasses.dataclass(frozen=True)
class Notice:
    usage = "notice (チャンネル)^notice (channel)^notice (채널)^notice (canal)"
    brief = "運営の更新情報受け取り^Receive MilkChoco updates^밀크초코 업데이트 받기^Recibe actualice de MilkChoco"
    description = "MilkChoco運営の更新情報を受け取りの設定をします.^Configure MilkChoco's notifications setting.^MilkChoco 업데이트 받기^Reciba actualizaciones de MilkChoco"


@dataclasses.dataclass(frozen=True)
class Ads:
    usage = "ads^ads^ads^ads"
    brief = "10分のタイマーを設定^Set 10 minutes timer^10 분 타이머 설정^aviso después de 10 minutos"
    description = "広告のための10分間のタイマーを設定します.^Set a 10-minute timer for ads.^10 분 타이머 설정^Establecer un temporizador de 10 minutos"


@dataclasses.dataclass(frozen=True)
class Play:
    usage = "play [曲名/URL]^play [曲名/URL]^play [曲名/URL]^play [曲名/URL]"
    brief = "指定した音楽を再生^指定した音楽を再生^指定した音楽を再生^指定した音楽を再生"
    description = "指定した音楽を再生します^指定した音楽を再生します^指定した音楽を再生します^指定した音楽を再生します"


@dataclasses.dataclass(frozen=True)
class Join:
    usage = "join^join^join^join"
    brief = "VCに接続^VCに接続^VCに接続^VCに接続"
    description = "VCに接続します^VCに接続します^VCに接続します^VCに接続します"


@dataclasses.dataclass(frozen=True)
class Disconnect:
    usage = "disconnect^disconnect^disconnect^disconnect"
    brief = "VCから切断^VCから切断^VCから切断^VCから切断"
    description = "VCから切断します^VCから切断します^VCから切断します^VCから切断します"


@dataclasses.dataclass(frozen=True)
class Queue:
    usage = "queue^queue^queue^queue"
    brief = "予約済みの曲の表示^予約済みの曲の表示^予約済みの曲の表示^予約済みの曲の表示"
    description = "予約済みの曲一覧を表示します^予約済みの曲一覧を表示します^予約済みの曲一覧を表示します^予約済みの曲一覧を表示します"


@dataclasses.dataclass(frozen=True)
class Pause:
    usage = "pause^pause^pause^pause"
    brief = "再生を一時停止^再生を一時停止^再生を一時停止^再生を一時停止"
    description = "音楽の再生を一時停止します^音楽の再生を一時停止します^音楽の再生を一時停止します^音楽の再生を一時停止します"


@dataclasses.dataclass(frozen=True)
class Resume:
    usage = "resume^resume^resume^resume"
    brief = "再生の再開^再生の再開^再生の再開^再生の再開"
    description = "音楽の再生を再開します^音楽の再生を再開します^音楽の再生を再開します^音楽の再生を再開します"


@dataclasses.dataclass(frozen=True)
class Skip:
    usage = "skip^skip^skip^skip"
    brief = "音楽をスキップ^音楽をスキップ^音楽をスキップ^音楽をスキップ"
    description = "再生中の音楽をスキップします^再生中の音楽をスキップします^再生中の音楽をスキップします^再生中の音楽をスキップします"


@dataclasses.dataclass(frozen=True)
class NowPlaying:
    usage = "now_playing^now_playing^now_playing^now_playing"
    brief = "再生中の曲の表示^再生中の曲の表示^再生中の曲の表示^再生中の曲の表示"
    description = "再生中の曲を表示します^再生中の曲を表示します^再生中の曲を表示します^再生中の曲を表示します"


@dataclasses.dataclass(frozen=True)
class Remove:
    usage = "remove [位置番号]^remove [位置番号]^remove [位置番号]^remove [位置番号]"
    brief = "予約済みの曲の削除^予約済みの曲の削除^予約済みの曲の削除^予約済みの曲の削除"
    description = "予約済みの曲を削除します^予約済みの曲を削除します^予約済みの曲を削除します^予約済みの曲を削除します"


@dataclasses.dataclass(frozen=True)
class Clear:
    usage = "clear^clear^clear^clear"
    brief = "予約曲のクリア^予約曲のクリア^予約曲のクリア^予約曲のクリア"
    description = "予約済みの曲をすべて削除します^予約済みの曲をすべて削除します^予約済みの曲をすべて削除します^予約済みの曲をすべて削除します"


@dataclasses.dataclass(frozen=True)
class Shuffle:
    usage = "shuffle^shuffle^shuffle^shuffle"
    brief = "予約曲のシャッフル^予約曲のシャッフル^予約曲のシャッフル^予約曲のシャッフル"
    description = "予約済みの曲をシャッフルします^予約済みの曲をシャッフルします^予約済みの曲をシャッフルします^予約済みの曲をシャッフルします"


@dataclasses.dataclass(frozen=True)
class Loop:
    usage = "loop^loop^loop^loop"
    brief = "ループの設定^ループの設定^ループの設定^ループの設定^"
    description = "再生中の1曲をループする設定をします^再生中の1曲をループする設定をします^再生中の1曲をループする設定をします^再生中の1曲をループする設定をします"


@dataclasses.dataclass(frozen=True)
class LoopQueue:
    usage = "loop_queue^loop_queue^loop_queue^loop_queue"
    brief = "予約曲のループ設定^予約曲のループ設定^予約曲のループ設定^予約曲のループ設定"
    description = "予約済みの曲全体のループを設定します^予約済みの曲全体のループを設定します^予約済みの曲全体のループを設定します^予約済みの曲全体のループを設定します"


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
    show = Show()
    # Bot
    invite = Invite()
    language = Lang()
    # Notify
    follow = Follow()
    notice = Notice()
    ads = Ads()
    # Music
    play = Play()
    join = Join()
    disconnect = Disconnect()
    queue = Queue()
    pause = Pause()
    resume = Resume()
    skip = Skip()
    now_playing = NowPlaying()
    remove = Remove()
    clear = Clear()
    shuffle = Shuffle()
    loop = Loop()
    loop_queue = LoopQueue()
