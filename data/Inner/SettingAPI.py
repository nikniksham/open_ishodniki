from data import db_session
from data.Inner.LogsAPI import create_log
from data.Inner.PersonAPI import get_nickname_by_tel_id
from data.Inner.main_file import check_person
from data.settings import Settings


def get_settings():
    session = db_session.create_session()
    data = session.query(Settings).get(1).__repr__()
    session.close()
    return {"success": data}


def load_settings():
    session = db_session.create_session()
    data = session.query(Settings).get(1).to_dict()
    session.close()
    return {"success": data}


def admin_put_settings(admin_tel_id, args):
    admin, session = check_person(admin_tel_id, need_status=1)
    if type(admin) is dict:
        return admin
    settings = session.query(Settings).get(1)
    settings_dict = settings.to_dict(only=("new_users_can_reg", "users_can_change_queue"))
    keys = list(filter(lambda key: args[key] is not None and key in settings_dict and args[key] != settings_dict[key], list(args.keys())))
    changed_information = []
    for key in keys:
        if key == 'new_users_can_reg':
            changed_information.append(f"{settings.new_users_can_reg} -> {args['new_users_can_reg']}")
            settings.new_users_can_reg = args["new_users_can_reg"]
        elif key == "users_can_change_queue":
            changed_information.append(f"{settings.users_can_change_queue} -> {args['users_can_change_queue']}")
            settings.users_can_change_queue = args['users_can_change_queue']
    session.commit()
    session.close()

    if len(changed_information):
        create_log(admin_tel_id, f"Админ {get_nickname_by_tel_id(admin_tel_id)} изменил настройки: {'; '.join(changed_information)}")

    return {"success": f"Настройки изменены"}
