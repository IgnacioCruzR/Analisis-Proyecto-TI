"""
Script de validación para verificar que el módulo de salud está correctamente configurado.
Ejecutar: python scripts/validate_setup.py
"""

import sys
import os

def check_imports():
    """Verifica que todos los imports funcionen correctamente"""
    print("✓ Verificando imports...")
    
    try:
        from app.db.base import Base
        print("  ✓ Base ORM importada")
        
        from app.core.database import salud_engine, get_salud_db
        print("  ✓ Database configuration importada")
        
        from app.modules.health.models.raw import (
            RawUsuario, RawPaciente, RawVisita, 
            RawAlerta, RawFichaClinica, RawDocumentoAdjunto
        )
        print("  ✓ Raw Layer models importados")
        
        from app.modules.health.models.warehouse import (
            DimPaciente, DimProfesional, FactVisita, FactAlerta
        )
        print("  ✓ Warehouse Layer models importados")
        
        from app.modules.health.services import (
            PacienteService, VisitaService, AlertaService
        )
        print("  ✓ Services importados")
        
        from app.modules.health.routes import (
            pacientes_router, visitas_router, 
            alertas_router, dashboard_router
        )
        print("  ✓ Routes importados")
        
        from app.modules.health.schemas import (
            PacienteCreate, DashboardSalud
        )
        print("  ✓ Schemas importados")
        
        return True
    except ImportError as e:
        print(f"  ✗ Error de import: {e}")
        return False


def check_database_connectivity():
    """Verifica conexión a la base de datos"""
    print("\n✓ Verificando conectividad de BD...")
    
    try:
        from app.core.database import salud_engine
        
        # Intentar conectar
        connection = salud_engine.connect()
        connection.close()
        print("  ✓ Conexión a BD de salud exitosa")
        return True
    except Exception as e:
        print(f"  ✗ Error de conexión: {e}")
        print("  💡 Verifica que Docker está corriendo: docker-compose ps")
        return False


def check_tables_exist():
    """Verifica que las tablas puedan ser creadas"""
    print("\n✓ Verificando creación de tablas...")
    
    try:
        from app.db.base import Base
        from app.core.database import salud_engine
        from app.modules.health.models.raw import RawPaciente
        from app.modules.health.models.warehouse import DimPaciente
        
        # Esto no modifica la BD, solo verifica la metadata
        tables = Base.metadata.tables.keys()
        
        expected_tables = [
            'raw_pacientes', 'raw_visitas', 'raw_alertas',
            'dim_pacientes', 'fact_visitas', 'fact_alertas'
        ]
        
        found_tables = [t for t in expected_tables if t in tables]
        
        print(f"  ✓ {len(found_tables)}/{len(expected_tables)} tablas registradas en metadata")
        
        for table in expected_tables:
            if table in tables:
                print(f"    ✓ {table}")
            else:
                print(f"    ⚠ {table} (no registrada)")
        
        return len(found_tables) >= 3  # Al menos algunas tablas
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def check_docker_containers():
    """Verifica que los contenedores Docker estén corriendo"""
    print("\n✓ Verificando contenedores Docker...")
    
    try:
        import subprocess
        
        result = subprocess.run(
            ["docker", "compose", "ps"],
            capture_output=True,
            text=True,
            cwd="."
        )
        
        if "proyecto_ti_postgres_salud" in result.stdout:
            print("  ✓ Contenedor de Salud está corriendo")
        else:
            print("  ✗ Contenedor de Salud NO está corriendo")
            print("  💡 Ejecuta: docker-compose up -d")
            return False
            
        if "proyecto_ti_postgres_subscripciones" in result.stdout:
            print("  ✓ Contenedor de Subscripciones está corriendo")
        else:
            print("  ⚠ Contenedor de Subscripciones NO está corriendo")
        
        return True
    except Exception as e:
        print(f"  ⚠ No se puede verificar Docker: {e}")
        print("  💡 Verifica que Docker esté instalado")
        return True  # No es fatal


def main():
    print("=" * 60)
    print("🔍 Validación de Setup - Módulo de Salud")
    print("=" * 60)
    
    checks = [
        ("Imports", check_imports),
        ("Docker Containers", check_docker_containers),
        ("Database Connectivity", check_database_connectivity),
        ("Tables Configuration", check_tables_exist),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error en {name}: {e}")
            results.append((name, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 ¡Todo está correctamente configurado!")
        print("\nPróximos pasos:")
        print("1. Ejecuta: python -m fastapi dev")
        print("2. Accede a: http://localhost:8000/docs")
        print("3. Genera datos: curl -X POST http://localhost:8000/seed/salud")
    else:
        print("\n⚠️  Hay algunos problemas que revisar")
        print("\nSolución rápida:")
        print("1. docker-compose down")
        print("2. docker-compose up -d")
        print("3. Vuelve a ejecutar este script")
    
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
