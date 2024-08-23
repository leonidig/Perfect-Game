from sqlalchemy.orm import Mapped, mapped_column
from .. import Base



class Main(Base):
    __tablename__ = "users"

    username: Mapped[str]
    hero: Mapped[str] = None
    hp: Mapped[int] = mapped_column(default=0)
    heal: Mapped[int] = mapped_column(default=0)
    arrows: Mapped[int] = mapped_column(default=0)
    have_fight: Mapped[bool] = mapped_column(default=False)
    coins: Mapped[int] = mapped_column(default=0)
    guild: Mapped[str] = mapped_column(default="NOTHING")
    slot: Mapped[str] = mapped_column(default="")
    сorrect_answers: Mapped[int] = mapped_column(default=0)