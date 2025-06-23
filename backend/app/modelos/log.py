from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from ..core.database import Base

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    acao = Column(String(100), nullable=False, index=True)
    usuario_email = Column(String(255), nullable=False, index=True)
    detalhes = Column(JSON, nullable=True)
    ip_origem = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now()) 