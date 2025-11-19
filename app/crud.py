from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
from typing import Optional, List
from . import models, schemas


# ========== Location CRUD ==========

def create_local(db: Session, local: schemas.LocalCreate) -> models.Local:
    """Creates a new location."""
    db_local = models.Local(**local.model_dump())
    db.add(db_local)
    db.commit()
    db.refresh(db_local)
    return db_local


def get_local_by_id(db: Session, local_id: int) -> Optional[models.Local]:
    """Gets a location by ID (only active and not deleted)."""
    return db.query(models.Local).filter(
        models.Local.id == local_id,
        models.Local.deleted_at.is_(None)
    ).first()


def get_local_by_id_with_deleted(db: Session, local_id: int) -> Optional[models.Local]:
    """Gets a location by ID including deleted ones (for internal validations)."""
    return db.query(models.Local).filter(models.Local.id == local_id).first()


def list_locais(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None
) -> List[models.Local]:
    """Lists locations with optional filters."""
    query = db.query(models.Local).filter(models.Local.deleted_at.is_(None))
    
    if ativo is not None:
        query = query.filter(models.Local.ativo == ativo)
    
    return query.order_by(models.Local.nome).offset(skip).limit(limit).all()


def count_locais(db: Session, ativo: Optional[bool] = None) -> int:
    """Counts total locations (for pagination)."""
    query = db.query(models.Local).filter(models.Local.deleted_at.is_(None))
    if ativo is not None:
        query = query.filter(models.Local.ativo == ativo)
    return query.count()


def update_local(db: Session, local_id: int, local_update: schemas.LocalUpdate) -> Optional[models.Local]:
    """Updates a location."""
    db_local = get_local_by_id(db, local_id)
    if not db_local:
        return None
    
    update_data = local_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_local, field, value)
    
    db.commit()
    db.refresh(db_local)
    return db_local


def delete_local(db: Session, local_id: int) -> bool:
    """Soft delete of a location."""
    db_local = get_local_by_id(db, local_id)
    if not db_local:
        return False
    
    db_local.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True


# ========== Room CRUD ==========

def create_sala(db: Session, sala: schemas.SalaCreate) -> models.Sala:
    """Creates a new room."""
    # Validate that location exists and is active
    local = get_local_by_id(db, sala.local_id)
    if not local:
        raise ValueError("Local não encontrado ou inativo")
    
    # Check name uniqueness within the location
    existing = db.query(models.Sala).filter(
        models.Sala.local_id == sala.local_id,
        models.Sala.nome == sala.nome,
        models.Sala.deleted_at.is_(None)
    ).first()
    if existing:
        raise ValueError("Já existe uma sala com este nome neste local")
    
    db_sala = models.Sala(**sala.model_dump())
    db.add(db_sala)
    db.commit()
    db.refresh(db_sala)
    return db_sala


def get_sala_by_id(db: Session, sala_id: int) -> Optional[models.Sala]:
    """Gets a room by ID (only active and not deleted)."""
    return db.query(models.Sala).filter(
        models.Sala.id == sala_id,
        models.Sala.deleted_at.is_(None)
    ).first()


def get_sala_by_id_with_deleted(db: Session, sala_id: int) -> Optional[models.Sala]:
    """Gets a room by ID including deleted ones."""
    return db.query(models.Sala).filter(models.Sala.id == sala_id).first()


def list_salas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    local_id: Optional[int] = None,
    ativo: Optional[bool] = None,
    capacidade_minima: Optional[int] = None
) -> List[models.Sala]:
    """Lists rooms with optional filters."""
    query = db.query(models.Sala).filter(models.Sala.deleted_at.is_(None))
    
    if local_id is not None:
        query = query.filter(models.Sala.local_id == local_id)
    
    if ativo is not None:
        query = query.filter(models.Sala.ativo == ativo)
    
    if capacidade_minima is not None:
        query = query.filter(models.Sala.capacidade >= capacidade_minima)
    
    return query.order_by(models.Sala.nome).offset(skip).limit(limit).all()


def count_salas(
    db: Session,
    local_id: Optional[int] = None,
    ativo: Optional[bool] = None,
    capacidade_minima: Optional[int] = None
) -> int:
    """Counts total rooms (for pagination)."""
    query = db.query(models.Sala).filter(models.Sala.deleted_at.is_(None))
    if local_id is not None:
        query = query.filter(models.Sala.local_id == local_id)
    if ativo is not None:
        query = query.filter(models.Sala.ativo == ativo)
    if capacidade_minima is not None:
        query = query.filter(models.Sala.capacidade >= capacidade_minima)
    return query.count()


