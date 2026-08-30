from __future__ import annotations

DEFAULT_LANGUAGE = "ru"
LANGUAGES = ("ru", "en", "tk")

# Each language's own name, shown on the language-picker buttons — always in
# that language itself, never translated into the currently active one.
LANGUAGE_LABELS = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "tk": "🇹🇲 Türkmençe",
}


def resolve_language(code: str | None) -> str:
    if code:
        code = code.lower()
        if code in LANGUAGES:
            return code
    return DEFAULT_LANGUAGE


_STRINGS: dict[str, dict[str, str]] = {
    "welcome": {
        "ru": (
            "{icon} <b>ArsiCloudBot</b> 🌐\n\n"
            "<i>Умный помощник для управления VPN: ноды, облако, шифрование и "
            "безопасность — всё в одном месте.</i>\n\n"
            "👇 Выберите раздел, чтобы начать"
        ),
        "en": (
            "{icon} <b>ArsiCloudBot</b> 🌐\n\n"
            "<i>Your smart VPN companion: nodes, cloud, encryption and security — "
            "all in one place.</i>\n\n"
            "👇 Choose a section to get started"
        ),
        "tk": (
            "{icon} <b>ArsiCloudBot</b> 🌐\n\n"
            "<i>VPN dolandyryşy üçin akylly kömekçiňiz: node-lar, bulut, şifrleme "
            "we howpsuzlyk — bary-ýogy bir ýerde.</i>\n\n"
            "👇 Başlamak üçin bölümi saýlaň"
        ),
    },
    # --- Button labels ---
    "btn_node": {"ru": "🖥 Node", "en": "🖥 Node", "tk": "🖥 Node"},
    "btn_cloud_vpn": {"ru": "☁️ Cloud VPN", "en": "☁️ Cloud VPN", "tk": "☁️ Cloud VPN"},
    "btn_cloud_account": {"ru": "👤 Cloud Account", "en": "👤 Cloud Account", "tk": "👤 Cloud Account"},
    "btn_crypt": {"ru": "🔐 Crypt/Decrypt", "en": "🔐 Crypt/Decrypt", "tk": "🔐 Crypt/Decrypt"},
    "btn_language": {"ru": "🌐 Язык", "en": "🌐 Language", "tk": "🌐 Dil"},
    "btn_info": {"ru": "ℹ️ Инфо", "en": "ℹ️ Info", "tk": "ℹ️ Maglumat"},
    "btn_sos": {"ru": "🆘 SOS", "en": "🆘 SOS", "tk": "🆘 SOS"},
    "sos_greeting": {
        "ru": "Здравствуйте! У меня вопрос:",
        "en": "Hello! I have a question:",
        "tk": "Salam! Bir soragym bar:",
    },
    "btn_back": {"ru": "⬅️ Назад", "en": "⬅️ Back", "tk": "⬅️ Yza"},
    "btn_cancel": {"ru": "❌ Отмена", "en": "❌ Cancel", "tk": "❌ Ýatyr"},
    "btn_marzban": {"ru": "⚡ Marzban Node", "en": "⚡ Marzban Node", "tk": "⚡ Marzban Node"},
    "btn_pasarguard": {"ru": "🛡 PasarGuard", "en": "🛡 PasarGuard", "tk": "🛡 PasarGuard"},
    "btn_install": {"ru": "✅ Установить", "en": "✅ Install", "tk": "✅ Ornaşdyr"},
    "btn_node_menu": {"ru": "🖥 В меню Node", "en": "🖥 Node menu", "tk": "🖥 Node menýusy"},
    "btn_main_menu": {"ru": "🏠 Главное меню", "en": "🏠 Main menu", "tk": "🏠 Baş menýu"},
    "btn_panel": {"ru": "⚙️ Panel", "en": "⚙️ Panel", "tk": "⚙️ Panel"},
    "btn_panel_marzban": {"ru": "⚡ Marzban", "en": "⚡ Marzban", "tk": "⚡ Marzban"},
    "btn_panel_pasarguard": {"ru": "🛡 PasarGuard", "en": "🛡 PasarGuard", "tk": "🛡 PasarGuard"},
    "btn_panel_3xui": {"ru": "3️⃣ 3X-UI", "en": "3️⃣ 3X-UI", "tk": "3️⃣ 3X-UI"},
    "btn_panel_stats": {"ru": "📊 Статистика", "en": "📊 Statistics", "tk": "📊 Statistika"},
    "btn_panel_users": {"ru": "👥 Пользователи", "en": "👥 Users", "tk": "👥 Ulanyjylar"},
    "btn_panel_remove": {
        "ru": "🗑 Убрать панель",
        "en": "🗑 Remove panel",
        "tk": "🗑 Paneli aýyr",
    },
    "btn_panel_remove_confirm": {
        "ru": "🗑 Да, убрать",
        "en": "🗑 Yes, remove",
        "tk": "🗑 Hawa, aýyr",
    },
    "btn_panel_dashboard": {"ru": "⬅️ К панели", "en": "⬅️ Back to panel", "tk": "⬅️ Panele gaýt"},
    "btn_panel_menu": {"ru": "⚙️ Меню Panel", "en": "⚙️ Panel menu", "tk": "⚙️ Panel menýusy"},
    "btn_panel_add": {"ru": "➕ Добавить панель", "en": "➕ Add panel", "tk": "➕ Panel goş"},
    "btn_panel_list": {"ru": "📋 Мои панели", "en": "📋 My panels", "tk": "📋 Panellerim"},
    "btn_profile": {"ru": "👤 Профиль", "en": "👤 Profile", "tk": "👤 Profil"},
    "profile_no_username": {"ru": "не указан", "en": "not set", "tk": "görkezilmedik"},
    "profile_text": {
        "ru": (
            "{icon} <b>Профиль</b>\n\n"
            "👋 Имя: {name}\n"
            "🔗 Юзернейм: {username}\n"
            "🆔 Telegram ID: <code>{user_id}</code>\n"
            "🌐 Язык: {language}\n"
            "⚙️ Подключено панелей: <b>{panels_count}</b>\n\n"
            "💰 Баланс: скоро появится здесь"
        ),
        "en": (
            "{icon} <b>Profile</b>\n\n"
            "👋 Name: {name}\n"
            "🔗 Username: {username}\n"
            "🆔 Telegram ID: <code>{user_id}</code>\n"
            "🌐 Language: {language}\n"
            "⚙️ Panels connected: <b>{panels_count}</b>\n\n"
            "💰 Balance: coming soon"
        ),
        "tk": (
            "{icon} <b>Profil</b>\n\n"
            "👋 Ady: {name}\n"
            "🔗 Ulanyjy ady: {username}\n"
            "🆔 Telegram ID: <code>{user_id}</code>\n"
            "🌐 Dili: {language}\n"
            "⚙️ Birikdirilen panel: <b>{panels_count}</b>\n\n"
            "💰 Balans: ýakynda bu ýerde peýda bolar"
        ),
    },
    "btn_panel_create_user": {
        "ru": "➕ Создать пользователя",
        "en": "➕ Create user",
        "tk": "➕ Ulanyjy döret",
    },
    "btn_panel_create_confirm": {"ru": "✅ Создать", "en": "✅ Create", "tk": "✅ Döret"},
    "btn_panel_user_enable": {"ru": "✅ Включить", "en": "✅ Enable", "tk": "✅ Işjeňleşdir"},
    "btn_panel_user_disable": {"ru": "⛔ Отключить", "en": "⛔ Disable", "tk": "⛔ Öçür"},
    "btn_panel_user_reset": {
        "ru": "🔄 Сбросить трафик",
        "en": "🔄 Reset traffic",
        "tk": "🔄 Traffigi arassala",
    },
    "btn_panel_user_edit": {"ru": "✏️ Изменить", "en": "✏️ Edit", "tk": "✏️ Üýtget"},
    "btn_panel_user_delete": {"ru": "🗑 Удалить", "en": "🗑 Delete", "tk": "🗑 Poz"},
    "btn_panel_user_delete_confirm": {
        "ru": "🗑 Да, удалить",
        "en": "🗑 Yes, delete",
        "tk": "🗑 Hawa, poz",
    },
    # --- Section placeholders ---
    "section_cloud_vpn": {
        "ru": (
            "{icon} <b>Cloud VPN</b> 📶\n\n"
            "<i>Управление облачными VPN-подключениями появится здесь совсем скоро.</i>\n\n"
            "🛠️ Уже в разработке"
        ),
        "en": (
            "{icon} <b>Cloud VPN</b> 📶\n\n"
            "<i>Cloud VPN connection management is coming here very soon.</i>\n\n"
            "🛠️ Already in the works"
        ),
        "tk": (
            "{icon} <b>Cloud VPN</b> 📶\n\n"
            "<i>Bulut VPN birikmelerini dolandyrmak ýakynda bu ýerde peýda bolar.</i>\n\n"
            "🛠️ Eýýäm işlenilýär"
        ),
    },
    "section_cloud_account": {
        "ru": (
            "{icon} <b>Cloud Account</b> 🔑\n\n"
            "<i>Управление вашим аккаунтом появится совсем скоро.</i>\n\n"
            "🛠️ Уже в разработке"
        ),
        "en": (
            "{icon} <b>Cloud Account</b> 🔑\n\n"
            "<i>Account management is coming very soon.</i>\n\n"
            "🛠️ Already in the works"
        ),
        "tk": (
            "{icon} <b>Cloud Account</b> 🔑\n\n"
            "<i>Hasabyňyzy dolandyrmak ýakyn wagtda goşular.</i>\n\n"
            "🛠️ Eýýäm işlenilýär"
        ),
    },
    "section_crypt": {
        "ru": (
            "{icon} <b>Crypt / Decrypt</b> 🗝️\n\n"
            "<i>Шифрование и дешифрование данных — уже в работе.</i>\n\n"
            "🛠️ Скоро будет доступно"
        ),
        "en": (
            "{icon} <b>Crypt / Decrypt</b> 🗝️\n\n"
            "<i>Data encryption and decryption tools are already in the works.</i>\n\n"
            "🛠️ Coming soon"
        ),
        "tk": (
            "{icon} <b>Crypt / Decrypt</b> 🗝️\n\n"
            "<i>Maglumatlary şifrlemek we deşifrlemek eýýäm işlenilýär.</i>\n\n"
            "🛠️ Ýakynda elýeterli bolar"
        ),
    },
    "section_info": {
        "ru": (
            "{icon} <b>ArsiCloudBot</b> 🖥️\n\n"
            "<i>Ваш помощник по управлению VPN — просто, быстро и безопасно.</i>\n\n"
            "🏷️ Версия <code>0.1.0</code>"
        ),
        "en": (
            "{icon} <b>ArsiCloudBot</b> 🖥️\n\n"
            "<i>Your VPN management companion — simple, fast and secure.</i>\n\n"
            "🏷️ Version <code>0.1.0</code>"
        ),
        "tk": (
            "{icon} <b>ArsiCloudBot</b> 🖥️\n\n"
            "<i>VPN dolandyryş kömekçiňiz — ýönekeý, çalt we howpsuz.</i>\n\n"
            "🏷️ Wersiýa <code>0.1.0</code>"
        ),
    },
    "section_sos_contact": {
        "ru": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Что-то пошло не так? Мы всегда на связи.</i>\n\n"
            "📩 Напишите нам: {contact}"
        ),
        "en": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Something's not working? We're always here.</i>\n\n"
            "📩 Contact us: {contact}"
        ),
        "tk": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Bir zat nädogry gitdimi? Biz hemişe ýanyňyzda.</i>\n\n"
            "📩 Bize ýazyň: {contact}"
        ),
    },
    "section_sos_empty": {
        "ru": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Что-то пошло не так? Мы всегда на связи.</i>\n\n"
            "📩 Поддержка появится здесь совсем скоро"
        ),
        "en": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Something's not working? We're always here.</i>\n\n"
            "📩 Support contact is coming very soon"
        ),
        "tk": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Bir zat nädogry gitdimi? Biz hemişe ýanyňyzda.</i>\n\n"
            "📩 Goldaw ýakynda bu ýerde peýda bolar"
        ),
    },
    # --- Language picker ---
    "language_prompt": {
        "ru": (
            "{icon} <b>Язык интерфейса</b> 📡\n\n"
            "<i>Выберите, на каком языке вам удобнее общаться с ботом.</i>\n\n"
            "👇 Доступные языки"
        ),
        "en": (
            "{icon} <b>Interface language</b> 📡\n\n"
            "<i>Choose the language you'd like the bot to speak.</i>\n\n"
            "👇 Available languages"
        ),
        "tk": (
            "{icon} <b>Interfeýsiň dili</b> 📡\n\n"
            "<i>Bot bilen haýsy dilde gürleşmek isleýändigiňizi saýlaň.</i>\n\n"
            "👇 Elýeterli diller"
        ),
    },
    "language_saved": {
        "ru": "✅ <b>Готово!</b>\n\nИнтерфейс переключён на русский язык 🇷🇺",
        "en": "✅ <b>Done!</b>\n\nThe interface is now in English 🇬🇧",
        "tk": "✅ <b>Taýyn!</b>\n\nInterfeýs indi türkmen dilinde 🇹🇲",
    },
    # --- Node flow ---
    "title_marzban": {"ru": "Marzban Node", "en": "Marzban Node", "tk": "Marzban Node"},
    "title_pasarguard": {"ru": "PasarGuard", "en": "PasarGuard", "tk": "PasarGuard"},
    "node_menu": {
        "ru": (
            "{icon} <b>Node</b> 🖧\n\n"
            "<i>Разверните VPN-ноду на своём сервере за пару минут — бот сделает всё сам.</i>\n\n"
            "👇 Выберите платформу"
        ),
        "en": (
            "{icon} <b>Node</b> 🖧\n\n"
            "<i>Deploy a VPN node on your server in a couple of minutes — the bot handles the rest.</i>\n\n"
            "👇 Choose a platform"
        ),
        "tk": (
            "{icon} <b>Node</b> 🖧\n\n"
            "<i>Serweriňizde birnäçe minutda VPN node ornaşdyryň — galanyny bot eder.</i>\n\n"
            "👇 Platformany saýlaň"
        ),
    },
    "node_cancelled": {
        "ru": (
            "{icon} <b>Node</b>\n\n"
            "🚫 <i>Установка отменена — данные не сохранены.</i>\n\n"
            "👇 Можно начать заново в любой момент"
        ),
        "en": (
            "{icon} <b>Node</b>\n\n"
            "🚫 <i>Installation cancelled — nothing was saved.</i>\n\n"
            "👇 You can start again anytime"
        ),
        "tk": (
            "{icon} <b>Node</b>\n\n"
            "🚫 <i>Ornaşdyrma ýatyryldy — hiç zat ýatda saklanmady.</i>\n\n"
            "👇 Islän wagtyňyz täzeden başlap bilersiňiz"
        ),
    },
    "step_ip": {
        "ru": "{header}\n<i>Шаг 1 из 3</i>\n\n{icon} Пришлите IP-адрес или домен сервера.",
        "en": "{header}\n<i>Step 1 of 3</i>\n\n{icon} Send the server's IP address or domain.",
        "tk": "{header}\n<i>1-nji ädim / 3</i>\n\n{icon} Serweriň IP salgysyny ýa-da domenini iberiň.",
    },
    "invalid_host": {
        "ru": "Похоже, это не IP-адрес и не домен. Попробуйте ещё раз — например: <code>203.0.113.10</code>",
        "en": "That doesn't look like an IP address or domain. Try again — for example: <code>203.0.113.10</code>",
        "tk": "Bu IP salga ýa-da domene meňzänok. Täzeden synanyşyň — mysal üçin: <code>203.0.113.10</code>",
    },
    "step_ssh_user": {
        "ru": (
            "{header}\n<i>Шаг 2 из 3</i>\n\n"
            "Кто главный на сервере? Напишите имя SSH-пользователя — подойдёт и "
            "<code>root</code>, и обычный sudo-пользователь, бот сам разберётся с правами."
        ),
        "en": (
            "{header}\n<i>Step 2 of 3</i>\n\n"
            "Who's in charge on the server? Type the SSH username — <code>root</code> or a "
            "regular sudo user both work, the bot will handle the privileges."
        ),
        "tk": (
            "{header}\n<i>2-nji ädim / 3</i>\n\n"
            "Serwerde kim esasy? SSH ulanyjy adyny ýazyň — <code>root</code> hem, adaty sudo "
            "ulanyjy hem bolýar, bot hukuklary özi çözer."
        ),
    },
    "invalid_ssh_user": {
        "ru": "Имя пользователя может содержать только буквы, цифры, «_» и «-». Попробуйте ещё раз.",
        "en": "The username can only contain letters, digits, “_” and “-”. Try again.",
        "tk": "Ulanyjy ady diňe harplardan, sanlardan, «_» we «-» dan ybarat bolup biler. Täzeden synanyşyň.",
    },
    "step_password": {
        "ru": (
            "{header}\n<i>Шаг 3 из 3</i>\n\n"
            "Пароль от <b>{username}</b>, пожалуйста.\n\n"
            "{icon} <i>Сообщение с паролем удалится сразу после отправки — он нужен только "
            "для подключения и нигде не сохраняется.</i>"
        ),
        "en": (
            "{header}\n<i>Step 3 of 3</i>\n\n"
            "Password for <b>{username}</b>, please.\n\n"
            "{icon} <i>The message with the password will be deleted right after you send it — "
            "it's only used to connect and is never stored.</i>"
        ),
        "tk": (
            "{header}\n<i>3-nji ädim / 3</i>\n\n"
            "<b>{username}</b> üçin parol, haýyş edýäris.\n\n"
            "{icon} <i>Parol bilen habar iberilenden soň derrew öçüriler — ol diňe birikmek "
            "üçin gerek we hiç ýerde saklanmaýar.</i>"
        ),
    },
    "empty_password": {
        "ru": "Пароль не может быть пустым. Отправьте его ещё раз.",
        "en": "The password can't be empty. Send it again.",
        "tk": "Parol boş bolup bilmez. Ony täzeden iberiň.",
    },
    "ask_cert": {
        "ru": (
            "{icon} Остался сертификат клиента из панели Marzban (его выдают при добавлении ноды).\n"
            "<i>Пришлите файлом (.pem / .crt) или просто текстом.</i>"
        ),
        "en": (
            "{icon} Last thing — the client certificate from the Marzban panel (you get it when "
            "adding a node).\n<i>Send it as a file (.pem / .crt) or as plain text.</i>"
        ),
        "tk": (
            "{icon} Marzban panelinden alynýan müşderi sertifikaty galdy (node goşulanda berilýär).\n"
            "<i>Faýl (.pem / .crt) ýa-da ýönekeý tekst hökmünde iberiň.</i>"
        ),
    },
    "invalid_cert": {
        "ru": (
            "Это не похоже на сертификат в формате PEM — он должен начинаться с "
            "<code>-----BEGIN CERTIFICATE-----</code>. Пришлите ещё раз."
        ),
        "en": (
            "That doesn't look like a PEM certificate — it should start with "
            "<code>-----BEGIN CERTIFICATE-----</code>. Send it again."
        ),
        "tk": (
            "Bu PEM formatly sertifikata meňzänok — ol <code>-----BEGIN CERTIFICATE-----</code> "
            "bilen başlamaly. Täzeden iberiň."
        ),
    },
    "confirmation": {
        "ru": (
            "{header}\n\n"
            "📋 <b>Проверьте данные:</b>\n"
            "🌍 Сервер: <code>{host}</code>\n"
            "👤 Пользователь: <code>{user}</code>\n\n"
            "🚀 Всё готово — начинаем установку?"
        ),
        "en": (
            "{header}\n\n"
            "📋 <b>Please confirm:</b>\n"
            "🌍 Server: <code>{host}</code>\n"
            "👤 User: <code>{user}</code>\n\n"
            "🚀 Ready — start the installation?"
        ),
        "tk": (
            "{header}\n\n"
            "📋 <b>Maglumatlary barlaň:</b>\n"
            "🌍 Server: <code>{host}</code>\n"
            "👤 Ulanyjy: <code>{user}</code>\n\n"
            "🚀 Taýyn — ornaşdyrmaga başlaýarysmy?"
        ),
    },
    "installing_started": {
        "ru": "{icon} Начинаю установку...",
        "en": "{icon} Starting the installation...",
        "tk": "{icon} Ornaşdyrma başlanýar...",
    },
    "error": {
        "ru": (
            "{icon} <b>Не получилось установить ноду</b>\n\n"
            "{reason}\n\n"
            "🔁 Попробуйте ещё раз или обратитесь в поддержку"
        ),
        "en": (
            "{icon} <b>Couldn't install the node</b>\n\n"
            "{reason}\n\n"
            "🔁 Try again, or reach out to support"
        ),
        "tk": (
            "{icon} <b>Node ornaşdyrylyp bilinmedi</b>\n\n"
            "{reason}\n\n"
            "🔁 Täzeden synanyşyň ýa-da goldawa ýüz tutuň"
        ),
    },
    "unexpected_error": {
        "ru": "{icon} <b>Непредвиденная ошибка</b>\n\n{reason}",
        "en": "{icon} <b>Unexpected error</b>\n\n{reason}",
        "tk": "{icon} <b>Garaşylmadyk ýalňyşlyk</b>\n\n{reason}",
    },
    "result_header": {
        "ru": "{icon} {header} успешно запущена на <code>{host}</code> 🚀",
        "en": "{icon} {header} is up and running on <code>{host}</code> 🚀",
        "tk": "{icon} {header} <code>{host}</code> serwerde üstünlikli işledildi 🚀",
    },
    "result_dir": {
        "ru": "📁 Папка: <code>{dir}</code>",
        "en": "📁 Folder: <code>{dir}</code>",
        "tk": "📁 Bukja: <code>{dir}</code>",
    },
    "result_status": {
        "ru": "📶 Статус: <code>{status}</code>",
        "en": "📶 Status: <code>{status}</code>",
        "tk": "📶 Ýagdaýy: <code>{status}</code>",
    },
    "result_pasarguard_intro": {
        "ru": "🛡 <b>Добавьте ноду в панели PasarGuard:</b>",
        "en": "🛡 <b>Add this node in the PasarGuard panel:</b>",
        "tk": "🛡 <b>Bu node-y PasarGuard panelinde goşuň:</b>",
    },
    "result_pasarguard_creds": {
        "ru": "🔌 Порт <code>{port}</code> · 🔑 API_KEY <code>{key}</code>",
        "en": "🔌 Port <code>{port}</code> · 🔑 API_KEY <code>{key}</code>",
        "tk": "🔌 Port <code>{port}</code> · 🔑 API_KEY <code>{key}</code>",
    },
    "result_pasarguard_cert_intro": {
        "ru": "📜 Сертификат ноды:",
        "en": "📜 Node certificate:",
        "tk": "📜 Node sertifikaty:",
    },
    # --- Install progress ---
    "progress_connecting": {
        "ru": "{icon} Захожу на сервер...",
        "en": "{icon} Connecting to the server...",
        "tk": "{icon} Servere birikilýär...",
    },
    "progress_checking_docker": {
        "ru": "{icon} Проверяю Docker...",
        "en": "{icon} Checking Docker...",
        "tk": "{icon} Docker barlanýar...",
    },
    "progress_installing_docker": {
        "ru": "{icon} Docker не найден — ставлю (пара минут)...",
        "en": "{icon} Docker not found — installing it (a couple of minutes)...",
        "tk": "{icon} Docker tapylmady — gurnalýar (birnäçe minut)...",
    },
    "progress_installing_compose": {
        "ru": "{icon} Добавляю плагин docker compose...",
        "en": "{icon} Adding the docker compose plugin...",
        "tk": "{icon} docker compose plugini goşulýar...",
    },
    "progress_uploading_marzban": {
        "ru": "{icon} Загружаю сертификат и конфигурацию...",
        "en": "{icon} Uploading the certificate and configuration...",
        "tk": "{icon} Sertifikat we konfigurasiýa ýüklenilýär...",
    },
    "progress_generating_pasarguard_cert": {
        "ru": "{icon} Готовлю сертификат ноды...",
        "en": "{icon} Generating the node certificate...",
        "tk": "{icon} Node sertifikaty taýýarlanylýar...",
    },
    "progress_uploading_pasarguard": {
        "ru": "{icon} Настраиваю docker-compose и .env...",
        "en": "{icon} Setting up docker-compose and .env...",
        "tk": "{icon} docker-compose we .env sazlanylýar...",
    },
    "progress_launching": {
        "ru": "{icon} Запускаю контейнер {container}...",
        "en": "{icon} Starting the {container} container...",
        "tk": "{icon} {container} konteýneri işe girizilýär...",
    },
    # --- Technical error hints (SSH / installer) ---
    "err_ssh_timeout": {
        "ru": "Не удалось подключиться по SSH: сервер не отвечает (таймаут). Проверьте IP-адрес, порт 22 и firewall.",
        "en": "Couldn't connect over SSH: the server isn't responding (timeout). Check the IP address, port 22 and the firewall.",
        "tk": "SSH arkaly birikip bolmady: server jogap bermeýär (wagt gutardy). IP salgyny, 22-nji porty we firewall-y barlaň.",
    },
    "err_ssh_auth": {
        "ru": "Неверный логин или пароль SSH. Проверьте данные и попробуйте снова.",
        "en": "Wrong SSH login or password. Check the details and try again.",
        "tk": "SSH logini ýa-da paroly nädogry. Maglumatlary barlaň we täzeden synanyşyň.",
    },
    "err_ssh_connect": {
        "ru": "Не удалось подключиться к серверу: {error}",
        "en": "Couldn't connect to the server: {error}",
        "tk": "Servere birikip bolmady: {error}",
    },
    "err_sudo_denied": {
        "ru": (
            "Пользователь '{user}' не может выполнять команды через sudo на этом сервере "
            "(в том числе с указанным паролем). Выдайте пользователю права sudo или "
            "подключитесь под пользователем root."
        ),
        "en": (
            "User '{user}' can't run commands via sudo on this server (even with the given "
            "password). Grant the user sudo rights, or connect as root."
        ),
        "tk": (
            "'{user}' ulanyjysy bu serwerde sudo arkaly buýruklary ýerine ýetirip bilenok "
            "(berlen parol bilen hem). Ulanyja sudo hukugyny beriň ýa-da root hökmünde birikiň."
        ),
    },
    "err_no_details": {
        "ru": "без деталей",
        "en": "no details",
        "tk": "jikme-jik ýok",
    },
    "err_write_file": {
        "ru": "Не удалось записать файл {filename} на сервер.",
        "en": "Couldn't write the file {filename} to the server.",
        "tk": "{filename} faýlyny serwere ýazyp bolmady.",
    },
    "err_docker_start": {
        "ru": "Docker установлен на сервере, но не удалось его запустить.",
        "en": "Docker is installed on the server, but it couldn't be started.",
        "tk": "Docker serwerde gurnalan, ýöne işe girizip bolmady.",
    },
    "err_docker_install": {
        "ru": "Не удалось установить Docker автоматически. Установите его вручную и повторите попытку.",
        "en": "Couldn't install Docker automatically. Install it manually and try again.",
        "tk": "Docker awtomatiki gurup bolmady. Ony elle gurnaň we täzeden synanyşyň.",
    },
    "err_docker_after_install": {
        "ru": "Docker установлен, но не удалось его запустить.",
        "en": "Docker was installed, but it couldn't be started.",
        "tk": "Docker gurnaldy, ýöne işe girizip bolmady.",
    },
    "err_compose_install": {
        "ru": "Не удалось установить docker compose plugin.",
        "en": "Couldn't install the docker compose plugin.",
        "tk": "docker compose pluginini gurup bolmady.",
    },
    "err_marzban_up": {
        "ru": "Не удалось запустить контейнер marzban-node.",
        "en": "Couldn't start the marzban-node container.",
        "tk": "marzban-node konteýnerini işe girizip bolmady.",
    },
    "err_mkdir": {
        "ru": "Не удалось создать директорию ноды.",
        "en": "Couldn't create the node directory.",
        "tk": "Node üçin bukja döredip bolmady.",
    },
    "err_cert_gen": {
        "ru": "Не удалось сгенерировать сертификат ноды.",
        "en": "Couldn't generate the node certificate.",
        "tk": "Node sertifikatyny döredip bolmady.",
    },
    "err_pasarguard_up": {
        "ru": "Не удалось запустить контейнер pg-node.",
        "en": "Couldn't start the pg-node container.",
        "tk": "pg-node konteýnerini işe girizip bolmady.",
    },
    # --- Panel flow ---
    "title_panel_marzban": {"ru": "Marzban", "en": "Marzban", "tk": "Marzban"},
    "title_panel_pasarguard": {"ru": "PasarGuard", "en": "PasarGuard", "tk": "PasarGuard"},
    "title_panel_3xui": {"ru": "3X-UI", "en": "3X-UI", "tk": "3X-UI"},
    "panel_list_header": {
        "ru": (
            "{icon} <b>Мои панели</b>\n\n"
            "<i>Список подключённых панелей — управляйте каждой отдельно.</i>\n\n"
            "👇 Выберите панель или добавьте новую"
        ),
        "en": (
            "{icon} <b>My panels</b>\n\n"
            "<i>Your connected panels — manage each one separately.</i>\n\n"
            "👇 Pick a panel or add a new one"
        ),
        "tk": (
            "{icon} <b>Panellerim</b>\n\n"
            "<i>Birikdirilen panelleriňiz — her birini aýratyn dolandyryň.</i>\n\n"
            "👇 Paneli saýlaň ýa-da täzesini goşuň"
        ),
    },
    "panel_list_empty": {
        "ru": (
            "{icon} <b>Мои панели</b>\n\n"
            "<i>Панелей пока нет — подключите свою первую панель.</i>\n\n"
            "👇 Нажмите «Добавить панель»"
        ),
        "en": (
            "{icon} <b>My panels</b>\n\n"
            "<i>No panels yet — connect your first one.</i>\n\n"
            "👇 Tap “Add panel”"
        ),
        "tk": (
            "{icon} <b>Panellerim</b>\n\n"
            "<i>Heniz panel ýok — ilkinji paneliňizi birikdiriň.</i>\n\n"
            "👇 «Panel goş» düwmesine basyň"
        ),
    },
    "panel_add_menu": {
        "ru": "{icon} <b>Добавить панель</b>\n\n<i>Какую панель подключаем?</i>\n\n👇 Выберите платформу",
        "en": "{icon} <b>Add a panel</b>\n\n<i>Which panel are we connecting?</i>\n\n👇 Choose a platform",
        "tk": "{icon} <b>Panel goş</b>\n\n<i>Haýsy paneli birikdirýäris?</i>\n\n👇 Platformany saýlaň",
    },
    "panel_cancelled": {
        "ru": (
            "{icon} <b>Panel</b>\n\n"
            "🚫 <i>Подключение отменено — данные не сохранены.</i>\n\n"
            "👇 Можно начать заново в любой момент"
        ),
        "en": (
            "{icon} <b>Panel</b>\n\n"
            "🚫 <i>Connection cancelled — nothing was saved.</i>\n\n"
            "👇 You can start again anytime"
        ),
        "tk": (
            "{icon} <b>Panel</b>\n\n"
            "🚫 <i>Birikdirme ýatyryldy — hiç zat ýatda saklanmady.</i>\n\n"
            "👇 Islän wagtyňyz täzeden başlap bilersiňiz"
        ),
    },
    "step_panel_url": {
        "ru": (
            "{header}\n<i>Шаг 1 из 3</i>\n\n"
            "🌍 Пришлите ссылку на панель — например: <code>https://panel.example.com:8000</code>"
        ),
        "en": (
            "{header}\n<i>Step 1 of 3</i>\n\n"
            "🌍 Send the panel URL — for example: <code>https://panel.example.com:8000</code>"
        ),
        "tk": (
            "{header}\n<i>1-nji ädim / 3</i>\n\n"
            "🌍 Panel salgysyny iberiň — mysal üçin: <code>https://panel.example.com:8000</code>"
        ),
    },
    "invalid_panel_url": {
        "ru": "Похоже, это не ссылка. Попробуйте ещё раз — например: <code>https://panel.example.com:8000</code>",
        "en": "That doesn't look like a URL. Try again — for example: <code>https://panel.example.com:8000</code>",
        "tk": "Bu salga meňzänok. Täzeden synanyşyň — mysal üçin: <code>https://panel.example.com:8000</code>",
    },
    "step_panel_username": {
        "ru": "{header}\n<i>Шаг 2 из 3</i>\n\n👤 Пришлите логин администратора панели.",
        "en": "{header}\n<i>Step 2 of 3</i>\n\n👤 Send the panel admin username.",
        "tk": "{header}\n<i>2-nji ädim / 3</i>\n\n👤 Panel administratorynyň logini iberiň.",
    },
    "invalid_panel_username": {
        "ru": "Логин не может быть пустым. Отправьте его ещё раз.",
        "en": "The username can't be empty. Send it again.",
        "tk": "Login boş bolup bilmez. Ony täzeden iberiň.",
    },
    "step_panel_password": {
        "ru": (
            "{header}\n<i>Шаг 3 из 3</i>\n\n"
            "Пароль от <b>{username}</b>, пожалуйста.\n\n"
            "{icon} <i>Сообщение с паролем удалится сразу после отправки — он нужен только "
            "для подключения к панели и нигде не хранится в чате.</i>"
        ),
        "en": (
            "{header}\n<i>Step 3 of 3</i>\n\n"
            "Password for <b>{username}</b>, please.\n\n"
            "{icon} <i>The message with the password will be deleted right after you send it — "
            "it's only used to connect to the panel and never kept in the chat.</i>"
        ),
        "tk": (
            "{header}\n<i>3-nji ädim / 3</i>\n\n"
            "<b>{username}</b> üçin parol, haýyş edýäris.\n\n"
            "{icon} <i>Parol bilen habar iberilenden soň derrew öçüriler — ol diňe panele "
            "birikmek üçin gerek we çatda saklanmaýar.</i>"
        ),
    },
    "empty_panel_password": {
        "ru": "Пароль не может быть пустым. Отправьте его ещё раз.",
        "en": "The password can't be empty. Send it again.",
        "tk": "Parol boş bolup bilmez. Ony täzeden iberiň.",
    },
    "panel_connecting": {
        "ru": "🔌 Подключаюсь к панели...",
        "en": "🔌 Connecting to the panel...",
        "tk": "🔌 Panele birikilýär...",
    },
    "panel_login_error": {
        "ru": (
            "{icon} <b>Не удалось подключиться к панели</b>\n\n"
            "{reason}\n\n"
            "🔁 Проверьте ссылку, логин и пароль и попробуйте снова"
        ),
        "en": (
            "{icon} <b>Couldn't connect to the panel</b>\n\n"
            "{reason}\n\n"
            "🔁 Check the URL, username and password, then try again"
        ),
        "tk": (
            "{icon} <b>Panele birikip bolmady</b>\n\n"
            "{reason}\n\n"
            "🔁 Salgyny, logini we paroly barlaň-da, täzeden synanyşyň"
        ),
    },
    "panel_err_wrong_credentials": {
        "ru": "Неверный логин или пароль.",
        "en": "Wrong username or password.",
        "tk": "Login ýa-da parol nädogry.",
    },
    "panel_err_connect_failed": {
        "ru": "Не удалось связаться с панелью — проверьте ссылку и доступность сервера.",
        "en": "Couldn't reach the panel — check the URL and that the server is reachable.",
        "tk": "Panel bilen habarlaşyp bolmady — salgyny we serweriň elýeterligini barlaň.",
    },
    "panel_err_bad_response": {
        "ru": "Панель ответила в неожиданном формате.",
        "en": "The panel responded in an unexpected format.",
        "tk": "Panel garaşylmadyk formatda jogap berdi.",
    },
    "panel_err_http": {
        "ru": "Панель ответила с ошибкой (код {status}).",
        "en": "The panel responded with an error (code {status}).",
        "tk": "Panel ýalňyşlyk bilen jogap berdi (kod {status}).",
    },
    "panel_connected": {
        "ru": "{icon} {header} успешно подключена 🚀",
        "en": "{icon} {header} connected successfully 🚀",
        "tk": "{icon} {header} üstünlikli birikdirildi 🚀",
    },
    "panel_dashboard": {
        "ru": "{header}\n\n👇 Что делаем?",
        "en": "{header}\n\n👇 What next?",
        "tk": "{header}\n\n👇 Näme edeliň?",
    },
    "panel_stats_marzban": {
        "ru": (
            "{header}\n📊 <b>Статистика</b>\n\n"
            "🏷 Версия: <code>{version}</code>\n"
            "👥 Всего пользователей: <b>{total}</b>\n"
            "🟢 Активных: {active} · 🔴 Отключённых: {disabled}\n"
            "⌛ Истёкших: {expired} · 🚧 Лимит исчерпан: {limited} · ⏸ На паузе: {on_hold}\n"
            "📶 Онлайн сейчас: <b>{online}</b>\n\n"
            "⬇️ Скачано: {down}\n⬆️ Загружено: {up}"
        ),
        "en": (
            "{header}\n📊 <b>Statistics</b>\n\n"
            "🏷 Version: <code>{version}</code>\n"
            "👥 Total users: <b>{total}</b>\n"
            "🟢 Active: {active} · 🔴 Disabled: {disabled}\n"
            "⌛ Expired: {expired} · 🚧 Limited: {limited} · ⏸ On hold: {on_hold}\n"
            "📶 Online now: <b>{online}</b>\n\n"
            "⬇️ Downloaded: {down}\n⬆️ Uploaded: {up}"
        ),
        "tk": (
            "{header}\n📊 <b>Statistika</b>\n\n"
            "🏷 Wersiýa: <code>{version}</code>\n"
            "👥 Jemi ulanyjy: <b>{total}</b>\n"
            "🟢 Işjeň: {active} · 🔴 Öçürilen: {disabled}\n"
            "⌛ Möhleti geçen: {expired} · 🚧 Limiti dolan: {limited} · ⏸ Duruzlan: {on_hold}\n"
            "📶 Häzir onlaýn: <b>{online}</b>\n\n"
            "⬇️ Ýüklenen: {down}\n⬆️ Iberilen: {up}"
        ),
    },
    "panel_stats_3xui": {
        "ru": "{header}\n📊 <b>Статистика</b>\n\n📡 Inbound'ов: <b>{inbounds_count}</b>\n👥 Клиентов: <b>{clients_count}</b>",
        "en": "{header}\n📊 <b>Statistics</b>\n\n📡 Inbounds: <b>{inbounds_count}</b>\n👥 Clients: <b>{clients_count}</b>",
        "tk": "{header}\n📊 <b>Statistika</b>\n\n📡 Inbound sany: <b>{inbounds_count}</b>\n👥 Müşderi sany: <b>{clients_count}</b>",
    },
    "panel_users_list_header": {
        "ru": "{header}\n👥 <b>Пользователи</b>\n\nПоказаны {start}–{end} из {total} · 📄 Стр. {page}/{pages}:",
        "en": "{header}\n👥 <b>Users</b>\n\nShowing {start}–{end} of {total} · 📄 Page {page}/{pages}:",
        "tk": "{header}\n👥 <b>Ulanyjylar</b>\n\n{start}–{end} / {total} görkezilýär · 📄 Sah. {page}/{pages}:",
    },
    "panel_users_list_empty": {
        "ru": "{header}\n👥 <b>Пользователи</b>\n\nПока пользователей нет.",
        "en": "{header}\n👥 <b>Users</b>\n\nNo users yet.",
        "tk": "{header}\n👥 <b>Ulanyjylar</b>\n\nHeniz ulanyjy ýok.",
    },
    "panel_remove_confirm": {
        "ru": (
            "{header}\n\n"
            "⚠️ Убрать эту панель из бота? Сама панель продолжит работать как обычно — "
            "отвяжется только управление через бота. Чтобы вернуть его, подключите панель заново."
        ),
        "en": (
            "{header}\n\n"
            "⚠️ Remove this panel from the bot? The panel itself keeps running as usual — "
            "only bot management is unlinked. Connect it again to bring it back."
        ),
        "tk": (
            "{header}\n\n"
            "⚠️ Bu paneli botdan aýyrmakmy? Paneliň özi adatdakysy ýaly işlemegini dowam etdirer — "
            "diňe bot arkaly dolandyryş aýrylar. Yzyna almak üçin paneli täzeden birikdiriň."
        ),
    },
    "panel_removed": {
        "ru": "🗑 Панель убрана из бота.\n\n👇 Можно подключить другую в любой момент",
        "en": "🗑 Panel removed from the bot.\n\n👇 You can connect another one anytime",
        "tk": "🗑 Panel botdan aýryldy.\n\n👇 Islän wagtyňyz başga birini birikdirip bilersiňiz",
    },
    # --- Panel: user management (Marzban/PasarGuard) ---
    "status_active": {"ru": "Активен", "en": "Active", "tk": "Işjeň"},
    "status_disabled": {"ru": "Отключён", "en": "Disabled", "tk": "Öçürilen"},
    "status_expired": {"ru": "Истёк", "en": "Expired", "tk": "Möhleti geçen"},
    "status_limited": {"ru": "Лимит исчерпан", "en": "Limit reached", "tk": "Limiti gutardy"},
    "status_on_hold": {"ru": "На паузе", "en": "On hold", "tk": "Duruzlan"},
    "limit_unlimited": {"ru": "без ограничений", "en": "unlimited", "tk": "çäksiz"},
    "expire_never": {"ru": "бессрочно", "en": "never expires", "tk": "möhletsiz"},
    "limit_gb": {"ru": "{gb} ГБ", "en": "{gb} GB", "tk": "{gb} GB"},
    "expire_days": {"ru": "{days} дн.", "en": "{days} days", "tk": "{days} gün"},
    "panel_create_user_step_username": {
        "ru": (
            "{header}\n\n➕ <b>Новый пользователь</b>\n<i>Шаг 1 из 2</i>\n\n"
            "👤 Отправьте имя пользователя (латиница, цифры, «_», 3–32 символа)"
        ),
        "en": (
            "{header}\n\n➕ <b>New user</b>\n<i>Step 1 of 2</i>\n\n"
            "👤 Send the username (letters, digits, «_», 3–32 characters)"
        ),
        "tk": (
            "{header}\n\n➕ <b>Täze ulanyjy</b>\n<i>1-nji ädim / 2</i>\n\n"
            "👤 Ulanyjy adyny iberiň (latyn harplar, sanlar, «_», 3–32 belgi)"
        ),
    },
    "panel_create_user_invalid_username": {
        "ru": "Некорректное имя — используйте латинские буквы, цифры и «_», от 3 до 32 символов.",
        "en": "Invalid username — use letters, digits and «_», 3 to 32 characters.",
        "tk": "Nädogry at — latyn harplary, sanlary we «_» ulanyň, 3–32 belgi.",
    },
    "panel_create_user_step_limits": {
        "ru": (
            "{header}\n\n➕ <b>Новый пользователь: {username}</b>\n<i>Шаг 2 из 2</i>\n\n"
            "📦 Отправьте лимит трафика в ГБ и срок в днях через пробел.\n"
            "<i>Например: <code>50 30</code>. Значение 0 — без ограничений.</i>"
        ),
        "en": (
            "{header}\n\n➕ <b>New user: {username}</b>\n<i>Step 2 of 2</i>\n\n"
            "📦 Send the traffic limit in GB and validity in days, separated by a space.\n"
            "<i>For example: <code>50 30</code>. Use 0 for unlimited.</i>"
        ),
        "tk": (
            "{header}\n\n➕ <b>Täze ulanyjy: {username}</b>\n<i>2-nji ädim / 2</i>\n\n"
            "📦 Traffik limitini (GB) we möhletini (gün) boşluk bilen iberiň.\n"
            "<i>Mysal: <code>50 30</code>. 0 — çäksiz diýmek.</i>"
        ),
    },
    "panel_invalid_limits": {
        "ru": "Не понял формат. Отправьте два числа через пробел — лимит в ГБ и срок в днях, например: <code>50 30</code>",
        "en": "Couldn't parse that. Send two numbers separated by a space — GB limit and days, e.g.: <code>50 30</code>",
        "tk": "Format düşnüksiz. Boşluk bilen iki san iberiň — GB limit we gün, mysal: <code>50 30</code>",
    },
    "panel_create_user_confirm": {
        "ru": (
            "{header}\n\n📋 <b>Проверьте данные:</b>\n"
            "👤 Имя: <code>{username}</code>\n📦 Лимит: {limit}\n⏳ Срок: {expire}\n\n🚀 Создаём?"
        ),
        "en": (
            "{header}\n\n📋 <b>Please confirm:</b>\n"
            "👤 Name: <code>{username}</code>\n📦 Limit: {limit}\n⏳ Validity: {expire}\n\n🚀 Create it?"
        ),
        "tk": (
            "{header}\n\n📋 <b>Maglumatlary barlaň:</b>\n"
            "👤 At: <code>{username}</code>\n📦 Limit: {limit}\n⏳ Möhlet: {expire}\n\n🚀 Dörediliňmi?"
        ),
    },
    "panel_create_user_success": {
        "ru": "{icon} <b>Пользователь создан</b> 🎉\n\n👤 <code>{username}</code>\n\n🔗 Ссылка подписки:\n<code>{sub_link}</code>",
        "en": "{icon} <b>User created</b> 🎉\n\n👤 <code>{username}</code>\n\n🔗 Subscription link:\n<code>{sub_link}</code>",
        "tk": "{icon} <b>Ulanyjy döredildi</b> 🎉\n\n👤 <code>{username}</code>\n\n🔗 Abunalyk salgysy:\n<code>{sub_link}</code>",
    },
    "panel_action_error": {
        "ru": "{icon} <b>Не получилось выполнить действие</b>\n\n{reason}",
        "en": "{icon} <b>Couldn't complete the action</b>\n\n{reason}",
        "tk": "{icon} <b>Amal ýerine ýetirilmedi</b>\n\n{reason}",
    },
    "panel_edit_user_prompt": {
        "ru": (
            "{header}\n\n✏️ <b>Изменение: {username}</b>\n\n"
            "📦 Отправьте новый лимит трафика в ГБ и новый срок в днях через пробел.\n"
            "<i>Например: <code>100 60</code>. Значение 0 — без ограничений.</i>"
        ),
        "en": (
            "{header}\n\n✏️ <b>Editing: {username}</b>\n\n"
            "📦 Send the new traffic limit in GB and new validity in days, separated by a space.\n"
            "<i>For example: <code>100 60</code>. Use 0 for unlimited.</i>"
        ),
        "tk": (
            "{header}\n\n✏️ <b>Üýtgedilýär: {username}</b>\n\n"
            "📦 Täze traffik limitini (GB) we möhletini (gün) boşluk bilen iberiň.\n"
            "<i>Mysal: <code>100 60</code>. 0 — çäksiz diýmek.</i>"
        ),
    },
    "panel_edit_user_success": {
        "ru": "{icon} Данные пользователя <code>{username}</code> обновлены.",
        "en": "{icon} User <code>{username}</code> updated.",
        "tk": "{icon} <code>{username}</code> ulanyjysynyň maglumatlary täzelendi.",
    },
    "panel_user_detail": {
        "ru": (
            "{header}\n\n👤 <b>{username}</b>\n{status_emoji} Статус: {status_label}\n\n"
            "📊 Использовано: {used}\n📦 Лимит: {limit}\n⏳ Срок: {expire}\n\n"
            "🔗 Ссылка подписки:\n<code>{sub_link}</code>"
        ),
        "en": (
            "{header}\n\n👤 <b>{username}</b>\n{status_emoji} Status: {status_label}\n\n"
            "📊 Used: {used}\n📦 Limit: {limit}\n⏳ Validity: {expire}\n\n"
            "🔗 Subscription link:\n<code>{sub_link}</code>"
        ),
        "tk": (
            "{header}\n\n👤 <b>{username}</b>\n{status_emoji} Ýagdaýy: {status_label}\n\n"
            "📊 Ulanyldy: {used}\n📦 Limit: {limit}\n⏳ Möhlet: {expire}\n\n"
            "🔗 Abunalyk salgysy:\n<code>{sub_link}</code>"
        ),
    },
    "panel_user_not_found": {
        "ru": "Пользователь не найден — возможно, его уже удалили.",
        "en": "User not found — maybe it was already deleted.",
        "tk": "Ulanyjy tapylmady — belki eýýäm pozulandyr.",
    },
    "panel_delete_confirm_user": {
        "ru": "{header}\n\n⚠️ Точно удалить пользователя <code>{username}</code>? Это действие необратимо.",
        "en": "{header}\n\n⚠️ Delete user <code>{username}</code>? This can't be undone.",
        "tk": "{header}\n\n⚠️ <code>{username}</code> ulanyjysyny pozmakçymysyňyz? Bu amal yzyna gaýtarylmaýar.",
    },
    "panel_delete_success": {
        "ru": "{icon} Пользователь <code>{username}</code> удалён.",
        "en": "{icon} User <code>{username}</code> deleted.",
        "tk": "{icon} <code>{username}</code> ulanyjysy pozuldy.",
    },
    "panel_toggle_success": {
        "ru": "{icon} <code>{username}</code>: новый статус — {status_label}.",
        "en": "{icon} <code>{username}</code>: new status — {status_label}.",
        "tk": "{icon} <code>{username}</code>: täze ýagdaýy — {status_label}.",
    },
    "panel_reset_success": {
        "ru": "{icon} Трафик пользователя <code>{username}</code> сброшен.",
        "en": "{icon} Traffic for <code>{username}</code> has been reset.",
        "tk": "{icon} <code>{username}</code> ulanyjysynyň traffigi arassalandy.",
    },
    # --- Arsi WhoIs ---
    "btn_whois": {"ru": "🌐 Arsi WhoIs", "en": "🌐 Arsi WhoIs", "tk": "🌐 Arsi WhoIs"},
    "btn_whois_again": {"ru": "🔎 Новый запрос", "en": "🔎 New lookup", "tk": "🔎 Täze sorag"},
    "whois_prompt": {
        "ru": (
            "{icon} <b>Arsi WhoIs</b>\n\n"
            "Отправьте IP-адрес или домен — соберу всё, что доступно: геолокацию, "
            "провайдера, ASN, признаки VPN/прокси/хостинга, а для доменов — "
            "регистратора, дату регистрации и серверы имён.\n\n"
            "✏️ Например: <code>8.8.8.8</code> или <code>example.com</code>"
        ),
        "en": (
            "{icon} <b>Arsi WhoIs</b>\n\n"
            "Send an IP address or a domain — I'll gather everything available: "
            "geolocation, provider, ASN, VPN/proxy/hosting flags, and for domains "
            "— registrar, registration date and nameservers.\n\n"
            "✏️ Example: <code>8.8.8.8</code> or <code>example.com</code>"
        ),
        "tk": (
            "{icon} <b>Arsi WhoIs</b>\n\n"
            "IP salgysyny ýa-da domeni iberiň — geolokasiýa, provaýder, ASN, "
            "VPN/proksi/hosting alamatlaryny, domenler üçin bolsa — registratory, "
            "hasaba alnan senesini we at serwerlerini tapyp bererin.\n\n"
            "✏️ Mysal: <code>8.8.8.8</code> ýa-da <code>example.com</code>"
        ),
    },
    "whois_cancelled": {
        "ru": "🚫 <i>Запрос отменён.</i>",
        "en": "🚫 <i>Lookup cancelled.</i>",
        "tk": "🚫 <i>Sorag ýatyryldy.</i>",
    },
    "whois_invalid": {
        "ru": "🤔 Это не похоже на IP-адрес или домен. Попробуйте ещё раз — например: <code>1.1.1.1</code> или <code>example.com</code>",
        "en": "🤔 That doesn't look like an IP address or a domain. Try again — for example: <code>1.1.1.1</code> or <code>example.com</code>",
        "tk": "🤔 Bu IP salgy ýa-da domen ýaly görnenok. Täzeden synanyşyň — mysal üçin: <code>1.1.1.1</code> ýa-da <code>example.com</code>",
    },
    "whois_error": {
        "ru": "{icon} Не удалось получить информацию — {reason}.",
        "en": "{icon} Couldn't fetch information — {reason}.",
        "tk": "{icon} Maglumat alynmady — {reason}.",
    },
    "whois_err_connect": {
        "ru": "не удалось подключиться к источнику данных, попробуйте позже",
        "en": "couldn't reach the data source, try again later",
        "tk": "maglumat çeşmesine birikip bolmady, soňrak synanyşyň",
    },
    "whois_err_not_found": {
        "ru": "ничего не найдено по этому запросу",
        "en": "nothing found for this query",
        "tk": "bu sorag boýunça hiç zat tapylmady",
    },
    "whois_err_bad_response": {
        "ru": "источник данных вернул некорректный ответ",
        "en": "the data source returned an invalid response",
        "tk": "maglumat çeşmesi nädogry jogap gaýtardy",
    },
    "whois_yes": {"ru": "Да", "en": "Yes", "tk": "Hawa"},
    "whois_no": {"ru": "Нет", "en": "No", "tk": "Ýok"},
    "whois_ip_result": {
        "ru": (
            "<code>┌ Arsi WhoIs Bot 🌐\n"
            "│\n"
            "├ IP: {ip}\n"
            "├ Хост: {host}\n"
            "├ Страна: {country}\n"
            "├ Город: {city}\n"
            "├ Провайдер: {isp} ({asn})\n"
            "├ Часовой пояс: {timezone}\n"
            "│\n"
            "├ Прокси: {proxy}\n"
            "├ VPN: {vpn}\n"
            "├ Tor: {tor}\n"
            "├ Хостинг: {hosting}\n"
            "└ Cloudflare: {cloudflare}</code>"
        ),
        "en": (
            "<code>┌ Arsi WhoIs Bot 🌐\n"
            "│\n"
            "├ IP: {ip}\n"
            "├ Host: {host}\n"
            "├ Country: {country}\n"
            "├ City: {city}\n"
            "├ Provider: {isp} ({asn})\n"
            "├ Timezone: {timezone}\n"
            "│\n"
            "├ Proxy: {proxy}\n"
            "├ VPN: {vpn}\n"
            "├ Tor: {tor}\n"
            "├ Hosting: {hosting}\n"
            "└ Cloudflare: {cloudflare}</code>"
        ),
        "tk": (
            "<code>┌ Arsi WhoIs Bot 🌐\n"
            "│\n"
            "├ IP: {ip}\n"
            "├ Host: {host}\n"
            "├ Ýurt: {country}\n"
            "├ Şäher: {city}\n"
            "├ Provaýder: {isp} ({asn})\n"
            "├ Wagt guşagy: {timezone}\n"
            "│\n"
            "├ Proksi: {proxy}\n"
            "├ VPN: {vpn}\n"
            "├ Tor: {tor}\n"
            "├ Hosting: {hosting}\n"
            "└ Cloudflare: {cloudflare}</code>"
        ),
    },
    "whois_domain_result": {
        "ru": (
            "<code>┌ Arsi WhoIs Bot 🌐\n"
            "│\n"
            "├ Домен: {domain}\n"
            "├ Регистратор: {registrar}\n"
            "├ Зарегистрирован: {created}\n"
            "├ Истекает: {expires}\n"
            "├ Обновлён: {updated}\n"
            "├ Статус: {status}\n"
            "├ Cloudflare NS: {cloudflare}\n"
            "├ IP сервера: {resolved_ip}{ip_extra}\n"
            "│\n"
            "├ Серверы имён:\n"
            "{nameservers}</code>"
        ),
        "en": (
            "<code>┌ Arsi WhoIs Bot 🌐\n"
            "│\n"
            "├ Domain: {domain}\n"
            "├ Registrar: {registrar}\n"
            "├ Registered: {created}\n"
            "├ Expires: {expires}\n"
            "├ Updated: {updated}\n"
            "├ Status: {status}\n"
            "├ Cloudflare NS: {cloudflare}\n"
            "├ Server IP: {resolved_ip}{ip_extra}\n"
            "│\n"
            "├ Nameservers:\n"
            "{nameservers}</code>"
        ),
        "tk": (
            "<code>┌ Arsi WhoIs Bot 🌐\n"
            "│\n"
            "├ Domen: {domain}\n"
            "├ Registrator: {registrar}\n"
            "├ Hasaba alnan: {created}\n"
            "├ Möhleti: {expires}\n"
            "├ Täzelenen: {updated}\n"
            "├ Status: {status}\n"
            "├ Cloudflare NS: {cloudflare}\n"
            "├ Server IP: {resolved_ip}{ip_extra}\n"
            "│\n"
            "├ At serwerleri:\n"
            "{nameservers}</code>"
        ),
    },
}


def t(lang: str, translation_key: str, **kwargs: object) -> str:
    # `**kwargs` feeds template placeholders like {key} (e.g. an API key) or
    # {host}, so this parameter can't be named `key` itself — that would
    # collide with any translation using {key} as a placeholder name.
    lang = lang if lang in LANGUAGES else DEFAULT_LANGUAGE
    strings = _STRINGS.get(translation_key)
    if strings is None:
        return translation_key
    template = strings.get(lang) or strings.get(DEFAULT_LANGUAGE) or translation_key
    return template.format(**kwargs) if kwargs else template
