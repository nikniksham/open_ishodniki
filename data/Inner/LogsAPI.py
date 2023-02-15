from data import db_session
from data.Inner.main_file import check_person
from data.logs import Logs
from sqlalchemy import and_


def get_logs_by_page(admin_tel_id, page_number=1, tel_id=None):
    admin, session = check_person(admin_tel_id, need_status=2)
    srez = 20
    if type(admin) is dict:
        return admin

    if tel_id and tel_id.isdigit():
        person, session = check_person(int(tel_id), session=session)
        if type(person) is dict:
            return person

    min_log = session.query(Logs).order_by(Logs.id).first()
    min_id = 0
    if min_log:
        min_id = session.query(Logs).order_by(Logs.id).first().id - 1
    count = session.query(Logs).count()
    max_page = count // srez + (1 if count % srez else 0)

    if page_number < 1:
        page_number = 1
    elif page_number > max_page:
        page_number = max_page

    min_border = (count - (min_id + srez * page_number))
    max_border = (count - (min_id + srez * (page_number - 1)))

    if tel_id:
        logs = session.query(Logs).filter(Logs.user_tel_id == tel_id).all()
        page_number -= 1
        per = min(len(logs), len(logs) - max(0, page_number) * srez)
        logs = logs[max(per - srez, 0):per]
    else:
        logs = session.query(Logs).filter(and_(Logs.id <= max_border, Logs.id >= min_border)).all()

    logs = logs[::-1]

    data = []
    for log in logs:
        data.append(log.__repr__())
    session.close()
    return {"success": data}


def clear_logs(admin_tel_id):
    admin, session = check_person(admin_tel_id, need_status=2)
    if type(admin) is dict:
        return admin
    session.query(Logs).delete()
    session.commit()
    session.close()
    return {"success": "история очищена"}


def create_log(tel_id, action):
    session = db_session.create_session()

    new_log = Logs()
    new_log.user_tel_id = tel_id
    new_log.action = action

    session.add(new_log)
    session.commit()
    session.close()

    return {"success": "Новый лог добавлен"}
