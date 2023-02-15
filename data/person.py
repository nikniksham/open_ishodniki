import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Person(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'person'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    tel_id = sqlalchemy.Column(sqlalchemy.Integer)
    status = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    nickname = sqlalchemy.Column(sqlalchemy.String)
    last_queue_name = sqlalchemy.Column(sqlalchemy.String)
    last_person_name = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f'<Person> {self.id} юзер {self.fullname}'
