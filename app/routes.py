from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta
import os
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests

from . import crud, schemas, models
from .services.database import get_db
from .services.auth import get_current_user_email

router = APIRouter()


# ========== Location Endpoints ==========

@router.post("/v1/locais", response_model=schemas.LocalOut, status_code=201)
def create_local(local: schemas.LocalCreate, db: Session = Depends(get_db)):
    """Creates a new location."""
    try:
        return crud.create_local(db=db, local=local)
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=409, detail="Já existe um local com este nome")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/v1/locais", response_model=List[schemas.LocalOut])
def list_locais(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    ativo: Optional[bool] = Query(None, description="Filter by active/inactive status"),
    db: Session = Depends(get_db)
):
    """Lists locations with optional filters."""
    return crud.list_locais(db=db, skip=skip, limit=limit, ativo=ativo)


@router.get("/v1/locais/{local_id}", response_model=schemas.LocalOut)
def get_local(local_id: int, db: Session = Depends(get_db)):
    """Gets a location by ID."""
    local = crud.get_local_by_id(db, local_id=local_id)
    if local is None:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return local


@router.put("/v1/locais/{local_id}", response_model=schemas.LocalOut)
def update_local(local_id: int, local_update: schemas.LocalUpdate, db: Session = Depends(get_db)):
    """Updates a location."""
    try:
        local = crud.update_local(db, local_id=local_id, local_update=local_update)
        if local is None:
            raise HTTPException(status_code=404, detail="Local não encontrado")
        return local
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=409, detail="Já existe um local com este nome")
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/v1/locais/{local_id}", response_model=schemas.LocalOut)
def partial_update_local(local_id: int, local_update: schemas.LocalUpdate, db: Session = Depends(get_db)):
    """Partially updates a location."""
    try:
        local = crud.update_local(db, local_id=local_id, local_update=local_update)
        if local is None:
            raise HTTPException(status_code=404, detail="Local não encontrado")
        return local
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=409, detail="Já existe um local com este nome")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/v1/locais/{local_id}", status_code=200)
def delete_local(local_id: int, db: Session = Depends(get_db)):
    """Deletes a location (soft delete)."""
    success = crud.delete_local(db, local_id=local_id)
    if not success:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return {"message": "Local excluído com sucesso"}


# ========== Room Endpoints ==========

@router.post("/v1/salas", response_model=schemas.SalaOut, status_code=201)
def create_sala(sala: schemas.SalaCreate, db: Session = Depends(get_db)):
    """Creates a new room."""
    try:
        return crud.create_sala(db=db, sala=sala)
    except ValueError as e:
        if "não encontrado" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        if "já existe" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/v1/salas", response_model=List[schemas.SalaOut])
def list_salas(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    local_id: Optional[int] = Query(None, description="Filter by location ID"),
    ativo: Optional[bool] = Query(None, description="Filter by active/inactive status"),
    capacidade_minima: Optional[int] = Query(None, ge=1, description="Filter by minimum capacity"),
    db: Session = Depends(get_db)
):
    """Lists rooms with optional filters."""
    return crud.list_salas(
        db=db,
        skip=skip,
        limit=limit,
        local_id=local_id,
        ativo=ativo,
        capacidade_minima=capacidade_minima
    )


@router.get("/v1/salas/{sala_id}", response_model=schemas.SalaOut)
def get_sala(sala_id: int, db: Session = Depends(get_db)):
    """Gets a room by ID."""
    sala = crud.get_sala_by_id(db, sala_id=sala_id)
    if sala is None:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    return sala


@router.put("/v1/salas/{sala_id}", response_model=schemas.SalaOut)
def update_sala(sala_id: int, sala_update: schemas.SalaUpdate, db: Session = Depends(get_db)):
    """Updates a room."""
    try:
        sala = crud.update_sala(db, sala_id=sala_id, sala_update=sala_update)
        if sala is None:
            raise HTTPException(status_code=404, detail="Sala não encontrada")
        return sala
    except ValueError as e:
        if "não encontrado" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        if "já existe" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/v1/salas/{sala_id}", response_model=schemas.SalaOut)
def partial_update_sala(sala_id: int, sala_update: schemas.SalaUpdate, db: Session = Depends(get_db)):
    """Partially updates a room."""
    try:
        sala = crud.update_sala(db, sala_id=sala_id, sala_update=sala_update)
        if sala is None:
            raise HTTPException(status_code=404, detail="Sala não encontrada")
        return sala
    except ValueError as e:
        if "não encontrado" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        if "já existe" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/v1/salas/{sala_id}", status_code=200)
