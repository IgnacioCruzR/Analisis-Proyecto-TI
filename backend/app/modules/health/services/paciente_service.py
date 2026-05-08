from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from app.modules.health.models.raw import RawPaciente
from app.modules.health.models.warehouse import DimPaciente, FactVisita
from app.modules.health.schemas import PacienteCreate, PacienteUpdate


class PacienteService:
    @staticmethod
    def crear_paciente(db: Session, paciente_data: PacienteCreate) -> RawPaciente:
        """Crea un nuevo paciente en la capa Raw"""
        raw_paciente = RawPaciente(
            **paciente_data.dict(),
            event_type="created",
            source="health_module"
        )
        db.add(raw_paciente)
        db.commit()
        db.refresh(raw_paciente)
        return raw_paciente

    @staticmethod
    def obtener_paciente(db: Session, paciente_id: UUID) -> RawPaciente:
        """Obtiene un paciente por ID"""
        return db.query(RawPaciente).filter(RawPaciente.id == paciente_id).first()

    @staticmethod
    def listar_pacientes(db: Session, skip: int = 0, limit: int = 100) -> list:
        """Lista todos los pacientes"""
        return db.query(RawPaciente).offset(skip).limit(limit).all()

    @staticmethod
    def actualizar_paciente(
        db: Session, paciente_id: UUID, paciente_data: PacienteUpdate
    ) -> RawPaciente:
        """Actualiza un paciente existente"""
        raw_paciente = db.query(RawPaciente).filter(RawPaciente.id == paciente_id).first()
        if raw_paciente:
            update_data = paciente_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(raw_paciente, key, value)
            raw_paciente.event_type = "updated"
            db.add(raw_paciente)
            db.commit()
            db.refresh(raw_paciente)
        return raw_paciente

    @staticmethod
    def eliminar_paciente(db: Session, paciente_id: UUID) -> bool:
        """Marca un paciente como eliminado (soft delete)"""
        raw_paciente = db.query(RawPaciente).filter(RawPaciente.id == paciente_id).first()
        if raw_paciente:
            raw_paciente.event_type = "deleted"
            raw_paciente.processed = True
            db.add(raw_paciente)
            db.commit()
            return True
        return False

    @staticmethod
    def obtener_estadisticas_paciente(db: Session, paciente_id: UUID) -> dict:
        """Obtiene estadísticas de un paciente desde el warehouse"""
        dim_paciente = db.query(DimPaciente).filter(
            DimPaciente.paciente_id == paciente_id
        ).first()
        
        if not dim_paciente:
            return {"error": "Paciente no encontrado en warehouse"}
        
        return {
            "total_visitas": dim_paciente.total_visitas,
            "total_alertas": dim_paciente.total_alertas,
            "alertas_criticas": dim_paciente.alertas_criticas,
            "ultima_visita": dim_paciente.ultima_visita,
            "zona": dim_paciente.zona,
            "edad": dim_paciente.edad,
        }
