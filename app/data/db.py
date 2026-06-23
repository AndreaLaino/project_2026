from sqlmodel import create_engine, SQLModel, Session
from typing import Annotated
from fastapi import Depends
import os
from faker import Faker #WHAT WAS THAT
from app.config import config
from app.models.registration import Registration
from app.models.event import Event
from app.models.user import User


sqlite_file_name = config.root_dir / "data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def init_database() -> None:
    ds_exists = os.path.isfile(sqlite_file_name)
    SQLModel.metadata.create_all(engine)
    if not ds_exists:
        f = Faker("it_IT")
        with Session(engine) as session:
            events = []
            for i in range(10):
                event = Event(
                    title=f.sentence(nb_words=4)[:50],
                    description=f.text(max_nb_chars=300),
                    date=f.date_time_between(start_date="now", end_date="+1y"),
                    location=f.city(),
                )
                session.add(event)
                events.append(event)

            users = []
            for i in range(10):
                user = User(
                    username=f.unique.user_name()[:50],
                    name=f.name()[:50],
                    email=f.unique.email()[:100],
                )
                session.add(user)
                users.append(user)

            session.commit()

            for i in range(5):
                registration = Registration(
                    username=users[i].username,
                    event_id=events[i].id,
                )
                session.add(registration)

            session.commit()


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
