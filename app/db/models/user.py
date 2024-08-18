from sqlalchemy.orm import Mapped
from .. import Base



class Main(Base):
    __tablename__ = "users"

    username: Mapped[str]
    hero: Mapped[str] = None