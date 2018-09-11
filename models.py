import pandas as pd

from utils import serialise_matched_reference, serialise_reference
from settings import settings
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class Organisation(Base):
    __tablename__ = 'organisation'
    id = Column(Integer, primary_key=True)

    name = Column(String(64))


class Document(Base):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True)

    author = Column(String(256))
    issue = Column(String(256))
    journal = Column(String(256))
    volume = Column(String(256))
    pub_year = Column(Integer)
    pagination = Column(String(256))
    title = Column(String(1024))
    file_hash = Column(String(32))

    id_organisation = Column(Integer, ForeignKey('organisation.id'))
    organisation = relationship(Organisation)

    datetime_creation = Column(DateTime)
    datetime_update = Column(DateTime, default=datetime.now())


class Reference(Base):
    __tablename__ = 'reference'
    id = Column(Integer, primary_key=True)

    publication_id = Column(String(256))
    cosine_similarity = Column(String(256))

    id_document = Column(Integer, ForeignKey('document.id'))
    document = relationship(Document)

    datetime_creation = Column(DateTime)
    datetime_update = Column(DateTime, default=datetime.now())


class DatabaseEngine():
    def _get_session(self, url):
        engine = create_engine(url)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        return DBSession()

    def __init__(self):
        self.meta = Base.metadata
        self.session = self._get_session(settings.RDS_URL)

    def save_to_database(self, documents, references):
        doc_list = documents.where(
            (pd.notnull(documents)),
            None
        ).to_dict(orient='records')
        ref_list = references.where(
            (pd.notnull(references)),
            None
        ).to_dict(orient='records')
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        org = self.session.query(Organisation).filter(
            Organisation.name == settings.ORGANISATION
        ).first()

        if not org:
            org = Organisation(name=settings.ORGANISATION)
            self.session.add(org)
        for doc in doc_list:
            serial_doc = serialise_reference(doc, now)
            new_doc = self.session.query(Document).filter(
                Document.file_hash == serial_doc['file_hash']
                and Document.authors == serial_doc['author']
                and Document.title == serial_doc['title']
            ).first()
            if not new_doc:
                new_doc = Document(
                    author=serial_doc['author'],
                    issue=serial_doc['issue'],
                    journal=serial_doc['journal'],
                    volume=serial_doc['volume'],
                    pub_year=serial_doc['pub_year'],
                    pagination=serial_doc['pagination'],
                    title=serial_doc['title'],
                    file_hash=serial_doc['file_hash'],
                    datetime_creation=serial_doc['datetime_creation'],
                    organisation=org,
                )
                self.session.add(new_doc)
        self.session.commit()
        for ref in ref_list:
            serial_ref = serialise_matched_reference(ref, now)
            document = self.session.query(Document).filter(
                Document.file_hash == serial_ref['document_hash']
            ).first()
            new_ref = self.session.query(Reference).filter(
                Reference.publication_id == serial_ref['publication_id']
                and Reference.id_document == document.id
            ).first()
            if not new_ref:
                new_ref = Reference(
                    document=document,
                    publication_id=serial_ref['publication_id'],
                    cosine_similarity=serial_ref['cosine_similarity'],
                    datetime_creation=serial_ref['datetime_creation']
                )
                self.session.add(new_ref)
        self.session.commit()
