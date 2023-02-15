import copy
import telebot
from telebot import types
import config
from data import db_session
from data.Inner.PersonAPI import get_person_by_tel_id, create_person, put_self_person, get_nicknames_by_tel_ids, \
    get_list_person_admin, get_persons_with_lower_status, delete_person_admin, get_nickname_by_tel_id, put_person_admin
from data.Inner.QueueAPI import get_list_queue, create_queue, get_queue_by_name, admin_put_queue, put_queue, \
    get_users_from_queue, admin_put_user_queue
from data.Inner.SettingAPI import load_settings, get_settings, admin_put_settings
from data.Inner.main_file import unzip_spisok
from data.Inner.LogsAPI import get_logs_by_page, clear_logs


db_session.global_init("db/mydatabase.sqlite")

bot = telebot.TeleBot(config.token)

# buttons
back_btn = types.KeyboardButton("🔙 В главное меню")
admin_btn = types.KeyboardButton("🔑 Панель администратора")
help_btn = types.KeyboardButton("❓ Помощь")
queues_btn = types.KeyboardButton("🗂 Список очередей на лабы")
change_btn = types.KeyboardButton("🖍 Изменить информацию о себе")
reg_btn = types.KeyboardButton("📔 Зарегистрироваться")
setting_queue_btn = types.KeyboardButton("🪛 Настройка очередей")
create_queue_btn = types.KeyboardButton("➕ Создать очередь")
ready_btn = types.KeyboardButton("✅ Я готов сдавать")
not_ready_btn = types.KeyboardButton("❌ Я не готов сдавать")
sdal_btn = types.KeyboardButton("😎 Лабу сдал (или просто хочу в конец очереди)")
zapis_btn = types.KeyboardButton("✏️ записаться в очередь")
refresh_btn = types.KeyboardButton("♻️ Обновить список")
rename_btn = types.KeyboardButton("🖍 Переименоваться")
common_log_btn = types.KeyboardButton("📑 Общий список логов‍")
personal_log_btn = types.KeyboardButton("🕵️ Список логов определённого человека")
clear_btn = types.KeyboardButton("🗑 Очистить историю логов")
setting_btn = types.KeyboardButton("⚙️ Настройки")
prava1_btn = types.KeyboardButton("👮 Дать/забрать право на регистрацию")
prava2_btn = types.KeyboardButton("👮 Дать/забрать право на изменение информации")
dvigat_vverh_btn = types.KeyboardButton("⬆️ Подвинуть вверх")
dvigat_vniz_btn = types.KeyboardButton("⬇️️ Подвинуть вниз")
clear_user_btn = types.KeyboardButton("🗑 Удалить из очереди")
change_user_btn = types.KeyboardButton("🟢 Сменить пользователя")
delete_user_btn = types.KeyboardButton("🗑 Удалить пользователя")
change_user_info_btn = types.KeyboardButton("🖍 Изменить данные пользователя")
yes_btn = types.KeyboardButton("✅ Да")
no_btn = types.KeyboardButton("❌ Нет")
rename_other_btn = types.KeyboardButton("🖍 Переименовать")
give_admin_btn = types.KeyboardButton("💎 Дать админку")
pick_up_admin_btn = types.KeyboardButton("💩 Забрать админку")

# markups
base_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

main_menu_markup = copy.deepcopy(base_markup)
main_menu_markup.add(help_btn, queues_btn, rename_btn)

main_menu_admin_markup = copy.deepcopy(main_menu_markup)
main_menu_admin_markup.add(admin_btn)

back_to_menu_markup = copy.deepcopy(base_markup)
back_to_menu_markup.add(back_btn)

reg_markup = copy.deepcopy(base_markup)
reg_markup.add(reg_btn)

admin_panel_markup = copy.deepcopy(back_to_menu_markup)
admin_panel_markup.add(setting_queue_btn, setting_btn)

queue_menu_reg_markup = copy.deepcopy(back_to_menu_markup)
queue_menu_reg_markup.add(ready_btn, not_ready_btn, sdal_btn, refresh_btn)

