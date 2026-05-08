from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from datetime import datetime
from app.modules.health.models.raw import RawVisita
from app.modules.health.models.warehouse import FactVisita
from app.modules.health.schemas import VisitaCreate, VisitaUpdate


class VisitaService:
    @staticmethod
    def crear_visita(db: Session, visita_data: VisitaCreate) -> RawVisita:
        """Crea una nueva visita en la capa Raw"""
        raw_visita = RawVisita(
            **visita_data.dict(),
            event_type="created",
            source="health_module",
            processed="pending"
        )
        db.add(raw_visita)
        db.commit()
        db.refresh(raw_visita)
        return raw_visita

    @staticmethod
    def obtener_visita(db: Session, visita_id: UUID) -> RawVisita:
        """Obtiene una visita por ID"""
        return db.query(RawVisita).filter(RawVisita.id == visita_id).first()

    @staticmethod
    def listar_visitas_paciente(
        db: Session, paciente_id: UUID, skip: int = 0, limit: int = 100
    ) -> list:
        """Lista todas las visitas de un paciente"""
        return db.query(RawVisita).filter(
            RawVisita.paciente_id == paciente_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def listar_visitas_profesional(
        db: Session, profesional_id: UUID, skip: int = 0, limit: int = 100
    ) -> list:
        """Lista todas las visitas de un profesional"""
        return db.query(RawVisita).filter(
            RawVisita.profesional_salud_id == profesional_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def actualizar_visita(
        db: Session, visita_id: UUID, visita_data: VisitaUpdate
    ) -> RawVisita:
        """Actualiza una visita existente"""
        raw_visita = db.query(RawVisita).filter(RawVisita.id == visita_id).first()
        if raw_visita:
            update_data = visita_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(raw_visita, key, value)
            raw_visita.event_type = "updated"
            db.add(raw_visita)
            db.commit()
            db.refresh(raw_visita)
        return raw_visita

    @staticmethod
    def completar_visita(
        db: Session, visita_id: UUID, hora_fin: datetime = None
    ) -> RawVisita:
        """Marca una visita como completada"""
        raw_visita = db.query(RawVisita).filter(RawVisita.id == visita_id).first()
        if raw_visita:
            raw_visita.estado = "completada"
            raw_visita.fecha_hora_fin_real = hora_fin or datetime.utcnow()
            raw_visita.event_type = "completed"
            raw_visita.processed = "pending"
            db.add(raw_visita)
            db.commit()
            db.refresh(raw_visita)
        return raw_visita

    @staticmethod
    def cancelar_visita(db: Session, visita_id: UUID) -> RawVisita:
        """Cancela una visita"""
        raw_visita = db.query(RawVisita).filter(RawVisita.id == visita_id).first()
        if raw_visita:
            raw_visita.estado = "cancelada"
            raw_visita.event_type = "cancelled"
            db.add(raw_visita)
            db.commit()
            db.refresh(raw_visita)
        return raw_visita

    @staticmethod
    def obtener_visitas_hoy(db: Session, zona_id: UUID = None) -> list:
        """Obtiene las visitas programadas para hoy"""
        from datetime import date
        hoy = str(date.today())
        query = db.query(RawVisita).filter(
            RawVisita.fecha_programada == hoy,
            RawVisita.estado.in_(["programada", "en_progreso"])
        )
        if zona_id:
            query = query.filter(RawVisita.zona_id == zona_id)
        return query.all()
