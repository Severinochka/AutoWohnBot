# === Translations ===
SUPPORTED_LANGUAGES = ["en", "de", "ru", "ar", "tr"]
DEFAULT_LANGUAGE = "en"
translations = {
    "en": {
        "start": "Welcome to Wohnungsbot!",
        "trial": "Free trial activated until",
        "menu": ["🔎 Enable Search", "⛔ Stop Search", "🏠 Set Filters", "💳 Subscribe", "ℹ️ My Subscription",
                 "👥 Invite Friends", "🆘 Help"],
        "back_to_menu": "🔙 Back to Menu",
        "change_language": "🌐 Change Language",
        "help_button": "🆘 Help",
        "help_text": "For any questions, please contact {help_username}",
        "welcome_message": "👋 *Welcome to Wohnungsbot!*\n\n"
"📢 You've received a *7-day free trial* - active until *{date}*\n\n"
"🏠 Wohnungsbot helps you be the first to see new rental listings in Germany.\n"
"🔔 We instantly notify you about listings that match your filters.\n\n"
"📍 Specify the city, price, area and other parameters by going to 🏠 *Set Filters* in the buttons menu.\n"
"📬 All listings will be sent directly here in Telegram.",
        "subscription": {
            "active": "📅 Your subscription is active until: *{date}* ",
            "expired": "❌ Your subscription *has expired*. You can renew it via 💳 *Subscribe*",
            "none": "❌ You don't have an active subscription.",
            "activated": "✅ Subscription activated until *{date}*! Thank you!",
            "will_expire_in_days": "⚠️ Your subscription will expire in {days} days.",
            "will_expire_tomorrow": "⚠️ Your subscription will expire *tomorrow*.",
            "expired_notice": "❌ Your subscription *has expired*. Please renew via 💳 *Subscribe*.",
        },
        "webapp_error": "Please set filters first by going to button 🏠 *Set Filters*.",
        "invoice": {
            "title": "Subscription",
            "description": "You will get access to automatic listing updates for 30 days"
        },
        "filters": {
            "open": "📋 Click the button below to set your filters:",
            "saved": "✅ *Filter saved!*\n💰 Price: {min_price}€ – {max_price}€\n📏 Size: {min_size}m² – {max_size}m²\n🏷️ Swap apartments: {tauschwohnung}\n📄 WBS required: {wbs}\n🌐 Websites: {websites}\n\n🔎 *Search is ON!* You will receive new listings as they appear.",
            "not_set": "not set",
            "yes": "Yes",
            "no": "No"
        },
        "search": {
            "started": "🔎 Search started. You will receive new listings.",
            "stopped": "⛔ Search stopped. You will no longer receive listings."
        },
        "open_webapp": "🏠 Open Filter Settings",
        "data_error": "Please check your numbers.",
        "invite_friends_text": "👥 Invite a friend and get 14 days free subscription!",
        "referral": {
            "success": "🎉 You got *+{days} days* subscription for inviting *{new_user}*!",
            "new_user_notification": "👋 You joined via referral link! Your free trial has been activated.",
            "self_invite": "❌ You can't invite yourself!",
            "already_invited": "⚠️ You've already invited this user"
        }
    },
    "de": {
        "start": "Willkommen beim Wohnungsbot!",
        "trial": "Kostenlose Testphase aktiviert bis",
        "menu": ["🔎 Suche einschalten", "⛔ Suche stoppen", "🏠 Filter setzen", "💳 Abonnieren", "ℹ️ Mein Abo",
                 "👥 Freunde einladen", "🆘 Hilfe"],
        "back_to_menu": "🔙 Zurück zum Menü",
        "change_language": "🌐 Sprache ändern",
        "help_button": "🆘 Hilfe",
        "help_text": "Bei Fragen wenden Sie sich bitte an {help_username}",
        "welcome_message": "👋 *Willkommen beim Wohnungsbot!*\n\n"
"📢 Sie haben eine *7-tägige kostenlose Testphase* – aktiv bis *{date}* ({days} Tage)\n\n"
"🏠 Wohnungsbot hilft Ihnen, als Erster neue Wohnungsanzeigen in Deutschland zu sehen.\n"
"🔔 Wir benachrichtigen Sie sofort über passende Angebote nach Ihren Filtern.\n\n"
"📍 Klicken Sie auf 🏠 *Filter setzen*, um Stadt, Preis, Größe usw. auszuwählen.\n"
"📬 Alle Vorschläge werden direkt hier auf Telegram kommen.",
        "subscription": {
            "active": "📅 Ihr Abonnement ist aktiv bis: *{date}* ",
            "expired": "❌ Ihr Abonnement *ist abgelaufen*. Sie können es über 💳 *Abonnieren* erneuern",
            "none": "❌ Sie haben kein aktives Abonnement.",
            "activated": "✅ Abonnement aktiviert bis *{date}*! Vielen Dank!",
            "will_expire_in_days": "⚠️ Ihr Abonnement läuft in {days} Tagen ab.",
            "will_expire_tomorrow": "⚠️ Ihr Abonnement läuft *morgen* ab.",
            "expired_notice": "❌ Ihr Abonnement *ist abgelaufen*. Bitte erneuern Sie es über 💳 *Abonnieren*.",
        },
        "webapp_error": "Bitte setzen Sie zuerst die Filter über 🏠 Filter setzen.",
        "invoice": {
            "title": "Abonnement",
            "description": "Sie erhalten 30 Tage lang Zugang zu automatischen Wohnungsangeboten"
        },
        "filters": {
            "open": "📋 Klicken Sie auf die Schaltfläche unten, um Ihre Filter einzustellen:",
            "saved": "✅ *Filter gespeichert!*\n💰 Preis: {min_price}€ – {max_price}€\n📏 Größe: {min_size}m² – {max_size}m²\n🏷️ Wohnungstausch: {tauschwohnung}\n📄 WBS erforderlich: {wbs}\n🌐 Websites: {websites}\n\n🔎 *Suche ist AKTIV!* Sie erhalten neue Angebote, sobald sie erscheinen.",
            "not_set": "nicht festgelegt",
            "yes": "Ja",
            "no": "Nein"
        },
        "search": {
            "started": "🔎 Suche gestartet. Sie erhalten neue Angebote.",
            "stopped": "⛔ Suche gestoppt. Sie erhalten keine weiteren Angebote."
        },
        "open_webapp": "🏠 Filtereinstellungen öffnen",
        "data_error": "Bitte überprüfen Sie Ihre Eingaben.",
        "invite_friends_text": "👥 Laden Sie einen Freund ein und erhalten Sie 14 Tage kostenloses Abonnement!",
        "referral": {
            "success": "🎉 Sie haben *+{days} Tage* Abonnement für die Einladung von *{new_user}* erhalten!",
            "new_user_notification": "👋 Sie sind über einen Empfehlungslink beigetreten! Ihre kostenlose Testversion wurde aktiviert.",
            "self_invite": "❌ Sie können sich nicht selbst einladen!",
            "already_invited": "⚠️ Sie haben diesen Benutzer bereits eingeladen"
        }
    },
    "ru": {
        "start": "Добро пожаловать в Wohnungsbot!",
        "trial": "Бесплатный пробный период до",
        "menu": ["🔎 Включить поиск", "⛔ Остановить поиск", "🏠 Установить фильтры", "💳 Подписка", "ℹ️ Моя подписка",
                 "👥 Пригласить друга", "🆘 Помощь"],
        "back_to_menu": "🔙 Назад в меню",
        "change_language": "🌐 Сменить язык",
        "help_button": "🆘 Помощь",
        "help_text": "По всем вопросам обращайтесь к {help_username}",
        "welcome_message": "👋 *Добро пожаловать в Wohnungsbot!*\n\n"
"📢 Вы получили *бесплатный пробный период на 7 дней* – он активен до *{date}*\n\n"
"🏠 Wohnungsbot помогает вам первыми узнавать о новых объявлениях по аренде жилья в Германии.\n"
"🔔 Мы моментально уведомляем вас о новых предложениях, которые соответствуют вашим фильтрам.\n\n"
"📍 Укажите город, цену, площадь и другие параметры, перейдя в раздел 🏠 *Установить фильтры* из меню кнопок.\n"
"📬 Все предложения будут приходить прямо сюда, в Telegram.",
        "subscription": {
            "active": "📅 Ваша подписка активна до: *{date}* ",
            "expired": "❌ Ваша подписка *истекла*. Вы можете оформить новую через раздел 💳 *Подписка*",
            "none": "❌ У вас нет активной подписки.",
            "activated": "✅ Подписка активирована до *{date}*! Спасибо!",
            "will_expire_in_days": "⚠️ Ваша подписка истекает через {days} дн.",
            "will_expire_tomorrow": "⚠️ Ваша подписка истекает *завтра*.",
            "expired_notice": "❌ Ваша подписка *истекла*. Пожалуйста, оформите новую через раздел 💳 *Подписка*.",
        },
        "webapp_error": "Пожалуйста, сначала установите фильтры через раздел 🏠 *Установить фильтры*.",
        "invoice": {
            "title": "Подписка на сервис",
            "description": "Вы получите доступ к автоматической рассылке новых объявлений на 30 дней"
        },
        "filters": {
            "open": "📋 Нажмите кнопку ниже, чтобы установить фильтры:",
            "saved": "✅ *Фильтры сохранены!*\n💰 Цена: {min_price}€ – {max_price}€\n📏 Размер: {min_size}m² – {max_size}m²\n🏷️ Обмен квартир: {tauschwohnung}\n📄 Требуется WBS: {wbs}\n🌐 Сайты: {websites}\n\n🔎 *Поиск ВКЛЮЧЕН!* Вы будете получать новые объявления по мере их появления.",
            "not_set": "не установлено",
            "yes": "Да",
            "no": "Нет"
        },
        "search": {
            "started": "🔎 Поиск начат. Вы будете получать новые объявления.",
            "stopped": "⛔ Поиск остановлен. Вы больше не будете получать объявления."
        },
        "open_webapp": "🏠 Открыть настройки фильтров",
        "data_error": "Пожалуйста, проверьте ваши числа.",
        "invite_friends_text": "👥 Пригласите друга и получите 14 дней подписки бесплатно!",
        "referral": {
            "success": "🎉 Вы получили *+{days} дней* подписки за приглашение *{new_user}*!",
            "new_user_notification": "👋 Вы присоединились по реферальной ссылке! Ваш пробный период активирован.",
            "self_invite": "❌ Вы не можете пригласить самого себя!",
            "already_invited": "⚠️ Вы уже приглашали этого пользователя"
        }
    },
    "ar": {
        "start": "مرحبًا بك في بوت Wohnungsbot!",
        "trial": "تم تفعيل الفترة التجريبية المجانية حتى",
        "menu": ["🔎 تمكين البحث", "⛔ إيقاف البحث", "🏠 إعداد الفلاتر", "💳 الاشتراك", "ℹ️ اشتراكي",
                 "👥 دعوة الأصدقاء", "🆘 مساعدة"],
        "back_to_menu": "🔙 العودة إلى القائمة",
        "change_language": "🌐 تغيير اللغة",
        "help_button": "🆘 مساعدة",
        "help_text": "لأي استفسارات، يرجى التواصل مع {help_username}",
        "welcome_message": "👋 *مرحبًا بك في Wohnungsbot Bot!*\n\n"
                       "📢 لقد حصلت على *فترة تجريبية مجانية لمدة 7 أيام* – سارية حتى *{date}* \n\n"
                       "🏠 يساعدك Wohnungsbot في العثور على أحدث عروض الإيجار في ألمانيا.\n"
                       "🔔 نُرسل لك إشعارات فورية بالعروض التي تطابق فلاترك.\n\n"
                       "📍 حدد المدينة والسعر والمنطقة والمعلمات الأخرى بالانتقال إلى 🏠 *تعيين الفلاتر* في قائمة الأزرار.\n"
                       "📬 سيتم إرسال جميع الإعلانات هنا على Telegram.",
        "subscription": {
            "active": "📅 اشتراكك فعال حتى: *{date}* ",
            "expired": "❌ انتهت صلاحية اشتراكك. يمكنك تجديده عبر 💳 *الاشتراك*",
            "none": "❌ لا يوجد لديك اشتراك نشط.",
            "activated": "✅ تم تفعيل الاشتراك حتى *{date}*! شكرًا لك!",
            "will_expire_in_days": "⚠️ سينتهي اشتراكك خلال {days} يومًا.",
            "will_expire_tomorrow": "⚠️ سينتهي اشتراكك *غدًا*.",
            "expired_notice": "❌ انتهت صلاحية اشتراكك. يرجى التجديد عبر 💳 *الاشتراك*."
        },
        "webapp_error": "يرجى إعداد الفلاتر أولاً عبر 🏠 إعداد الفلاتر.",
        "invoice": {
            "title": "الاشتراك",
            "description": "سوف تحصل على تحديثات تلقائية للعروض لمدة 30 يومًا"
        },
        "filters": {
            "open": "📋 انقر على الزر أدناه لإعداد الفلاتر:",
            "saved": "✅ *تم حفظ الفلاتر!*\n💰 السعر: {min_price}€ – {max_price}€\n📏 المساحة: {min_size}م² – {max_size}م²\n🏷️ تبادل الشقق: {tauschwohnung}\n📄 مطلوب WBS: {wbs}\n🌐 المواقع: {websites}\n\n🔎 *البحث مفعل!* سيتم إرسال العروض الجديدة إليك فور توفرها.",
            "not_set": "غير محدد",
            "yes": "نعم",
            "no": "لا"
        },
        "search": {
            "started": "🔎 تم بدء البحث. ستتلقى العروض الجديدة.",
            "stopped": "⛔ تم إيقاف البحث. لن تتلقى أي عروض جديدة."
        },
        "open_webapp": "🏠 إعدادات الفلاتر",
        "data_error": "يرجى التحقق من الأرقام المدخلة.",
        "invite_friends_text": "👥 ادعُ صديقًا واحصل على اشتراك مجاني لمدة 14 يومًا!",
        "referral": {
            "success": "🎉 حصلت على *+{days} يومًا* من الاشتراك لدعوة *{new_user}*!",
            "new_user_notification": "👋 لقد انضممت عبر رابط الإحالة! تم تفعيل الفترة التجريبية الخاصة بك.",
            "self_invite": "❌ لا يمكنك دعوة نفسك!",
            "already_invited": "⚠️ لقد دعوت هذا المستخدم من قبل"
        }
    },
    "tr": {
        "start": "Wohnungsbot'a hoş geldiniz!",
        "trial": "Ücretsiz deneme süresi şu tarihe kadar aktif:",
        "menu": ["🔎 Aramayı Başlat", "⛔ Aramayı Durdur", "🏠 Filtreleri Ayarla", "💳 Abone Ol", "ℹ️ Aboneliğim",
                 "👥 Arkadaş Davet Et", "🆘 Yardım"],
        "back_to_menu": "🔙 Menüye Dön",
        "change_language": "🌐 Dili Değiştir",
        "help_button": "🆘 Yardım",
        "help_text": "Herhangi bir sorunuz için lütfen {help_username} ile iletişime geçin",
        "welcome_message": "👋 *Wohnungsbot'a Hoş Geldiniz!*\n\n"
                       "📢 *7 günlük ücretsiz deneme süresi* kazandınız – geçerlilik tarihi: *{date}* ({days} gün)\n\n"
                       "🏠 Wohnungsbot, Almanya'daki yeni kiralık ilanları ilk sizin görmenizi sağlar.\n"
                       "🔔 Filtrelerinize uyan ilanlar anında size bildirilir.\n\n"
                       "📍 Düğmeler menüsünden 🏠 *Filtreleri Ayarla* seçeneğine giderek şehir, fiyat, bölge ve diğer parametreleri belirleyin.\n"
                       "📬 Tüm ilanlar doğrudan Telegram'a gönderilecektir.",
        "subscription": {
            "active": "📅 Aboneliğinizin bitiş tarihi: *{date}* ",
            "expired": "❌ Aboneliğiniz *sona erdi*. 💳 *Abone Ol* ile yenileyebilirsiniz.",
            "none": "❌ Aktif bir aboneliğiniz yok.",
            "activated": "✅ Abonelik *{date}* tarihine kadar etkinleştirildi! Teşekkürler!",
            "will_expire_in_days": "⚠️ Aboneliğiniz {days} gün içinde sona erecek.",
            "will_expire_tomorrow": "⚠️ Aboneliğiniz *yarın* sona erecek.",
            "expired_notice": "❌ Aboneliğiniz sona erdi. Lütfen 💳 *Abone Ol* üzerinden yenileyin."
        },
        "webapp_error": "Lütfen önce 🏠 Filtreleri Ayarla üzerinden filtreleri ayarlayın.",
        "invoice": {
            "title": "Abonelik",
            "description": "30 gün boyunca otomatik ilan güncellemelerine erişim kazanırsınız"
        },
        "filters": {
            "open": "📋 Filtrelerinizi ayarlamak için aşağıdaki butona tıklayın:",
            "saved": "✅ *Filtre kaydedildi!*\n💰 Fiyat: {min_price}€ – {max_price}€\n📏 Büyüklük: {min_size}m² – {max_size}m²\n🏷️ Daire takası: {tauschwohnung}\n📄 WBS gerekli: {wbs}\n🌐 Web siteleri: {websites}\n\n🔎 *Arama açık!* Yeni ilanlar geldiğinde gönderilecektir.",
            "not_set": "ayarlanmadı",
            "yes": "Evet",
            "no": "Hayır"
        },
        "search": {
            "started": "🔎 Arama başlatıldı. Yeni ilanlar size gönderilecek.",
            "stopped": "⛔ Arama durduruldu. Artık ilan almayacaksınız."
        },
        "open_webapp": "🏠 Filtre Ayarlarını Aç",
        "data_error": "Lütfen sayıların doğruluğunu kontrol edin.",
        "invite_friends_text": "👥 Bir arkadaş davet et ve 14 gün ücretsiz abonelik kazan!",
        "referral": {
            "success": "🎉 *{new_user}* kişisini davet ettiğiniz için *+{days} gün* abonelik kazandınız!",
            "new_user_notification": "👋 Referans linkiyle katıldınız! Ücretsiz denemeniz etkinleştirildi.",
            "self_invite": "❌ Kendinizi davet edemezsiniz!",
            "already_invited": "⚠️ Bu kullanıcıyı zaten davet ettiniz"
        }
    }
}
