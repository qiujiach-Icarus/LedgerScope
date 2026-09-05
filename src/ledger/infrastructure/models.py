from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LedgerModel(Base):
    __tablename__ = 'ledger_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    voucher_id = Column(String(50), index=True)
    date = Column(DateTime, nullable=True)
    account = Column(String(100), index=True)
    direction = Column(String(10))
    amount = Column(Float)
    direction_code = Column(Integer)
    month = Column(Integer)
    day_of_week = Column(Integer)
    source_sheet = Column(String(100))
    description = Column(Text, nullable=True)
