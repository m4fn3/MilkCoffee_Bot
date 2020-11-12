import dataclasses


@dataclasses.dataclass(frozen=True)
class Strings:
    """多言語対応置換用テキスト"""
    # NOTE: common
    your_account_banned = ["あなたのアカウントはブロックされています.\n異議申し立ては、公式サーバーの <#{}> にてご対応させていただきます", "Your account is blocked\nIf you have an objection, please come to <#{}> in Official Server", "당신의 계정은 차단되어 있습니다\n차단에 대한 이의 신청은 공식 서버 <#{}> 에서 대응하겠습니다.", "Su cuenta está prohibida\nSi tiene una objeción a la BAN, utilice <#{}> en el servidor oficial."]
    missing_arguments = ["必須の引数が不足しています!\n正しい使い方: `{0}{1}`\n詳しくは `{0}help {2}`", "Missing required arguments!\nUsage: `{0}help {1}` \nFor more information `{0}help {2}", "f 인수가 충분하지 않습니다. \n사용법 :`{0} {1}`\n 자세한 내용은`{0}help {2}", "No hay suficientes argumentos. \nUso: {0} {1} \nPara obtener más información, `{0}help {2}"]
    interval_too_fast = ["このコマンドの使用が速すぎます!\n`{:.2f}`秒後に再度使用できます.", "You are using this command too quickly!\nTry again in `{:.2f}` seconds.", "명령 실행 간격이 너무 빠릅니다! `{:.2f}` 초 후에 다시 사용할 수 있습니다!", "¡El intervalo de ejecución del comando es demasiado rápido! ¡Puede volver a utilizarlo en `{:.2f}` segundos!"]
    error_occurred = ["未知のエラーが発生しました.開発者にお尋ねください.\n{}", "Unknown error has occurred.Please contact to the developer.\n{}", "오류가 발생했습니다.관리자에게 문의하십시오.\n{}", "Se ha producido un error. Pregunte al administrador.\n{}"]
    missing_subcommand = ["サブコマンドが不足しています!\n`{}help {}`で使い方を確認して下さい.", "Missing subcommand!\n`{}help {}` to know usage.", "하위 명령이 부족한거야! \n`{}help {}` 사용법을 확인 해!", "¡Faltan subcomandos! \n`{}help {}` para ver cómo se usa!"]
    # NOTE: main.py
    prefix_of_the_bot = ["MilkCoffeeのprefixは`{}`です!\n`{}help`で使い方を確認して下さい.", "The prefix for MilkCoffee is `{}`\n`{}help` to know usage.", "이 봇의 접두사는`{}`입니다! 사용 방법에 대한 자세한 내용은 \n` {} 도움말`을 참조하세요.", "¡El prefijo de este bot es `{}`! \n`{}help` para obtener más detalles sobre cómo usarlo."]
    # NOTE: help.py
    help_how_title = ["ヘルプの見方", "How to read the help", "명령 설명 견해", "Cómo leer la descripción del comando"]
    help_how_description = ['リアクションを使用してページ移動できます.', 'You can move the page by the reaction', '메시지의 반응을 눌러 페이지 이동 할 수 있어!', '¡Puede leer más acerca del comando presionando la reacción debajo del mensaje!']
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
    item_not_found = ["検索結果がありません.アイテム名が正しいことを確認してください.", "No results. Make sure that item name is correct.", "결과가 없습니다. 이름을 다시 확인하십시오.", "No hay resultados. Vuelva a comprobar el nombre."]
    wrong_item_index = ["アイテム番号が間違っています. (番号が小さすぎるか大きすぎます)", "Invalid item number. (too big or too small)", "항목 번호가 잘못되었습니다. (숫자가 너무 작거나 큽니다)", "Número de artículo incorrecto (el número es demasiado pequeño o demasiado grande)"]
    menu_find_item = ["アイテム検索", "Search item", "항목 검색", "Artículo de búsqueda"]
    menu_find_description = ["追加するアイテムの名前を入力してください.", "Enter the item name you want to add.", "추가 할 항목 이름을 입력하세요!", "Ingrese el nombre del artículo que desea agregar!"]
    menu_config = ["データ設定", "Data Setup", "데이터 설정", "Configuración de datos"]
    menu_config_description = ["読み込みか保存かをリアクションで選択してください.\n{}: 保存\n{}: 読み込み", "Select either save or load by the reaction.\n{}: save\n{}: load", "저장 또는로드를 선택하십시오.\n{}: 저장\n{}: 로드", "Seleccione guardar o cargar.\n{}: guardar\n{}: cargar"]
    menu_save = ["保存", "Save", "저장", "Salvar"]
    menu_save_description = ["保存時につける名前を入力してください.", "Enter the save name you want to give.", "제공 할 이름을 입력하십시오.", "Ingrese el nombre que desea dar."]
    menu_load = ["読み込み", "Load", "하중", "Carga"]
    menu_load_description = ["読み込みたい保存済み作品の名前または番号を入力してください.", "Enter the saved work name or index that you want to load.", "로드하려는 이름 또는 색인을 입력하십시오.", "Ingrese el nombre o índice que desea cargar."]
    menu_cc = ["装飾コードで設定", "Set the costume code", "의상 코드로 설정", "Establecer el código"]
    menu_cc_description = ["設定したい装飾コードを入力してください.", "Enter the costume code you want to set", "설정하려는 의상 코드를 입력하세요.", "Ingrese el código de vestuario que desea configurar"]
    # costume_table
    costume_table_base = ["ベース色", "base", "색상", "base"]
    costume_table_character = ["キャラクター", "character", "캐릭터", "caracteres"]
    costume_table_weapon = ["武器", "weapon", "무기", "arma"]
    costume_table_head = ["頭装飾", "head", "머리", "cabeza"]
    costume_table_body = ["体装飾", "body", "몸", "cuerpo"]
    costume_table_back = ["背中装飾", "back", "허리", "espalda"]
    costume_table_code = ["装飾コード: {}", "CostumeCode: {}", "장식 코드: {}", "código de decoración: {}"]
    wrong_costume_code = ["間違った装飾コードです.", "Invalid CostumeCode", "잘못된 장식 코드", "Inválido código de decoración"]
    # my, load, save
    no_th_saved_work = ["{}番目に保存された作品はありません.", "No {}th saved work found.", "{} 번째로 저장된 작품은 아니야!", "¡No hay {}th trabajo guardado!"]
    specify_between_1_20 = ["1~20の間で指定して下さい!.", "Specify between 1 and 20 !.", "1 ~ 20 사이의 값을!.", "Por favor, especifique entre 1 y 20."]
    not_found_with_name = ["そのような名前の作品はありません.", "No saved work found with such name.", "그런 이름의 작품은 아니에요!", "¡No hay obra con tal nombre!"]
    loaded_work = ["{}番目の {} を読み込みました.", "Successfully loaded {}th {}", "{} 번째 \"{}\"을 읽어 습니다.", "{}th \"{}\" cargado"]
    save_up_to_20 = ["保存上限数に達しました.", "You have reached maximum numbers of save.", "불필요한 것들은 빼고 20개까지 저장해줄거야!", "¡Puedes guardar hasta 20! ¡Elimina los innecesarios antes de guardar!"]
    int_only_name_not_allowed = ["数字のみの名前は使用できません!", "Numbers-only names are not allowed!", "숫자를 이름으로는 사용할 수 없어!", "¡No puedes usar nombres de solo números!"]
    name_already_used = ["この名前は既に他の作品で使用しています.", "That name is already in use for other works.", "이 이름은 이미 다른 작품에 사용되었어요!", "¡Este nombre ya está en otros trabajos!"]
    name_length_between_1_20 = ["名前は1文字以上20文字以下で指定して下さい.", "For works name, input more than 1 characters but less than 20.", "이름은 1 ~ 20자로 지정주세요!", "Por favor, especifique el nombre con 1 a 20 caracteres."]
    saved_work = ["作品を保存しました!\n名前: {}", "Successfully saved the works!\nName: {}", "저장 했어! 이름: '{}'", "¡Guardado!. Nombre: '{}'"]
    my_title = ["保存した作品集", "Saved works list", "저장된 작품집 ({} / {} 페이지)", "Colección de trabajos guardados ({} / {} páginas)"]
    deleted_work = ["{}番目の {} を削除しました.", "Successfully deleted {}th {}", "{} 번째 {}를 삭제 했어!", "¡El {} th {} ha sido eliminado!"]
    no_any_saved_work = ["まだ保存された作品はありません.", "You haven't saved any works yet.", "당신은 아직 저장하지 않습니다", "Aún no has guardado"]
    # add
    showing_page = ["{} / {} ページを表示中", "current page {} / {} ", "{} / {} 페이를보기", "{} / {} Página de visualización"]
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
    invite_description = ["BOTのリンク集です.わからないことがあれば,お気軽に公式サーバーでお尋ねください.", "Here are some links. If you need help, please feel free to ask in Support Server. Thanks!", "여기에 링크가 있습니다. 도움이 필요하시면 언제든지공식 서버에 문의하십시오. 감사!", "Aquí hay enlaces. Si necesita ayuda, no dude en preguntar en Support Server. ¡Gracias!"]
    invite_url = ["招待URL", "Invite URL", "환대 URL", "URL de invitación"]
    invite_server = ["公式サーバー", "Support Server", "공식 서버", "Servidor de soporte"]
    invite_add = ["その他のリンク", "Additional links", "추가 링크", "enlaces adicionales"]
    invite_vote = ["top.ggで評価する", "Vote me on top.gg", "top.gg 으로 평가", "Vótame en top.gg"]
    lang_not_found = ["言語が見つかりませんでした。", "Language not found.", "언어를 찾을 수 없습니다.", "No se encontró el idioma."]
    # NOTE: notice.py
    # notice
    followed_channel = ["{}でお知らせ用チャンネルをフォローしました.", "Successfully followed news channel in {}!", "{}에서 BOT 알림 채널을 따라갔습니다!", "Seguí el canal de notificación BOT en {}."]
    missing_manage_webhook = ["`manage_webhooks(webhookの管理)`権限が不足しています。\n代わりに公式サーバーの<#{}>を手動でフォローすることもできます。", "Missing required `manage_webhooks` permissions.\nYou can also manually follow <#{}> on the official server instead.", "`manage_webhooks` 권한이 없습니다. \n 공식 서버에서 수동으로 <#{}> 팔로우 할 수도 있습니다.", "`manage_webhooks` No tiene permisos. \nTambién puede seguir manualmente <#{}> en el servidor oficial."]
    notice_title = ["MilkChoco運営の更新情報通知設定", "Setup notifications of MilkChoco!", "MilkChoco 운영의 업데이트 알림 설정!", "¡Configuración de notificaciones de información de actualización de MilkChoco!"]
    notice_description = ['リアクションを押して設定対象チャンネルを設定して下さい.', 'Press the reaction to choose the target channel.', '아래 반응을 누르면 알림 채널이 설정되어 있지 않으면 설정되고, 이미 설정되어 있으면 취소됩니다!',
                          'Si presiona la reacción a continuación, se configurará si no está configurado en el canal de notificación, y se cancelará si ya se configuró.']
    follow_perm_error = ["この操作を行うにはコマンド使用者に**webhookの管理**権限が必要です", "To use this command, you need **manage_webhooks** permission.", "이 명령어를 사용하려면 **webhook 관리** 권한이 필요합니다.", "Para usar este comando, necesita permiso **administrar webhook**"]
    notice_perm_error = ["この操作を行うにはコマンド使用者に**メッセージの管理**権限が必要です", "To use this command, you need **manage_messages** permission.", "이 명령어를 사용하려면 **메시지 관리** 권한이 필요합니다.", "Para usar este comando, necesita permiso **administrar mensajes**"]
    notice_select_channel = ["通知先チャンネル選択", "Select notification channel", "알림 채널 선택", "Seleccionar canal de notificación"]
    notice_select_desc = ["通知を設定したいチャンネルを指定してください\n例: {}\noff と入力すると通知を無効化します.", "Enter the channel that you want to receive notification\nFor example: {}\nType off to disable notification", "알림을 수신 할 채널을 입력하십시오. \n 예 : {} \n 알림을 비활성화하려면 off를 입력하십시오.", "Ingrese el canal en el que desea recibir la notificación \nPor ejemplo: {} \nEscriba off para deshabilitar la notificación"]
    notice_channel_not_found = ["チャンネルが見つかりませんでした.", "Channel not found.", "채널을 찾을 수 없습니다.", "Canal no encontrado"]
    notice_off = ["{}の通知をオフにしました", "Turned off {} notifications", "{}의 알림을 해제했습니다", "Desactivó {} notificaciones"]
    notice_perm_send = ["BOTに{}内での**メッセージの送信**権限がありません", "BOT missing **send_message** permission in {}", "{}에서 **문자 보내** 권한이 BOT 누락 됨", "BOT no tiene permiso **enviar mensaje** en {}"]
    notice_success = ["{0}の通知先を{1}に設定しました", "Successfully configured {1} as {0}'s notification channel!", "{1}에 {0}의 알림을 설정했습니다.", "Estableció correctamente la notificación de {0} en {1}"]
    # ad
    tell_you_after_10_min = ["10分後に再度お知らせします!", "I'll inform you after 10 minutes!", "10 분 후에 다시 알려주세요!", "¡Te lo haré saber en 10 minutos!"]
    passed_10_min = ["10分が経過しました!", "10 minutes have passed!", "{} 님! \n10분 후 요!", "{}\n ¡Han pasado 10 minutos!"]
    # NOTE: help.py
    help_error_title = ["ヘルプ表示のエラー", "Error on help", "도움말 표시 오류", "Ayuda mostrando error"]
    help_command_not_found = ["`{}` というコマンドは存在しません.コマンド名を再確認してください.", "No command `{}` exists. Make sure that command name is correct.", "`{}`명령을 찾을 수 없습니다. 명령 이름을 다시 확인하십시오!", "No pude encontrar el comando {}. ¡Verifique el nombre del comando!"]
    help_subcommand_not_found = ["`{1}` に `{0}` というサブコマンドは存在しません。`{2}help {1}` で使い方を確認できます", "Subcommand `{0}` is not registered in `{1}`. Please check the correct usage with `{2}help {1}`", "하위 명령어`{0}`이 (가)`{1}`에 등록되지 않았습니다. `{2}help {1}`로 사용법을 확인하세요!", "El subcomando `{0}` no está registrado en `{1}`. ¡Compruebe el uso con la `{2}help {1}`!"]
    help_no_subcommand = ["`{0}` にサブコマンドは存在しません。`{1}help {0}` で使い方を確認できます", "No subcommand exists on `{0}`. Please check the correct usage with `{1}help {0}`", "`{0}`에 등록 된 하위 명령이 없습니다.`{1}help {0}`로 사용법을 확인하세요!", "No hay subcomandos registrados en `{0}`.¡Compruebe el uso con la `{1}help {0}`!"]
