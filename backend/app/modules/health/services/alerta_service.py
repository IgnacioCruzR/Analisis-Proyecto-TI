from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from app.modules.health.models.raw import RawAlerta
from app.modules.health.models.warehouse import FactAlerta
from app.modules.health.schemas import AlertaCreate, AlertaUpdate


class AlertaService:
    @staticmethod
    def crear_alerta(db: Session, alerta_data: AlertaCreate) -> RawAlerta:
        """Crea una nueva alerta en la capa Raw"""
        raw_alerta = RawAlerta(
            **alerta_data.dict(),
            event_type="created",
            source="health_module",
            processed="pending"
        )
        db.add(raw_alerta)
        db.commit()
        db.refresh(raw_alerta)
        return raw_alerta

    @staticmethod
    def obtener_alerta(db: Session, alerta_id: UUID) -> RawAlerta:
        """Obtiene una alerta por ID"""
        return db.query(RawAlerta).filter(RawAlerta.id == alerta_id).first()

    @staticmethod
    def listar_alertas_paciente(
        db: Session, paciente_id: UUID, skip: int = 0, limit: int = 100
    ) -> list:
        """Lista todas las alertas de un paciente"""
        return db.query(RawAlerta).filter(
            RawAlerta.paciente_id == paciente_id
        ).order_by(RawAlerta.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def listar_alertas_criticas(db: Session, skip: int = 0, limit: int = 100) -> list:
        """Lista todas las alertas críticas abiertas"""
        return db.query(RawAlerta).filter(
            and_(
                RawAlerta.prioridad == "CRITICAL",
                RawAlerta.estado == "OPEN"
            )
        ).order_by(RawAlerta.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def actualizar_alerta(
        db: Session, alerta_id: UUID, alerta_data: AlertaUpdate
    ) -> RawAlerta:
        """Actualiza una alerta existente"""
        raw_alerta = db.query(RawAlerta).filter(RawAlerta.id == alerta_id).first()
        if raw_alerta:
            update_data = alerta_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(raw_alerta, key, value)
            raw_alerta.event_type = "updated"
            db.add(raw_alerta)
            db.commit()
            db.refresh(raw_alerta)
        return raw_alerta

    @staticmethod
    def resolver_alerta(db: Session, alerta_id: UUID) -> RawAlerta:
        """Resuelve una alerta"""
        raw_alerta = db.query(RawAlerta).filter(RawAlerta.id == alerta_id).first()
        if raw_alerta:
            raw_alerta.estado = "RESOLVED"
            raw_alerta.event_type = "resolved"
            raw_alerta.processed = "pending"
            db.add(raw_alerta)
            db.commit()
            db.refresh(raw_alerta)
        return raw_alerta

    @staticmethod
    def contar_alertas_por_prioridad(db: Session) -> dict:
        """Cuenta las alertas abiertas por prioridad"""
        from sqlalchemy import func
        result = db.query(
            RawAlerta.prioridad,
            func.count(RawAlerta.id).label("count")
        ).filter(
            RawAlerta.estado == "OPEN"
        ).group_by(RawAlerta.prioridad).all()
        
        return {
            "CRITICAL": next((r[1] for r in result if r[0] == "CRITICAL"), 0),
            "HIGH": next((r[1] for r in result if r[0] == "HIGH"), 0),
            "MEDIUM": next((r[1] for r in result if r[0] == "MEDIUM"), 0),
            "LOW": next((r[1] for r in result if r[0] == "LOW"), 0),
        }
