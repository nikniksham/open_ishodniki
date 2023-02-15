from data import db_session
from data.person import Person
from data.Inner.main_file import raise_error, check_person, unzip_spisok, zip_spisok
from data.queue import Queue
from data.Inner.LogsAPI import create_log


def get_nicknames_by_tel_ids(tel_ids):
    session = db_session.create_session()
    spis = {}
    for tel_id in tel_ids:
        person = session.query(Person).filter(Person.tel_id == int(tel_id)).first()
        if person:
            spis[tel_id] = person.nickname
    session.close()
    return spis


def get_nickname_by_tel_id(tel_id):
    session = db_session.create_session()
    person = session.query(Person).filter(Person.tel_id == int(tel_id)).first()
    if not person:
        return raise_error("Пользователь не найден", session)
    name = person.nickname
    session.close()
    return name


def get_person_by_tel_id(tel_id):
    if tel_id is str and tel_id.isdigit():
        tel_id = int(tel_id)
    person, session = check_person(tel_id)
    if type(person) is dict:
        return person
    data = person.to_dict()
    session.close()
    return {"success": "есть такой", 'person': data}


def get_persons_with_lower_status(admin_tel_id):
    admin, session = check_person(admin_tel_id, need_status=1)
    if type(admin) is dict:
        return admin
    data = [per.to_dict() for per in session.query(Person).filter(Person.status < admin.status).all()]
    session.close()
    return {"success": "есть такой", 'persons': data}


def del_person_from_queue(person, queues):
    tel_id = str(person.tel_id)
    for queue in queues:
        spisok = unzip_spisok(queue.spisok)
        if tel_id in spisok:
            del spisok[tel_id]
        queue.spisok = zip_spisok(spisok)


def put_self_person(tel_id, args):
    person, session = check_person(tel_id)
    if type(person) is dict:
        return person
    person_dict = person.to_dict(only=('nickname', 'last_queue_name', 'last_person_name'))
    keys = list(filter(lambda key: args[key] is not None and key in person_dict and args[key] != person_dict[key], list(args.keys())))
    changed_information = []
    for key in keys:
        if key == 'nickname':
            changed_information.append(f"{person.nickname} -> {args['nickname']}")
            person.nickname = args["nickname"]
        if key == 'last_queue_name':
            person.last_queue_name = args["last_queue_name"]
        if key == 'last_person_name':
            person.last_person_name = args['last_person_name']
    session.commit()
    session.close()

    if len(changed_information):
        create_log(tel_id, f"Пользователь {get_nickname_by_tel_id(tel_id)} изменил информацию о себе: {'; '.join(changed_information)}")

    return {"success": f"Изменения сохранены"}


def create_person(args):
    session = db_session.create_session()

    if session.query(Person).filter(Person.tel_id == args['tel_id']).first():
        return raise_error("Уже зарегистрирован", session)[0]

    new_person = Person()
    new_person.nickname = args["nickname"]
    new_person.tel_id = args['tel_id']

    session.add(new_person)
    session.commit()
    session.close()

    create_log(args['tel_id'], f"Новый пользователь {args['nickname']} зарегистрировался")

    return {'success': f'Успешная регистрация'}


def delete_person(tel_id):
    person, session = check_person(tel_id)
    del_person_from_queue(person, session.query(Queue).all())
    session.delete(person)
    session.commit()
    session.close()

    create_log(tel_id, f"Пользователь {get_nickname_by_tel_id(tel_id)} удалил свой аккаунт")

    return {'success': f'Получается суицид иногда выход'}


def put_person_admin(admin_tel_id, tel_id, args):
    admin, session = check_person(admin_tel_id, 1)
    if type(admin) is dict:
        return admin

    person, session = check_person(tel_id, session=session)
    if type(person) is dict:
        return person

    person_dict = person.to_dict(only=('nickname', 'status'))
    keys = list(filter(lambda key: args[key] is not None and key in person_dict and args[key] != person_dict[key], list(args.keys())))
    changed_information = []
    for key in keys:
        if key == 'nickname':
            changed_information.append(f"{person.nickname} -> {args['nickname']}")
            person.nickname = args["nickname"]
        if key == 'status' and admin.status >= args['status']:
            changed_information.append(f"{person.status} -> {args['status']}")
            person.status = args['status']
    session.commit()
    session.close()

    if len(changed_information):
        create_log(admin_tel_id, f"Админ {get_nickname_by_tel_id(admin_tel_id)} изменил информацию о пользователе {tel_id}: {'; '.join(changed_information)}")

    return {"success": f"Токмо не шалить сверхнормы"}


def delete_person_admin(admin_tel_id, tel_id):
    admin, session = check_person(admin_tel_id, 1)
    if type(admin) is dict:
        return admin

    person, session = check_person(tel_id, session=session)
    if type(person) is dict:
        return person

    del_person_from_queue(person, session.query(Queue).all())

    session.delete(person)
    session.commit()
    session.close()

    create_log(admin_tel_id, f"Админ {get_nickname_by_tel_id(admin_tel_id)} удалил пользователя {tel_id}")

    return {'success': f'Туда его!'}


def get_list_person_admin(admin_tel_id):
    admin, session = check_person(admin_tel_id, 1)
    if type(admin) is dict:
        return admin
    persons = session.query(Person).all()
    data = [item.to_dict(only=('id', 'status', 'nickname', "tel_id")) for item in persons]
    session.close()
    return data