queue_menu_unreg_markup = copy.deepcopy(back_to_menu_markup)
queue_menu_unreg_markup.add(zapis_btn)

log_menu_markup = copy.deepcopy(back_to_menu_markup)
log_menu_markup.add(common_log_btn, personal_log_btn, clear_btn)

settings_menu_markup = copy.deepcopy(back_to_menu_markup)
settings_menu_markup.add(prava1_btn, prava2_btn)

change_users_queue_markup = copy.deepcopy(back_to_menu_markup)
change_users_queue_markup.add(dvigat_vverh_btn, dvigat_vniz_btn, clear_user_btn, change_user_btn)

user_menu_markup = copy.deepcopy(back_to_menu_markup)
user_menu_markup.add(change_user_btn, change_user_info_btn, delete_user_btn)

yes_not_markup = copy.deepcopy(back_to_menu_markup)
yes_not_markup.add(yes_btn, no_btn)


def prepare_spisok(spisok):
    zameni = get_nicknames_by_tel_ids(list(spisok.keys()))
    res = [f"{zameni[key]} {spisok[key]}" for key in spisok.keys()]
    res.insert(0, "Список:")
    return "\n".join(res)


class Dialogs:
    def __init__(self):
        pass

    def base_check(self, message):
        if message.text == "🔙 В главное меню":
            self.return_to_main_menu(message)
            return True
        return False

    def return_to_main_menu(self, message, text="Возвращаю в главное меню"):
        bot.send_message(message.chat.id, text=text, reply_markup=(
            main_menu_admin_markup if get_person_by_tel_id(message.from_user.id)['person'][
                                          'status'] > 0 else main_menu_markup))


