from typing import List

from sqlalchemy import create_engine, Column, Integer, String, DateTime, and_, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class ScreenShot(Base):
    __tablename__ = "screenshot"
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    path = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.now)


class DBData:
    def __init__(self, database_name:str):
        engine = create_engine(f"sqlite:///{database_name}", echo=False)
        Base.metadata.create_all(engine)
        self._Session = sessionmaker(bind=engine)
    
    def add(self, url:str, content:str, path:str):
        session = self._Session()
        query = session.query(ScreenShot).where(ScreenShot.url == url.lower())
        result = query.first()
        if not result:
            session.add(ScreenShot(url=url.lower(), content=content,path=path))
            session.commit()
            return None
        
        return result.id

    def get_all(self) -> List[ScreenShot]:
        session = self._Session()
        query = session.query(ScreenShot).all()
        session.close()
        return query

    def get_by_extension(self, extension):
        session = self._Session()
        filters = and_(ScreenShot.content != '', ScreenShot.url.like(f'%{extension}'), ScreenShot.content != '\n\t')
        query = session.query(ScreenShot).filter(filters ).all()
        session.close()
        return query

    def get_pages(self):
        rows = []
        session = self._Session()
        query = session.query(ScreenShot.url).all()
        for url in query:
            rows.append(url[0])
        
        session.close()
        return rows
    
    # def get(self):
    #     rows = []
    #     session = self._Session()
    #     query = session.query(ScreenShot).all()
    #     for url in query:
    #         rows.append(domain.domain)
        
    #     session.close()
    #     return rows


    # def add(self, item):
    #     session = self._Session()
    #     session.add(item)
    #     session.commit()
    #     #session.close()
    #     return item.id

    # def add_all(self, items):
    #     session = self._Session()
    #     session.add_all(items)
    #     session.commit()
    #     session.close()
    
    # def select_page(self, url:str):
    #     session = self._Session()
    #     query = session.query(Pages).where(Pages.url == url).all()
    #     #session.close()
    #     return query
    
    # def select_files(self, url:str):
    #     session = self._Session()
    #     query = session.query(Files).where(Files.url == url).all()
    #     #session.close()
    #     return query

    # def get_files(self):
    #     rows = []
    #     session = self._Session()
    #     query = session.query(Files.url).join(Metadata, Metadata.file_id == Files.id).where(Metadata.value != "").distinct()
    #     result = query.all()
    #     for item in result:
    #         rows.append(Files(url=item.url))

    #     session.close()
    #     return rows

    # def get_metadata_total(self, domain) -> int:
    #     session = self._Session()
    #     query = session.query(Metadata.id).join(Files, Files.id==Metadata.file_id).where(Files.domain == domain)
    #     total = query.count()
    #     session.close()
    #     return total

    
    # def get_metadata(self,domain, filters) -> MetadataItem:
    #     session = self._Session()
    #     conditions = [Metadata.key.like(f"%{k}") for k in filters]
    #     query = session.query(Metadata, Files.url).join(Files, Files.id == Metadata.file_id).where(
    #         or_(*conditions)).where(Metadata.value != "", Files.domain == domain).distinct()
        
    #     result = query.all()
    #     rows = []
    #     for v,u in result:
    #         rows.append(MetadataItem(key=v.key, id=v.id, url=u, value=v.value, created=v.created))
        
    #     return rows
    
    # def get_users(self):
    #     return self.get_metadata(['Author','author','user','User'])

    # def get_software(self, domain:str):
    