-- ICFES AI Tutor - Database Initialization Script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial question areas
INSERT INTO question_areas (id, name, display_name, description, icon_url, color_hex, order_index, is_active) VALUES
(uuid_generate_v4(), 'matematicas', 'Matemáticas', 'Álgebra, geometría, estadística y probabilidad', '/icons/calculator.svg', '#3B82F6', 1, true),
(uuid_generate_v4(), 'lectura_critica', 'Lectura Crítica', 'Comprensión de textos y análisis crítico', '/icons/book.svg', '#10B981', 2, true),
(uuid_generate_v4(), 'ciencias_naturales', 'Ciencias Naturales', 'Física, química y biología', '/icons/brain.svg', '#8B5CF6', 3, true),
(uuid_generate_v4(), 'ciencias_sociales', 'Ciencias Sociales', 'Historia, geografía y ciudadanía', '/icons/users.svg', '#F59E0B', 4, true),
(uuid_generate_v4(), 'ingles', 'Inglés', 'Comprensión lectora y uso del idioma', '/icons/globe.svg', '#EF4444', 5, true);

-- Create sample questions for Mathematics
DO $$
DECLARE
    math_question_id uuid := uuid_generate_v4();
BEGIN
    -- Sample Math Question 1
    INSERT INTO questions (
        id, question_text, question_type, subject_area, options, correct_answer,
        competencia, sub_competencia, contexto, nivel_bloom, difficulty_level,
        estimated_time_seconds, status, created_at
    ) VALUES (
        math_question_id,
        'Si f(x) = 2x + 3 y g(x) = x² - 1, ¿cuál es el valor de f(g(2))?',
        'multiple_choice',
        'matematicas',
        '["A) 9", "B) 8", "C) 7", "D) 6"]',
        'A',
        'Formulación y ejecución',
        'Composición de funciones',
        'cientifico',
        'aplicar',
        'medium',
        120,
        'active',
        NOW()
    );

    -- Insert IRT parameters for the question
    INSERT INTO irt_parameters (
        id, question_id, discrimination_a, difficulty_b, guessing_c,
        is_calibrated, last_calibrated, created_at
    ) VALUES (
        uuid_generate_v4(),
        math_question_id,
        1.2,
        0.5,
        0.25,
        true,
        NOW(),
        NOW()
    );
END $$;

-- Sample Math Question 2
DO $$
DECLARE
    math_question_id2 uuid := uuid_generate_v4();
BEGIN
    INSERT INTO questions (
        id, question_text, question_type, subject_area, options, correct_answer,
        competencia, sub_competencia, contexto, nivel_bloom, difficulty_level,
        estimated_time_seconds, status, created_at
    ) VALUES (
        math_question_id2,
        'En un triángulo rectángulo, si un cateto mide 3 cm y la hipotenusa mide 5 cm, ¿cuánto mide el otro cateto?',
        'multiple_choice',
        'matematicas',
        '["A) 4 cm", "B) 3 cm", "C) 5 cm", "D) 6 cm"]',
        'A',
        'Interpretación y representación',
        'Teorema de Pitágoras',
        'personal',
        'aplicar',
        'easy',
        90,
        'active',
        NOW()
    );

    INSERT INTO irt_parameters (
        id, question_id, discrimination_a, difficulty_b, guessing_c,
        is_calibrated, last_calibrated, created_at
    ) VALUES (
        uuid_generate_v4(),
        math_question_id2,
        1.5,
        -0.8,
        0.25,
        true,
        NOW(),
        NOW()
    );
END $$;

-- Sample Reading Question
DO $$
DECLARE
    reading_question_id uuid := uuid_generate_v4();
BEGIN
    INSERT INTO questions (
        id, question_text, question_type, subject_area, options, correct_answer,
        competencia, sub_competencia, contexto, nivel_bloom, difficulty_level,
        estimated_time_seconds, status, created_at
    ) VALUES (
        reading_question_id,
        'Según el texto: "La biodiversidad es fundamental para el equilibrio de los ecosistemas. Sin embargo, las actividades humanas han provocado una pérdida acelerada de especies." ¿Cuál es la idea principal del fragmento?',
        'multiple_choice',
        'lectura_critica',
        '["A) Las actividades humanas son beneficiosas", "B) La biodiversidad está en peligro por acción humana", "C) Los ecosistemas no necesitan equilibrio", "D) Las especies se pierden naturalmente"]',
        'B',
        'Comprender estructura global',
        'Identificación de idea principal',
        'social',
        'comprender',
        'medium',
        150,
        'active',
        NOW()
    );

    INSERT INTO irt_parameters (
        id, question_id, discrimination_a, difficulty_b, guessing_c,
        is_calibrated, last_calibrated, created_at
    ) VALUES (
        uuid_generate_v4(),
        reading_question_id,
        1.3,
        0.2,
        0.25,
        true,
        NOW(),
        NOW()
    );