class AdminDialogs(Dialogs):
    def __init__(self):
        super().__init__()

    def menu_queue(self, message):
        if self.base_check(message):
            return

        markup = copy.deepcopy(back_to_menu_markup)
        person = get_person_by_tel_id(message.from_user.id)['person']

        if message.text == "➕ Создать очередь":
            bot.send_message(message.from_user.id, "Как назовём очередь?", reply_markup=markup)
            bot.register_next_step_handler(message, admin_dialogs.create_new_queue)

        elif message.text[:20] == "✏️ Изменить очередь:":
            name = message.text[21:]
            if "error" in get_queue_by_name(name):
                bot.send_message(message.from_user.id, f"Очередь с таким названием не найдена - {name}", reply_markup=markup)
            else:
                put_self_person(message.from_user.id, args={"last_queue_name": name})
                markup.add(types.KeyboardButton("🖋 название"), types.KeyboardButton("♻️ порядок очереди"))
                spisok = unzip_spisok(get_queue_by_name(person['last_queue_name'])["success"]["spisok"])
                bot.send_message(message.from_user.id, f"Что меняем в очереди {name}?\n{prepare_spisok(spisok)}", reply_markup=markup)
                bot.register_next_step_handler(message, admin_dialogs.edit_queue)

        else:
            self.return_to_main_menu(message, 'таких команд не знаю')

    def edit_queue(self, message):
        if self.base_check(message):
            return

        if message.text == "🖋 название":
            bot.send_message(message.from_user.id, "Как назовём?", reply_markup=back_to_menu_markup)
            bot.register_next_step_handler(message, admin_dialogs.rename_queue)

        elif message.text == "♻️ порядок очереди":
            markup = copy.deepcopy(back_to_menu_markup)
            for user in get_users_from_queue(message.from_user.id, get_person_by_tel_id(message.from_user.id)['person']['last_queue_name']):
                markup.add(types.KeyboardButton(f"Пользователь: {user[1]} &&0&& {user[0]}"))
            bot.send_message(message.from_user.id, "Кого будем настраивать?", reply_markup=markup)
            bot.register_next_step_handler(message, admin_dialogs.change_queue)

        else:
            self.return_to_main_menu(message, 'таких команд не знаю')

    def create_new_queue(self, message):
        if self.base_check(message):
            return

        create_queue(message.from_user.id, message.text)
        self.return_to_main_menu(message, "Прекрасное название, так и назовём")

    def rename_queue(self, message):
        if self.base_check(message):
            return

        admin_put_queue(message.from_user.id, get_person_by_tel_id(message.from_user.id)['person']['last_queue_name'], {"name": message.text})
        self.return_to_main_menu(message, "Прекрасное название, так и назовём")

    def change_queue(self, message):
        if self.base_check(message):
            return

        person = get_person_by_tel_id(message.from_user.id)['person']

        if message.text[:13] == "Пользователь:":
            put_self_person(message.from_user.id, args={"last_person_name": message.text.split(' &&0&& ')[-1]})
            spisok = unzip_spisok(get_queue_by_name(person['last_queue_name'])["success"]["spisok"])
            bot.send_message(message.from_user.id, f"Выбран пользователь - {message.text.split(' &&0&& ')[-1]}\n{prepare_spisok(spisok)}", reply_markup=change_users_queue_markup)
            bot.register_next_step_handler(message, admin_dialogs.change_queue)

        elif message.text == "⬆️ Подвинуть вверх":
            admin_put_user_queue(message.from_user.id, person['last_person_name'], get_queue_by_name(person['last_queue_name'])["success"]['name'], "вверх")
            spisok = unzip_spisok(get_queue_by_name(person['last_queue_name'])["success"]["spisok"])
            bot.send_message(message.from_user.id, f"Выбран пользователь - {message.text.split(' &&0&& ')[-1]}\n{prepare_spisok(spisok)}", reply_markup=change_users_queue_markup)
            bot.register_next_step_handler(message, admin_dialogs.change_queue)

        elif message.text == "⬇️️ Подвинуть вниз":
            admin_put_user_queue(message.from_user.id, person['last_person_name'], get_queue_by_name(person['last_queue_name'])["success"]['name'], "вниз")
            spisok = unzip_spisok(get_queue_by_name(person['last_queue_name'])["success"]["spisok"])
            bot.send_message(message.from_user.id, f"Выбран пользователь - {message.text.split(' &&0&& ')[-1]}\n{prepare_spisok(spisok)}", reply_markup=change_users_queue_markup)
            bot.register_next_step_handler(message, admin_dialogs.change_queue)

        elif message.text in ["🟢 Сменить пользователя", "🗑 Удалить из очереди"]:
            text = ""
            if message.text == "🗑 Удалить из очереди":
                admin_put_user_queue(message.from_user.id, person['last_person_name'], get_queue_by_name(person['last_queue_name'])["success"]['name'], "удалить")
                text = f"Пользователь {person['last_person_name']} удалён из очереди\n"

            put_self_person(message.from_user.id, args={"last_person_name": ""})
            markup = copy.deepcopy(back_to_menu_markup)
            for user in get_users_from_queue(message.from_user.id, get_person_by_tel_id(message.from_user.id)['person']['last_queue_name']):
                markup.add(types.KeyboardButton(f"Пользователь: {user[1]} &&0&& {user[0]}"))
            bot.register_next_step_handler(message, admin_dialogs.change_queue)
            bot.send_message(message.from_user.id, text+"Кого теперь будем настраивать?", reply_markup=markup)

        else:
            self.return_to_main_menu(message, "Такого не умею")

    def log_menu(self, message):
        if self.base_check(message):
            return

        person = get_person_by_tel_id(message.from_user.id)['person']

        if message.text == "📑 Общий список логов‍":
            logs = '\n'.join(get_logs_by_page(message.from_user.id, tel_id=person['last_person_name'])['success'])
            markup = copy.deepcopy(log_menu_markup)
            markup.add(types.KeyboardButton("Указать номер страницы"))
            bot.send_message(message.from_user.id, f"Список логов:\n{logs}", reply_markup=markup)
            bot.register_next_step_handler(message, admin_dialogs.log_menu)

        elif message.text == "🕵️ Список логов определённого человека":
            markup = copy.deepcopy(back_to_menu_markup)
            for person in get_list_person_admin(message.from_user.id):
                markup.add(types.KeyboardButton(f"Следим за: {person['nickname']} &&0&& {person['tel_id']}"))
            bot.send_message(message.from_user.id, f"За которым смотреть?", reply_markup=markup)
            bot.register_next_step_handler(message, admin_dialogs.log_menu)

        elif message.text == "Указать номер страницы":
            markup = copy.deepcopy(back_to_menu_markup)
            bot.send_message(message.from_user.id, f"На какой странице искать?", reply_markup=markup)
            bot.register_next_step_handler(message, admin_dialogs.pokazat_page)

        elif message.text[:10] == "Следим за:":
            markup = copy.deepcopy(log_menu_markup)
            markup.add(types.KeyboardButton("Указать номер страницы"))
            put_self_person(message.from_user.id, args={"last_person_name": message.text.split(' &&0&& ')[-1]})
            bot.send_message(message.from_user.id, f"Жертва зафиксирована", reply_markup=markup)
            bot.register_next_step_handler(message, admin_dialogs.log_menu)

        elif message.text == "🗑 Очистить историю логов":
            markup = copy.deepcopy(log_menu_markup)
            clear_logs(message.from_user.id)
            bot.send_message(message.from_user.id, f"История логов успешно очищена", reply_markup=markup)
            bot.register_next_step_handler(message, admin_dialogs.log_menu)

        else:
            self.return_to_main_menu(message, 'неизвестная команда')

    def pokazat_page(self, message):
        if self.base_check(message):
            return

        person = get_person_by_tel_id(message.from_user.id)['person']

        if message.text.isdigit():
            logs = '\n'.join(get_logs_by_page(message.from_user.id, int(message.text), tel_id=person['last_person_name'])['success'])
            markup = copy.deepcopy(log_menu_markup)
            markup.add(types.KeyboardButton("Указать номер страницы"))
            bot.send_message(message.from_user.id, f"Список логов:\n{logs}", reply_markup=markup)
            bot.register_next_step_handler(message, admin_dialogs.log_menu)

        else:
            self.return_to_main_menu(message, 'сюда надо писать чиселку!')

    def setting_menu(self, message):
        if self.base_check(message):
            return

        if message.text == "👮 Дать/забрать право на регистрацию":
            admin_put_settings(message.from_user.id, {"new_users_can_reg": not (load_settings()["success"]["new_users_can_reg"])})
            bot.send_message(message.from_user.id, f"{get_settings()['success']}", reply_markup=settings_menu_markup)
            bot.register_next_step_handler(message, admin_dialogs.setting_menu)

        elif message.text == "👮 Дать/забрать право на изменение информации":
            admin_put_settings(message.from_user.id, {"users_can_change_queue": not load_settings()["success"]["users_can_change_queue"]})
            bot.send_message(message.from_user.id, f"{get_settings()['success']}", reply_markup=settings_menu_markup)
            bot.register_next_step_handler(message, admin_dialogs.setting_menu)

        else:
            self.return_to_main_menu(message, "Неизвестная команда")

    def user_menu(self, message):
        if self.base_check(message):
            return

        person = get_person_by_tel_id(message.from_user.id)['person']

        if message.text[:13] == "Пользователь:":
            put_self_person(message.from_user.id, args={"last_person_name": message.text.split(' &&0&& ')[-1]})
            bot.send_message(message.from_user.id, f"Выбран пользователь - {message.text.split(' &&0&& ')[-1]}", reply_markup=user_menu_markup)
            bot.register_next_step_handler(message, admin_dialogs.user_menu)

        elif message.text == "🟢 Сменить пользователя":
            put_self_person(message.from_user.id, args={"last_person_name": ""})
            markup = copy.deepcopy(back_to_menu_markup)
            for user in get_persons_with_lower_status(message.from_user.id)['persons']:
                markup.add(f"Пользователь: {user['nickname']} &&0&& {user['tel_id']}")
            bot.register_next_step_handler(message, admin_dialogs.user_menu)
            bot.send_message(message.from_user.id, "Кого теперь будем настраивать?", reply_markup=markup)

        elif message.text == "🗑 Удалить пользователя":
            bot.register_next_step_handler(message, admin_dialogs.podtverjdenie)
            bot.send_message(message.from_user.id, f"Вы уверены, что хотите удалить {get_nickname_by_tel_id(person['last_person_name'])}", reply_markup=yes_not_markup)

        elif message.text == "🖍 Изменить данные пользователя":
            markup = copy.deepcopy(back_to_menu_markup)
            markup.add(rename_other_btn)
            if get_person_by_tel_id(person['last_person_name'])['person']['status'] > 0:
                markup.add(pick_up_admin_btn)
            else:
                markup.add(give_admin_btn)
            markup.add(change_user_btn)
            bot.register_next_step_handler(message, admin_dialogs.user_menu)
            bot.send_message(message.from_user.id, "Что с ним сделаем?", reply_markup=markup)

        elif message.text == "🖍 Переименовать":
            markup = copy.deepcopy(back_to_menu_markup)
            bot.register_next_step_handler(message, admin_dialogs.rename_user)
            bot.send_message(message.from_user.id, "Каково его новое имя?", reply_markup=markup)

        elif message.text == "💎 Дать админку":
            put_person_admin(message.from_user.id, person['last_person_name'], {"status": 1})
            bot.register_next_step_handler(message, admin_dialogs.user_menu)
            markup = copy.deepcopy(back_to_menu_markup)
            markup.add(rename_other_btn, pick_up_admin_btn, change_user_btn)
            bot.send_message(message.from_user.id, "Что дальше?", reply_markup=markup)

        elif message.text == "💩 Забрать админку":
            put_person_admin(message.from_user.id, person['last_person_name'], {"status": 0})
            bot.register_next_step_handler(message, admin_dialogs.user_menu)
            markup = copy.deepcopy(back_to_menu_markup)
            markup.add(rename_other_btn, give_admin_btn, change_user_btn)
            bot.send_message(message.from_user.id, "Что дальше?", reply_markup=markup)

        else:
            self.return_to_main_menu(message, "Неизвестная команда")

    def podtverjdenie(self, message):
        if self.base_check(message):
            return

        person = get_person_by_tel_id(message.from_user.id)['person']

        if message.text == "✅ Да":
            markup = copy.deepcopy(back_to_menu_markup)
            markup.add(change_user_btn)
            delete_person_admin(message.from_user.id, person['last_person_name'])
            bot.register_next_step_handler(message, admin_dialogs.user_menu)
            bot.send_message(message.from_user.id, f"Пользователь {person['last_person_name']} удалён", reply_markup=markup)
            put_self_person(message.from_user.id, args={"last_person_name": ""})

        elif message.text == "❌ Нет":
            markup = copy.deepcopy(back_to_menu_markup)
            markup.add(change_user_btn)
            bot.register_next_step_handler(message, admin_dialogs.user_menu)
            bot.send_message(message.from_user.id, f"Ну и ладно, в другой раз удалим", reply_markup=markup)
            put_self_person(message.from_user.id, args={"last_person_name": ""})

        else:
            self.return_to_main_menu(message, "Такой ответ не предусмотрен)")

    def rename_user(self, message):
        if self.base_check(message):
            return

        person = get_person_by_tel_id(message.from_user.id)['person']

        if len(message.text) <= 30:
            if "&&0&&" not in message.text:
                put_person_admin(message.from_user.id, person['last_person_name'], {"nickname": message.text})
                bot.send_message(message.from_user.id, f"Чужое имя изменено", reply_markup=user_menu_markup)
                bot.register_next_step_handler(message, admin_dialogs.user_menu)
            else:
                bot.send_message(message.from_user.id, f"Недопустимый набор символов в имени - &&0&&, повторите попытку", reply_markup=back_to_menu_markup)
                bot.register_next_step_handler(message, admin_dialogs.rename_user)
        else:
            bot.send_message(message.from_user.id, f"Слишком длинное имя (максимальная длинна 30 символов), повторите попытку", reply_markup=back_to_menu_markup)
            bot.register_next_step_handler(message, admin_dialogs.rename_user)


