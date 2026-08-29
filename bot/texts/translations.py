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
    "btn_panel": {"ru": "🎛 Panel", "en": "🎛 Panel", "tk": "🎛 Panel"},
    "btn_panel_marzban": {"ru": "⚡ Marzban", "en": "⚡ Marzban", "tk": "⚡ Marzban"},
    "btn_panel_pasarguard": {"ru": "🛡 PasarGuard", "en": "🛡 PasarGuard", "tk": "🛡 PasarGuard"},
    "btn_panel_3xui": {"ru": "3️⃣ 3X-UI", "en": "3️⃣ 3X-UI", "tk": "3️⃣ 3X-UI"},
    "btn_panel_stats": {"ru": "📊 Статистика", "en": "📊 Statistics", "tk": "📊 Statistika"},
    "btn_panel_users": {"ru": "👥 Пользователи", "en": "👥 Users", "tk": "👥 Ulanyjylar"},
    "btn_panel_disconnect": {
        "ru": "🔌 Отключить панель",
        "en": "🔌 Disconnect panel",
        "tk": "🔌 Paneli aýyr",
    },
    "btn_panel_disconnect_confirm": {
        "ru": "✅ Да, отключить",
        "en": "✅ Yes, disconnect",
        "tk": "✅ Hawa, aýyr",
    },
    "btn_panel_dashboard": {"ru": "⬅️ К панели", "en": "⬅️ Back to panel", "tk": "⬅️ Panele gaýt"},
    "btn_panel_menu": {"ru": "🎛 Меню Panel", "en": "🎛 Panel menu", "tk": "🎛 Panel menýusy"},
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
    "panel_menu": {
        "ru": (
            "{icon} <b>Panel</b>\n\n"
            "<i>Подключите свою панель и управляйте ей прямо здесь.</i>\n\n"
            "👇 Выберите панель"
        ),
        "en": (
            "{icon} <b>Panel</b>\n\n"
            "<i>Connect your panel and manage it right here.</i>\n\n"
            "👇 Choose your panel"
        ),
        "tk": (
            "{icon} <b>Panel</b>\n\n"
            "<i>Paneliňizi birikdiriň we ony şu ýerden dolandyryň.</i>\n\n"
            "👇 Paneli saýlaň"
        ),
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
        "ru": "{icon} {header} успешно подключена 🚀\n\n🌍 <code>{url}</code>",
        "en": "{icon} {header} connected successfully 🚀\n\n🌍 <code>{url}</code>",
        "tk": "{icon} {header} üstünlikli birikdirildi 🚀\n\n🌍 <code>{url}</code>",
    },
    "panel_dashboard": {
        "ru": "{header}\n\n🌍 <code>{url}</code>\n\n👇 Что делаем?",
        "en": "{header}\n\n🌍 <code>{url}</code>\n\n👇 What next?",
        "tk": "{header}\n\n🌍 <code>{url}</code>\n\n👇 Näme edeliň?",
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
        "ru": "{header}\n👥 <b>Пользователи</b>\n\nПоказаны первые {count}:",
        "en": "{header}\n👥 <b>Users</b>\n\nShowing the first {count}:",
        "tk": "{header}\n👥 <b>Ulanyjylar</b>\n\nIlkinji {count} görkezilýär:",
    },
    "panel_users_list_empty": {
        "ru": "{header}\n👥 <b>Пользователи</b>\n\nПока пользователей нет.",
        "en": "{header}\n👥 <b>Users</b>\n\nNo users yet.",
        "tk": "{header}\n👥 <b>Ulanyjylar</b>\n\nHeniz ulanyjy ýok.",
    },
    "panel_disconnect_confirm": {
        "ru": (
            "{header}\n\n"
            "⚠️ Точно отключить эту панель? Доступ через бота закроется, пока вы не "
            "подключите её заново."
        ),
        "en": (
            "{header}\n\n"
            "⚠️ Disconnect this panel? Bot access will stop until you connect it again."
        ),
        "tk": (
            "{header}\n\n"
            "⚠️ Bu paneli aýyrmakçymysyňyz? Täzeden birikdirilýänçä bot arkaly giriş ýapylar."
        ),
    },
    "panel_disconnected": {
        "ru": "🔌 Панель отключена.\n\n👇 Можно подключить другую в любой момент",
        "en": "🔌 Panel disconnected.\n\n👇 You can connect another one anytime",
        "tk": "🔌 Panel aýryldy.\n\n👇 Islän wagtyňyz başga birini birikdirip bilersiňiz",
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
