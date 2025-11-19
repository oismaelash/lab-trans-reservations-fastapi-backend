from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .services.database import Base


class Local(Base):
    __tablename__ = "locais"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    salas = relationship("Sala", back_populates="local", cascade="all, delete-orphan")


class Sala(Base):
    __tablename__ = "salas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    local_id = Column(Integer, ForeignKey("locais.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    capacidade = Column(Integer, nullable=True)
    recursos = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    local = relationship("Local", back_populates="salas")
    reservas = relationship("Reserva", back_populates="sala_obj")

    __table_args__ = (
        Index('idx_sala_local_nome', 'local_id', 'nome'),
    )


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    google_id = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    nome = Column(String(255), nullable=False)
    foto_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    participantes = relationship("Participante", back_populates="usuario")


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    local_id = Column(Integer, ForeignKey("locais.id"), nullable=False)
    sala_id = Column(Integer, ForeignKey("salas.id"), nullable=False)
    # Denormalized fields to facilitate queries and maintain compatibility
    local = Column(String(100), nullable=False)
    sala = Column(String(100), nullable=False)
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True), nullable=False)
    responsavel = Column(String(150), nullable=False)
    cafe = Column(Boolean, default=False, nullable=False)
    quantidade_cafe = Column(Integer, nullable=True)
    descricao = Column(Text, nullable=True)
    criado_por_email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    local_obj = relationship("Local", foreign_keys=[local_id])
    sala_obj = relationship("Sala", foreign_keys=[sala_id], back_populates="reservas")
    participantes = relationship("Participante", back_populates="reserva", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_reserva_sala_datas', 'sala', 'data_inicio', 'data_fim'),
    )


class Participante(Base):
    __tablename__ = "participantes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    nome_manual = Column(String(255), nullable=True)  # Name when there's no associated user
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    reserva = relationship("Reserva", back_populates="participantes")
    usuario = relationship("Usuario", back_populates="participantes")

    __table_args__ = (
        Index('idx_participante_reserva', 'reserva_id'),
        Index('idx_participante_usuario', 'usuario_id'),
    )