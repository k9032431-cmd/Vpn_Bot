from __future__ import annotations

DEFAULT_LANGUAGE = "ru"
LANGUAGES = ("ru", "en", "tk")

# Decorative divider used on "screen" texts (menus, results) to separate the
# intro from the call-to-action, keeping the layout consistent everywhere.
DIVIDER = "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈"

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
            "{div}\n"
            "👇 Выберите раздел, чтобы начать"
        ),
        "en": (
            "{icon} <b>ArsiCloudBot</b> 🌐\n\n"
            "<i>Your smart VPN companion: nodes, cloud, encryption and security — "
            "all in one place.</i>\n\n"
            "{div}\n"
            "👇 Choose a section to get started"
        ),
        "tk": (
            "{icon} <b>ArsiCloudBot</b> 🌐\n\n"
            "<i>VPN dolandyryşy üçin akylly kömekçiňiz: node-lar, bulut, şifrleme "
            "we howpsuzlyk — bary-ýogy bir ýerde.</i>\n\n"
            "{div}\n"
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
    # --- Section placeholders ---
    "section_cloud_vpn": {
        "ru": (
            "{icon} <b>Cloud VPN</b> 📶\n\n"
            "<i>Управление облачными VPN-подключениями появится здесь совсем скоро.</i>\n\n"
            "{div}\n🛠️ Уже в разработке"
        ),
        "en": (
            "{icon} <b>Cloud VPN</b> 📶\n\n"
            "<i>Cloud VPN connection management is coming here very soon.</i>\n\n"
            "{div}\n🛠️ Already in the works"
        ),
        "tk": (
            "{icon} <b>Cloud VPN</b> 📶\n\n"
            "<i>Bulut VPN birikmelerini dolandyrmak ýakynda bu ýerde peýda bolar.</i>\n\n"
            "{div}\n🛠️ Eýýäm işlenilýär"
        ),
    },
    "section_cloud_account": {
        "ru": (
            "{icon} <b>Cloud Account</b> 🔑\n\n"
            "<i>Управление вашим аккаунтом появится совсем скоро.</i>\n\n"
            "{div}\n🛠️ Уже в разработке"
        ),
        "en": (
            "{icon} <b>Cloud Account</b> 🔑\n\n"
            "<i>Account management is coming very soon.</i>\n\n"
            "{div}\n🛠️ Already in the works"
        ),
        "tk": (
            "{icon} <b>Cloud Account</b> 🔑\n\n"
            "<i>Hasabyňyzy dolandyrmak ýakyn wagtda goşular.</i>\n\n"
            "{div}\n🛠️ Eýýäm işlenilýär"
        ),
    },
    "section_crypt": {
        "ru": (
            "{icon} <b>Crypt / Decrypt</b> 🗝️\n\n"
            "<i>Шифрование и дешифрование данных — уже в работе.</i>\n\n"
            "{div}\n🛠️ Скоро будет доступно"
        ),
        "en": (
            "{icon} <b>Crypt / Decrypt</b> 🗝️\n\n"
            "<i>Data encryption and decryption tools are already in the works.</i>\n\n"
            "{div}\n🛠️ Coming soon"
        ),
        "tk": (
            "{icon} <b>Crypt / Decrypt</b> 🗝️\n\n"
            "<i>Maglumatlary şifrlemek we deşifrlemek eýýäm işlenilýär.</i>\n\n"
            "{div}\n🛠️ Ýakynda elýeterli bolar"
        ),
    },
    "section_info": {
        "ru": (
            "{icon} <b>ArsiCloudBot</b> 🖥️\n\n"
            "<i>Ваш помощник по управлению VPN — просто, быстро и безопасно.</i>\n\n"
            "{div}\n🏷️ Версия <code>0.1.0</code>"
        ),
        "en": (
            "{icon} <b>ArsiCloudBot</b> 🖥️\n\n"
            "<i>Your VPN management companion — simple, fast and secure.</i>\n\n"
            "{div}\n🏷️ Version <code>0.1.0</code>"
        ),
        "tk": (
            "{icon} <b>ArsiCloudBot</b> 🖥️\n\n"
            "<i>VPN dolandyryş kömekçiňiz — ýönekeý, çalt we howpsuz.</i>\n\n"
            "{div}\n🏷️ Wersiýa <code>0.1.0</code>"
        ),
    },
    "section_sos_contact": {
        "ru": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Что-то пошло не так? Мы всегда на связи.</i>\n\n"
            "{div}\n📩 Напишите нам: {contact}"
        ),
        "en": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Something's not working? We're always here.</i>\n\n"
            "{div}\n📩 Contact us: {contact}"
        ),
        "tk": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Bir zat nädogry gitdimi? Biz hemişe ýanyňyzda.</i>\n\n"
            "{div}\n📩 Bize ýazyň: {contact}"
        ),
    },
    "section_sos_empty": {
        "ru": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Что-то пошло не так? Мы всегда на связи.</i>\n\n"
            "{div}\n📩 Поддержка появится здесь совсем скоро"
        ),
        "en": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Something's not working? We're always here.</i>\n\n"
            "{div}\n📩 Support contact is coming very soon"
        ),
        "tk": (
            "{icon} <b>SOS</b> 🔌\n\n"
            "<i>Bir zat nädogry gitdimi? Biz hemişe ýanyňyzda.</i>\n\n"
            "{div}\n📩 Goldaw ýakynda bu ýerde peýda bolar"
        ),
    },
    # --- Language picker ---
    "language_prompt": {
        "ru": (
            "{icon} <b>Язык интерфейса</b> 📡\n\n"
            "<i>Выберите, на каком языке вам удобнее общаться с ботом.</i>\n\n"
            "{div}\n👇 Доступные языки"
        ),
        "en": (
            "{icon} <b>Interface language</b> 📡\n\n"
            "<i>Choose the language you'd like the bot to speak.</i>\n\n"
            "{div}\n👇 Available languages"
        ),
        "tk": (
            "{icon} <b>Interfeýsiň dili</b> 📡\n\n"
            "<i>Bot bilen haýsy dilde gürleşmek isleýändigiňizi saýlaň.</i>\n\n"
            "{div}\n👇 Elýeterli diller"
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
            "{div}\n👇 Выберите платформу"
        ),
        "en": (
            "{icon} <b>Node</b> 🖧\n\n"
            "<i>Deploy a VPN node on your server in a couple of minutes — the bot handles the rest.</i>\n\n"
            "{div}\n👇 Choose a platform"
        ),
        "tk": (
            "{icon} <b>Node</b> 🖧\n\n"
            "<i>Serweriňizde birnäçe minutda VPN node ornaşdyryň — galanyny bot eder.</i>\n\n"
            "{div}\n👇 Platformany saýlaň"
        ),
    },
    "node_cancelled": {
        "ru": (
            "{icon} <b>Node</b>\n\n"
            "🚫 <i>Установка отменена — данные не сохранены.</i>\n\n"
            "{div}\n👇 Можно начать заново в любой момент"
        ),
        "en": (
            "{icon} <b>Node</b>\n\n"
            "🚫 <i>Installation cancelled — nothing was saved.</i>\n\n"
            "{div}\n👇 You can start again anytime"
        ),
        "tk": (
            "{icon} <b>Node</b>\n\n"
            "🚫 <i>Ornaşdyrma ýatyryldy — hiç zat ýatda saklanmady.</i>\n\n"
            "{div}\n👇 Islän wagtyňyz täzeden başlap bilersiňiz"
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
            "{div}\n🚀 Всё готово — начинаем установку?"
        ),
        "en": (
            "{header}\n\n"
            "📋 <b>Please confirm:</b>\n"
            "🌍 Server: <code>{host}</code>\n"
            "👤 User: <code>{user}</code>\n\n"
            "{div}\n🚀 Ready — start the installation?"
        ),
        "tk": (
            "{header}\n\n"
            "📋 <b>Maglumatlary barlaň:</b>\n"
            "🌍 Server: <code>{host}</code>\n"
            "👤 Ulanyjy: <code>{user}</code>\n\n"
            "{div}\n🚀 Taýyn — ornaşdyrmaga başlaýarysmy?"
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
            "{div}\n🔁 Попробуйте ещё раз или обратитесь в поддержку"
        ),
        "en": (
            "{icon} <b>Couldn't install the node</b>\n\n"
            "{reason}\n\n"
            "{div}\n🔁 Try again, or reach out to support"
        ),
        "tk": (
            "{icon} <b>Node ornaşdyrylyp bilinmedi</b>\n\n"
            "{reason}\n\n"
            "{div}\n🔁 Täzeden synanyşyň ýa-da goldawa ýüz tutuň"
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
}


def t(lang: str, key: str, **kwargs: object) -> str:
    lang = lang if lang in LANGUAGES else DEFAULT_LANGUAGE
    strings = _STRINGS.get(key)
    if strings is None:
        return key
    template = strings.get(lang) or strings.get(DEFAULT_LANGUAGE) or key
    return template.format(**kwargs) if kwargs else template
