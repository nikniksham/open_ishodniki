import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Settings(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'settings'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    new_users_can_reg = sqlalchemy.Column(sqlalchemy.Boolean)
    users_can_change_queue = sqlalchemy.Column(sqlalchemy.Boolean)

    def __repr__(self):
        return f'<Settings> настройки:\n' \
               f'Новые пользователи могут регистрироваться: {self.new_users_can_reg}\n' \
               f'Пользователи могут менять информацию в очередях: {self.users_can_change_queue}'
