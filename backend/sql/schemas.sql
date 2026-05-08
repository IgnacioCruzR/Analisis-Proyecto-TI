-- ============================================
-- ESQUEMAS - MÓDULO DE SALUD
-- ============================================
-- Archivo: backend/sql/schemas.sql
-- Copiar y ejecutar en PostgreSQL para inicializar la BD de salud

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =========================
-- USER MANAGEMENT
-- =========================

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS zonas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    comuna VARCHAR(100),
    region VARCHAR(100),
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identity_user_id VARCHAR(100),
    rol_id UUID NOT NULL,
    rut VARCHAR(20),
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    telefono VARCHAR(30),
    activo BOOLEAN DEFAULT TRUE,
    ultimo_acceso_at TIMESTAMP,

    CONSTRAINT fk_usuarios_roles
        FOREIGN KEY (rol_id) REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS auditorias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID,
    entidad VARCHAR(100),
    entidad_id UUID,
    accion VARCHAR(100),
    detalle TEXT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_auditorias_usuarios
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- =========================
-- HEALTHCARE PROFESSIONALS
-- =========================

CREATE TABLE IF NOT EXISTS profesionales_salud (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL,
    profesion VARCHAR(50),
    numero_registro VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_profesionales_usuarios
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),

    CONSTRAINT uq_profesionales_usuario
        UNIQUE (usuario_id)
);

CREATE TABLE IF NOT EXISTS especialidades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profesional_zona (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profesional_salud_id UUID NOT NULL,
    zona_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_profesional_zona_profesional
        FOREIGN KEY (profesional_salud_id) REFERENCES profesionales_salud(id),

    CONSTRAINT fk_profesional_zona_zona
        FOREIGN KEY (zona_id) REFERENCES zonas(id),

    CONSTRAINT uq_profesional_zona
        UNIQUE (profesional_salud_id, zona_id)
);

CREATE TABLE IF NOT EXISTS profesional_especialidad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profesional_salud_id UUID NOT NULL,
    especialidad_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_profesional_especialidad_profesional
        FOREIGN KEY (profesional_salud_id) REFERENCES profesionales_salud(id),

    CONSTRAINT fk_profesional_especialidad_especialidad
        FOREIGN KEY (especialidad_id) REFERENCES especialidades(id),

    CONSTRAINT uq_profesional_especialidad
        UNIQUE (profesional_salud_id, especialidad_id)
);

-- =========================
-- PATIENT & VISIT DATA
-- =========================

CREATE TABLE IF NOT EXISTS pacientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rut VARCHAR(20),
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    sexo VARCHAR(20),
    telefono VARCHAR(30),
    email VARCHAR(150),
    direccion TEXT,
    zona_id UUID,

    CONSTRAINT fk_pacientes_zonas
        FOREIGN KEY (zona_id) REFERENCES zonas(id)
);

CREATE TABLE IF NOT EXISTS visitas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL,
    profesional_salud_id UUID NOT NULL,
    zona_id UUID,
    fecha_programada DATE,
    hora_programada TIME,
    fecha_hora_inicio_real TIMESTAMP,
    fecha_hora_fin_real TIMESTAMP,
    estado VARCHAR(30),
    creada_por_usuario_id UUID,

    CONSTRAINT fk_visitas_pacientes
        FOREIGN KEY (paciente_id) REFERENCES pacientes(id),

    CONSTRAINT fk_visitas_profesionales
        FOREIGN KEY (profesional_salud_id) REFERENCES profesionales_salud(id),

    CONSTRAINT fk_visitas_zonas
        FOREIGN KEY (zona_id) REFERENCES zonas(id),

    CONSTRAINT fk_visitas_creada_por
        FOREIGN KEY (creada_por_usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS alertas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL,
    visita_id UUID,
    tipo VARCHAR(50),
    mensaje TEXT,
    prioridad VARCHAR(20),
    estado VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_alertas_pacientes
        FOREIGN KEY (paciente_id) REFERENCES pacientes(id),

    CONSTRAINT fk_alertas_visitas
        FOREIGN KEY (visita_id) REFERENCES visitas(id)
);

CREATE TABLE IF NOT EXISTS fichas_clinicas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visita_id UUID NOT NULL,
    estado VARCHAR(30),
    contenido JSONB,
    creada_por_usuario_id UUID,
    actualizada_por_usuario_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_fichas_visitas
        FOREIGN KEY (visita_id) REFERENCES visitas(id),

    CONSTRAINT fk_fichas_creada_por
        FOREIGN KEY (creada_por_usuario_id) REFERENCES usuarios(id),

    CONSTRAINT fk_fichas_actualizada_por
        FOREIGN KEY (actualizada_por_usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS documentos_adjuntos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ficha_clinica_id UUID NOT NULL,
    nombre_archivo VARCHAR(150),
    tipo_archivo VARCHAR(50),
    url TEXT,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_documentos_fichas
        FOREIGN KEY (ficha_clinica_id) REFERENCES fichas_clinicas(id)
);

-- =========================
-- INDEXES FOR PERFORMANCE
-- =========================

CREATE INDEX IF NOT EXISTS idx_pacientes_rut ON pacientes(rut);
CREATE INDEX IF NOT EXISTS idx_pacientes_email ON pacientes(email);
CREATE INDEX IF NOT EXISTS idx_pacientes_zona_id ON pacientes(zona_id);

CREATE INDEX IF NOT EXISTS idx_visitas_paciente_id ON visitas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_visitas_profesional_id ON visitas(profesional_salud_id);
CREATE INDEX IF NOT EXISTS idx_visitas_fecha_programada ON visitas(fecha_programada);
CREATE INDEX IF NOT EXISTS idx_visitas_estado ON visitas(estado);

CREATE INDEX IF NOT EXISTS idx_alertas_paciente_id ON alertas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_alertas_prioridad ON alertas(prioridad);
CREATE INDEX IF NOT EXISTS idx_alertas_estado ON alertas(estado);

CREATE INDEX IF NOT EXISTS idx_fichas_visita_id ON fichas_clinicas(visita_id);
CREATE INDEX IF NOT EXISTS idx_fichas_estado ON fichas_clinicas(estado);

CREATE INDEX IF NOT EXISTS idx_documentos_ficha_id ON documentos_adjuntos(ficha_clinica_id);

-- ============================================
-- ✅ ESQUEMAS CREADOS EXITOSAMENTE
-- ============================================
