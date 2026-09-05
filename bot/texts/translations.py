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
    "btn_cloud_vps": {"ru": "☁️ Cloud VPS", "en": "☁️ Cloud VPS", "tk": "☁️ Cloud VPS"},
    "btn_cloud_account": {"ru": "📇 Cloud Account", "en": "📇 Cloud Account", "tk": "📇 Cloud Account"},
    "btn_crypt": {"ru": "🔐 Crypt/Decrypt", "en": "🔐 Crypt/Decrypt", "tk": "🔐 Crypt/Decrypt"},
    "btn_language": {"ru": "💬 Язык", "en": "💬 Language", "tk": "💬 Dil"},
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
    "btn_panel_nodes": {"ru": "🖧 Ноды", "en": "🖧 Nodes", "tk": "🖧 Node-lar"},
    "btn_panel_core": {"ru": "🧬 Xray Core", "en": "🧬 Xray Core", "tk": "🧬 Xray Core"},
    "btn_panel_core_view": {"ru": "📄 Показать конфиг", "en": "📄 Show config", "tk": "📄 Konfigi görkez"},
    "btn_panel_core_edit": {"ru": "✏️ Изменить конфиг", "en": "✏️ Edit config", "tk": "✏️ Konfigi üýtget"},
    "btn_panel_core_restart": {"ru": "🔄 Перезапустить Core", "en": "🔄 Restart Core", "tk": "🔄 Core-y täzeden başlat"},
    "btn_panel_core_apply": {"ru": "⚠️ Применить", "en": "⚠️ Apply", "tk": "⚠️ Ulan"},
    "btn_panel_core_restart_confirm": {"ru": "🔄 Да, перезапустить", "en": "🔄 Yes, restart", "tk": "🔄 Hawa, täzeden başlat"},
    "btn_panel_admins": {"ru": "👑 Админы", "en": "👑 Admins", "tk": "👑 Adminler"},
    "btn_panel_admin_add": {"ru": "➕ Добавить админа", "en": "➕ Add admin", "tk": "➕ Admin goş"},
    "btn_panel_admin_create_normal": {"ru": "✅ Создать (обычный)", "en": "✅ Create (regular)", "tk": "✅ Döret (adaty)"},
    "btn_panel_admin_create_sudo": {"ru": "👑 Создать (sudo)", "en": "👑 Create (sudo)", "tk": "👑 Döret (sudo)"},
    "btn_panel_admin_toggle_sudo_on": {"ru": "👑 Сделать sudo", "en": "👑 Make sudo", "tk": "👑 Sudo et"},
    "btn_panel_admin_toggle_sudo_off": {"ru": "👤 Убрать sudo", "en": "👤 Remove sudo", "tk": "👤 Sudo aýyr"},
    "btn_panel_admin_delete": {"ru": "🗑 Удалить админа", "en": "🗑 Delete admin", "tk": "🗑 Admin poz"},
    "btn_panel_admin_delete_confirm": {"ru": "🗑 Да, удалить", "en": "🗑 Yes, delete", "tk": "🗑 Hawa, poz"},
    "btn_panel_hosts": {"ru": "🏠 Хосты", "en": "🏠 Hosts", "tk": "🏠 Hostlar"},
    "btn_panel_host_add": {"ru": "➕ Добавить хост", "en": "➕ Add host", "tk": "➕ Host goş"},
    "btn_panel_host_edit": {"ru": "✏️ Изменить", "en": "✏️ Edit", "tk": "✏️ Üýtget"},
    "btn_panel_host_toggle_on": {"ru": "✅ Включить", "en": "✅ Enable", "tk": "✅ Işjeňleşdir"},
    "btn_panel_host_toggle_off": {"ru": "⛔ Отключить", "en": "⛔ Disable", "tk": "⛔ Öçür"},
    "btn_panel_host_delete": {"ru": "🗑 Удалить хост", "en": "🗑 Delete host", "tk": "🗑 Host poz"},
    "btn_panel_host_delete_confirm": {"ru": "🗑 Да, удалить", "en": "🗑 Yes, delete", "tk": "🗑 Hawa, poz"},
    "btn_panel_host_create_confirm": {"ru": "✅ Добавить", "en": "✅ Add", "tk": "✅ Goş"},
    "btn_panel_host_apply": {"ru": "✅ Применить", "en": "✅ Apply", "tk": "✅ Ulan"},
    "btn_panel_hosts_list": {"ru": "🏠 К списку хостов", "en": "🏠 Back to hosts", "tk": "🏠 Hostlara gaýt"},
    "btn_panel_inbounds": {"ru": "📡 Инбаунды", "en": "📡 Inbounds", "tk": "📡 Inboundlar"},
    "btn_panel_inbound_edit": {"ru": "✏️ Remark/порт", "en": "✏️ Remark/port", "tk": "✏️ Remark/port"},
    "btn_panel_inbound_toggle_on": {"ru": "✅ Включить", "en": "✅ Enable", "tk": "✅ Işjeňleşdir"},
    "btn_panel_inbound_toggle_off": {"ru": "⛔ Отключить", "en": "⛔ Disable", "tk": "⛔ Öçür"},
    "btn_panel_inbound_delete": {"ru": "🗑 Удалить инбаунд", "en": "🗑 Delete inbound", "tk": "🗑 Inbound poz"},
    "btn_panel_inbound_delete_confirm": {"ru": "🗑 Да, удалить", "en": "🗑 Yes, delete", "tk": "🗑 Hawa, poz"},
    "btn_panel_inbound_apply": {"ru": "✅ Применить", "en": "✅ Apply", "tk": "✅ Ulan"},
    "btn_panel_inbounds_list": {"ru": "📡 К инбаундам", "en": "📡 Back to inbounds", "tk": "📡 Inboundlara gaýt"},
    "btn_panel_clients": {"ru": "👥 Клиенты", "en": "👥 Clients", "tk": "👥 Müşderiler"},
    "btn_panel_client_add": {"ru": "➕ Добавить клиента", "en": "➕ Add client", "tk": "➕ Müşderi goş"},
    "btn_panel_client_edit": {"ru": "✏️ Лимит/срок", "en": "✏️ Limit/expiry", "tk": "✏️ Limit/möhlet"},
    "btn_panel_client_toggle_on": {"ru": "✅ Включить", "en": "✅ Enable", "tk": "✅ Işjeňleşdir"},
    "btn_panel_client_toggle_off": {"ru": "⛔ Отключить", "en": "⛔ Disable", "tk": "⛔ Öçür"},
    "btn_panel_client_delete": {"ru": "🗑 Удалить клиента", "en": "🗑 Delete client", "tk": "🗑 Müşderi poz"},
    "btn_panel_client_delete_confirm": {"ru": "🗑 Да, удалить", "en": "🗑 Yes, delete", "tk": "🗑 Hawa, poz"},
    "btn_panel_client_create_confirm": {"ru": "✅ Добавить", "en": "✅ Add", "tk": "✅ Goş"},
    "btn_panel_client_apply": {"ru": "✅ Применить", "en": "✅ Apply", "tk": "✅ Ulan"},
    "btn_panel_clients_list": {"ru": "👥 К клиентам", "en": "👥 Back to clients", "tk": "👥 Müşderilere gaýt"},
    "btn_panel_node_add": {"ru": "➕ Добавить ноду", "en": "➕ Add node", "tk": "➕ Node goş"},
    "btn_panel_node_reconnect": {"ru": "🔄 Переподключить", "en": "🔄 Reconnect", "tk": "🔄 Gaýtadan birik"},
    "btn_panel_node_delete": {"ru": "🗑 Удалить ноду", "en": "🗑 Delete node", "tk": "🗑 Node poz"},
    "btn_panel_node_delete_confirm": {"ru": "🗑 Да, удалить", "en": "🗑 Yes, delete", "tk": "🗑 Hawa, poz"},
    "btn_panel_node_create_confirm": {"ru": "✅ Добавить", "en": "✅ Add", "tk": "✅ Goş"},
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
            "{icon} <b>Node</b> 🖥\n\n"
            "<i>Разверните VPN-ноду на своём сервере за пару минут — бот сделает всё сам.</i>\n\n"
            "👇 Выберите платформу"
        ),
        "en": (
            "{icon} <b>Node</b> 🖥\n\n"
            "<i>Deploy a VPN node on your server in a couple of minutes — the bot handles the rest.</i>\n\n"
            "👇 Choose a platform"
        ),
        "tk": (
            "{icon} <b>Node</b> 🖥\n\n"
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
    # --- Ноды (Marzban/PasarGuard) ---
    "node_status_connected": {"ru": "Подключена", "en": "Connected", "tk": "Birikdirilen"},
    "node_status_connecting": {"ru": "Подключается", "en": "Connecting", "tk": "Birikdirilýär"},
    "node_status_error": {"ru": "Ошибка", "en": "Error", "tk": "Ýalňyşlyk"},
    "node_status_disabled": {"ru": "Отключена", "en": "Disabled", "tk": "Öçürilen"},
    "panel_nodes_list_header": {
        "ru": "{header}\n🖧 <b>Ноды</b>\n\nВсего: {count}",
        "en": "{header}\n🖧 <b>Nodes</b>\n\nTotal: {count}",
        "tk": "{header}\n🖧 <b>Node-lar</b>\n\nJemi: {count}",
    },
    "panel_nodes_list_empty": {
        "ru": "{header}\n🖧 <b>Ноды</b>\n\nПока ни одной ноды не добавлено.",
        "en": "{header}\n🖧 <b>Nodes</b>\n\nNo nodes added yet.",
        "tk": "{header}\n🖧 <b>Node-lar</b>\n\nHeniz node goşulmady.",
    },
    "panel_node_detail": {
        "ru": (
            "{header}\n\n🖧 <b>{name}</b>\n{status_emoji} Статус: {status_label}\n\n"
            "🌍 Адрес: <code>{address}</code>\n🔌 Порт: <code>{port}</code>\n"
            "🔌 API-порт: <code>{api_port}</code>\n📦 Xray: {xray_version}\n\n"
            "💬 Сообщение: {message}"
        ),
        "en": (
            "{header}\n\n🖧 <b>{name}</b>\n{status_emoji} Status: {status_label}\n\n"
            "🌍 Address: <code>{address}</code>\n🔌 Port: <code>{port}</code>\n"
            "🔌 API port: <code>{api_port}</code>\n📦 Xray: {xray_version}\n\n"
            "💬 Message: {message}"
        ),
        "tk": (
            "{header}\n\n🖧 <b>{name}</b>\n{status_emoji} Ýagdaýy: {status_label}\n\n"
            "🌍 Salgysy: <code>{address}</code>\n🔌 Port: <code>{port}</code>\n"
            "🔌 API-port: <code>{api_port}</code>\n📦 Xray: {xray_version}\n\n"
            "💬 Habar: {message}"
        ),
    },
    "panel_create_node_step_name": {
        "ru": "{header}\n\n🖧 Введите название новой ноды (произвольное, для себя):",
        "en": "{header}\n\n🖧 Enter a name for the new node (any label, for your own reference):",
        "tk": "{header}\n\n🖧 Täze node üçin at ýazyň (islendik, öz üçiňiz):",
    },
    "panel_create_node_invalid_name": {
        "ru": "Название не может быть пустым. Попробуйте ещё раз:",
        "en": "The name can't be empty. Try again:",
        "tk": "At boş bolup bilmez. Täzeden synanyşyň:",
    },
    "panel_create_node_step_address": {
        "ru": "{header}\n\n🌍 Название: <b>{name}</b>\n\nТеперь пришлите IP-адрес или домен ноды:",
        "en": "{header}\n\n🌍 Name: <b>{name}</b>\n\nNow send the node's IP address or domain:",
        "tk": "{header}\n\n🌍 Ady: <b>{name}</b>\n\nIndi node-yň IP salgysyny ýa-da domenini iberiň:",
    },
    "panel_create_node_invalid_address": {
        "ru": "Похоже, это не IP-адрес и не домен. Попробуйте ещё раз:",
        "en": "That doesn't look like an IP address or domain. Try again:",
        "tk": "Bu IP salgy ýa-da domen ýaly görnenok. Täzeden synanyşyň:",
    },
    "panel_create_node_step_port": {
        "ru": (
            "{header}\n\n🔌 Пришлите порт ноды (обычно 62050) и, через двоеточие, "
            "API-порт (обычно 62051) — например: <code>62050:62051</code>. "
            "Можно прислать только один порт — тогда API-портом будет порт+1."
        ),
        "en": (
            "{header}\n\n🔌 Send the node's port (usually 62050) and, separated by a colon, "
            "its API port (usually 62051) — for example: <code>62050:62051</code>. "
            "A single port is fine too — the API port will then be port+1."
        ),
        "tk": (
            "{header}\n\n🔌 Node-yň portyny (adatça 62050) we, iki nokat bilen bölüp, "
            "API-portyny (adatça 62051) iberiň — mysal üçin: <code>62050:62051</code>. "
            "Diňe bir port hem bolýar — API-port onda port+1 bolar."
        ),
    },
    "panel_create_node_invalid_port": {
        "ru": "Похоже, это не порт. Пришлите число или два числа через двоеточие, например: <code>62050:62051</code>",
        "en": "That doesn't look like a port. Send a number, or two separated by a colon, e.g.: <code>62050:62051</code>",
        "tk": "Bu port ýaly görnenok. San ýa-da iki nokat bilen iki san iberiň, mysal: <code>62050:62051</code>",
    },
    "panel_create_node_confirm": {
        "ru": (
            "{header}\n\n🖧 Добавить ноду?\n\n🏷 Название: <b>{name}</b>\n🌍 Адрес: <code>{address}</code>\n"
            "🔌 Порт: <code>{port}</code>\n🔌 API-порт: <code>{api_port}</code>"
        ),
        "en": (
            "{header}\n\n🖧 Add this node?\n\n🏷 Name: <b>{name}</b>\n🌍 Address: <code>{address}</code>\n"
            "🔌 Port: <code>{port}</code>\n🔌 API port: <code>{api_port}</code>"
        ),
        "tk": (
            "{header}\n\n🖧 Bu node goşulsynmy?\n\n🏷 Ady: <b>{name}</b>\n🌍 Salgysy: <code>{address}</code>\n"
            "🔌 Port: <code>{port}</code>\n🔌 API-port: <code>{api_port}</code>"
        ),
    },
    "panel_create_node_success": {
        "ru": "{icon} Нода <b>{name}</b> добавлена в панель.",
        "en": "{icon} Node <b>{name}</b> has been added to the panel.",
        "tk": "{icon} <b>{name}</b> node-y panele goşuldy.",
    },
    "panel_node_delete_confirm": {
        "ru": "{header}\n\n⚠️ Точно удалить ноду <b>{name}</b> из панели? Это действие необратимо.",
        "en": "{header}\n\n⚠️ Delete node <b>{name}</b> from the panel? This can't be undone.",
        "tk": "{header}\n\n⚠️ <b>{name}</b> node-yny panelden pozmakçymysyňyz? Bu amal yzyna gaýtarylmaýar.",
    },
    "panel_node_delete_success": {
        "ru": "{icon} Нода <b>{name}</b> удалена.",
        "en": "{icon} Node <b>{name}</b> deleted.",
        "tk": "{icon} <b>{name}</b> node-y pozuldy.",
    },
    "panel_node_reconnect_success": {
        "ru": "{icon} Нода <b>{name}</b> переподключается...",
        "en": "{icon} Node <b>{name}</b> is reconnecting...",
        "tk": "{icon} <b>{name}</b> node-y gaýtadan birikdirilýär...",
    },
    # --- Xray core config (Marzban/PasarGuard) ---
    "panel_core_menu": {
        "ru": (
            "{header}\n\n🧬 <b>Xray Core</b>\n\n📦 Версия: <code>{version}</code>\n{status_emoji} Статус: {status_label}\n\n"
            "⚠️ <i>Изменение конфига напрямую влияет на работу VPN — будьте осторожны.</i>"
        ),
        "en": (
            "{header}\n\n🧬 <b>Xray Core</b>\n\n📦 Version: <code>{version}</code>\n{status_emoji} Status: {status_label}\n\n"
            "⚠️ <i>Editing the config directly affects the running VPN — be careful.</i>"
        ),
        "tk": (
            "{header}\n\n🧬 <b>Xray Core</b>\n\n📦 Wersiýa: <code>{version}</code>\n{status_emoji} Ýagdaýy: {status_label}\n\n"
            "⚠️ <i>Konfigi üýtgetmek gönüden-göni işleýän VPN-e täsir edýär — seresap boluň.</i>"
        ),
    },
    "core_status_started": {"ru": "Запущен", "en": "Running", "tk": "Işleýär"},
    "core_status_stopped": {"ru": "Остановлен", "en": "Stopped", "tk": "Duran"},
    "panel_core_config_caption": {
        "ru": "🧬 Текущий Xray-конфиг панели {header}",
        "en": "🧬 Current Xray config of panel {header}",
        "tk": "🧬 {header} panelynyň häzirki Xray konfigi",
    },
    "panel_core_edit_prompt": {
        "ru": (
            "{header}\n\n✏️ Пришлите новый конфиг — текстом (если короткий) или файлом <code>.json</code>.\n\n"
            "⚠️ Конфиг будет применён к работающему серверу — если он некорректен, VPN может перестать работать."
        ),
        "en": (
            "{header}\n\n✏️ Send the new config — as text (if short) or as a <code>.json</code> file.\n\n"
            "⚠️ The config will be applied to the running server — if it's invalid, the VPN may stop working."
        ),
        "tk": (
            "{header}\n\n✏️ Täze konfigi iberiň — tekst hökmünde (gysga bolsa) ýa-da <code>.json</code> faýl hökmünde.\n\n"
            "⚠️ Konfig işleýän serwere ulanylar — nädogry bolsa, VPN işlemegini bes edip biler."
        ),
    },
    "panel_core_err_not_json": {
        "ru": "Это не похоже на корректный JSON. Проверьте синтаксис и пришлите ещё раз.",
        "en": "That doesn't look like valid JSON. Check the syntax and send it again.",
        "tk": "Bu dogry JSON ýaly görnenok. Sintaksisi barlaň we täzeden iberiň.",
    },
    "panel_core_err_not_object": {
        "ru": "Конфиг должен быть JSON-объектом (в фигурных скобках), а не списком или значением.",
        "en": "The config must be a JSON object (curly braces), not a list or a plain value.",
        "tk": "Konfig JSON obýekti bolmaly (üýtgeşik alamatlar bilen), sanaw ýa-da baha däl.",
    },
    "panel_core_err_missing_inbounds": {
        "ru": "В конфиге нет поля <code>inbounds</code> — это не похоже на валидный Xray-конфиг.",
        "en": "The config has no <code>inbounds</code> field — this doesn't look like a valid Xray config.",
        "tk": "Konfigde <code>inbounds</code> meýdany ýok — bu dogry Xray konfigi ýaly görnenok.",
    },
    "panel_core_edit_confirm": {
        "ru": (
            "{header}\n\n⚠️ <b>Применить новый конфиг?</b>\n\n"
            "📥 Inbound'ов: <b>{inbounds}</b>\n📤 Outbound'ов: <b>{outbounds}</b>\n\n"
            "Core перезапустится с новыми настройками. Если конфиг ошибочен, VPN может перестать работать."
        ),
        "en": (
            "{header}\n\n⚠️ <b>Apply the new config?</b>\n\n"
            "📥 Inbounds: <b>{inbounds}</b>\n📤 Outbounds: <b>{outbounds}</b>\n\n"
            "The core will restart with the new settings. If the config is wrong, the VPN may stop working."
        ),
        "tk": (
            "{header}\n\n⚠️ <b>Täze konfig ulanylsynmy?</b>\n\n"
            "📥 Inbound: <b>{inbounds}</b>\n📤 Outbound: <b>{outbounds}</b>\n\n"
            "Core täze sazlamalar bilen täzeden başlar. Konfig ýalňyş bolsa, VPN işlemegini bes edip biler."
        ),
    },
    "panel_core_edit_success": {
        "ru": "{icon} Новый конфиг применён, Core перезапущен.",
        "en": "{icon} New config applied, Core restarted.",
        "tk": "{icon} Täze konfig ulanyldy, Core täzeden başlady.",
    },
    "panel_core_restart_confirm": {
        "ru": "{header}\n\n🔄 Перезапустить Xray Core? Активные соединения будут ненадолго прерваны.",
        "en": "{header}\n\n🔄 Restart Xray Core? Active connections will be briefly interrupted.",
        "tk": "{header}\n\n🔄 Xray Core täzeden başladylsynmy? Işjeň birikmeler gysga wagtlyk kesiler.",
    },
    "panel_core_restart_success": {
        "ru": "{icon} Xray Core перезапущен.",
        "en": "{icon} Xray Core restarted.",
        "tk": "{icon} Xray Core täzeden başlady.",
    },
    # --- Суб-админы (Marzban/PasarGuard) ---
    "panel_admins_list_header": {
        "ru": "{header}\n👑 <b>Админы</b>\n\nВсего: {count}",
        "en": "{header}\n👑 <b>Admins</b>\n\nTotal: {count}",
        "tk": "{header}\n👑 <b>Adminler</b>\n\nJemi: {count}",
    },
    "panel_admins_list_empty": {
        "ru": "{header}\n👑 <b>Админы</b>\n\nПока ни одного доп. админа не создано.",
        "en": "{header}\n👑 <b>Admins</b>\n\nNo extra admins created yet.",
        "tk": "{header}\n👑 <b>Adminler</b>\n\nHeniz goşmaça admin döredilmedi.",
    },
    "panel_admin_detail": {
        "ru": "{header}\n\n👤 <b>{username}</b>\n{sudo_emoji} {sudo_label}\n🆔 Telegram ID: {telegram_id}",
        "en": "{header}\n\n👤 <b>{username}</b>\n{sudo_emoji} {sudo_label}\n🆔 Telegram ID: {telegram_id}",
        "tk": "{header}\n\n👤 <b>{username}</b>\n{sudo_emoji} {sudo_label}\n🆔 Telegram ID: {telegram_id}",
    },
    "admin_sudo_yes": {"ru": "Sudo-админ", "en": "Sudo admin", "tk": "Sudo admin"},
    "admin_sudo_no": {"ru": "Обычный админ", "en": "Regular admin", "tk": "Adaty admin"},
    "panel_create_admin_step_username": {
        "ru": "{header}\n\n👑 Введите логин нового админа:",
        "en": "{header}\n\n👑 Enter the new admin's username:",
        "tk": "{header}\n\n👑 Täze adminiň logini ýazyň:",
    },
    "panel_create_admin_invalid_username": {
        "ru": "Логин должен быть на латинице, 3–32 символа (буквы, цифры, _). Попробуйте ещё раз:",
        "en": "The username must be Latin letters, 3-32 chars (letters, digits, _). Try again:",
        "tk": "Login latyn harplary bilen, 3-32 belgi (harplar, sanlar, _) bolmaly. Täzeden synanyşyň:",
    },
    "panel_create_admin_step_password": {
        "ru": "{header}\n\n🔑 Логин: <b>{username}</b>\n\nТеперь пришлите пароль для нового админа:",
        "en": "{header}\n\n🔑 Username: <b>{username}</b>\n\nNow send the password for the new admin:",
        "tk": "{header}\n\n🔑 Login: <b>{username}</b>\n\nIndi täze admin üçin parol iberiň:",
    },
    "panel_create_admin_empty_password": {
        "ru": "Пароль не может быть пустым. Попробуйте ещё раз:",
        "en": "The password can't be empty. Try again:",
        "tk": "Parol boş bolup bilmez. Täzeden synanyşyň:",
    },
    "panel_create_admin_confirm": {
        "ru": "{header}\n\n👑 Создать админа <b>{username}</b>?\n\nВыберите уровень доступа:",
        "en": "{header}\n\n👑 Create admin <b>{username}</b>?\n\nChoose the access level:",
        "tk": "{header}\n\n👑 <b>{username}</b> admini döredilsinmi?\n\nElýeterlilik derejesini saýlaň:",
    },
    "panel_create_admin_success": {
        "ru": "{icon} Админ <b>{username}</b> создан ({sudo_label}).",
        "en": "{icon} Admin <b>{username}</b> created ({sudo_label}).",
        "tk": "{icon} <b>{username}</b> admini döredildi ({sudo_label}).",
    },
    "panel_admin_toggle_sudo_success": {
        "ru": "{icon} Админ <b>{username}</b>: теперь {sudo_label}.",
        "en": "{icon} Admin <b>{username}</b> is now {sudo_label}.",
        "tk": "{icon} <b>{username}</b> admini indi {sudo_label}.",
    },
    "panel_admin_delete_confirm": {
        "ru": "{header}\n\n⚠️ Точно удалить админа <b>{username}</b>? Это действие необратимо.",
        "en": "{header}\n\n⚠️ Delete admin <b>{username}</b>? This can't be undone.",
        "tk": "{header}\n\n⚠️ <b>{username}</b> adminini pozmakçymysyňyz? Bu amal yzyna gaýtarylmaýar.",
    },
    "panel_admin_delete_success": {
        "ru": "{icon} Админ <b>{username}</b> удалён.",
        "en": "{icon} Admin <b>{username}</b> deleted.",
        "tk": "{icon} <b>{username}</b> admini pozuldy.",
    },
    # --- Хосты подписки (Marzban/PasarGuard) ---
    "panel_hosts_tags_header": {
        "ru": "{header}\n🏠 <b>Хосты подписки</b>\n\nВыберите inbound:",
        "en": "{header}\n🏠 <b>Subscription hosts</b>\n\nChoose an inbound:",
        "tk": "{header}\n🏠 <b>Abunalyk hostlary</b>\n\nInbound saýlaň:",
    },
    "panel_hosts_tags_empty": {
        "ru": "{header}\n🏠 <b>Хосты подписки</b>\n\nНа панели нет ни одного inbound'а.",
        "en": "{header}\n🏠 <b>Subscription hosts</b>\n\nThe panel has no inbounds.",
        "tk": "{header}\n🏠 <b>Abunalyk hostlary</b>\n\nPanelde inbound ýok.",
    },
    "panel_hosts_list_header": {
        "ru": "{header}\n🏠 <b>{tag}</b>\n\nХостов: {count}",
        "en": "{header}\n🏠 <b>{tag}</b>\n\nHosts: {count}",
        "tk": "{header}\n🏠 <b>{tag}</b>\n\nHost sany: {count}",
    },
    "panel_hosts_list_empty": {
        "ru": "{header}\n🏠 <b>{tag}</b>\n\nХостов пока нет.",
        "en": "{header}\n🏠 <b>{tag}</b>\n\nNo hosts yet.",
        "tk": "{header}\n🏠 <b>{tag}</b>\n\nHeniz host ýok.",
    },
    "panel_host_detail": {
        "ru": (
            "{header}\n🏠 <b>{tag}</b>\n\n{status_emoji} {status_label}\n\n"
            "📝 Remark: <b>{remark}</b>\n🌍 Адрес: <code>{address}</code>\n🔌 Порт: <code>{port}</code>\n"
            "🔒 SNI: <code>{sni}</code>\n🏷 Host: <code>{host}</code>\n📁 Path: <code>{path}</code>\n"
            "🛡 Security: <code>{security}</code>"
        ),
        "en": (
            "{header}\n🏠 <b>{tag}</b>\n\n{status_emoji} {status_label}\n\n"
            "📝 Remark: <b>{remark}</b>\n🌍 Address: <code>{address}</code>\n🔌 Port: <code>{port}</code>\n"
            "🔒 SNI: <code>{sni}</code>\n🏷 Host: <code>{host}</code>\n📁 Path: <code>{path}</code>\n"
            "🛡 Security: <code>{security}</code>"
        ),
        "tk": (
            "{header}\n🏠 <b>{tag}</b>\n\n{status_emoji} {status_label}\n\n"
            "📝 Remark: <b>{remark}</b>\n🌍 Salgysy: <code>{address}</code>\n🔌 Port: <code>{port}</code>\n"
            "🔒 SNI: <code>{sni}</code>\n🏷 Host: <code>{host}</code>\n📁 Path: <code>{path}</code>\n"
            "🛡 Security: <code>{security}</code>"
        ),
    },
    "host_status_enabled": {"ru": "Включён", "en": "Enabled", "tk": "Işjeň"},
    "host_status_disabled": {"ru": "Отключён", "en": "Disabled", "tk": "Öçürilen"},
    "panel_host_edit_prompt": {
        "ru": (
            "{header}\n\n✏️ Пришлите одной строкой через «|»:\n"
            "<code>remark|адрес|порт|sni|host|path</code>\n\n"
            "Пустой сегмент — не менять это поле, «-» — очистить (для порта/sni/host/path).\n\n"
            "Например: <code>|new.example.com||-||</code> изменит только адрес и очистит SNI."
        ),
        "en": (
            "{header}\n\n✏️ Send one line separated by \"|\":\n"
            "<code>remark|address|port|sni|host|path</code>\n\n"
            "An empty segment leaves that field unchanged, \"-\" clears it (for port/sni/host/path).\n\n"
            "Example: <code>|new.example.com||-||</code> changes only the address and clears SNI."
        ),
        "tk": (
            "{header}\n\n✏️ «|» bilen bir setirde iberiň:\n"
            "<code>remark|salgy|port|sni|host|path</code>\n\n"
            "Boş segment — üýtgetmez, «-» — arassalar (port/sni/host/path üçin).\n\n"
            "Mysal: <code>|new.example.com||-||</code> diňe salgyny üýtgeder we SNI-ni arassalar."
        ),
    },
    "panel_host_err_wrong_field_count": {
        "ru": "Нужно ровно 6 сегментов через «|» (можно пустых). Пример: <code>|||||</code>",
        "en": "Exactly 6 segments separated by \"|\" are required (empty ones are fine). Example: <code>|||||</code>",
        "tk": "«|» bilen takyk 6 segment gerek (boşlary bolýar). Mysal: <code>|||||</code>",
    },
    "panel_host_err_bad_port": {
        "ru": "Порт должен быть числом от 1 до 65535, либо «-» чтобы очистить.",
        "en": "The port must be a number from 1 to 65535, or \"-\" to clear it.",
        "tk": "Port 1-den 65535-e çenli san bolmaly, ýa-da arassalamak üçin «-».",
    },
    "panel_host_edit_confirm": {
        "ru": (
            "{header}\n\n✏️ Применить изменения?\n\n"
            "📝 Remark: <b>{remark}</b>\n🌍 Адрес: <code>{address}</code>\n🔌 Порт: <code>{port}</code>\n"
            "🔒 SNI: <code>{sni}</code>\n🏷 Host: <code>{host}</code>\n📁 Path: <code>{path}</code>"
        ),
        "en": (
            "{header}\n\n✏️ Apply these changes?\n\n"
            "📝 Remark: <b>{remark}</b>\n🌍 Address: <code>{address}</code>\n🔌 Port: <code>{port}</code>\n"
            "🔒 SNI: <code>{sni}</code>\n🏷 Host: <code>{host}</code>\n📁 Path: <code>{path}</code>"
        ),
        "tk": (
            "{header}\n\n✏️ Üýtgeşmeler ulanylsynmy?\n\n"
            "📝 Remark: <b>{remark}</b>\n🌍 Salgysy: <code>{address}</code>\n🔌 Port: <code>{port}</code>\n"
            "🔒 SNI: <code>{sni}</code>\n🏷 Host: <code>{host}</code>\n📁 Path: <code>{path}</code>"
        ),
    },
    "panel_host_edit_success": {
        "ru": "{icon} Хост обновлён.",
        "en": "{icon} Host updated.",
        "tk": "{icon} Host täzelendi.",
    },
    "panel_host_toggle_success": {
        "ru": "{icon} Хост теперь {status_label}.",
        "en": "{icon} The host is now {status_label}.",
        "tk": "{icon} Host indi {status_label}.",
    },
    "panel_host_delete_confirm": {
        "ru": "{header}\n\n⚠️ Точно удалить хост <b>{remark}</b>? Это действие необратимо.",
        "en": "{header}\n\n⚠️ Delete host <b>{remark}</b>? This can't be undone.",
        "tk": "{header}\n\n⚠️ <b>{remark}</b> hosty pozmakçymysyňyz? Bu amal yzyna gaýtarylmaýar.",
    },
    "panel_host_delete_success": {
        "ru": "{icon} Хост удалён.",
        "en": "{icon} Host deleted.",
        "tk": "{icon} Host pozuldy.",
    },
    "panel_create_host_step_remark": {
        "ru": "{header}\n🏠 <b>{tag}</b>\n\n📝 Введите remark (название) нового хоста:",
        "en": "{header}\n🏠 <b>{tag}</b>\n\n📝 Enter the new host's remark (name):",
        "tk": "{header}\n🏠 <b>{tag}</b>\n\n📝 Täze hostuň remark (ady) ýazyň:",
    },
    "panel_create_host_invalid_remark": {
        "ru": "Remark не может быть пустым. Попробуйте ещё раз:",
        "en": "The remark can't be empty. Try again:",
        "tk": "Remark boş bolup bilmez. Täzeden synanyşyň:",
    },
    "panel_create_host_step_address": {
        "ru": "{header}\n\n🌍 Теперь пришлите адрес хоста (домен или IP):",
        "en": "{header}\n\n🌍 Now send the host's address (domain or IP):",
        "tk": "{header}\n\n🌍 Indi hostuň salgysyny iberiň (domen ýa-da IP):",
    },
    "panel_create_host_invalid_address": {
        "ru": "Похоже, это не адрес. Попробуйте ещё раз:",
        "en": "That doesn't look like an address. Try again:",
        "tk": "Bu salgy ýaly görnenok. Täzeden synanyşyň:",
    },
    "panel_create_host_step_port": {
        "ru": "{header}\n\n🔌 Пришлите порт, либо «-» чтобы оставить пустым (порт inbound'а по умолчанию):",
        "en": "{header}\n\n🔌 Send the port, or \"-\" to leave it empty (the inbound's default port):",
        "tk": "{header}\n\n🔌 Porty iberiň, ýa-da boş goýmak üçin «-» (inboundyň öz porty):",
    },
    "panel_create_host_confirm": {
        "ru": (
            "{header}\n🏠 <b>{tag}</b>\n\n➕ Добавить хост?\n\n"
            "📝 Remark: <b>{remark}</b>\n🌍 Адрес: <code>{address}</code>\n🔌 Порт: <code>{port}</code>"
        ),
        "en": (
            "{header}\n🏠 <b>{tag}</b>\n\n➕ Add this host?\n\n"
            "📝 Remark: <b>{remark}</b>\n🌍 Address: <code>{address}</code>\n🔌 Port: <code>{port}</code>"
        ),
        "tk": (
            "{header}\n🏠 <b>{tag}</b>\n\n➕ Bu host goşulsynmy?\n\n"
            "📝 Remark: <b>{remark}</b>\n🌍 Salgysy: <code>{address}</code>\n🔌 Port: <code>{port}</code>"
        ),
    },
    "panel_create_host_success": {
        "ru": "{icon} Хост <b>{remark}</b> добавлен.",
        "en": "{icon} Host <b>{remark}</b> added.",
        "tk": "{icon} <b>{remark}</b> hosty goşuldy.",
    },
    # --- Инбаунды 3X-UI ---
    "panel_inbounds_list_header": {
        "ru": "{header}\n📡 <b>Инбаунды</b>\n\nВсего: {count}",
        "en": "{header}\n📡 <b>Inbounds</b>\n\nTotal: {count}",
        "tk": "{header}\n📡 <b>Inboundlar</b>\n\nJemi: {count}",
    },
    "panel_inbounds_list_empty": {
        "ru": "{header}\n📡 <b>Инбаунды</b>\n\nНа панели нет ни одного инбаунда.",
        "en": "{header}\n📡 <b>Inbounds</b>\n\nThe panel has no inbounds.",
        "tk": "{header}\n📡 <b>Inboundlar</b>\n\nPanelde inbound ýok.",
    },
    "panel_inbound_detail": {
        "ru": (
            "{header}\n\n📡 <b>{remark}</b>\n{status_emoji} {status_label}\n\n"
            "🔌 Протокол: <code>{protocol}</code>\n🔢 Порт: <code>{port}</code>\n👥 Клиентов: <b>{clients}</b>"
        ),
        "en": (
            "{header}\n\n📡 <b>{remark}</b>\n{status_emoji} {status_label}\n\n"
            "🔌 Protocol: <code>{protocol}</code>\n🔢 Port: <code>{port}</code>\n👥 Clients: <b>{clients}</b>"
        ),
        "tk": (
            "{header}\n\n📡 <b>{remark}</b>\n{status_emoji} {status_label}\n\n"
            "🔌 Protokol: <code>{protocol}</code>\n🔢 Port: <code>{port}</code>\n👥 Müşderi: <b>{clients}</b>"
        ),
    },
    "inbound_status_enabled": {"ru": "Включён", "en": "Enabled", "tk": "Işjeň"},
    "inbound_status_disabled": {"ru": "Отключён", "en": "Disabled", "tk": "Öçürilen"},
    "panel_inbound_edit_prompt": {
        "ru": "{header}\n\n✏️ Пришлите новый remark и порт через «|», например: <code>Мой сервер|8443</code>",
        "en": "{header}\n\n✏️ Send the new remark and port separated by \"|\", e.g.: <code>My server|8443</code>",
        "tk": "{header}\n\n✏️ Täze remark we porty «|» bilen iberiň, mysal: <code>Serweri m|8443</code>",
    },
    "panel_inbound_err_wrong_format": {
        "ru": "Нужно 2 сегмента через «|»: remark|порт. Пример: <code>Мой сервер|8443</code>",
        "en": "Exactly 2 segments separated by \"|\" are needed: remark|port. Example: <code>My server|8443</code>",
        "tk": "«|» bilen 2 segment gerek: remark|port. Mysal: <code>Serweri m|8443</code>",
    },
    "panel_inbound_err_bad_port": {
        "ru": "Порт должен быть числом от 1 до 65535.",
        "en": "The port must be a number from 1 to 65535.",
        "tk": "Port 1-den 65535-e çenli san bolmaly.",
    },
    "panel_inbound_edit_confirm": {
        "ru": "{header}\n\n✏️ Применить: remark — <b>{remark}</b>, порт — <code>{port}</code>?",
        "en": "{header}\n\n✏️ Apply: remark — <b>{remark}</b>, port — <code>{port}</code>?",
        "tk": "{header}\n\n✏️ Ulanylsynmy: remark — <b>{remark}</b>, port — <code>{port}</code>?",
    },
    "panel_inbound_edit_success": {
        "ru": "{icon} Инбаунд обновлён.",
        "en": "{icon} Inbound updated.",
        "tk": "{icon} Inbound täzelendi.",
    },
    "panel_inbound_toggle_success": {
        "ru": "{icon} Инбаунд теперь {status_label}.",
        "en": "{icon} The inbound is now {status_label}.",
        "tk": "{icon} Inbound indi {status_label}.",
    },
    "panel_inbound_delete_confirm": {
        "ru": "{header}\n\n⚠️ Точно удалить инбаунд <b>{remark}</b>? Все его клиенты перестанут работать.",
        "en": "{header}\n\n⚠️ Delete inbound <b>{remark}</b>? All its clients will stop working.",
        "tk": "{header}\n\n⚠️ <b>{remark}</b> inboundy pozmakçymysyňyz? Onuň ähli müşderileri işlemegini bes eder.",
    },
    "panel_inbound_delete_success": {
        "ru": "{icon} Инбаунд удалён.",
        "en": "{icon} Inbound deleted.",
        "tk": "{icon} Inbound pozuldy.",
    },
    # --- Клиенты инбаунда (3X-UI) ---
    "panel_clients_list_header": {
        "ru": "{header}\n📡 <b>{remark}</b>\n👥 <b>Клиенты</b>\n\nВсего: {count}",
        "en": "{header}\n📡 <b>{remark}</b>\n👥 <b>Clients</b>\n\nTotal: {count}",
        "tk": "{header}\n📡 <b>{remark}</b>\n👥 <b>Müşderiler</b>\n\nJemi: {count}",
    },
    "panel_clients_list_empty": {
        "ru": "{header}\n📡 <b>{remark}</b>\n👥 <b>Клиенты</b>\n\nПока клиентов нет.",
        "en": "{header}\n📡 <b>{remark}</b>\n👥 <b>Clients</b>\n\nNo clients yet.",
        "tk": "{header}\n📡 <b>{remark}</b>\n👥 <b>Müşderiler</b>\n\nHeniz müşderi ýok.",
    },
    "panel_client_detail": {
        "ru": (
            "{header}\n📡 <b>{remark}</b>\n\n👤 <b>{email}</b>\n{status_emoji} {status_label}\n\n"
            "📊 Использовано: {used}\n📦 Лимит: {limit}\n⏳ Срок: {expire}\n🔢 Лимит IP: {limit_ip}"
        ),
        "en": (
            "{header}\n📡 <b>{remark}</b>\n\n👤 <b>{email}</b>\n{status_emoji} {status_label}\n\n"
            "📊 Used: {used}\n📦 Limit: {limit}\n⏳ Expiry: {expire}\n🔢 IP limit: {limit_ip}"
        ),
        "tk": (
            "{header}\n📡 <b>{remark}</b>\n\n👤 <b>{email}</b>\n{status_emoji} {status_label}\n\n"
            "📊 Ulanyldy: {used}\n📦 Limit: {limit}\n⏳ Möhlet: {expire}\n🔢 IP limiti: {limit_ip}"
        ),
    },
    "client_status_enabled": {"ru": "Включён", "en": "Enabled", "tk": "Işjeň"},
    "client_status_disabled": {"ru": "Отключён", "en": "Disabled", "tk": "Öçürilen"},
    "client_limit_unlimited": {"ru": "без ограничений", "en": "unlimited", "tk": "çäksiz"},
    "client_expire_never": {"ru": "бессрочно", "en": "never", "tk": "möhletsiz"},
    "client_limit_ip_unlimited": {"ru": "без ограничений", "en": "unlimited", "tk": "çäksiz"},
    "panel_create_client_step_email": {
        "ru": "{header}\n📡 <b>{remark}</b>\n\n👤 Введите email/имя нового клиента:",
        "en": "{header}\n📡 <b>{remark}</b>\n\n👤 Enter the new client's email/name:",
        "tk": "{header}\n📡 <b>{remark}</b>\n\n👤 Täze müşderiniň email/adyny ýazyň:",
    },
    "panel_create_client_invalid_email": {
        "ru": "Имя не может быть пустым. Попробуйте ещё раз:",
        "en": "The name can't be empty. Try again:",
        "tk": "At boş bolup bilmez. Täzeden synanyşyň:",
    },
    "panel_client_step_limits": {
        "ru": (
            "{header}\n\n📦 Пришлите лимит трафика в ГБ и срок действия в днях через «|», "
            "например: <code>50|30</code>. «0» в любом поле — без ограничений/бессрочно."
        ),
        "en": (
            "{header}\n\n📦 Send the traffic limit in GB and validity in days separated by \"|\", "
            "e.g.: <code>50|30</code>. \"0\" in either field means unlimited/never expires."
        ),
        "tk": (
            "{header}\n\n📦 Traffik limitini GB-de we möhletini gün bilen «|» arkaly iberiň, "
            "mysal: <code>50|30</code>. Islendik meýdanda «0» — çäksiz/möhletsiz diýmek."
        ),
    },
    "panel_client_err_wrong_format": {
        "ru": "Нужно 2 числа через «|»: ГБ|дни. Пример: <code>50|30</code>",
        "en": "Two numbers separated by \"|\" are needed: GB|days. Example: <code>50|30</code>",
        "tk": "«|» bilen 2 san gerek: GB|gün. Mysal: <code>50|30</code>",
    },
    "panel_client_err_not_numbers": {
        "ru": "Оба значения должны быть неотрицательными числами.",
        "en": "Both values must be non-negative numbers.",
        "tk": "Iki baha-da otrisatel bolmadyk san bolmaly.",
    },
    "panel_create_client_confirm": {
        "ru": "{header}\n📡 <b>{remark}</b>\n\n➕ Добавить клиента <b>{email}</b>?\n\n📦 Лимит: {limit}\n⏳ Срок: {expire}",
        "en": "{header}\n📡 <b>{remark}</b>\n\n➕ Add client <b>{email}</b>?\n\n📦 Limit: {limit}\n⏳ Expiry: {expire}",
        "tk": "{header}\n📡 <b>{remark}</b>\n\n➕ <b>{email}</b> müşderisi goşulsynmy?\n\n📦 Limit: {limit}\n⏳ Möhlet: {expire}",
    },
    "panel_create_client_success": {
        "ru": "{icon} Клиент <b>{email}</b> добавлен.",
        "en": "{icon} Client <b>{email}</b> added.",
        "tk": "{icon} <b>{email}</b> müşderisi goşuldy.",
    },
    "panel_client_edit_confirm": {
        "ru": "{header}\n\n✏️ Применить: лимит — {limit}, срок — {expire}?",
        "en": "{header}\n\n✏️ Apply: limit — {limit}, expiry — {expire}?",
        "tk": "{header}\n\n✏️ Ulanylsynmy: limit — {limit}, möhlet — {expire}?",
    },
    "panel_client_edit_success": {
        "ru": "{icon} Клиент обновлён.",
        "en": "{icon} Client updated.",
        "tk": "{icon} Müşderi täzelendi.",
    },
    "panel_client_toggle_success": {
        "ru": "{icon} Клиент теперь {status_label}.",
        "en": "{icon} The client is now {status_label}.",
        "tk": "{icon} Müşderi indi {status_label}.",
    },
    "panel_client_delete_confirm": {
        "ru": "{header}\n\n⚠️ Точно удалить клиента <b>{email}</b>? Это действие необратимо.",
        "en": "{header}\n\n⚠️ Delete client <b>{email}</b>? This can't be undone.",
        "tk": "{header}\n\n⚠️ <b>{email}</b> müşderisini pozmakçymysyňyz? Bu amal yzyna gaýtarylmaýar.",
    },
    "panel_client_delete_success": {
        "ru": "{icon} Клиент удалён.",
        "en": "{icon} Client deleted.",
        "tk": "{icon} Müşderi pozuldy.",
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
    "whois_l_ip": {"ru": "📍 IP", "en": "📍 IP", "tk": "📍 IP"},
    "whois_l_host": {"ru": "🖥 Хост", "en": "🖥 Host", "tk": "🖥 Host"},
    "whois_l_country": {"ru": "🌍 Страна", "en": "🌍 Country", "tk": "🌍 Ýurt"},
    "whois_l_city": {"ru": "🏙 Город", "en": "🏙 City", "tk": "🏙 Şäher"},
    "whois_l_provider": {"ru": "🏢 Провайдер", "en": "🏢 Provider", "tk": "🏢 Provaýder"},
    "whois_l_org": {"ru": "🏬 Организация", "en": "🏬 Organization", "tk": "🏬 Guramasy"},
    "whois_l_network": {"ru": "🏷 Сеть (реестр)", "en": "🏷 Network (registry)", "tk": "🏷 Ulgam (registr)"},
    "whois_l_timezone": {"ru": "🕒 Часовой пояс", "en": "🕒 Timezone", "tk": "🕒 Wagt guşagy"},
    "whois_l_proxy": {"ru": "🎭 Прокси", "en": "🎭 Proxy", "tk": "🎭 Proksi"},
    "whois_l_vpn": {"ru": "🛡 VPN", "en": "🛡 VPN", "tk": "🛡 VPN"},
    "whois_l_tor": {"ru": "🕵️ Tor", "en": "🕵️ Tor", "tk": "🕵️ Tor"},
    "whois_l_hosting": {"ru": "🏭 Хостинг", "en": "🏭 Hosting", "tk": "🏭 Hosting"},
    "whois_l_cloudflare": {"ru": "☁️ Cloudflare", "en": "☁️ Cloudflare", "tk": "☁️ Cloudflare"},
    "whois_l_domain": {"ru": "📛 Домен", "en": "📛 Domain", "tk": "📛 Domen"},
    "whois_l_registrar": {"ru": "🏛 Регистратор", "en": "🏛 Registrar", "tk": "🏛 Registrator"},
    "whois_l_created": {"ru": "📅 Зарегистрирован", "en": "📅 Registered", "tk": "📅 Hasaba alnan"},
    "whois_l_expires": {"ru": "⏳ Истекает", "en": "⏳ Expires", "tk": "⏳ Möhleti"},
    "whois_l_updated": {"ru": "🔄 Обновлён", "en": "🔄 Updated", "tk": "🔄 Täzelenen"},
    "whois_l_status": {"ru": "🚦 Статус", "en": "🚦 Status", "tk": "🚦 Status"},
    "whois_l_cloudflare_ns": {"ru": "☁️ Cloudflare NS", "en": "☁️ Cloudflare NS", "tk": "☁️ Cloudflare NS"},
    "whois_l_nameservers": {"ru": "📡 Серверы имён", "en": "📡 Nameservers", "tk": "📡 At serwerleri"},
    "whois_l_dns_a": {"ru": "🔢 DNS A", "en": "🔢 DNS A", "tk": "🔢 DNS A"},
    "whois_l_dns_mx": {"ru": "📧 DNS MX", "en": "📧 DNS MX", "tk": "📧 DNS MX"},
    "whois_l_dns_txt": {"ru": "📝 DNS TXT", "en": "📝 DNS TXT", "tk": "📝 DNS TXT"},
    # --- Cloud VPS ---
    "cloud_provider_list": {
        "ru": (
            "{icon} <b>Cloud VPS</b> 🖥\n\n"
            "<i>Покупка и управление серверами напрямую через API облачных "
            "провайдеров — выберите провайдера:</i>"
        ),
        "en": (
            "{icon} <b>Cloud VPS</b> 🖥\n\n"
            "<i>Buy and manage servers directly through cloud-provider APIs — "
            "choose a provider:</i>"
        ),
        "tk": (
            "{icon} <b>Cloud VPS</b> 🖥\n\n"
            "<i>Bulut provaýderleriň API-si arkaly serwer satyn almak we dolandyrmak — "
            "provaýderi saýlaň:</i>"
        ),
    },
    "btn_cloud_provider_upcloud": {"ru": "☁️ UpCloud", "en": "☁️ UpCloud", "tk": "☁️ UpCloud"},
    "btn_cloud_provider_aws": {"ru": "🟧 AWS (скоро)", "en": "🟧 AWS (soon)", "tk": "🟧 AWS (ýakynda)"},
    "btn_cloud_provider_azure": {"ru": "🔷 Azure (скоро)", "en": "🔷 Azure (soon)", "tk": "🔷 Azure (ýakynda)"},
    "btn_cloud_provider_linode": {"ru": "🟩 Linode (скоро)", "en": "🟩 Linode (soon)", "tk": "🟩 Linode (ýakynda)"},
    "btn_cloud_provider_kamatera": {
        "ru": "🟪 Kamatera (скоро)",
        "en": "🟪 Kamatera (soon)",
        "tk": "🟪 Kamatera (ýakynda)",
    },
    "cloud_provider_soon": {
        "ru": "{icon} Этот провайдер появится здесь в одном из следующих обновлений — сейчас доступен UpCloud.",
        "en": "{icon} This provider is coming in a future update — UpCloud is available right now.",
        "tk": "{icon} Bu provaýder indiki täzelenmede goşular — häzir UpCloud elýeterli.",
    },
    "title_cloud_provider_upcloud": {"ru": "UpCloud", "en": "UpCloud", "tk": "UpCloud"},
    "cloud_account_list_header": {
        "ru": "{icon} <b>{provider}</b>\n\n{body}",
        "en": "{icon} <b>{provider}</b>\n\n{body}",
        "tk": "{icon} <b>{provider}</b>\n\n{body}",
    },
    "cloud_account_list_empty": {
        "ru": "<i>Пока нет подключённых аккаунтов.</i>",
        "en": "<i>No accounts connected yet.</i>",
        "tk": "<i>Entek birikdirilen hasap ýok.</i>",
    },
    "cloud_account_list_hint": {
        "ru": "<i>Выберите аккаунт или подключите новый.</i>",
        "en": "<i>Pick an account or connect a new one.</i>",
        "tk": "<i>Hasaby saýlaň ýa-da täzesini birikdiriň.</i>",
    },
    "btn_cloud_account_add": {"ru": "➕ Подключить аккаунт", "en": "➕ Connect account", "tk": "➕ Hasap birikdir"},
    "btn_cloud_provider_list": {"ru": "☁️ К провайдерам", "en": "☁️ Back to providers", "tk": "☁️ Provaýderlere gaýt"},
    "cloud_step_username_upcloud": {
        "ru": (
            "🔑 <b>Подключение UpCloud</b>\n\n"
            "Введите <b>API-логин</b> — имя суб-аккаунта с доступом к API "
            "(создаётся в панели UpCloud: People → сотрудник с правами API), "
            "а не email от основного аккаунта."
        ),
        "en": (
            "🔑 <b>Connect UpCloud</b>\n\n"
            "Enter the <b>API username</b> — an API-access sub-account name "
            "(created in the UpCloud panel: People → a user with API rights), "
            "not the main account's email."
        ),
        "tk": (
            "🔑 <b>UpCloud birikdirmek</b>\n\n"
            "<b>API-login</b> giriziň — API girişi bolan sub-hasabyň ady "
            "(UpCloud panelinde döredilýär: People → API hukukly ulanyjy), "
            "esasy hasabyň e-poçtasy däl."
        ),
    },
    "cloud_step_password": {
        "ru": "🔒 Теперь введите пароль от этого аккаунта (сообщение удалится сразу после отправки):",
        "en": "🔒 Now enter that account's password (the message is deleted right after you send it):",
        "tk": "🔒 Indi şol hasabyň parolyny giriziň (habar iberilenden soň derrew pozulýar):",
    },
    "cloud_empty_password": {
        "ru": "Пароль не может быть пустым. Попробуйте ещё раз:",
        "en": "The password can't be empty. Try again:",
        "tk": "Parol boş bolup bilmez. Gaýtadan synanyň:",
    },
    "cloud_connecting": {
        "ru": "🔌 Подключаюсь к провайдеру...",
        "en": "🔌 Connecting to the provider...",
        "tk": "🔌 Provaýdere birikilýär...",
    },
    "cloud_login_error": {
        "ru": (
            "{icon} <b>Не удалось подключиться</b>\n\n"
            "{reason}\n\n"
            "🔁 Проверьте логин и пароль и попробуйте снова"
        ),
        "en": (
            "{icon} <b>Couldn't connect</b>\n\n"
            "{reason}\n\n"
            "🔁 Check the username and password and try again"
        ),
        "tk": (
            "{icon} <b>Birikdirip bolmady</b>\n\n"
            "{reason}\n\n"
            "🔁 Login we paroly barlaň we gaýtadan synanyň"
        ),
    },
    "cloud_action_error": {
        "ru": "{icon} <b>Не получилось выполнить действие</b>\n\n{reason}",
        "en": "{icon} <b>Couldn't complete the action</b>\n\n{reason}",
        "tk": "{icon} <b>Amal ýerine ýetirilmedi</b>\n\n{reason}",
    },
    "cloud_err_wrong_credentials": {
        "ru": "Неверный API-логин или пароль.",
        "en": "Wrong API username or password.",
        "tk": "API-login ýa-da parol nädogry.",
    },
    "cloud_err_connect_failed": {
        "ru": "Не удалось связаться с провайдером — проверьте подключение к интернету и повторите попытку.",
        "en": "Couldn't reach the provider — check the connection and try again.",
        "tk": "Provaýder bilen habarlaşyp bolmady — internet birikmesini barlaň we gaýtadan synanyň.",
    },
    "cloud_err_bad_response": {
        "ru": "Провайдер ответил в неожиданном формате.",
        "en": "The provider responded in an unexpected format.",
        "tk": "Provaýder garaşylmadyk formatda jogap berdi.",
    },
    "cloud_connected": {
        "ru": "{icon} Аккаунт {provider} успешно подключен 🚀",
        "en": "{icon} {provider} account connected successfully 🚀",
        "tk": "{icon} {provider} hasaby üstünlikli birikdirildi 🚀",
    },
    "btn_cloud_cancel": {"ru": "❌ Отмена", "en": "❌ Cancel", "tk": "❌ Ýatyr"},
    "cloud_account_dashboard": {
        "ru": (
            "☁️ <b>{provider}</b>\n\n"
            "👤 Аккаунт: <code>{username}</code>\n"
            "💰 Баланс: {credits} {currency}"
        ),
        "en": (
            "☁️ <b>{provider}</b>\n\n"
            "👤 Account: <code>{username}</code>\n"
            "💰 Balance: {credits} {currency}"
        ),
        "tk": (
            "☁️ <b>{provider}</b>\n\n"
            "👤 Hasap: <code>{username}</code>\n"
            "💰 Balans: {credits} {currency}"
        ),
    },
    "btn_cloud_servers": {"ru": "🖥 Серверы", "en": "🖥 Servers", "tk": "🖥 Serwerler"},
    "btn_cloud_account_remove": {"ru": "🗑 Убрать аккаунт", "en": "🗑 Remove account", "tk": "🗑 Hasaby aýyr"},
    "btn_cloud_account_remove_confirm": {"ru": "🗑 Да, убрать", "en": "🗑 Yes, remove", "tk": "🗑 Hawa, aýyr"},
    "btn_cloud_account_list": {"ru": "⬅️ К аккаунтам", "en": "⬅️ Back to accounts", "tk": "⬅️ Hasaplara gaýt"},
    "btn_cloud_account_dashboard": {"ru": "⬅️ К аккаунту", "en": "⬅️ Back to account", "tk": "⬅️ Hasaba gaýt"},
    "cloud_account_remove_confirm": {
        "ru": "{icon} Убрать аккаунт <b>{username}</b> из бота? Сами серверы в облаке не удаляются.",
        "en": "{icon} Remove account <b>{username}</b> from the bot? The cloud servers themselves stay untouched.",
        "tk": "{icon} <b>{username}</b> hasabyny botdan aýyrmalymy? Buluddaky serwerler pozulmaz.",
    },
    "cloud_account_removed": {
        "ru": "{icon} Аккаунт убран.",
        "en": "{icon} Account removed.",
        "tk": "{icon} Hasap aýryldy.",
    },
    "cloud_servers_header": {
        "ru": "🖥 <b>Серверы — {username}</b>\n\n{body}",
        "en": "🖥 <b>Servers — {username}</b>\n\n{body}",
        "tk": "🖥 <b>Serwerler — {username}</b>\n\n{body}",
    },
    "cloud_servers_empty": {
        "ru": "<i>Серверов пока нет.</i>",
        "en": "<i>No servers yet.</i>",
        "tk": "<i>Entek serwer ýok.</i>",
    },
    "cloud_servers_hint": {
        "ru": "<i>Выберите сервер или создайте новый.</i>",
        "en": "<i>Pick a server or create a new one.</i>",
        "tk": "<i>Serweri saýlaň ýa-da täzesini dörediň.</i>",
    },
    "btn_cloud_server_add": {"ru": "➕ Создать сервер", "en": "➕ Create server", "tk": "➕ Serwer döret"},
    "btn_cloud_servers_list": {"ru": "🖥 К серверам", "en": "🖥 Back to servers", "tk": "🖥 Serwerlere gaýt"},
    "cloud_server_detail": {
        "ru": (
            "🖥 <b>{title}</b>\n\n"
            "🌐 Hostname: <code>{hostname}</code>\n"
            "🚦 Статус: {state}\n"
            "📍 Зона: {zone}\n"
            "⚙️ План: {plan} ({cores} CPU / {memory} MB RAM)\n"
            "🌍 IP: {ips}"
        ),
        "en": (
            "🖥 <b>{title}</b>\n\n"
            "🌐 Hostname: <code>{hostname}</code>\n"
            "🚦 State: {state}\n"
            "📍 Zone: {zone}\n"
            "⚙️ Plan: {plan} ({cores} CPU / {memory} MB RAM)\n"
            "🌍 IP: {ips}"
        ),
        "tk": (
            "🖥 <b>{title}</b>\n\n"
            "🌐 Hostname: <code>{hostname}</code>\n"
            "🚦 Ýagdaýy: {state}\n"
            "📍 Zolak: {zone}\n"
            "⚙️ Meýilnama: {plan} ({cores} CPU / {memory} MB RAM)\n"
            "🌍 IP: {ips}"
        ),
    },
    "cloud_server_no_ip": {"ru": "—", "en": "—", "tk": "—"},
    "btn_cloud_server_start": {"ru": "▶️ Включить", "en": "▶️ Start", "tk": "▶️ Işe girizmek"},
    "btn_cloud_server_stop": {"ru": "⏹ Выключить", "en": "⏹ Stop", "tk": "⏹ Duruzmak"},
    "btn_cloud_server_restart": {"ru": "🔄 Перезагрузить", "en": "🔄 Restart", "tk": "🔄 Täzeden başlat"},
    "btn_cloud_server_delete": {"ru": "🗑 Удалить сервер", "en": "🗑 Delete server", "tk": "🗑 Serweri poz"},
    "btn_cloud_server_delete_confirm": {"ru": "🗑 Да, удалить", "en": "🗑 Yes, delete", "tk": "🗑 Hawa, poz"},
    "cloud_server_action_ok": {
        "ru": "{icon} Команда отправлена, статус сервера скоро обновится.",
        "en": "{icon} Command sent, the server's status will update shortly.",
        "tk": "{icon} Buýruk iberildi, serweriň ýagdaýy ýakynda täzelener.",
    },
    "cloud_server_delete_confirm": {
        "ru": (
            "{icon} <b>Удалить сервер {title}?</b>\n\n"
            "⚠️ Действие необратимо: сервер и его диски будут удалены "
            "на стороне провайдера безвозвратно."
        ),
        "en": (
            "{icon} <b>Delete server {title}?</b>\n\n"
            "⚠️ This is irreversible: the server and its disks will be "
            "permanently deleted on the provider's side."
        ),
        "tk": (
            "{icon} <b>{title} serweri pozulsynmy?</b>\n\n"
            "⚠️ Bu amal yzyna gaýtarylmaz: serwer we onuň disklari "
            "provaýderde hemişelik pozular."
        ),
    },
    "cloud_server_deleted": {
        "ru": "{icon} Сервер удалён.",
        "en": "{icon} Server deleted.",
        "tk": "{icon} Serwer pozuldy.",
    },
    "cloud_create_choose_zone": {
        "ru": "🌍 <b>Новый сервер — шаг 1/4</b>\n\nВыберите зону (дата-центр):",
        "en": "🌍 <b>New server — step 1/4</b>\n\nChoose a zone (data center):",
        "tk": "🌍 <b>Täze serwer — 1/4 ädim</b>\n\nZolak saýlaň (maglumat merkezi):",
    },
    "cloud_create_choose_plan": {
        "ru": "⚙️ <b>Новый сервер — шаг 2/4</b>\n\nВыберите тарифный план:",
        "en": "⚙️ <b>New server — step 2/4</b>\n\nChoose a plan:",
        "tk": "⚙️ <b>Täze serwer — 2/4 ädim</b>\n\nMeýilnama saýlaň:",
    },
    "cloud_create_choose_template": {
        "ru": "💿 <b>Новый сервер — шаг 3/4</b>\n\nВыберите операционную систему:",
        "en": "💿 <b>New server — step 3/4</b>\n\nChoose an operating system:",
        "tk": "💿 <b>Täze serwer — 3/4 ädim</b>\n\nOperasion ulgamy saýlaň:",
    },
    "cloud_create_waiting_hostname": {
        "ru": "✏️ <b>Новый сервер — шаг 4/4</b>\n\nВведите hostname сервера (например, my-server.example.com):",
        "en": "✏️ <b>New server — step 4/4</b>\n\nEnter the server's hostname (e.g. my-server.example.com):",
        "tk": "✏️ <b>Täze serwer — 4/4 ädim</b>\n\nServeriň hostname-ini giriziň (mysal: my-server.example.com):",
    },
    "cloud_create_invalid_hostname": {
        "ru": "Некорректный hostname. Используйте только буквы, цифры, точки и дефисы. Попробуйте ещё раз:",
        "en": "Invalid hostname. Use only letters, digits, dots and hyphens. Try again:",
        "tk": "Hostname nädogry. Diňe harp, san, nokat we defis ulanyň. Gaýtadan synanyň:",
    },
    "cloud_create_confirm": {
        "ru": (
            "✅ <b>Проверьте параметры сервера</b>\n\n"
            "🌐 Hostname: <code>{hostname}</code>\n"
            "📍 Зона: {zone}\n"
            "⚙️ План: {plan}\n"
            "💿 ОС: {template}\n\n"
            "💰 Это создаст платный ресурс на стороне провайдера. Создать?"
        ),
        "en": (
            "✅ <b>Review server parameters</b>\n\n"
            "🌐 Hostname: <code>{hostname}</code>\n"
            "📍 Zone: {zone}\n"
            "⚙️ Plan: {plan}\n"
            "💿 OS: {template}\n\n"
            "💰 This will create a billable resource with the provider. Create it?"
        ),
        "tk": (
            "✅ <b>Serweriň parametrlerini barlaň</b>\n\n"
            "🌐 Hostname: <code>{hostname}</code>\n"
            "📍 Zolak: {zone}\n"
            "⚙️ Meýilnama: {plan}\n"
            "💿 OS: {template}\n\n"
            "💰 Bu provaýderde tölegli resurs dörediler. Döredilsinmi?"
        ),
    },
    "btn_cloud_create_confirm": {"ru": "✅ Создать", "en": "✅ Create", "tk": "✅ Döret"},
    "cloud_creating": {
        "ru": "🚀 Создаю сервер, это может занять до минуты...",
        "en": "🚀 Creating the server, this can take up to a minute...",
        "tk": "🚀 Serwer döredilýär, bir minuda çenli wagt alyp biler...",
    },
    "cloud_create_success": {
        "ru": (
            "{icon} <b>Сервер создан!</b>\n\n"
            "🖥 {title}\n"
            "🌐 IP: {ips}\n"
            "{password_line}"
        ),
        "en": (
            "{icon} <b>Server created!</b>\n\n"
            "🖥 {title}\n"
            "🌐 IP: {ips}\n"
            "{password_line}"
        ),
        "tk": (
            "{icon} <b>Serwer döredildi!</b>\n\n"
            "🖥 {title}\n"
            "🌐 IP: {ips}\n"
            "{password_line}"
        ),
    },
    "cloud_create_password_line": {
        "ru": "🔑 Пароль root: <code>{password}</code> (сохраните, повторно показан не будет)",
        "en": "🔑 Root password: <code>{password}</code> (save it, it won't be shown again)",
        "tk": "🔑 Root paroly: <code>{password}</code> (ýatda saklaň, indi görkezilmez)",
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