class BaseDialogs(Dialogs):
    def __init__(self):
        super().__init__()

    def menu_queue(self, message):
        if self.base_check(message):
            return

        if not load_settings()["success"]["users_can_change_queue"]:
            self.return_to_main_menu(message, "Извините, сейчас недоступно 🧸")
            return

        if message.text[:8] == "Очередь:":
            name = message.text[9:]
            queue = get_queue_by_name(name)
            if "error" in queue:
                self.return_to_main_menu(message, f"Очередь с таким названием не найдена - {name}")
            else:
                spisok = unzip_spisok(queue["success"]["spisok"])
                if str(message.from_user.id) in spisok:
                    markup = queue_menu_reg_markup
                else:
                    markup = queue_menu_unreg_markup
                put_self_person(message.from_user.id, args={"last_queue_name": name})
                bot.send_message(message.chat.id, text=prepare_spisok(spisok), reply_markup=markup)
                bot.register_next_step_handler(message, base_dialogs.do_something_queue)

        else:
            self.return_to_main_menu(message, 'таких команд не знаю')

    def do_something_queue(self, message):
        if self.base_check(message):
            return

        person = get_person_by_tel_id(message.from_user.id)['person']

        if message.text in ["✏️ записаться в очередь", "😎 Лабу сдал (или просто хочу в конец очереди)"]:
            put_queue(message.from_user.id, person['last_queue_name'], "записаться")
            spisok = unzip_spisok(get_queue_by_name(person['last_queue_name'])["success"]["spisok"])
            bot.send_message(message.chat.id, text=prepare_spisok(spisok), reply_markup=queue_menu_reg_markup)
            bot.register_next_step_handler(message, base_dialogs.do_something_queue)

        elif message.text == "✅ Я готов сдавать":
            put_queue(message.from_user.id, person['last_queue_name'], "я готов")
            spisok = unzip_spisok(get_queue_by_name(person['last_queue_name'])["success"]["spisok"])
            bot.send_message(message.chat.id, text=prepare_spisok(spisok), reply_markup=queue_menu_reg_markup)
            bot.register_next_step_handler(message, base_dialogs.do_something_queue)

        elif message.text == "❌ Я не готов сдавать":
            put_queue(message.from_user.id, person['last_queue_name'], "я не готов")
            spisok = unzip_spisok(get_queue_by_name(person['last_queue_name'])["success"]["spisok"])
            bot.send_message(message.chat.id, text=prepare_spisok(spisok), reply_markup=queue_menu_reg_markup)
            bot.register_next_step_handler(message, base_dialogs.do_something_queue)

        elif message.text == "♻️ Обновить список":
            spisok = unzip_spisok(get_queue_by_name(person['last_queue_name'])["success"]["spisok"])
            bot.send_message(message.chat.id, text=prepare_spisok(spisok), reply_markup=queue_menu_reg_markup)
            bot.register_next_step_handler(message, base_dialogs.do_something_queue)

        else:
            self.return_to_main_menu(message, 'таких команд не знаю')

    def change_self_nickname(self, message):
        if self.base_check(message):
            return

        if len(message.text) <= 30:
            if "&&0&&" not in message.text:
                put_self_person(message.from_user.id, {"nickname": message.text})
                self.return_to_main_menu(message, "Запомнил новое имя")
            else:
                self.return_to_main_menu(message, "Недопустимый набор символов в имени - &&0&&")
        else:
            self.return_to_main_menu(message, "Слишком длинное имя (максимальная длинна 30 символов)")


