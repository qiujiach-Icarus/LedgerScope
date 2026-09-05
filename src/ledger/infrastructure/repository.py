from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from .models import Base, LedgerModel

class SQLRepository:
    def __init__(self, db_url: str = "sqlite:///data/audit_storage.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_dataframe(self, df: pd.DataFrame):
        """将 DataFrame 批量存入数据库"""
        session = self.Session()
        try:
            for _, row in df.iterrows():
                entry = LedgerModel(
                    voucher_id=str(row.get('voucher_id', '')),
                    date=row.get('date') if pd.notnull(row.get('date')) else None,
                    account=str(row.get('account', '')),
                    direction=str(row.get('direction', '')),
                    amount=float(row.get('amount', 0)),
                    direction_code=int(row.get('direction_code', 0)),
                    month=int(row.get('month', 0)),
                    day_of_week=int(row.get('day_of_week', 0)),
                    source_sheet=str(row.get('source_sheet', '')),
                    description=str(row.get('摘要', row.get('description', '')))
                )
                session.add(entry)
            session.commit()
            print(f"✅ 已成功将 {len(df)} 条记录存入数据库")
        except Exception as e:
            session.rollback()
            print(f"❌ 数据库存储失败: {str(e)}")
            raise e
        finally:
            session.close()
