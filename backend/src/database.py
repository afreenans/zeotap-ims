from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite database
DATABASE_URL = "sqlite:///./ims.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Enable SQL logging for debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class WorkItem(Base):
    __tablename__ = "work_items"
    
    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(String, index=True)
    severity = Column(String)
    state = Column(String, default="OPEN")
    signal_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Create all tables"""
    print("📊 Initializing database...")
    Base.metadata.create_all(bind=engine)
    
    # Verify table created
    db = SessionLocal()
    try:
        count = db.query(WorkItem).count()
        print(f"✅ Database initialized! Current incidents: {count}")
    except Exception as e:
        print(f"⚠️ Database check error: {e}")
    finally:
        db.close()