admin_dialogs = AdminDialogs()
base_dialogs = BaseDialogs()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text="Привет, {0.first_name}! Я теперь я буду надзирать за порядком в списке на лабесдание. Просьба не регистрировать фейковые аккаунты (будет применена высшая мера анальной кары)".format(message.from_user), reply_markup=reg_markup)


@bot.message_handler(content_types=['text'])
def func(message):
    result = get_person_by_tel_id(message.from_user.id)
    is_login = "success" in result
    if not is_login:
        if message.text == "📔 Зарегистрироваться":
            if load_settings()["success"]["new_users_can_reg"]:
                create_person({"tel_id": message.from_user.id, "nickname": message.from_user.username.replace("&&0&&", "бан")})
                bot.send_message(message.chat.id, text="Теперь ты зарегистрирован", reply_markup=back_to_menu_markup)
            else:
                bot.send_message(message.chat.id, text="Упс, похоже в данный момент регистрация закрыта", reply_markup=back_to_menu_markup)

        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            reg_btn = types.KeyboardButton("📔 Зарегистрироваться")
            markup.add(reg_btn)
            bot.send_message(message.chat.id, text="Я тебя не знаю", reply_markup=markup)

    else:
        status = result['person']['status']
        if message.text == "📔 Зарегистрироваться":
            bot.send_message(message.chat.id, text="Ты уже зарегистрирован", reply_markup=back_to_menu_markup)

        elif message.text == "❓ Помощь":
            bot.send_message(message.chat.id, text="Этот бот создан для избавления от предыдущего колхоза при записи на сдачу лаб. Интерфейс бота реализован через кнопочки и интуитивно понятен. Если что-то непонятно или обнаружен баг, то писать -> @niko_lausus", reply_markup=back_to_menu_markup)

        elif message.text == "🔙 В главное меню":
            markup = (main_menu_admin_markup if status > 0 else main_menu_markup)
            bot.send_message(message.chat.id, text="Вы в главном меню", reply_markup=markup)

        elif message.text == "🗂 Список очередей на лабы":
            markup = copy.deepcopy(back_to_menu_markup)
            for queue in get_list_queue():
                markup.add(types.KeyboardButton(f"Очередь: {queue['name']}"))
            bot.send_message(message.chat.id, text="Список очередей:", reply_markup=markup)
            bot.register_next_step_handler(message, base_dialogs.menu_queue)

        elif message.text == "🔑 Панель администратора" and status > 0:
            markup = copy.deepcopy(admin_panel_markup)
            if status > 1:
                markup.add(types.KeyboardButton("🗓 логи"))
                markup.add(types.KeyboardButton("👨‍👦‍👦 Настройка пользователей"))
            bot.send_message(message.chat.id, text="Добро пожаловать, мой лорд", reply_markup=markup)

        elif message.text == "🪛 Настройка очередей" and status > 0:
            markup = copy.deepcopy(back_to_menu_markup)
            markup.add(create_queue_btn)
            for queue in get_list_queue():
                markup.add(types.KeyboardButton(f"✏️ Изменить очередь: {queue['name']}"))
            bot.send_message(message.from_user.id, "Что будем делать?", reply_markup=markup)
            bot.register_next_step_handler(message, admin_dialogs.menu_queue)

        elif message.text == "🗓 логи" and status > 1:
            put_self_person(message.from_user.id, args={"last_person_name": ""})
            bot.send_message(message.from_user.id, "За кем шпионим?", reply_markup=log_menu_markup)
            bot.register_next_step_handler(message, admin_dialogs.log_menu)

        elif message.text == "🖍 Переименоваться":
            markup = copy.deepcopy(back_to_menu_markup)
            bot.send_message(message.from_user.id, "Как теперь зовут?", reply_markup=markup)
            bot.register_next_step_handler(message, base_dialogs.change_self_nickname)

        elif message.text == "⚙️ Настройки" and status > 0:
            bot.send_message(message.from_user.id, f"Поглядим, что там можно настроить\n{get_settings()['success']}", reply_markup=settings_menu_markup)
            bot.register_next_step_handler(message, admin_dialogs.setting_menu)

        elif message.text == "👨‍👦‍👦 Настройка пользователей" and status > 0:
            markup = copy.deepcopy(back_to_menu_markup)
            for user in get_persons_with_lower_status(message.from_user.id)["persons"]:
                markup.add(f"Пользователь: {user['nickname']} &&0&& {user['tel_id']}")
            bot.send_message(message.from_user.id, f"Кого редактируем?", reply_markup=markup)
            bot.register_next_step_handler(message, admin_dialogs.user_menu)

        else:
            base_dialogs.return_to_main_menu(message, "Такому меня не учили")


bot.polling(none_stop=True)