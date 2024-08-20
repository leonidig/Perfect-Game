from sqlalchemy.orm import Mapped, mapped_column
from .. import Base



class Main(Base):
    __tablename__ = "users"

    username: Mapped[str]
    hero: Mapped[str] = None
    heal: Mapped[int] = mapped_column(default=0)
    arrows: Mapped[int] = mapped_column(default=0)
    have_fight: Mapped[bool] = mapped_column(default=False)