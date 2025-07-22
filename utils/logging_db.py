import logging
from db.database import SessionLocal
from models.models import LogEntry


class DBLogHandler(logging.Handler):
    def emit(self, record):
        session = SessionLocal()
        try:
            log_entry = LogEntry(level=record.levelname, message=self.format(record))
            session.add(log_entry)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
