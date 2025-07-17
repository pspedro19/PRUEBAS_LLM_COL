-- =======================================================
-- MODELO DE BASE DE DATOS ICFES BASADO EN ICFES.xlsx
-- =======================================================

-- 1. TAXONOMÍA EDUCATIVA
-- =======================================================

CREATE TABLE areas_evaluacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,         -- 'MATEMATICAS', 'LECTURA_CRITICA'
    nombre VARCHAR(100) NOT NULL,               -- 'Matemáticas', 'Lectura Crítica'
    descripcion TEXT,
    color_tema VARCHAR(7) DEFAULT '#3B82F6',   -- Color hex para UI
    icono_url VARCHAR(500),
    orden_visualizacion INTEGER DEFAULT 0,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE competencias_icfes (
    id SERIAL PRIMARY KEY,
    area_evaluacion_id INTEGER REFERENCES areas_evaluacion(id),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,               -- 'Interpretación y representación'
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE componentes_conocimiento (
    id SERIAL PRIMARY KEY,
    competencia_id INTEGER REFERENCES competencias_icfes(id),
    codigo VARCHAR(50) NOT NULL,
    nombre VARCHAR(200) NOT NULL,               -- 'Conocimientos genéricos'
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE procesos_cognitivos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,               -- 'Interpretación', 'Argumentación'
    descripcion TEXT,
    nivel_bloom INTEGER,                        -- 1-6 según taxonomía de Bloom
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE tipos_conocimiento (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,               -- 'Genérico', 'Específico'
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE contextos_aplicacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,               -- 'Comunitario/social', 'Personal/familiar'
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE
);

-- 2. TEMAS ESPECÍFICOS Y ÁREAS TEMÁTICAS
-- =======================================================

CREATE TABLE areas_tematicas (
    id SERIAL PRIMARY KEY,
    area_evaluacion_id INTEGER REFERENCES areas_evaluacion(id),
    codigo VARCHAR(50) NOT NULL,
    nombre VARCHAR(200) NOT NULL,               -- 'Aritmética y Operaciones Básicas'
    descripcion TEXT,
    keywords JSONB DEFAULT '[]',                -- Palabras clave para clasificación automática
    color_tema VARCHAR(7),
    icono_url VARCHAR(500),
    orden INTEGER DEFAULT 0,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE temas_especificos (
    id SERIAL PRIMARY KEY,
    area_tematica_id INTEGER REFERENCES areas_tematicas(id),
    nombre VARCHAR(300) NOT NULL,               -- 'Sistemas de transporte y optimización'
    descripcion TEXT,
    keywords JSONB DEFAULT '[]',
    prerequisitos_ids INTEGER[],                -- Array de IDs de temas prerequisito
    nivel_dificultad INTEGER DEFAULT 1,        -- 1-5
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. CUADERNILLOS Y PERÍODOS
-- =======================================================

CREATE TABLE periodos_aplicacion (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,        -- '2024-1', '2024-2'
    nombre VARCHAR(100) NOT NULL,               -- '2024 Período 1'
    fecha_inicio DATE,
    fecha_fin DATE,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cuadernillos_icfes (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    area_evaluacion_id INTEGER REFERENCES areas_evaluacion(id),
    periodo_aplicacion_id INTEGER REFERENCES periodos_aplicacion(id),
    tipo_cuadernillo VARCHAR(20) DEFAULT 'SABER_11',  -- 'SABER_11', 'SABER_PRO', 'SIMULACRO'
    grado_escolar INTEGER NOT NULL,
    total_preguntas INTEGER DEFAULT 0,
    archivo_fuente_url VARCHAR(500),
    procesado BOOLEAN DEFAULT FALSE,
    notas_procesamiento TEXT,
    metadatos JSONB DEFAULT '{}',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. PREGUNTAS PRINCIPALES
-- =======================================================

CREATE TABLE preguntas_icfes (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    
    -- Identificación básica
    id_pregunta_original INTEGER NOT NULL,     -- ID del Excel
    cuadernillo_id INTEGER REFERENCES cuadernillos_icfes(id),
    numero_pregunta VARCHAR(10),
    
    -- Clasificación taxonómica
    area_evaluacion_id INTEGER REFERENCES areas_evaluacion(id) NOT NULL,
    competencia_id INTEGER REFERENCES competencias_icfes(id),
    componente_id INTEGER REFERENCES componentes_conocimiento(id),
    proceso_cognitivo_id INTEGER REFERENCES procesos_cognitivos(id),
    tipo_conocimiento_id INTEGER REFERENCES tipos_conocimiento(id),
    contexto_aplicacion_id INTEGER REFERENCES contextos_aplicacion(id),
    
    -- Contenido principal
    pregunta_texto TEXT NOT NULL,
    afirmacion TEXT,                            -- Lo que se evalúa
    evidencia TEXT,                             -- Evidencia de aprendizaje
    
    -- Metadatos de dificultad
    nivel_dificultad INTEGER NOT NULL,         -- 1, 2, 3 del Excel
    nivel_desempeno_esperado VARCHAR(50),      -- 'Mínimo', 'Satisfactorio', 'Avanzado'
    tiempo_estimado_segundos INTEGER,          -- Tiempo estimado en segundos
    
    -- Clasificación temática
    area_tematica_id INTEGER REFERENCES areas_tematicas(id),
    tema_especifico_id INTEGER REFERENCES temas_especificos(id),
    grado_escolar INTEGER NOT NULL,
    
    -- Respuesta correcta
    respuesta_correcta CHAR(1) NOT NULL,       -- 'A', 'B', 'C', 'D'
    
    -- Gamificación
    puntos_xp INTEGER DEFAULT 20,
    
    -- Multimedia
    requiere_imagen BOOLEAN DEFAULT FALSE,
    imagen_pregunta_url VARCHAR(500),
    
    -- Estado y metadatos
    verificada BOOLEAN DEFAULT FALSE,
    activa BOOLEAN DEFAULT TRUE,
    
    -- Estadísticas de uso
    veces_preguntada INTEGER DEFAULT 0,
    veces_correcta INTEGER DEFAULT 0,
    tiempo_promedio_respuesta FLOAT DEFAULT 0,
    
    -- Timestamps
    fecha_aplicacion DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    CONSTRAINT nivel_dificultad_valido CHECK (nivel_dificultad BETWEEN 1 AND 5),
    CONSTRAINT respuesta_correcta_valida CHECK (respuesta_correcta IN ('A', 'B', 'C', 'D')),
    CONSTRAINT puntos_xp_positivos CHECK (puntos_xp > 0)
);

-- 5. OPCIONES DE RESPUESTA
-- =======================================================

CREATE TABLE opciones_respuesta (
    id SERIAL PRIMARY KEY,
    pregunta_id INTEGER REFERENCES preguntas_icfes(id) ON DELETE CASCADE,
    letra_opcion CHAR(1) NOT NULL,              -- 'A', 'B', 'C', 'D'
    texto_opcion TEXT NOT NULL,
    es_correcta BOOLEAN NOT NULL,
    imagen_opcion_url VARCHAR(500),
    
    -- Metadatos de análisis
    tipo_distractor VARCHAR(50),                -- Tipo de distractor si es incorrecta
    explicacion_opcion TEXT,                    -- Por qué es correcta o incorrecta
    
    orden INTEGER DEFAULT 0,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT letra_opcion_valida CHECK (letra_opcion IN ('A', 'B', 'C', 'D')),
    UNIQUE(pregunta_id, letra_opcion)
);

-- 6. SISTEMA DE AYUDAS Y EXPLICACIONES
-- =======================================================

CREATE TABLE pistas_pregunta (
    id SERIAL PRIMARY KEY,
    pregunta_id INTEGER REFERENCES preguntas_icfes(id) ON DELETE CASCADE,
    numero_pista INTEGER NOT NULL,              -- 1, 2, 3
    texto_pista TEXT NOT NULL,
    tipo_pista VARCHAR(50) DEFAULT 'CONCEPTUAL', -- 'CONCEPTUAL', 'PROCEDIMENTAL', 'ESTRATEGICA'
    rol_objetivo VARCHAR(20),                   -- Para personalizar por rol: 'TANK', 'DPS', etc.
    orden INTEGER DEFAULT 0,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT numero_pista_valido CHECK (numero_pista BETWEEN 1 AND 5),
    UNIQUE(pregunta_id, numero_pista)
);

CREATE TABLE explicaciones_respuesta (
    id SERIAL PRIMARY KEY,
    pregunta_id INTEGER REFERENCES preguntas_icfes(id) ON DELETE CASCADE,
    tipo_explicacion VARCHAR(50) NOT NULL,     -- 'SOLUCION', 'TEORIA', 'ESTRATEGIA'
    titulo VARCHAR(200),
    contenido TEXT NOT NULL,
    
    -- Personalización por rol
    rol_objetivo VARCHAR(20) DEFAULT 'ALL',    -- 'ALL', 'TANK', 'DPS', 'SUPPORT', 'SPECIALIST'
    nivel_detalle VARCHAR(20) DEFAULT 'MEDIO', -- 'BASICO', 'MEDIO', 'AVANZADO'
    
    -- Multimedia
    imagen_explicacion_url VARCHAR(500),
    video_explicacion_url VARCHAR(500),
    
    -- Metadatos
    dificultad_explicacion INTEGER DEFAULT 2,
    tiempo_lectura_estimado INTEGER,            -- Segundos
    
    orden INTEGER DEFAULT 0,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE errores_comunes (
    id SERIAL PRIMARY KEY,
    pregunta_id INTEGER REFERENCES preguntas_icfes(id) ON DELETE CASCADE,
    descripcion_error TEXT NOT NULL,
    opcion_elegida CHAR(1),                     -- Qué opción suelen elegir cuando cometen este error
    frecuencia_error FLOAT DEFAULT 0,           -- % de estudiantes que cometen este error
    explicacion_error TEXT,                     -- Por qué ocurre este error
    sugerencia_correccion TEXT,                 -- Cómo evitar el error
    
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT opcion_elegida_valida CHECK (opcion_elegida IN ('A', 'B', 'C', 'D') OR opcion_elegida IS NULL)
);

-- 7. RESPUESTAS DE USUARIOS (Integración con sistema existente)
-- =======================================================

CREATE TABLE respuestas_usuarios_icfes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,                   -- Referencia a la tabla users existente
    pregunta_id INTEGER REFERENCES preguntas_icfes(id),
    
    -- Respuesta del usuario
    opcion_seleccionada CHAR(1),
    es_correcta BOOLEAN NOT NULL,
    tiempo_respuesta_segundos INTEGER NOT NULL,
    nivel_confianza INTEGER,                    -- 1-5 (slider de confianza)
    
    -- Contexto de la sesión
    session_id VARCHAR(100),
    tipo_evaluacion VARCHAR(50),               -- 'PRACTICA', 'SIMULACRO', 'BATALLA'
    dispositivo VARCHAR(50),                   -- 'MOBILE', 'DESKTOP', 'TABLET'
    
    -- Ayudas utilizadas
    pistas_usadas INTEGER[] DEFAULT '{}',      -- Array de IDs de pistas utilizadas
    explicacion_solicitada BOOLEAN DEFAULT FALSE,
    tiempo_en_explicacion INTEGER DEFAULT 0,
    
    -- Gamificación
    xp_ganado INTEGER DEFAULT 0,
    bonus_aplicado VARCHAR(100),               -- Tipo de bonus aplicado
    
    -- Análisis de comportamiento
    intentos_respuesta INTEGER DEFAULT 1,
    cambio_respuesta BOOLEAN DEFAULT FALSE,
    patron_respuesta JSONB DEFAULT '{}',       -- Metadata del comportamiento
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT opcion_seleccionada_valida CHECK (opcion_seleccionada IN ('A', 'B', 'C', 'D') OR opcion_seleccionada IS NULL),
    CONSTRAINT nivel_confianza_valido CHECK (nivel_confianza BETWEEN 1 AND 5 OR nivel_confianza IS NULL),
    CONSTRAINT tiempo_respuesta_positivo CHECK (tiempo_respuesta_segundos > 0)
);

-- 8. ÍNDICES PARA OPTIMIZACIÓN
-- =======================================================

-- Índices para consultas frecuentes
CREATE INDEX idx_preguntas_area_dificultad ON preguntas_icfes(area_evaluacion_id, nivel_dificultad);
CREATE INDEX idx_preguntas_competencia ON preguntas_icfes(competencia_id);
CREATE INDEX idx_preguntas_tema ON preguntas_icfes(tema_especifico_id);
CREATE INDEX idx_preguntas_grado ON preguntas_icfes(grado_escolar);
CREATE INDEX idx_preguntas_activa ON preguntas_icfes(activa, verificada);

-- Índices para respuestas de usuarios
CREATE INDEX idx_respuestas_usuario ON respuestas_usuarios_icfes(user_id);
CREATE INDEX idx_respuestas_pregunta ON respuestas_usuarios_icfes(pregunta_id);
CREATE INDEX idx_respuestas_session ON respuestas_usuarios_icfes(session_id);
CREATE INDEX idx_respuestas_fecha ON respuestas_usuarios_icfes(created_at);

-- Índices para opciones
CREATE INDEX idx_opciones_pregunta ON opciones_respuesta(pregunta_id);

-- Índices para ayudas
CREATE INDEX idx_pistas_pregunta ON pistas_pregunta(pregunta_id);
CREATE INDEX idx_explicaciones_pregunta ON explicaciones_respuesta(pregunta_id);

-- 9. DATOS INICIALES BASADOS EN EL EXCEL
-- =======================================================

-- Insertar áreas de evaluación
INSERT INTO areas_evaluacion (codigo, nombre, descripcion, color_tema) VALUES 
('MATEMATICAS', 'Matemáticas', 'Competencias matemáticas para educación media', '#FF6B35'),
('LECTURA_CRITICA', 'Lectura Crítica', 'Competencias de comprensión lectora', '#4ECDC4'),
('CIENCIAS_NATURALES', 'Ciencias Naturales', 'Competencias científicas', '#45B7D1'),
('SOCIALES_CIUDADANAS', 'Sociales y Ciudadanas', 'Competencias cívicas y sociales', '#96CEB4'),
('INGLES', 'Inglés', 'Competencias en segunda lengua', '#FFEAA7');

-- Insertar competencias de matemáticas (basado en los datos del Excel)
INSERT INTO competencias_icfes (area_evaluacion_id, codigo, nombre, descripcion) VALUES 
(1, 'INTERPRETACION_REPRESENTACION', 'Interpretación y representación', 'Interpretar información presentada en diversos formatos'),
(1, 'ARGUMENTACION', 'Argumentación', 'Justificar la validez de afirmaciones usando propiedades matemáticas'),
(1, 'FORMULACION_EJECUCION', 'Formulación y ejecución', 'Formular estrategias para resolver problemas');

-- Insertar procesos cognitivos
INSERT INTO procesos_cognitivos (codigo, nombre, descripcion, nivel_bloom) VALUES 
('INTERPRETACION', 'Interpretación', 'Comprensión e interpretación de información', 2),
('ARGUMENTACION', 'Argumentación', 'Justificación y validación de afirmaciones', 5),
('PROPOSICION', 'Proposición', 'Formulación de estrategias y soluciones', 4);

-- Insertar tipos de conocimiento
INSERT INTO tipos_conocimiento (codigo, nombre, descripcion) VALUES 
('GENERICO', 'Genérico', 'Conocimientos generales aplicables en diversos contextos'),
('ESPECIFICO', 'Específico', 'Conocimientos específicos de un dominio particular');

-- Insertar contextos de aplicación
INSERT INTO contextos_aplicacion (codigo, nombre, descripcion) VALUES 
('COMUNITARIO_SOCIAL', 'Comunitario/social', 'Situaciones del ámbito comunitario y social'),
('PERSONAL_FAMILIAR', 'Personal/familiar', 'Situaciones del ámbito personal y familiar'),
('LABORAL_OCUPACIONAL', 'Laboral/ocupacional', 'Situaciones del ámbito laboral y ocupacional'),
('ACADEMICO_CIENTIFICO', 'Académico/científico', 'Situaciones del ámbito académico y científico');

-- Insertar áreas temáticas de matemáticas
INSERT INTO areas_tematicas (area_evaluacion_id, codigo, nombre, descripcion, color_tema) VALUES 
(1, 'ARITMETICA_OPERACIONES', 'Aritmética y Operaciones Básicas', 'Operaciones fundamentales, porcentajes, proporciones', '#FF6B35'),
(1, 'PROBLEMAS_APLICADOS', 'Problemas Aplicados y Análisis', 'Problemas contextualizados y análisis cuantitativo', '#FF8A50');

-- Insertar período de aplicación
INSERT INTO periodos_aplicacion (codigo, nombre, fecha_inicio, fecha_fin) VALUES 
('2024-1', '2024 Período 1', '2024-02-01', '2024-06-30'),
('2024-2', '2024 Período 2', '2024-08-01', '2024-12-31');

-- =======================================================
-- VISTAS ÚTILES PARA CONSULTAS
-- =======================================================

-- Vista completa de preguntas con toda la taxonomía
CREATE VIEW vista_preguntas_completa AS
SELECT 
    p.id,
    p.uuid,
    p.id_pregunta_original,
    p.numero_pregunta,
    
    -- Taxonomía
    ae.nombre AS area_evaluada,
    c.nombre AS competencia,
    cc.nombre AS componente,
    pc.nombre AS proceso_cognitivo,
    tc.nombre AS tipo_conocimiento,
    ca.nombre AS contexto_aplicacion,
    
    -- Contenido
    p.pregunta_texto,
    p.afirmacion,
    p.evidencia,
    
    -- Dificultad
    p.nivel_dificultad,
    p.nivel_desempeno_esperado,
    p.tiempo_estimado_segundos,
    
    -- Temática
    at.nombre AS area_tematica,
    te.nombre AS tema_especifico,
    p.grado_escolar,
    
    -- Respuesta
    p.respuesta_correcta,
    p.puntos_xp,
    
    -- Multimedia
    p.requiere_imagen,
    p.imagen_pregunta_url,
    
    -- Estadísticas
    p.veces_preguntada,
    p.veces_correcta,
    CASE 
        WHEN p.veces_preguntada > 0 THEN (p.veces_correcta::FLOAT / p.veces_preguntada * 100)
        ELSE 0 
    END AS porcentaje_acierto,
    
    -- Metadatos
    p.verificada,
    p.activa,
    p.fecha_aplicacion,
    p.created_at

FROM preguntas_icfes p
JOIN areas_evaluacion ae ON p.area_evaluacion_id = ae.id
LEFT JOIN competencias_icfes c ON p.competencia_id = c.id
LEFT JOIN componentes_conocimiento cc ON p.componente_id = cc.id
LEFT JOIN procesos_cognitivos pc ON p.proceso_cognitivo_id = pc.id
LEFT JOIN tipos_conocimiento tc ON p.tipo_conocimiento_id = tc.id
LEFT JOIN contextos_aplicacion ca ON p.contexto_aplicacion_id = ca.id
LEFT JOIN areas_tematicas at ON p.area_tematica_id = at.id
LEFT JOIN temas_especificos te ON p.tema_especifico_id = te.id;

-- Vista de estadísticas por área
CREATE VIEW estadisticas_por_area AS
SELECT 
    ae.nombre AS area,
    COUNT(p.id) AS total_preguntas,
    COUNT(CASE WHEN p.verificada THEN 1 END) AS preguntas_verificadas,
    COUNT(CASE WHEN p.activa THEN 1 END) AS preguntas_activas,
    AVG(p.nivel_dificultad) AS dificultad_promedio,
    AVG(p.tiempo_estimado_segundos) AS tiempo_promedio,
    SUM(p.veces_preguntada) AS total_respuestas,
    AVG(CASE WHEN p.veces_preguntada > 0 THEN (p.veces_correcta::FLOAT / p.veces_preguntada * 100) ELSE 0 END) AS porcentaje_acierto_promedio
FROM areas_evaluacion ae
LEFT JOIN preguntas_icfes p ON ae.id = p.area_evaluacion_id
GROUP BY ae.id, ae.nombre
ORDER BY ae.nombre;

-- =======================================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- =======================================================

COMMENT ON TABLE preguntas_icfes IS 'Tabla principal de preguntas ICFES basada en la estructura del archivo Excel oficial';
COMMENT ON COLUMN preguntas_icfes.id_pregunta_original IS 'ID original del archivo Excel (1-49)';
COMMENT ON COLUMN preguntas_icfes.nivel_dificultad IS 'Nivel de dificultad: 1=Fácil, 2=Medio, 3=Difícil (del Excel)';
COMMENT ON COLUMN preguntas_icfes.puntos_xp IS 'Puntos de experiencia otorgados (20-40 según Excel)';
COMMENT ON VIEW vista_preguntas_completa IS 'Vista desnormalizada con toda la información de taxonomía para consultas rápidas'; 