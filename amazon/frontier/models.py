#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, SmallInteger, BigInteger
from sqlalchemy.ext.declarative import declarative_base

__author__ = "sunwei"

DeclarativeBase = declarative_base()

class SeedsModel(DeclarativeBase):
    __tablename__ = 'seeds'
    __table_args__ = (
        {
            'mysql_charset': 'utf8',
            'mysql_engine': 'InnoDB',
            'mysql_row_format': 'DYNAMIC',
        },
    )

    url = Column(String(250), primary_key=True, nullable=False)
    ref_no = Column(Integer, nullable=False)
    status = Column(SmallInteger, nullable=False)
    ts = Column(BigInteger, nullable=False)

    @classmethod
    def query(cls, session):
        return session.query(cls)

    def __repr__(self):
        return '<Seeds: %s, ref_no: %s, status: %s, ts: %s>' % (self.url, self.ref_no, self.status, self.ts)


class SimulateCartSeedsModel(DeclarativeBase):
    __tablename__ = 'seeds_simulatecart'
    __table_args__ = (
        {
            'mysql_charset': 'utf8',
            'mysql_engine': 'InnoDB',
            'mysql_row_format': 'DYNAMIC',
        },
    )

    url = Column(String(250), primary_key=True, nullable=False)
    ref_no = Column(Integer, nullable=False)
    status = Column(SmallInteger, nullable=False)
    asin = Column(String(20), nullable=False)
    ts = Column(BigInteger, nullable=False)

    @classmethod
    def query(cls, session):
        return session.query(cls)

    def __repr__(self):
        return '<SimulateCartSeedsModel, url: %s, ref_no: %s, status: %s, asin: %s, ts: %s' % \
               (self.url, self.ref_no, self.status, self.asin, self.ts)


class BSRSimulateCartSeedsModel(DeclarativeBase):
    __tablename__ = 'seeds_bsr_simulatecart'
    __table_args__ = (
        {
            'mysql_charset': 'utf8',
            'mysql_engine': 'InnoDB',
            'mysql_row_format': 'DYNAMIC',
        },
    )

    url = Column(String(250), primary_key=True, nullable=False)
    ref_no = Column(Integer, nullable=False)
    status = Column(SmallInteger, nullable=False)
    asin = Column(String(20), nullable=False)
    ts = Column(BigInteger, nullable=False)

    @classmethod
    def query(cls, session):
        return session.query(cls)

    def __repr__(self):
        return '<BSRSimulateCartSeedsModel, url: %s, ref_no: %s, status: %s, asin: %s, ts: %s' % \
               (self.url, self.ref_no, self.status, self.asin, self.ts)

class KeywordSeedsModel(DeclarativeBase):
    __tablename__ = 'seeds_keyword'
    __table_args__ = (
        {
            'mysql_charset': 'utf8',
            'mysql_engine': 'InnoDB',
            'mysql_row_format': 'DYNAMIC',
        },
    )

    id = Column(Integer, primary_key=True)
    url = Column(String(250), nullable=False)
    ref_no = Column(Integer, nullable=False)
    status = Column(SmallInteger, nullable=False)
    asin = Column(String(20), nullable=False)
    uuid = Column(String(50), nullable=False)
    keyword = Column(String(1024), nullable=False)
    ts = Column(BigInteger, nullable=False)

    @classmethod
    def query(cls, session):
        return session.query(cls)

    def __repr__(self):
        return f'url:{self.url}, asin:{self.asin}, status:{self.status}, ref_no:{self.ref_no}, uuid:{self.uuid}, ' \
               f'keyword:{self.keyword}, ts:{self.ts}'


class CompetingSeedsModel(DeclarativeBase):
    __tablename__ = 'seeds_competing'
    __table_args__ = (
        {
            'mysql_charset': 'utf8',
            'mysql_engine': 'InnoDB',
            'mysql_row_format': 'DYNAMIC',
        },
    )

    url = Column(String(250), nullable=False, primary_key=True)
    ref_no = Column(Integer, nullable=False)
    status = Column(SmallInteger, nullable=False)
    asin = Column(String(20), nullable=False)
    ts = Column(BigInteger, nullable=False)

    @classmethod
    def query(cls, session):
        return session.query(cls)

    def __repr__(self):
        return f'url:{self.url}, ref_no:{self.ref_no}, status:{self.status}, asin:{self.asin}, ts:{ts}'