def delete_sala(sala_id: int, db: Session = Depends(get_db)):
    """Deletes a room (soft delete)."""
    success = crud.delete_sala(db, sala_id=sala_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
    return {"message": "Sala excluída com sucesso"}


# ========== Reservation Endpoints ==========

@router.post("/v1/reservas", response_model=schemas.ReservaOut, status_code=201)
def create_reserva(
    reserva: schemas.ReservaCreate, 
    db: Session = Depends(get_db),
    usuario_email: str = Depends(get_current_user_email)
):
    """Creates a new reservation."""
    try:
        return crud.create_reserva(db=db, reserva=reserva, criado_por_email=usuario_email)
    except ValueError as e:
        error_msg = str(e).lower()
        if "conflito" in error_msg:
            raise HTTPException(status_code=409, detail=str(e))
        if "não encontrado" in error_msg or "inativo" in error_msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/v1/reservas", response_model=List[schemas.ReservaOut])
def list_reservas(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    data_inicio: Optional[datetime] = Query(None, description="Start date/time of interval (ISO 8601)"),
    data_fim: Optional[datetime] = Query(None, description="End date/time of interval (ISO 8601)"),
    sala: Optional[str] = Query(None, description="Filter by room name"),
    local: Optional[str] = Query(None, description="Filter by location name"),
    responsavel: Optional[str] = Query(None, description="Filter by responsible person"),
    db: Session = Depends(get_db)
):
    """
    Lists reservations with optional filters.
    If data_inicio and data_fim are provided, validates that data_inicio <= data_fim.
    """
    try:
        return crud.list_reservas(
            db=db,
            skip=skip,
            limit=limit,
            data_inicio=data_inicio,
            data_fim=data_fim,
            sala=sala,
            local=local,
            responsavel=responsavel
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/v1/reservas/{reserva_id}", response_model=schemas.ReservaOut)
def get_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """Gets a reservation by ID."""
    reserva = crud.get_reserva_by_id(db, reserva_id=reserva_id)
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return reserva


@router.put("/v1/reservas/{reserva_id}", response_model=schemas.ReservaOut)
def update_reserva(
    reserva_id: int, 
    reserva_update: schemas.ReservaUpdate, 
    db: Session = Depends(get_db),
    usuario_email: str = Depends(get_current_user_email)
):
    """Updates a reservation."""
    try:
        updated_reserva = crud.update_reserva(db, reserva_id=reserva_id, reserva_update=reserva_update, usuario_email=usuario_email)
        if updated_reserva is None:
            raise HTTPException(status_code=404, detail="Reserva não encontrada")
        return updated_reserva
    except ValueError as e:
        error_msg = str(e).lower()
        if "permissão" in error_msg:
            raise HTTPException(status_code=403, detail=str(e))
        if "conflito" in error_msg:
            raise HTTPException(status_code=409, detail=str(e))
        if "não encontrado" in error_msg or "inativo" in error_msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/v1/reservas/{reserva_id}", response_model=schemas.ReservaOut)
def partial_update_reserva(
    reserva_id: int, 
    reserva_update: schemas.ReservaUpdate, 
    db: Session = Depends(get_db),
    usuario_email: str = Depends(get_current_user_email)
):
    """Partially updates a reservation."""
    try:
        updated_reserva = crud.update_reserva(db, reserva_id=reserva_id, reserva_update=reserva_update, usuario_email=usuario_email)
        if updated_reserva is None:
            raise HTTPException(status_code=404, detail="Reserva não encontrada")
        return updated_reserva
    except ValueError as e:
        error_msg = str(e).lower()
        if "permissão" in error_msg:
            raise HTTPException(status_code=403, detail=str(e))
        if "conflito" in error_msg:
            raise HTTPException(status_code=409, detail=str(e))
        if "não encontrado" in error_msg or "inativo" in error_msg:
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/v1/reservas/{reserva_id}", status_code=200)
def delete_reserva(
    reserva_id: int, 
    db: Session = Depends(get_db),
    usuario_email: str = Depends(get_current_user_email)
):
    """Deletes a reservation (soft delete)."""
    try:
        success = crud.delete_reserva(db, reserva_id=reserva_id, usuario_email=usuario_email)
        if not success:
            raise HTTPException(status_code=404, detail="Reserva não encontrada")
        return {"message": "Reserva excluída com sucesso"}
    except ValueError as e:
        error_msg = str(e).lower()
        if "permissão" in error_msg:
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== Authentication Endpoints ==========

@router.post("/v1/auth/google", response_model=schemas.AuthResponse, status_code=200)
def login_with_google(request: schemas.GoogleTokenRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user using Google Identity Services token.
    
    Validates the Google JWT token, creates/updates the user in the database and returns a system token.
    """
    try:
        # Get Google Client ID from environment variables
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not google_client_id:
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_CLIENT_ID não configurado no servidor"
            )
        
        # Validate Google token
        try:
            idinfo = id_token.verify_oauth2_token(
                request.token,
                requests.Request(),
                google_client_id
            )
        except ValueError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Token do Google inválido: {str(e)}"
            )
        
        # Extract user information
        user_email = idinfo.get('email')
        user_name = idinfo.get('name', '')
        user_id = idinfo.get('sub', '')
        picture = idinfo.get('picture', '')
        
        if not user_email:
            raise HTTPException(
                status_code=400,
                detail="Email não encontrado no token do Google"
            )
        
        # Create or update user in database
        usuario = crud.get_or_create_usuario(
            db=db,
            google_id=user_id,
            email=user_email,
            nome=user_name,
            foto_url=picture if picture else None
        )
        
        # Generate system JWT token
        secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        token_expiry = datetime.utcnow() + timedelta(days=7)
        
        jwt_payload = {
            "sub": user_id,
            "email": user_email,
            "name": user_name,
            "exp": token_expiry
        }
        
        jwt_token = jwt.encode(jwt_payload, secret_key, algorithm="HS256")
        
        return {
            "token": jwt_token,
            "user": {
                "id": str(usuario.id),
                "email": user_email,
                "name": user_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar autenticação: {str(e)}"
        )


# ========== User Endpoints ==========

# IMPORTANT: More specific routes must come before routes with parameters
@router.get("/v1/usuarios/search", response_model=List[schemas.UsuarioOut])
def search_usuarios(
    q: str = Query(..., min_length=1, description="Search term (name or email)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Searches users by name or email (for form selection)."""
    return crud.list_usuarios(db=db, skip=0, limit=limit, search=q)


@router.get("/v1/usuarios", response_model=List[schemas.UsuarioOut])
def list_usuarios(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
    usuario_email: str = Depends(get_current_user_email)
):
    """
    Lists registered users (admin only).
    """
    # Check if user is admin (can be implemented with email verification in environment variable)
    admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")
    admin_emails = [e.strip().lower() for e in admin_emails if e.strip()]
    
    if usuario_email.lower() not in admin_emails:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem listar usuários.")
    
    return crud.list_usuarios(db=db, skip=skip, limit=limit, search=search)


@router.get("/v1/usuarios/{usuario_id}", response_model=schemas.UsuarioOut)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Gets a user by ID."""
    usuario = crud.get_usuario_by_id(db, usuario_id=usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


# ========== Participant Endpoints ==========

@router.post("/v1/participantes", response_model=schemas.ParticipanteOut, status_code=201)
def create_participante(
    participante: schemas.ParticipanteCreate,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(get_current_user_email)
):
    """Adds a participant to a reservation."""
    try:
        # Check if user has permission (is the reservation creator)
        reserva = crud.get_reserva_by_id(db, participante.reserva_id)
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva não encontrada")
        
        if reserva.criado_por_email and reserva.criado_por_email != usuario_email:
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para adicionar participantes a esta reserva"
            )
        
        db_participante = crud.create_participante(db=db, participante=participante)
        # Load user relationship
        db.refresh(db_participante)
        if db_participante.usuario_id:
            db_participante = db.query(models.Participante).options(joinedload(models.Participante.usuario)).filter(models.Participante.id == db_participante.id).first()
        return db_participante
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/v1/reservas/{reserva_id}/participantes", response_model=List[schemas.ParticipanteOut])
def list_participantes_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """Lists all participants of a reservation."""
    reserva = crud.get_reserva_by_id(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    participantes = db.query(models.Participante).options(joinedload(models.Participante.usuario)).filter(
        models.Participante.reserva_id == reserva_id
    ).order_by(models.Participante.created_at).all()
    return participantes


@router.delete("/v1/participantes/{participante_id}", status_code=200)
def delete_participante(
    participante_id: int,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(get_current_user_email)
):
    """Removes a participant from a reservation."""
    participante = crud.get_participante_by_id(db, participante_id)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    
    # Check if user has permission (is the reservation creator)
    reserva = crud.get_reserva_by_id(db, participante.reserva_id)
    if reserva and reserva.criado_por_email and reserva.criado_por_email != usuario_email:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para remover participantes desta reserva"
        )
    
    success = crud.delete_participante(db, participante_id)
    if not success:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return {"message": "Participante removido com sucesso"}