def update_sala(db: Session, sala_id: int, sala_update: schemas.SalaUpdate) -> Optional[models.Sala]:
    """Updates a room."""
    db_sala = get_sala_by_id(db, sala_id)
    if not db_sala:
        return None
    
    update_data = sala_update.model_dump(exclude_unset=True)
    
    # Validate local_id if provided
    if "local_id" in update_data:
        local = get_local_by_id(db, update_data["local_id"])
        if not local:
            raise ValueError("Local não encontrado ou inativo")
    
    # Validate name uniqueness if provided
    if "nome" in update_data:
        local_id_check = update_data.get("local_id", db_sala.local_id)
        existing = db.query(models.Sala).filter(
            models.Sala.local_id == local_id_check,
            models.Sala.nome == update_data["nome"],
            models.Sala.id != sala_id,
            models.Sala.deleted_at.is_(None)
        ).first()
        if existing:
            raise ValueError("Já existe uma sala com este nome neste local")
    
    for field, value in update_data.items():
        setattr(db_sala, field, value)
    
    db.commit()
    db.refresh(db_sala)
    return db_sala


def delete_sala(db: Session, sala_id: int) -> bool:
    """Soft delete of a room."""
    db_sala = get_sala_by_id(db, sala_id)
    if not db_sala:
        return False
    
    db_sala.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True


# ========== Reservation CRUD ==========

def check_time_conflict(
    db: Session,
    sala_id: int,
    data_inicio: datetime,
    data_fim: datetime,
    exclude_reserva_id: Optional[int] = None
) -> bool:
    """
    Checks time conflict for a room.
    Two reservations conflict if:
    - new_data_inicio < existing_data_fim AND
    - new_data_fim > existing_data_inicio
    - and they are for the same room
    
    Adjacent times (e.g., 10:00-11:00 and 11:00-12:00) are allowed.
    Returns True if there's a conflict, False otherwise.
    """
    query = db.query(models.Reserva).filter(
        models.Reserva.sala_id == sala_id,
        models.Reserva.deleted_at.is_(None)
    )
    
    if exclude_reserva_id:
        query = query.filter(models.Reserva.id != exclude_reserva_id)
    
    # Conflict algorithm: allow adjacent times
    conflicts = query.filter(
        and_(
            models.Reserva.data_inicio < data_fim,
            models.Reserva.data_fim > data_inicio
        )
    ).first()
    
    return conflicts is not None


def create_reserva(db: Session, reserva: schemas.ReservaCreate, criado_por_email: str) -> models.Reserva:
    """Creates a new reservation."""
    # Validate that location and room exist and are active
    local = get_local_by_id(db, reserva.local_id)
    if not local:
        raise ValueError("Local não encontrado ou inativo")
    
    sala = get_sala_by_id(db, reserva.sala_id)
    if not sala:
        raise ValueError("Sala não encontrada ou inativa")
    
    # Validate that room belongs to the specified location
    if sala.local_id != reserva.local_id:
        raise ValueError("A sala não pertence ao local informado")
    
    # Validate that dates are not in the past (decision: not allowed)
    now = datetime.now(timezone.utc)
    if reserva.data_inicio < now:
        raise ValueError("Não é permitido criar reservas no passado")
    
    # Validate time conflict
    if check_time_conflict(
        db=db,
        sala_id=reserva.sala_id,
        data_inicio=reserva.data_inicio,
        data_fim=reserva.data_fim
    ):
        raise ValueError("Conflito de horário: já existe uma reserva para esta sala neste intervalo")
    
    # Create reservation (denormalized fields will be filled)
    db_reserva = models.Reserva(
        local_id=reserva.local_id,
        sala_id=reserva.sala_id,
        local=local.nome,
        sala=sala.nome,
        data_inicio=reserva.data_inicio,
        data_fim=reserva.data_fim,
        responsavel=reserva.responsavel,
        cafe=reserva.cafe,
        quantidade_cafe=reserva.quantidade_cafe if reserva.cafe else None,
        descricao=reserva.descricao,
        criado_por_email=criado_por_email
    )
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva


def get_reserva_by_id(db: Session, reserva_id: int) -> Optional[models.Reserva]:
    """Gets a reservation by ID (only not deleted)."""
    return db.query(models.Reserva).filter(
        models.Reserva.id == reserva_id,
        models.Reserva.deleted_at.is_(None)
    ).first()


