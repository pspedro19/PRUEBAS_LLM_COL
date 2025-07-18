-- =====================================================
-- MIGRACIONES SQL PARA FASE 1
-- Base de datos: PostgreSQL
-- =====================================================

-- 1. CREAR TABLAS DE LEARNING PATHS
-- =====================================================

-- Tabla principal de Learning Paths
CREATE TABLE IF NOT EXISTS learning_paths (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    color_theme VARCHAR(7) DEFAULT '#6B46C1',
    order_index INTEGER DEFAULT 0,
    area_evaluacion_id INTEGER REFERENCES areas_evaluacion(id) ON DELETE CASCADE,
    estimated_hours INTEGER DEFAULT 10,
    total_nodes INTEGER DEFAULT 0,
    difficulty_level VARCHAR(20) DEFAULT 'beginner',
    is_premium BOOLEAN DEFAULT FALSE,
    unlock_requirements JSONB DEFAULT '{}',
    completion_xp INTEGER DEFAULT 1000,
    completion_rewards JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_difficulty_level CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced', 'expert'))
);

-- Índices para learning_paths
CREATE INDEX idx_learning_paths_slug ON learning_paths(slug);
CREATE INDEX idx_learning_paths_area_order ON learning_paths(area_evaluacion_id, order_index);

-- Tabla de nodos del Learning Path
CREATE TABLE IF NOT EXISTS learning_path_nodes (
    id SERIAL PRIMARY KEY,
    path_id INTEGER REFERENCES learning_paths(id) ON DELETE CASCADE,
    parent_node_id INTEGER REFERENCES learning_path_nodes(id) ON DELETE SET NULL,
    node_type VARCHAR(50) DEFAULT 'lesson',
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(255),
    icon_emoji VARCHAR(10) DEFAULT '📚',
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    order_index INTEGER DEFAULT 0,
    is_locked BOOLEAN DEFAULT TRUE,
    unlock_requirements JSONB DEFAULT '{}',
    content JSONB DEFAULT '{}',
    questions_count INTEGER DEFAULT 10,
    passing_score INTEGER DEFAULT 70 CHECK (passing_score >= 0 AND passing_score <= 100),
    allow_hints BOOLEAN DEFAULT TRUE,
    lives_count INTEGER DEFAULT 3,
    base_xp_reward INTEGER DEFAULT 100,
    perfect_bonus_xp INTEGER DEFAULT 50,
    speed_bonus_xp INTEGER DEFAULT 30,
    coin_reward INTEGER DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_node_type CHECK (node_type IN ('lesson', 'checkpoint', 'boss_battle', 'review', 'bonus')),
    CONSTRAINT unique_node_position UNIQUE (path_id, position_x, position_y)
);

-- Índices para nodes
CREATE INDEX idx_learning_path_nodes_path_order ON learning_path_nodes(path_id, order_index);
CREATE INDEX idx_learning_path_nodes_type ON learning_path_nodes(node_type);

-- Tabla de progreso del usuario
CREATE TABLE IF NOT EXISTS user_path_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    path_id INTEGER REFERENCES learning_paths(id) ON DELETE CASCADE,
    current_node_id INTEGER REFERENCES learning_path_nodes(id) ON DELETE SET NULL,
    nodes_completed INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    nodes_unlocked INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    completion_percentage DECIMAL(5,2) DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    total_xp_earned INTEGER DEFAULT 0,
    total_coins_earned INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    total_time_spent_minutes INTEGER DEFAULT 0,
    average_score DECIMAL(5,2) DEFAULT 0,
    perfect_nodes_count INTEGER DEFAULT 0,
    total_attempts INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT unique_user_path UNIQUE (user_id, path_id)
);

-- Índices para progreso
CREATE INDEX idx_user_path_progress_user_completion ON user_path_progress(user_id, completion_percentage);
CREATE INDEX idx_user_path_progress_activity ON user_path_progress(last_activity);

