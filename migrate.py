from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import Column, Integer, String, create_engine


PG_DSN = 'postgresql://postgres:postgres@127.0.0.1:5432/swapi'
engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class People(Base):
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    birth_year = Column(String(20), nullable=False)
    eye_color = Column(String(20), nullable=False)
    films = Column(String)
    gender = Column(String(20), nullable=False)
    hair_color = Column(String(20), nullable=False)
    height = Column(String(20), nullable=False)
    homeworld = Column(String(100), nullable=False)
    mass = Column(String(20), nullable=False)
    skin_color = Column(String(20), nullable=False)
    species = Column(String, nullable=False)
    starships = Column(String, nullable=False)
    vehicles = Column(String, nullable=False)


def main():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()