END $$;

-- Sample Science Question
DO $$
DECLARE
    science_question_id uuid := uuid_generate_v4();
BEGIN
    INSERT INTO questions (
        id, question_text, question_type, subject_area, options, correct_answer,
        competencia, sub_competencia, contexto, nivel_bloom, difficulty_level,
        estimated_time_seconds, status, created_at
    ) VALUES (
        science_question_id,
        'En la reacción: 2H₂ + O₂ → 2H₂O, si tenemos 4 moles de H₂ y 2 moles de O₂, ¿cuántos moles de agua se pueden formar?',
        'multiple_choice',
        'ciencias_naturales',
        '["A) 2 moles", "B) 4 moles", "C) 6 moles", "D) 8 moles"]',
        'B',
        'Uso comprensivo del conocimiento científico',
        'Estequiometría',
        'cientifico',
        'aplicar',
        'hard',
        180,
        'active',
        NOW()
    );

    INSERT INTO irt_parameters (
        id, question_id, discrimination_a, difficulty_b, guessing_c,
        is_calibrated, last_calibrated, created_at
    ) VALUES (
        uuid_generate_v4(),
        science_question_id,
        1.4,
        1.2,
        0.25,
        true,
        NOW(),
        NOW()
    );
END $$;

-- Sample English Question
DO $$
DECLARE
    english_question_id uuid := uuid_generate_v4();
BEGIN
    INSERT INTO questions (
        id, question_text, question_type, subject_area, options, correct_answer,
        competencia, sub_competencia, contexto, nivel_bloom, difficulty_level,
        estimated_time_seconds, status, created_at
    ) VALUES (
        english_question_id,
        'Choose the correct form: "She _____ to work every day by bus."',
        'multiple_choice',
        'ingles',
        '["A) go", "B) goes", "C) going", "D) gone"]',
        'B',
        'Uso del inglés',
        'Presente simple',
        'personal',
        'aplicar',
        'easy',
        60,
        'active',
        NOW()
    );

    INSERT INTO irt_parameters (
        id, question_id, discrimination_a, difficulty_b, guessing_c,
        is_calibrated, last_calibrated, created_at
    ) VALUES (
        uuid_generate_v4(),
        english_question_id,
        1.1,
        -1.0,
        0.25,
        true,
        NOW(),
        NOW()
    );
END $$;

-- Crear usuarios de prueba
INSERT INTO users (
    id,
    email,
    full_name,
    hashed_password,
    auth_provider,
    role,
    is_active,
    is_verified,
    created_at
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    'admin@icfes.com',
    'Administrador ICFES',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGRl3O5BK.K', -- hash de 'admin123'
    'email',
    'admin',
    true,
    true,
    CURRENT_TIMESTAMP
),
(
    '22222222-2222-2222-2222-222222222222',
    'estudiante@ejemplo.com',
    'Estudiante Ejemplo',
    '$2b$12$k8Y6XJU7lxjsL/Vp.WuJCO3pXHxE5qPV7xQoV3OIFH9EmQpzF9JB2', -- hash de 'user123'
    'email',
    'student',
    true,
    true,
    CURRENT_TIMESTAMP
);

-- Crear perfiles de usuario
INSERT INTO user_profiles (
    id,
    user_id,
    grade,
    institution,
    timezone,
    language,
    created_at
) VALUES (
    '33333333-3333-3333-3333-333333333333',
    '11111111-1111-1111-1111-111111111111',
    NULL,
    'ICFES',
    'America/Bogota',
    'es',
    CURRENT_TIMESTAMP
),
(
    '44444444-4444-4444-4444-444444444444',
    '22222222-2222-2222-2222-222222222222',
    '11',
    'Colegio Ejemplo',
    'America/Bogota',
    'es',
    CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_questions_subject_status ON questions(subject_area, status);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_user_responses_user_date ON user_responses(user_id, answered_at);
CREATE INDEX IF NOT EXISTS idx_irt_parameters_calibrated ON irt_parameters(is_calibrated);

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully!';
    RAISE NOTICE 'Sample questions created for all areas';
    RAISE NOTICE 'Admin user: admin@icfes.com / admin123';
    RAISE NOTICE 'Test user: estudiante@ejemplo.com / user123';
END $$; 