-- Tabla de intentos en nodos
CREATE TABLE IF NOT EXISTS node_attempts (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    node_id INTEGER REFERENCES learning_path_nodes(id) ON DELETE CASCADE,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    passed BOOLEAN DEFAULT FALSE,
    is_perfect BOOLEAN DEFAULT FALSE,
    lives_remaining INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    coins_earned INTEGER DEFAULT 0,
    bonuses_earned JSONB DEFAULT '[]',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Índices para attempts
CREATE INDEX idx_node_attempts_user_node_date ON node_attempts(user_id, node_id, started_at DESC);

-- 2. CREAR TABLAS DE SIMULACROS
-- =====================================================

-- Tabla principal de simulacros
CREATE TABLE IF NOT EXISTS simulacros (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    code VARCHAR(50) UNIQUE NOT NULL,
    duration_minutes INTEGER DEFAULT 270,
    total_questions INTEGER DEFAULT 0,
    question_distribution JSONB DEFAULT '{}',
    difficulty_level VARCHAR(20) DEFAULT 'medium',
    is_official BOOLEAN DEFAULT FALSE,
    is_diagnostic BOOLEAN DEFAULT FALSE,
    allows_pause BOOLEAN DEFAULT TRUE,
    shows_timer BOOLEAN DEFAULT TRUE,
    min_level_required INTEGER DEFAULT 1,
    is_premium BOOLEAN DEFAULT FALSE,
    unlock_requirements JSONB DEFAULT '{}',
    times_taken INTEGER DEFAULT 0,
    average_score DECIMAL(5,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_simulacro_difficulty CHECK (difficulty_level IN ('easy', 'medium', 'hard', 'realistic'))
);

-- Índices para simulacros
CREATE INDEX idx_simulacros_code ON simulacros(code);
CREATE INDEX idx_simulacros_difficulty_active ON simulacros(difficulty_level, is_active);

-- Tabla de sesiones de simulacro
CREATE TABLE IF NOT EXISTS simulacro_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    simulacro_id INTEGER REFERENCES simulacros(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'not_started',
    session_uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    current_section VARCHAR(50),
    current_question_index INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    sections_completed VARCHAR(50)[] DEFAULT ARRAY[]::VARCHAR(50)[],
    time_spent_seconds INTEGER DEFAULT 0,
    time_remaining_seconds INTEGER,
    pause_count INTEGER DEFAULT 0,
    total_pause_time_seconds INTEGER DEFAULT 0,
    score_total INTEGER,
    percentil_nacional INTEGER,
    areas_scores JSONB DEFAULT '{}',
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_session_status CHECK (status IN ('not_started', 'in_progress', 'paused', 'completed', 'abandoned'))
);

-- Índices para sesiones
CREATE INDEX idx_simulacro_sessions_user_status ON simulacro_sessions(user_id, status);
CREATE INDEX idx_simulacro_sessions_uuid ON simulacro_sessions(session_uuid);
CREATE INDEX idx_simulacro_sessions_created ON simulacro_sessions(created_at DESC);

-- Tabla de respuestas en simulacros
CREATE TABLE IF NOT EXISTS simulacro_answers (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES simulacro_sessions(id) ON DELETE CASCADE,
    pregunta_id UUID REFERENCES preguntas_icfes(uuid) ON DELETE CASCADE,
    section VARCHAR(50) NOT NULL,
    question_number INTEGER NOT NULL,
    selected_option VARCHAR(1),
    is_correct BOOLEAN DEFAULT FALSE,
    time_spent_seconds INTEGER DEFAULT 0,
    changed_answer BOOLEAN DEFAULT FALSE,
    marked_for_review BOOLEAN DEFAULT FALSE,
    confidence_level INTEGER CHECK (confidence_level >= 1 AND confidence_level <= 5),
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_session_question UNIQUE (session_id, pregunta_id)
);

-- Índices para respuestas
CREATE INDEX idx_simulacro_answers_session_section ON simulacro_answers(session_id, section);
CREATE INDEX idx_simulacro_answers_correct ON simulacro_answers(is_correct);

-- 3. CREAR TABLAS DE CONTENIDO EDUCATIVO
-- =====================================================

-- Tabla principal de contenido educativo
CREATE TABLE IF NOT EXISTS educational_content (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(255),
    slug VARCHAR(255) UNIQUE NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    description TEXT,
    summary VARCHAR(500),
    url VARCHAR(500),
    embed_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    preview_url VARCHAR(500),
    area_evaluacion_id INTEGER REFERENCES areas_evaluacion(id) ON DELETE SET NULL,
    duration_seconds INTEGER,
    reading_time_minutes INTEGER,
    difficulty_level VARCHAR(20) DEFAULT 'intermediate',
    tags VARCHAR(50)[] DEFAULT ARRAY[]::VARCHAR(50)[],
    keywords TEXT,
    author_name VARCHAR(255),
    author_bio TEXT,
    source_name VARCHAR(255),
    source_url VARCHAR(500),
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0 CHECK (average_rating >= 0 AND average_rating <= 5),
    rating_count INTEGER DEFAULT 0,
    is_premium BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    published_at TIMESTAMP,
    meta_title VARCHAR(255),
    meta_description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_content_type CHECK (content_type IN ('video', 'article', 'infographic', 'podcast', 'interactive', 'pdf')),
    CONSTRAINT check_content_difficulty CHECK (difficulty_level IN ('basic', 'intermediate', 'advanced'))
);

-- Índices para contenido
CREATE INDEX idx_educational_content_type_active ON educational_content(content_type, is_active);
CREATE INDEX idx_educational_content_area_difficulty ON educational_content(area_evaluacion_id, difficulty_level);
CREATE INDEX idx_educational_content_views ON educational_content(view_count DESC);
CREATE INDEX idx_educational_content_slug ON educational_content(slug);
CREATE INDEX idx_educational_content_uuid ON educational_content(uuid);

-- Tabla de relación contenido-competencias
CREATE TABLE IF NOT EXISTS educational_content_competencias (
    content_id INTEGER REFERENCES educational_content(id) ON DELETE CASCADE,
    competencia_id INTEGER REFERENCES competencias_icfes(id) ON DELETE CASCADE,
    PRIMARY KEY (content_id, competencia_id)
);

-- Tabla de relación contenido-componentes
CREATE TABLE IF NOT EXISTS educational_content_componentes (
    content_id INTEGER REFERENCES educational_content(id) ON DELETE CASCADE,
    componente_id INTEGER REFERENCES componentes_conocimiento(id) ON DELETE CASCADE,
    PRIMARY KEY (content_id, componente_id)
);

-- Tabla de explicaciones de preguntas
CREATE TABLE IF NOT EXISTS question_explanations (
    id SERIAL PRIMARY KEY,
    pregunta_id UUID REFERENCES preguntas_icfes(uuid) ON DELETE CASCADE,
    explanation_type VARCHAR(50) DEFAULT 'text',
    title VARCHAR(255) DEFAULT 'Explicación',
    content TEXT NOT NULL,
    summary VARCHAR(500),
    steps JSONB DEFAULT '[]',
    visual_aids JSONB DEFAULT '{}',
    common_mistakes TEXT[] DEFAULT ARRAY[]::TEXT[],
    pro_tips TEXT[] DEFAULT ARRAY[]::TEXT[],
    memory_tricks TEXT,
    key_concepts VARCHAR(100)[] DEFAULT ARRAY[]::VARCHAR(100)[],
    prerequisites VARCHAR(100)[] DEFAULT ARRAY[]::VARCHAR(100)[],
    difficulty_addressed VARCHAR(20),
    is_official BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_explanation_type CHECK (explanation_type IN ('text', 'video', 'step_by_step', 'visual', 'ai_generated')),
    CONSTRAINT check_difficulty_addressed CHECK (difficulty_addressed IN ('conceptual', 'procedural', 'calculation', 'interpretation', 'careless'))
);

-- Índices para explicaciones
CREATE INDEX idx_question_explanations_pregunta_type ON question_explanations(pregunta_id, explanation_type);
CREATE INDEX idx_question_explanations_official_active ON question_explanations(is_official, is_active);

-- Tabla de interacciones usuario-contenido
CREATE TABLE IF NOT EXISTS user_content_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER REFERENCES educational_content(id) ON DELETE CASCADE,
    interaction_type VARCHAR(20) NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    watch_percentage INTEGER DEFAULT 0 CHECK (watch_percentage >= 0 AND watch_percentage <= 100),
    time_spent_seconds INTEGER DEFAULT 0,
    notes TEXT,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_content_interaction UNIQUE (user_id, content_id, interaction_type),
    CONSTRAINT check_interaction_type CHECK (interaction_type IN ('view', 'like', 'dislike', 'save', 'share', 'complete', 'rating'))
);

-- Índices para interacciones
CREATE INDEX idx_user_content_interactions_user_type ON user_content_interactions(user_id, interaction_type);
CREATE INDEX idx_user_content_interactions_content_type ON user_content_interactions(content_id, interaction_type);
CREATE INDEX idx_user_content_interactions_created ON user_content_interactions(created_at DESC);

-- Tabla de feedback de explicaciones
CREATE TABLE IF NOT EXISTS explanation_feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    explanation_id INTEGER REFERENCES question_explanations(id) ON DELETE CASCADE,
    is_helpful BOOLEAN NOT NULL,
    feedback_text TEXT,
    issue_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_explanation_feedback UNIQUE (user_id, explanation_id),
    CONSTRAINT check_issue_type CHECK (issue_type IN ('too_complex', 'too_simple', 'incorrect', 'confusing', 'missing_info', 'other'))
);