def list_reservas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    sala: Optional[str] = None,
    local: Optional[str] = None,
    responsavel: Optional[str] = None
) -> List[models.Reserva]:
    """
    Lists reservations with optional filters.
    If data_inicio and data_fim are provided, filters by date range.
    """
    query = db.query(models.Reserva).filter(models.Reserva.deleted_at.is_(None))
    
    # Filter by date range
    if data_inicio and data_fim:
        if data_inicio > data_fim:
            raise ValueError("data_inicio não pode ser posterior a data_fim")
        # Reservations that overlap with the interval
        query = query.filter(
            and_(
                models.Reserva.data_inicio < data_fim,
                models.Reserva.data_fim > data_inicio
            )
        )
    elif data_inicio:
        query = query.filter(models.Reserva.data_inicio >= data_inicio)
    elif data_fim:
        query = query.filter(models.Reserva.data_fim <= data_fim)
    
    if sala:
        query = query.filter(models.Reserva.sala.ilike(f"%{sala}%"))
    
    if local:
        query = query.filter(models.Reserva.local.ilike(f"%{local}%"))
    
    if responsavel:
        query = query.filter(models.Reserva.responsavel.ilike(f"%{responsavel}%"))
    
    return query.order_by(models.Reserva.data_inicio).offset(skip).limit(limit).all()


def count_reservas(
    db: Session,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    sala: Optional[str] = None,
    local: Optional[str] = None,
    responsavel: Optional[str] = None
) -> int:
    """Counts total reservations (for pagination)."""
    query = db.query(models.Reserva).filter(models.Reserva.deleted_at.is_(None))
    
    if data_inicio and data_fim:
        if data_inicio > data_fim:
            raise ValueError("data_inicio não pode ser posterior a data_fim")
        query = query.filter(
            and_(
                models.Reserva.data_inicio < data_fim,
                models.Reserva.data_fim > data_inicio
            )
        )
    elif data_inicio:
        query = query.filter(models.Reserva.data_inicio >= data_inicio)
    elif data_fim:
        query = query.filter(models.Reserva.data_fim <= data_fim)
    
    if sala:
        query = query.filter(models.Reserva.sala.ilike(f"%{sala}%"))
    if local:
        query = query.filter(models.Reserva.local.ilike(f"%{local}%"))
    if responsavel:
        query = query.filter(models.Reserva.responsavel.ilike(f"%{responsavel}%"))
    
    return query.count()


def update_reserva(db: Session, reserva_id: int, reserva_update: schemas.ReservaUpdate, usuario_email: str) -> Optional[models.Reserva]:
    """Updates a reservation."""
    db_reserva = get_reserva_by_id(db, reserva_id)
    if not db_reserva:
        return None
    
    # Check if user is the reservation creator
    if db_reserva.criado_por_email and db_reserva.criado_por_email != usuario_email:
        raise ValueError("Você não tem permissão para editar esta reserva. Apenas o criador pode editá-la.")
    
    update_data = reserva_update.model_dump(exclude_unset=True)
    
    # Determine final values for validation
    final_local_id = update_data.get("local_id", db_reserva.local_id)
    final_sala_id = update_data.get("sala_id", db_reserva.sala_id)
    final_data_inicio = update_data.get("data_inicio", db_reserva.data_inicio)
    final_data_fim = update_data.get("data_fim", db_reserva.data_fim)
    
    # Validate dates
    if final_data_fim <= final_data_inicio:
        raise ValueError("data_fim deve ser posterior a data_inicio")
    
    # Validate that it's not in the past
    now = datetime.now(timezone.utc)
    if final_data_inicio < now:
        raise ValueError("Não é permitido atualizar reservas para o passado")
    
    # Validate location and room if provided
    if "local_id" in update_data or "sala_id" in update_data:
        local = get_local_by_id(db, final_local_id)
        if not local:
            raise ValueError("Local não encontrado ou inativo")
        
        sala = get_sala_by_id(db, final_sala_id)
        if not sala:
            raise ValueError("Sala não encontrada ou inativa")
        
        if sala.local_id != final_local_id:
            raise ValueError("A sala não pertence ao local informado")
        
        # Update denormalized fields
        update_data["local"] = local.nome
        update_data["sala"] = sala.nome
    
    # Validate time conflict (ignoring the reservation itself)
    if check_time_conflict(
        db=db,
        sala_id=final_sala_id,
        data_inicio=final_data_inicio,
        data_fim=final_data_fim,
        exclude_reserva_id=reserva_id
    ):
        raise ValueError("Conflito de horário: já existe uma reserva para esta sala neste intervalo")
    
    # Validate coffee
    final_cafe = update_data.get("cafe", db_reserva.cafe)
    final_quantidade_cafe = update_data.get("quantidade_cafe", db_reserva.quantidade_cafe)
    if final_cafe is True:
        if final_quantidade_cafe is None or final_quantidade_cafe <= 0:
            raise ValueError("quantidade_cafe é obrigatório e deve ser maior que 0 quando cafe = true")
    elif final_cafe is False:
        update_data["quantidade_cafe"] = None
    
    # Apply updates
    for field, value in update_data.items():
        setattr(db_reserva, field, value)
    
    db.commit()
    db.refresh(db_reserva)
    return db_reserva


