from sqlalchemy.orm import Mapped, mapped_column
from .. import Base



class Main(Base):
    __tablename__ = "users"

    username: Mapped[str]
    hero: Mapped[str] = None
    heal: Mapped[int] = mapped_column(default=0)