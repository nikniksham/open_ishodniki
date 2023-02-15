from data import db_session
from data.Inner.PersonAPI import get_nickname_by_tel_id, get_nicknames_by_tel_ids
from data.Inner.main_file import raise_error, check_person, zip_spisok, unzip_spisok
from data.queue import Queue
from data.Inner.LogsAPI import create_log


def find_by_name(name, session):
    queue = session.query(Queue).filter(Queue.name == name).first()
    if not queue:
        return raise_error(f"Такая очередь не найдена", session)
    return queue, session


def get_queue_by_name(name):
    queue, session = find_by_name(name, db_session.create_session())
    if type(queue) is dict:
        return queue
    data = queue.to_dict()
    session.close()
    return {"success": data}


def get_list_queue():
    session = db_session.create_session()
    queues = session.query(Queue).all()
    data = [item.to_dict(only=("name",)) for item in queues]
    session.close()
    return data


def get_users_from_queue(admin_tel_id, name):
    admin, session = check_person(admin_tel_id, need_status=1)
    if type(admin) is dict:
        return admin
    queue, session = find_by_name(name, session)
    if type(queue) is dict:
        return queue

    spisok = list(unzip_spisok(queue.spisok).keys())
    names = get_nicknames_by_tel_ids(spisok)

    return [[key, names[key]] for key in spisok]


def admin_put_queue(admin_tel_id, name, args):
    admin, session = check_person(admin_tel_id, need_status=1)
    if type(admin) is dict:
        return admin
    queue, session = find_by_name(name, session)
    if type(queue) is dict:
        return queue
    queue_dict = queue.to_dict(only=("name",))
    keys = list(filter(lambda key: args[key] is not None and key in queue_dict and args[key] != queue_dict[key], list(args.keys())))
    changed_information = []
    for key in keys:
        if key == 'name':
            if not session.query(Queue).filter(Queue.name == args['name']).first():
                changed_information.append(f"{queue.name} -> {args['name']}")
                queue.name = args["name"]
            else:
                return raise_error("Название уже занято", session)[0]
    session.commit()
    session.close()

    if len(changed_information):
        create_log(admin_tel_id, f"Админ {get_nickname_by_tel_id(admin_tel_id)} изменил информацию об очереди {'; '.join(changed_information)}")

    return {"success": f"Изменения сохранены"}


def admin_put_user_queue(admin_tel_id, tel_id, name, action):
    admin, session = check_person(admin_tel_id, 1)
    if type(admin) is dict:
        return admin

    person = check_person(tel_id, session=session)
    if type(person) is dict:
        return person

    queue, session = find_by_name(name, session)
    if type(queue) is dict:
        return queue

    spisok_users = unzip_spisok(queue.spisok)
    spis = list(spisok_users.keys())

    if action == "вверх":
        ind = max(spis.index(tel_id) - 1, 0)
        spis.remove(tel_id)
        spis.insert(ind, tel_id)

    elif action == "вниз":
        ind = min(spis.index(tel_id) + 1, len(spis))
        spis.remove(tel_id)
        spis.insert(ind, tel_id)

    elif action == "удалить":
        spis.remove(tel_id)

    new_spisok_users = {}
    for el in spis:
        new_spisok_users[el] = spisok_users[el]

    queue.spisok = zip_spisok(new_spisok_users)

    session.commit()
    session.close()

    create_log(admin_tel_id, f"Админ {get_nickname_by_tel_id(admin_tel_id)} изменил {get_nickname_by_tel_id(tel_id)} в очереди {name} -> {action}")

    return {"success": "Шалость удалась"}


def put_queue(tel_id, name, action):
    person, session = check_person(tel_id)
    if type(person) is dict:
        return person
    queue, session = find_by_name(name, session)
    if type(queue) is dict:
        return queue

    tel_id = str(person.tel_id)
    spisok = unzip_spisok(queue.spisok)

    if action in ["записаться", 'лабу сдал']:
        if tel_id in spisok:
            del spisok[tel_id]
        spisok[tel_id] = "❌"

    if action == "я готов":
        if tel_id in spisok:
            spisok[tel_id] = "✅"
        else:
            return raise_error("Сначала надо встать в очередь", session)

    if action == "я не готов":
        if tel_id in spisok:
            spisok[tel_id] = "❌"
        else:
            return raise_error("Сначала надо встать в очередь", session)

    queue.spisok = zip_spisok(spisok)
    session.commit()
    session.close()

    create_log(tel_id, f"пользователь {get_nickname_by_tel_id(tel_id)} изменил информацию о себе в очереди {name} -> {action}")

    return {"success": f"Информация сохранена"}


def admin_delete_queue(admin_tel_id, name):
    admin, session = check_person(admin_tel_id, need_status=1)
    if type(admin) is dict:
        return admin
    queue, session = find_by_name(name, session)
    if type(queue) is dict:
        return queue
    session.delete(queue)
    session.commit()
    session.close()

    create_log(admin_tel_id, f"Админ {get_nickname_by_tel_id(admin_tel_id)} удалил очередь {name}")

    return {'success': f'Очередь под нож'}


def create_queue(admin_tel_id, name):
    admin, session = check_person(admin_tel_id, need_status=1)
    if type(admin) is dict:
        return admin

    if session.query(Queue).filter(Queue.name == name).first():
        return raise_error("Имя уже занято", session)

    session = db_session.create_session()
    new_queue = Queue()
    new_queue.name = name
    new_queue.spisok = ""
    session.add(new_queue)
    session.commit()
    session.close()

    create_log(admin_tel_id, f"Админ {get_nickname_by_tel_id(admin_tel_id)} создал очередь {name}")

    return {'success': f'Очередь создана'}