def delete_reserva(db: Session, reserva_id: int, usuario_email: str) -> bool:
    """Soft delete of a reservation."""
    db_reserva = get_reserva_by_id(db, reserva_id)
    if not db_reserva:
        return False
    
    # Check if user is the reservation creator
    if db_reserva.criado_por_email and db_reserva.criado_por_email != usuario_email:
        raise ValueError("Você não tem permissão para excluir esta reserva. Apenas o criador pode excluí-la.")
    
    db_reserva.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True


# ========== User CRUD ==========

def get_or_create_usuario(
    db: Session,
    google_id: str,
    email: str,
    nome: str,
    foto_url: Optional[str] = None
) -> models.Usuario:
    """Gets a user by Google ID or email, or creates a new one."""
    # Try to find by google_id first
    usuario = db.query(models.Usuario).filter(models.Usuario.google_id == google_id).first()
    
    if not usuario:
        # Try to find by email
        usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    
    if usuario:
        # Update information
        usuario.nome = nome
        if foto_url:
            usuario.foto_url = foto_url
        usuario.last_login_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(usuario)
    else:
        # Create new user
        usuario = models.Usuario(
            google_id=google_id,
            email=email,
            nome=nome,
            foto_url=foto_url,
            last_login_at=datetime.now(timezone.utc)
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    
    return usuario


def get_usuario_by_id(db: Session, usuario_id: int) -> Optional[models.Usuario]:
    """Gets a user by ID."""
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()


def get_usuario_by_email(db: Session, email: str) -> Optional[models.Usuario]:
    """Gets a user by email."""
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def list_usuarios(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[models.Usuario]:
    """Lists users with optional filters."""
    query = db.query(models.Usuario)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Usuario.nome.ilike(search_pattern)) |
            (models.Usuario.email.ilike(search_pattern))
        )
    
    return query.order_by(models.Usuario.nome).offset(skip).limit(limit).all()


def count_usuarios(db: Session, search: Optional[str] = None) -> int:
    """Counts total users (for pagination)."""
    query = db.query(models.Usuario)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Usuario.nome.ilike(search_pattern)) |
            (models.Usuario.email.ilike(search_pattern))
        )
    
    return query.count()


# ========== Participant CRUD ==========

def create_participante(db: Session, participante: schemas.ParticipanteCreate) -> models.Participante:
    """Creates a new participant."""
    # Validate that reservation exists
    reserva = get_reserva_by_id(db, participante.reserva_id)
    if not reserva:
        raise ValueError("Reserva não encontrada")
    
    # Validate that usuario_id exists if provided
    if participante.usuario_id:
        usuario = get_usuario_by_id(db, participante.usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")
        
        # Check if participant with this user already exists in this reservation
        existing = db.query(models.Participante).filter(
            models.Participante.reserva_id == participante.reserva_id,
            models.Participante.usuario_id == participante.usuario_id
        ).first()
        if existing:
            raise ValueError("Este usuário já está participando desta reserva")
    
    # Check if participant with this manual name already exists in this reservation
    if participante.nome_manual:
        existing = db.query(models.Participante).filter(
            models.Participante.reserva_id == participante.reserva_id,
            models.Participante.nome_manual == participante.nome_manual
        ).first()
        if existing:
            raise ValueError("Já existe um participante com este nome nesta reserva")
    
    db_participante = models.Participante(**participante.model_dump())
    db.add(db_participante)
    db.commit()
    db.refresh(db_participante)
    return db_participante


def get_participante_by_id(db: Session, participante_id: int) -> Optional[models.Participante]:
    """Gets a participant by ID."""
    return db.query(models.Participante).filter(models.Participante.id == participante_id).first()


def list_participantes_by_reserva(db: Session, reserva_id: int) -> List[models.Participante]:
    """Lists all participants of a reservation."""
    return db.query(models.Participante).filter(
        models.Participante.reserva_id == reserva_id
    ).order_by(models.Participante.created_at).all()


def delete_participante(db: Session, participante_id: int) -> bool:
    """Deletes a participant."""
    db_participante = get_participante_by_id(db, participante_id)
    if not db_participante:
        return False
    
    db.delete(db_participante)
    db.commit()
    return True


def delete_participantes_by_reserva(db: Session, reserva_id: int) -> int:
    """Deletes all participants of a reservation. Returns the number of deleted participants."""
    count = db.query(models.Participante).filter(
        models.Participante.reserva_id == reserva_id
    ).delete()
    db.commit()
    return count