-- Índices para feedback
CREATE INDEX idx_explanation_feedback_explanation_helpful ON explanation_feedback(explanation_id, is_helpful);
CREATE INDEX idx_explanation_feedback_created ON explanation_feedback(created_at DESC);

-- Tabla de recomendaciones de contenido
CREATE TABLE IF NOT EXISTS content_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER REFERENCES educational_content(id) ON DELETE CASCADE,
    reason VARCHAR(50) NOT NULL,
    reason_detail TEXT,
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    context_data JSONB DEFAULT '{}',
    is_seen BOOLEAN DEFAULT FALSE,
    is_clicked BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    was_helpful BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    seen_at TIMESTAMP,
    expires_at TIMESTAMP,
    CONSTRAINT check_recommendation_reason CHECK (reason IN ('weak_area', 'similar_users', 'trending', 'new_content', 'follow_up', 'ai_suggested'))
);

-- Índices para recomendaciones
CREATE INDEX idx_content_recommendations_user_seen_priority ON content_recommendations(user_id, is_seen, priority DESC);
CREATE INDEX idx_content_recommendations_reason_created ON content_recommendations(reason, created_at DESC);

-- 4. FUNCIONES Y TRIGGERS
-- =====================================================

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar triggers a todas las tablas nuevas
CREATE TRIGGER update_learning_paths_updated_at BEFORE UPDATE ON learning_paths
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_path_nodes_updated_at BEFORE UPDATE ON learning_path_nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_simulacros_updated_at BEFORE UPDATE ON simulacros
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_educational_content_updated_at BEFORE UPDATE ON educational_content
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_question_explanations_updated_at BEFORE UPDATE ON question_explanations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_content_interactions_updated_at BEFORE UPDATE ON user_content_interactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 5. VISTAS ÚTILES
-- =====================================================

