from data import db_session
from data.person import Person


def raise_error(error, session=None):
    if session:
        session.close()
    return {"error": error}, 1


def check_person(tel_id, need_status=0, session=None):
    if not session:
        session = db_session.create_session()
    person = session.query(Person).filter(Person.tel_id == tel_id).first()
    if not person:
        return raise_error(f"Я вас не знаю", session)
    if person.status < need_status:
        return raise_error(f"Ты кто такой, чтобы это делать?", session)
    return person, session


def unzip_spisok(text):
    spisok = {}
    for el in text.split("&&"):
        if el:
            us, got = el.split("||")
            spisok[us] = got
    return spisok


def zip_spisok(spisok):
    return "&&".join([f"{key}||{spisok[key]}" for key in spisok.keys()])
