"""
Seed data para el módulo de salud
Genera datos de prueba para testing y desarrollo
"""

import uuid
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.modules.health.models.raw import (
    RawPaciente,
    RawVisita,
    RawAlerta,
)
from app.modules.health.models.warehouse import (
    DimPaciente,
    FactVisita,
    FactAlerta,
)


def seed_pacientes_raw(db: Session, count: int = 10) -> list:
    """Genera pacientes en la capa Raw"""
    pacientes = []
    nombres_list = ["Juan", "María", "Carlos", "Ana", "Roberto", "Elena", "Miguel", "Sofia", "Luis", "Carmen"]
    apellidos_list = ["García", "López", "Rodríguez", "Martínez", "Sánchez", "Torres", "Flores", "Jiménez", "Pérez", "Díaz"]
    
    for i in range(count):
        paciente = RawPaciente(
            id=uuid.uuid4(),
            event_type="created",
            source="health_module",
            rut=f"1{i+1:07d}-K",
            nombres=nombres_list[i % len(nombres_list)],
            apellidos=apellidos_list[i % len(apellidos_list)],
            fecha_nacimiento=date(1980 + i, 1, 15),
            sexo="M" if i % 2 == 0 else "F",
            telefono=f"+569{20000000 + i}",
            email=f"paciente{i+1}@example.com",
            direccion=f"Calle Principal {i+1}, Apt {i+100}",
            zona_id=uuid.uuid4(),
            processed=False,
            created_at=datetime.utcnow(),
        )
        db.add(paciente)
        pacientes.append(paciente)
    
    db.commit()
    return pacientes


def seed_visitas_raw(db: Session, pacientes: list, count: int = 15) -> list:
    """Genera visitas en la capa Raw"""
    visitas = []
    profesional_id = uuid.uuid4()
    estados = ["programada", "en_progreso", "completada", "cancelada"]
    
    for i in range(count):
        hoy = date.today()
        fecha = hoy - timedelta(days=i % 10)
        
        visita = RawVisita(
            id=uuid.uuid4(),
            event_type="created",
            source="health_module",
            paciente_id=pacientes[i % len(pacientes)].id,
            profesional_salud_id=profesional_id,
            zona_id=uuid.uuid4(),
            fecha_programada=str(fecha),
            hora_programada="14:30:00",
            fecha_hora_inicio_real=datetime.utcnow() - timedelta(hours=i),
            fecha_hora_fin_real=datetime.utcnow() - timedelta(hours=i-1) if i % 2 == 0 else None,
            estado=estados[i % len(estados)],
            creada_por_usuario_id=uuid.uuid4(),
            processed="pending",
            created_at=datetime.utcnow() - timedelta(days=i),
        )
        db.add(visita)
        visitas.append(visita)
    
    db.commit()
    return visitas


def seed_alertas_raw(db: Session, pacientes: list, count: int = 8) -> list:
    """Genera alertas en la capa Raw"""
    alertas = []
    tipos = ["presión_alta", "temperatura", "glucosa", "frecuencia_cardiaca", "saturación_oxígeno"]
    prioridades = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    estados = ["OPEN", "ACKNOWLEDGED", "RESOLVED"]
    
    for i in range(count):
        alerta = RawAlerta(
            id=uuid.uuid4(),
            event_type="created",
            source="health_module",
            paciente_id=pacientes[i % len(pacientes)].id,
            visita_id=None,
            tipo=tipos[i % len(tipos)],
            mensaje=f"Alerta {i+1}: Valor fuera de rango normal",
            prioridad=prioridades[i % len(prioridades)],
            estado=estados[i % len(estados)],
            metadata={"valor": 150 + i*5, "unidad": "mmHg"},
            processed="pending",
            created_at=datetime.utcnow() - timedelta(hours=i),
        )
        db.add(alerta)
        alertas.append(alerta)
    
    db.commit()
    return alertas


def seed_warehouse_data(db: Session, pacientes: list, visitas: list, alertas: list) -> None:
    """Genera datos en la capa Warehouse (Dimensiones y Hechos)"""
    
    # Crear dimensiones de pacientes
    for paciente in pacientes:
        dim_paciente = DimPaciente(
            id=uuid.uuid4(),
            paciente_id=paciente.id,
            nombres=paciente.nombres,
            apellidos=paciente.apellidos,
            rut=paciente.rut,
            sexo=paciente.sexo,
            edad=(datetime.now().year - paciente.fecha_nacimiento.year) if paciente.fecha_nacimiento else None,
            zona=str(paciente.zona_id)[:8],
            activo="active",
            total_visitas=len([v for v in visitas if v.paciente_id == paciente.id]),
            total_alertas=len([a for a in alertas if a.paciente_id == paciente.id]),
            alertas_criticas=len([a for a in alertas if a.paciente_id == paciente.id and a.prioridad == "CRITICAL"]),
            ultima_visita=str(max([v.fecha_programada for v in visitas if v.paciente_id == paciente.id], default=date.today())),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(dim_paciente)
    
    # Crear hechos de visitas
    for visita in visitas:
        duracion = 0
        if visita.fecha_hora_inicio_real and visita.fecha_hora_fin_real:
            duracion = int((visita.fecha_hora_fin_real - visita.fecha_hora_inicio_real).total_seconds() / 60)
        
        fact_visita = FactVisita(
            id=uuid.uuid4(),
            visita_id=visita.id,
            paciente_id=visita.paciente_id,
            profesional_id=visita.profesional_salud_id,
            zona_id=visita.zona_id,
            duracion_minutos=duracion,
            estado=visita.estado,
            completada=visita.estado == "completada",
            tuvo_alerta=False,
            alerta_critica=False,
            fecha_visita=visita.fecha_programada,
            hora_inicio=visita.hora_programada,
            hora_fin="15:30:00",
            documentos_adjuntos=0,
            notas_clinicas=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(fact_visita)
    
    # Crear hechos de alertas
    for alerta in alertas:
        fact_alerta = FactAlerta(
            id=uuid.uuid4(),
            alerta_id=alerta.id,
            paciente_id=alerta.paciente_id,
            visita_id=alerta.visita_id,
            tipo=alerta.tipo,
            prioridad=alerta.prioridad,
            estado=alerta.estado,
            minutos_sin_resolver=0 if alerta.estado == "RESOLVED" else 60,
            resuelta="resolved" if alerta.estado == "RESOLVED" else "pending",
            escalamientos=0,
            intentos_contacto=1,
            fecha_creacion=str(alerta.created_at.date()),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(fact_alerta)
    
    db.commit()


def run_seed(db: Session) -> dict:
    """Ejecuta todos los seeds y retorna el resumen"""
    print("🌱 Iniciando seed data para módulo de salud...")
    
    # Seed Raw Layer
    print("  ✓ Creando pacientes...")
    pacientes = seed_pacientes_raw(db, count=10)
    
    print("  ✓ Creando visitas...")
    visitas = seed_visitas_raw(db, pacientes, count=15)
    
    print("  ✓ Creando alertas...")
    alertas = seed_alertas_raw(db, pacientes, count=8)
    
    # Seed Warehouse Layer
    print("  ✓ Creando dimensiones y hechos...")
    seed_warehouse_data(db, pacientes, visitas, alertas)
    
    print("\n✅ Seed completado exitosamente!")
    
    return {
        "pacientes": len(pacientes),
        "visitas": len(visitas),
        "alertas": len(alertas),
        "warehouse_records": len(pacientes) + len(visitas) + len(alertas),
    }
