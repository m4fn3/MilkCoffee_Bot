import dataclasses


@dataclasses.dataclass(frozen=True)
class Strings:
    """多言語対応置換用テキスト"""
    # NOTE: common
    your_account_banned = ["あなたのアカウントはブロックされています.\n異議申し立ては、公式サーバーの <#{}> にてご対応させていただきます", "Your account is blocked\nIf you have an objection, please come to <#{}> in Official Server", "당신의 계정은 차단되어 있습니다\n차단에 대한 이의 신청은 공식 서버 <#{}> 에서 대응하겠습니다.", "Su cuenta está prohibida\nSi tiene una objeción a la BAN, utilice <#{}> en el servidor oficial."]
    missing_arguments = ["必須の引数が不足しています!\n正しい使い方: `{0}{1}`\n詳しくは `{0}help {2}`", "Missing required arguments!\nUsage: `{0}help {1}` \nFor more information `{0}help {2}", "필수 인수가 없습니다.\n사용법:`{0}help {1}`\n자세한 내용은 `{0}help {2}", "¡Faltan argumentos obligatorios!\nUso: `{0}help {1}`\nPara obtener más información `{0}help {2}"]
    interval_too_fast = ["このコマンドの使用が速すぎます!\n`{:.2f}`秒後に再度使用できます.", "You are using this command too quickly!\nTry again in `{:.2f}` seconds.", "이 명령을 너무 빨리 사용하고 있습니다!\n`{:.2f}`초 후에 다시 시도하십시오.", "¡Está usando este comando demasiado rápido! \ Vuelva a intentarlo en `{: .2f}` segundos."]
    error_occurred = ["未知のエラーが発生しました.開発者にお尋ねください.\n{}", "Unknown error has occurred.Please contact to the developer.\n{}", "알 수없는 오류가 발생했습니다. 개발자에게 문의하십시오. \n {}", "Se produjo un error desconocido. Comuníquese con el desarrollador.\n{}"]
    missing_subcommand = ["サブコマンドが不足しています!\n`{}help {}`で使い方を確認して下さい.", "Missing subcommand!\n`{}help {}` to know usage.", "하위 명령이 없습니다! \n 사용법을 알기위한 `{}help {}`.", "Falta el subcomando. \n`{}help {}` para conocer el uso."]
    # NOTE: main.py
    prefix_of_the_bot = ["MilkCoffeeのprefixは`{}`です!\n`{}help`で使い方を確認して下さい.", "The prefix for MilkCoffee is `{}`\n`{}help` to know usage.", "MilkCoffee의 접두사는 사용법을 알기위한 `{}`\n`{}help` 입니다.", "El prefijo de MilkCoffee es `{}` \n`{} help` para conocer el uso."]
    # NOTE: help.py
    help_how_title = ["ヘルプの見方", "How to read the help", "도움말 읽는 방법", "Cómo leer la help"]
    help_how_description = ['リアクションを使用してページ移動できます.', 'You can move the page by the reaction', '리액션을 사용하여 페이지 이동 할 수 있습니다.', 'Puedes mover la página por la reacción.']
    help_main = [
        "`[引数]　 :` __必須__の引数\n`(引数)　 :` __オプション__の引数\n`[A|B]   :` AまたはB",
        "`[argument] :` __required__ argument\n`(argument) :` __optional__ argument\n`[A|B]      :` either A or B",
        "`[인수]　 :` __필수__ 인수야\n`(인수) 　:` __옵션__ 인수야\n`[A|B]   :` A 또는 B",
        "`[argumento] :` __requerido__ argumento\n`(argumento) :` __opción__ argumento\n`[A|B]       :` A o B"
    ]
    # NOTE: costume.py
    # menu
    menu_base = ["`ベース色　　 :", "`base     :", "`색상　 :", "`base      :"]
    menu_character = ["`キャラクター :", "`character:", "`캐릭터 :", "`caracteres:"]
    menu_weapon = ["`武器　　　　 :", "`weapon   :", "`무기　 :", "`arma      :"]
    menu_head = ["`頭装飾　　　 :", "`head     :", "`머리　 :", "`cabeza    :"]
    menu_body = ["`体装飾　　　 :", "`body     :", "`몸　　 :", "`cuerpo    :"]
    menu_back = ["`背中装飾　　 :", "`back     :", "`허리　 :", "`espalda   :"]
    menu_code = ["装飾コード", "CostumeCode", "장식 코드", "código de decoración"]
    menu_selector_desc = ["追加したいアイテムの名前または番号を入力してください!", "Enter the item name or number that you want to add!", "추가 할 항목의 이름 또는 번호를 입력하십시오!", "Ingrese el nombre o número del artículo que desea agregar."]
    item_not_found = ["検索結果がありません.アイテム名が正しいことを確認してください.", "No results. Make sure that item name is correct.", "결과가 없습니다. 항목의 이름이 올바른지 확인하십시오.", "No hay resultados. Asegúrese de que el nombre del artículo sea correcto."]
    wrong_item_index = ["アイテム番号が間違っています. (番号が小さすぎるか大きすぎます)", "Invalid item number. (too big or too small)", "잘못된 항목 번호입니다. (너무 크거나 작음)", "Número de artículo no válido. (demasiado grande o demasiado pequeño)"]
    menu_find_item = ["アイテム検索", "Search item", "상품 검색", "Búsqueda de artículos"]
    menu_find_description = ["追加するアイテムの名前を入力してください.", "Enter the item name you want to add.", "추가 할 항목 이름을 입력하십시오.", "Ingrese el nombre del elemento que desea agregar."]
    menu_config = ["データ設定", "Data Setup", "데이터 설정", "Configuración de datos"]
    menu_config_description = ["読み込みか保存かをリアクションで選択してください.\n{}: 保存\n{}: 読み込み", "Select either save or load by the reaction.\n{}: save\n{}: load", "로드 또는 저장을 반응에서 선택하십시오.\n{} : 저장 \n{} :로드", "Seleccione guardar o cargar según la reacción. \n {}: guardar \n {}: cargar"]
    menu_save = ["保存", "Save", "저장", "Salvar"]
    menu_save_description = ["保存時につける名前を入力してください.", "Enter the save name you want to give.", "제공 할 이름을 입력하십시오.", "Ingrese el nombre que desea dar."]
    menu_load = ["読み込み", "Load", "하중", "Carga"]
    menu_load_description = ["読み込みたい保存済み作品の名前または番号を入力してください.", "Enter the saved works name or index that you want to load.", "불러 오려는 저장된 작품 명 또는 색인을 입력합니다.", "Introduzca el nombre o índice de las obras guardadas que desee cargar."]
    menu_cc = ["装飾コードで設定", "Set the costume code", "장식 코드 설정", "Establecer el código"]
    menu_cc_description = ["設定したい装飾コードを入力してください.", "Enter the costume code you want to set", "설정하려는 의상 코드를 입력하세요.", "Ingrese el código de vestuario que desea configurar"]
    menu_try_again = ["もう一度お試しください.3回無効なアイテム名を指定すると自動的にメニューに戻ります.", "Try again. If you give an invalid item name three times, it will automatically return to the menu.", "다시 시도하십시오. 잘못된 항목 이름을 세 번 입력하면 자동으로 메뉴로 돌아갑니다.", "Inténtalo de nuevo. Si da un nombre de elemento inválido tres veces, automáticamente regresará al menú."]
    # costume_table
    costume_table_base = ["ベース色", "base", "색상", "base"]
    costume_table_character = ["キャラクター", "character", "캐릭터", "caracteres"]
    costume_table_weapon = ["武器", "weapon", "무기", "arma"]
    costume_table_head = ["頭装飾", "head", "머리", "cabeza"]
    costume_table_body = ["体装飾", "body", "몸", "cuerpo"]
    costume_table_back = ["背中装飾", "back", "허리", "espalda"]
    costume_table_code = ["装飾コード: {}", "CostumeCode: {}", "장식 코드: {}", "código de decoración: {}"]
    wrong_costume_code = ["間違った装飾コードです.", "Invalid CostumeCode", "잘못된 의상 코드", "Código de vestuario no válido"]
    # my, load, save
    no_th_saved_work = ["{}番目に保存された作品はありません.", "No {}th saved work found.", "{} 번째로 저장된 작품은 아닙니다.", "No hay {}th trabajo guardado."]
    specify_between_1_20 = ["1~20の間で指定して下さい!.", "Specify between 1 and 20 !.", "1 ~ 20 사이의 값을!.", "Por favor, especifique entre 1 y 20."]
    not_found_with_name = ["そのような名前の作品はありません.", "No saved works found with such name.", "해당 이름으로 저장된 작품이 없습니다.", "No se encontraron obras guardadas con ese nombre."]
    loaded_work = ["{}番目の {} を読み込みました.", "Successfully loaded {}th {}", "{} 번째 {}를 가져 왔습니다.", "Se ha leído el {}th {}."]
    save_up_to_20 = ["保存上限数に達しました.", "You have reached maximum numbers of save.", "저장 최대 개수에 도달했습니다.", "Ha alcanzado el número máximo de guardado."]
    int_only_name_not_allowed = ["数字のみの名前は使用できません!", "Numbers-only names are not allowed!", "숫자 만 이름은 사용할 수 없습니다!", "¡No se permiten nombres de solo números!"]
    name_already_used = ["この名前は既に他の作品で使用しています.", "That name is already in use for other works.", "그 이름은 이미 다른 작품에 사용되고 있습니다.", "Ese nombre ya está en uso para otras obras."]
    name_length_between_1_20 = ["名前は1文字以上20文字以下で指定して下さい.", "For works name, input more than 1 characters but less than 20.", "이름은 1 ~ 20자로 지정주세요!", "Por favor, especifique el nombre con 1 a 20 caracteres."]
    saved_work = ["作品を保存しました!\n名前: {}", "Successfully saved the works!\nName: {}", "작품을 성공적으로 저장했습니다! \n 이름 : {}", "¡Guardado correctamente las obras! \nNombre: {}"]
    my_title = ["保存した作品集", "Saved works list", "저장된 작품 목록", "Lista de trabajos guardados"]
    deleted_work = ["{}番目の {} を削除しました.", "Successfully deleted {}th {}", "{} 번째 {}을 (를) 삭제했습니다.", "Eliminado {} th {}."]
    no_any_saved_work = ["まだ保存された作品はありません.", "You haven't saved any works yet.", "아직 저장 한 작품이 없습니다.", "Aún no has guardado ninguna obra."]
    # add
    showing_page = ["{} / {} ページを表示中", "Current page {} / {}", "{} / {} 페이를보기", "{} / {} Página de visualización"]
    # list
    list_base_title = ["色一覧", "base list", "base 목록", "lista base"]
    list_weapon_title = ["武器一覧", "Weapon list", "무기 목록", "lista de arma"]
    list_character_title = ["キャラ一覧", "Character list", "캐릭터 목록", "lista de personajes"]
    list_head_title = ["頭装飾一覧", "Head list", "머리 목록", "lista de head"]
    list_body_title = ["体装飾一覧", "Body list", "몸 목록", "lista de body"]
    list_back_title = ["背中装飾一覧", "Back list", "허리 목록", "lista de back"]
    # NOTE: bot.py
    # invite
    invite_title = ["招待リンク", "Invitation links", "초대 링크", "Enlace de invitación"]
    invite_description = ["BOTのリンク集です.わからないことがあれば,お気軽に公式サーバーでお尋ねください.", "Here are some links. If you need help, please feel free to ask in Support Server. Thanks!", "다음은 몇 가지 링크입니다. 도움이 필요하시면 언제든지 지원 서버에 문의하십시오. 감사!", "A continuación se muestran algunos enlaces. Si necesita ayuda, no dude en preguntar en el servidor de soporte. ¡Gracias!"]
    invite_url = ["招待URL", "Invite URL", "환대 URL", "URL de invitación"]
    invite_server = ["公式サーバー", "Support Server", "공식 서버", "Servidor de soporte"]
    invite_add = ["その他のリンク", "Additional links", "추가 링크", "enlaces adicionales"]
    invite_vote = ["top.ggで評価する", "Vote me on top.gg", "top.gg 으로 평가", "Vótame en top.gg"]
    lang_not_found = ["言語が見つかりませんでした。", "Language not found.", "언어를 찾을 수 없습니다.", "Idioma no encontrado."]
    # NOTE: notice.py
    # notice
    followed_channel = ["{}でお知らせ用チャンネルをフォローしました.", "Successfully followed news channel in {}!", "{}에서 뉴스 채널을 성공적으로 팔로우했습니다.", "Has seguido con éxito el canal de noticias en {}."]
    missing_manage_webhook = ["`manage_webhooks(webhookの管理)`権限が不足しています。\n代わりに公式サーバーの<#{}>を手動でフォローすることもできます。", "Missing required `manage_webhooks` permissions.\nYou can also manually follow <#{}> on the official server instead.", "`manage_webhooks` 권한이 없습니다. \n 공식 서버에서 수동으로 <#{}> 팔로우 할 수도 있습니다.", "`manage_webhooks` No tiene permisos. \nTambién puede seguir manualmente <#{}> en el servidor oficial."]
    notice_title = ["MilkChoco運営の更新情報通知設定", "Setup notifications of MilkChoco!", "MilkChoco 운영의 업데이트 알림 설정!", "¡Configuración de notificaciones de información de actualización de MilkChoco!"]
    notice_description = ['リアクションを押して設定対象チャンネルを設定して下さい.', 'Press the reaction to choose the target channel.', '리액션을 눌러 설정 대상 채널을 설정하십시오.', 'Presione la reacción para elegir el canal objetivo.']
    follow_perm_error = ["この操作を行うにはコマンド使用者に**webhookの管理**権限が必要です", "To use this command, you need **manage_webhooks** permission.", "이 명령어를 사용하려면 **webhook 관리** 권한이 필요합니다.", "Para usar este comando, necesita permiso **administrar webhook**"]
    notice_perm_error = ["この操作を行うにはコマンド使用者に**メッセージの管理**権限が必要です", "To use this command, you need **manage_messages** permission.", "이 명령어를 사용하려면 **메시지 관리** 권한이 필요합니다.", "Para usar este comando, necesita permiso **administrar mensajes**"]
    notice_select_channel = ["通知先チャンネル選択", "Select notification channel", "알림 채널 선택", "Seleccionar canal de notificación"]
    notice_select_desc = ["通知を設定したいチャンネルを指定してください\n例: {}\noff と入力すると通知を無効化します.", "Enter the channel that you want to receive notification\nFor example: {}\nType off to disable notification", "알림을 수신 할 채널을 입력하십시오. \n 예 : {} \n 알림을 비활성화하려면 off를 입력하십시오.", "Ingrese el canal en el que desea recibir la notificación \nPor ejemplo: {} \nEscriba off para deshabilitar la notificación"]
    notice_channel_not_found = ["チャンネルが見つかりませんでした.", "Channel not found.", "채널을 찾을 수 없습니다.", "Canal no encontrado."]
    notice_off = ["{}の通知をオフにしました.", "Turned off {} notifications.", "{}의 알림을 해제했습니다.", "Desactivó {} notificaciones."]
    notice_perm_send = ["BOTに{}内での**メッセージの送信**権限がありません", "BOT missing **send_message** permission in {}", "{}에서 **문자 보내** 권한이 BOT 누락 됨", "BOT no tiene permiso **enviar mensaje** en {}"]
    notice_success = ["{0}の通知先を{1}に設定しました", "Successfully configured {1} as {0}'s notification channel!", "{1}을 (를) {0}의 알림 채널로 구성했습니다.", "¡Configurado correctamente {1} como canal de notificación de {0}!"]
    # ad
    tell_you_after_10_min = ["10分後に再度お知らせします!", "I'll inform you after 10 minutes!", "10 분 후에 알려 드리겠습니다!", "¡Te informaré después de 10 minutos!"]
    passed_10_min = ["10分が経過しました!", "10 minutes have passed!", "10 분이 지났습니다!", "¡Han pasado 10 minutos!"]
    # NOTE: help.py
    help_error_title = ["ヘルプ表示のエラー", "Error on help", "도움말 표시 오류", "Ayuda mostrando error"]
    help_command_not_found = ["`{}` というコマンドは存在しません.コマンド名を再確認してください.", "No command `{}` exists. Make sure that command name is correct.", "`{}`명령을 찾을 수 없습니다. 명령 이름을 다시 확인하십시오!", "No pude encontrar el comando {}. ¡Verifique el nombre del comando!"]
    help_subcommand_not_found = ["`{1}` に `{0}` というサブコマンドは存在しません。`{2}help {1}` で使い方を確認できます", "Subcommand `{0}` is not registered in `{1}`. Please check the correct usage with `{2}help {1}`", "하위 명령어`{0}`이 (가)`{1}`에 등록되지 않았습니다. `{2}help {1}`로 사용법을 확인하세요!", "El subcomando `{0}` no está registrado en `{1}`. ¡Compruebe el uso con la `{2}help {1}`!"]
    help_no_subcommand = ["`{0}` にサブコマンドは存在しません。`{1}help {0}` で使い方を確認できます", "No subcommand exists on `{0}`. Please check the correct usage with `{1}help {0}`", "`{0}`에 등록 된 하위 명령이 없습니다.`{1}help {0}`로 사용법을 확인하세요!", "No hay subcomandos registrados en `{0}`.¡Compruebe el uso con la `{1}help {0}`!"]
