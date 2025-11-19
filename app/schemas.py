from pydantic import BaseModel, model_validator, Field
from datetime import datetime
from typing import Optional


# Standard Error Schemas
class ErrorDetail(BaseModel):
    message: str
    code: str
    details: Optional[dict] = None


# Location Schemas
class LocalBase(BaseModel):
    nome: str = Field(..., max_length=100)
    descricao: Optional[str] = Field(None, max_length=1000)


class LocalCreate(LocalBase):
    pass


class LocalUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    descricao: Optional[str] = Field(None, max_length=1000)
    ativo: Optional[bool] = None


class LocalOut(LocalBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Room Schemas
class SalaBase(BaseModel):
    local_id: int
    nome: str = Field(..., max_length=100)
    capacidade: Optional[int] = Field(None, gt=0)
    recursos: Optional[str] = Field(None, max_length=500)


class SalaCreate(SalaBase):
    pass


class SalaUpdate(BaseModel):
    local_id: Optional[int] = None
    nome: Optional[str] = Field(None, max_length=100)
    capacidade: Optional[int] = Field(None, gt=0)
    recursos: Optional[str] = Field(None, max_length=500)
    ativo: Optional[bool] = None


class SalaOut(SalaBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Reservation Schemas
class ReservaBase(BaseModel):
    local_id: int
    sala_id: int
    local: str = Field(..., max_length=100)
    sala: str = Field(..., max_length=100)
    data_inicio: datetime
    data_fim: datetime
    responsavel: str = Field(..., max_length=150)
    cafe: bool = False
    quantidade_cafe: Optional[int] = Field(None, ge=1)
    descricao: Optional[str] = Field(None, max_length=1000)

    @model_validator(mode='after')
    def validate_dates(self):
        if self.data_fim <= self.data_inicio:
            raise ValueError("data_fim deve ser posterior a data_inicio")
        return self

    @model_validator(mode='after')
    def validate_coffee(self):
        if self.cafe is True:
            if self.quantidade_cafe is None or self.quantidade_cafe <= 0:
                raise ValueError("quantidade_cafe é obrigatório e deve ser maior que 0 quando cafe = true")
        elif self.cafe is False:
            # If coffee is false, ignore quantidade_cafe
            self.quantidade_cafe = None
        return self


class ReservaCreate(ReservaBase):
    pass


class ReservaUpdate(BaseModel):
    local_id: Optional[int] = None
    sala_id: Optional[int] = None
    local: Optional[str] = Field(None, max_length=100)
    sala: Optional[str] = Field(None, max_length=100)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    responsavel: Optional[str] = Field(None, max_length=150)
    cafe: Optional[bool] = None
    quantidade_cafe: Optional[int] = Field(None, ge=1)
    descricao: Optional[str] = Field(None, max_length=1000)

    @model_validator(mode='after')
    def validate_dates(self):
        if self.data_inicio and self.data_fim:
            if self.data_fim <= self.data_inicio:
                raise ValueError("data_fim deve ser posterior a data_inicio")
        return self

    @model_validator(mode='after')
    def validate_coffee(self):
        if self.cafe is True:
            if self.quantidade_cafe is None or self.quantidade_cafe <= 0:
                raise ValueError("quantidade_cafe é obrigatório e deve ser maior que 0 quando cafe = true")
        return self


class ReservaOut(ReservaBase):
    id: int
    criado_por_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Pagination Schema
class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    pages: int


# User Schemas
class UsuarioBase(BaseModel):
    google_id: str = Field(..., max_length=255)
    email: str = Field(..., max_length=255)
    nome: str = Field(..., max_length=255)
    foto_url: Optional[str] = Field(None, max_length=500)


class UsuarioCreate(UsuarioBase):
    pass


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    foto_url: Optional[str] = Field(None, max_length=500)


class UsuarioOut(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Participant Schemas
class ParticipanteBase(BaseModel):
    reserva_id: int
    usuario_id: Optional[int] = None
    nome_manual: Optional[str] = Field(None, max_length=255)

    @model_validator(mode='after')
    def validate_participante(self):
        """Validates that either usuario_id or nome_manual must be provided."""
        if not self.usuario_id and not self.nome_manual:
            raise ValueError("É necessário fornecer usuario_id ou nome_manual")
        if self.usuario_id and self.nome_manual:
            raise ValueError("Não é possível fornecer usuario_id e nome_manual simultaneamente")
        return self


class ParticipanteCreate(ParticipanteBase):
    pass


class ParticipanteOut(BaseModel):
    id: int
    reserva_id: int
    usuario_id: Optional[int] = None
    nome_manual: Optional[str] = None
    created_at: datetime
    usuario: Optional[UsuarioOut] = None

    class Config:
        from_attributes = True


# Authentication Schemas
class GoogleTokenRequest(BaseModel):
    token: str = Field(..., description="JWT token from Google Identity Services")


class AuthResponse(BaseModel):
    token: str = Field(..., description="System JWT token")
    user: dict = Field(..., description="Authenticated user data")