-- Vista para el dashboard de progreso del usuario
CREATE OR REPLACE VIEW v_user_learning_dashboard AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT upp.path_id) as paths_started,
    COUNT(DISTINCT CASE WHEN upp.completion_percentage = 100 THEN upp.path_id END) as paths_completed,
    AVG(upp.completion_percentage) as avg_completion,
    SUM(upp.total_xp_earned) as total_xp_from_paths,
    MAX(upp.last_activity) as last_learning_activity
FROM users u
LEFT JOIN user_path_progress upp ON u.id = upp.user_id
GROUP BY u.id, u.username;

-- Vista para contenido popular
CREATE OR REPLACE VIEW v_popular_content AS
SELECT 
    ec.*,
    COUNT(DISTINCT uci.user_id) as unique_viewers,
    AVG(CASE WHEN uci.rating IS NOT NULL THEN uci.rating END) as calculated_rating
FROM educational_content ec
LEFT JOIN user_content_interactions uci ON ec.id = uci.content_id
WHERE ec.is_active = true
GROUP BY ec.id
ORDER BY ec.view_count DESC, unique_viewers DESC;

-- 6. DATOS INICIALES DE EJEMPLO
-- =====================================================

-- Insertar algunos learning paths de ejemplo
INSERT INTO learning_paths (name, slug, description, area_evaluacion_id, difficulty_level, estimated_hours)
SELECT 
    'Fundamentos de ' || ae.nombre,
    'fundamentos-' || ae.codigo,
    'Aprende los conceptos básicos de ' || ae.nombre,
    ae.id,
    'beginner',
    20
FROM areas_evaluacion ae
WHERE ae.activa = true
LIMIT 5;

-- Insertar nodos de ejemplo para cada path
INSERT INTO learning_path_nodes (path_id, title, node_type, order_index, position_x, position_y)
SELECT 
    lp.id,
    'Introducción a ' || lp.name,
    'lesson',
    1,
    0,
    0
FROM learning_paths lp;

-- GRANT permisos necesarios
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tu_usuario_django;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tu_usuario_django;
