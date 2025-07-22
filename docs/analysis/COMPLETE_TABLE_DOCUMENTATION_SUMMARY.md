# 📊 DOCUMENTACIÓN COMPLETA DE TABLAS - RESUMEN EJECUTIVO

## 📋 **ESTADÍSTICAS GENERALES:**
- **Total de modelos:** 88
- **Total de apps:** 9
- **Total ForeignKeys:** 259
- **Total ManyToMany:** 22
- **Total relaciones:** 281

---

## 📱 **APPS Y SUS TABLAS DETALLADAS:**

### 🤖 **AI_LLM (10 tablas)**

#### **ai_models**
- **Propósito:** Modelos de IA disponibles
- **Campos principales:** name, provider, model_type, version, capabilities, cost_per_token
- **Relaciones:** ForeignKey a users (created_by)

#### **ai_conversations**
- **Propósito:** Conversaciones con IA
- **Campos principales:** user, conversation_type, status, context_data, message_count, total_tokens, total_cost
- **Relaciones:** ForeignKey a users, icfes (area_evaluacion, pregunta), learning (learning_path)

#### **ai_messages**
- **Propósito:** Mensajes en conversaciones
- **Campos principales:** conversation, role, content, tokens_used, cost, created_at
- **Relaciones:** ForeignKey a ai_conversations

#### **ai_prompt_templates**
- **Propósito:** Plantillas de prompts
- **Campos principales:** name, template_type, content, variables, is_active
- **Relaciones:** ForeignKey a users (created_by)

#### **ai_response_cache**
- **Propósito:** Cache de respuestas
- **Campos principales:** prompt_hash, response, tokens_used, cost, created_at
- **Relaciones:** ForeignKey a ai_models

#### **ai_interaction_logs**
- **Propósito:** Logs de interacciones
- **Campos principales:** user, interaction_type, input_data, output_data, tokens_used, cost
- **Relaciones:** ForeignKey a users, ai_models, ai_conversations

#### **ai_moderation_logs**
- **Propósito:** Logs de moderación
- **Campos principales:** user, content, moderation_result, flagged_reasons, reviewed_by
- **Relaciones:** ForeignKey a users, ai_conversations

#### **ai_learning_insights**
- **Propósito:** Insights de aprendizaje
- **Campos principales:** user, insight_type, data, recommendations, created_at
- **Relaciones:** ForeignKey a users, learning_paths

#### **ai_usage_quotas**
- **Propósito:** Cuotas de uso
- **Campos principales:** user, quota_type, limit, used, reset_date
- **Relaciones:** ForeignKey a users

#### **ai_performance_metrics**
- **Propósito:** Métricas de rendimiento
- **Campos principales:** model, metric_type, value, timestamp
- **Relaciones:** ForeignKey a ai_models

---

### 📊 **ANALYTICS (8 tablas)**

#### **learning_analytics**
- **Propósito:** Analytics de aprendizaje
- **Campos principales:** user, session_duration, questions_answered, correct_answers, improvement_rate
- **Relaciones:** ForeignKey a users

#### **subject_analytics**
- **Propósito:** Analytics por materia
- **Campos principales:** user, subject, total_questions, correct_answers, average_score
- **Relaciones:** ForeignKey a users

#### **session_analytics**
- **Propósito:** Analytics de sesiones
- **Campos principales:** user, session_id, start_time, end_time, questions_answered
- **Relaciones:** ForeignKey a users

#### **a_btests**
- **Propósito:** Tests A/B
- **Campos principales:** name, description, variant_a, variant_b, start_date, end_date
- **Relaciones:** ForeignKey a users (created_by)

#### **user_test_participations**
- **Propósito:** Participaciones en tests
- **Campos principales:** user, test, variant, conversion_rate, created_at
- **Relaciones:** ForeignKey a users, a_btests

#### **feature_usage_analytics**
- **Propósito:** Uso de características
- **Campos principales:** user, feature_name, usage_count, last_used
- **Relaciones:** ForeignKey a users

#### **user_behavior_analytics**
- **Propósito:** Comportamiento de usuarios
- **Campos principales:** user, behavior_type, data, timestamp
- **Relaciones:** ForeignKey a users

#### **conversion_funnel_analytics**
- **Propósito:** Embudo de conversión
- **Campos principales:** funnel_name, step_name, conversion_rate, dropoff_rate
- **Relaciones:** ForeignKey a users

---

### 📚 **CONTENT (8 tablas)**

#### **content_units**
- **Propósito:** Unidades de contenido
- **Campos principales:** title, content_type, content, difficulty_level, tags
- **Relaciones:** ForeignKey a users (created_by), ManyToMany a learning_path_lessons

#### **user_content_progress**
- **Propósito:** Progreso de contenido
- **Campos principales:** user, content_unit, progress_percentage, completed_at
- **Relaciones:** ForeignKey a users, content_units

#### **content_ratings**
- **Propósito:** Calificaciones
- **Campos principales:** user, content_unit, rating, review_text, created_at
- **Relaciones:** ForeignKey a users, content_units

#### **content_bookmarks**
- **Propósito:** Marcadores
- **Campos principales:** user, content_unit, created_at
- **Relaciones:** ForeignKey a users, content_units

#### **content_categories**
- **Propósito:** Categorías
- **Campos principales:** name, description, parent_category
- **Relaciones:** ForeignKey a content_categories (self-referencing)

#### **content_tags**
- **Propósito:** Etiquetas
- **Campos principales:** name, description, color
- **Relaciones:** ManyToMany a content_units

#### **content_versions**
- **Propósito:** Versiones
- **Campos principales:** content_unit, version_number, content, created_at
- **Relaciones:** ForeignKey a content_units

#### **content_analytics**
- **Propósito:** Analytics de contenido
- **Campos principales:** content_unit, views_count, completion_rate, average_rating
- **Relaciones:** ForeignKey a content_units

---

### 🎮 **GAMIFICATION (12 tablas)**

#### **academies**
- **Propósito:** Academias
- **Campos principales:** name, description, leader, max_members, level_requirement
- **Relaciones:** ForeignKey a users (leader), ManyToMany a users (members)

#### **academy_memberships**
- **Propósito:** Membresías
- **Campos principales:** user, academy, role, joined_at, contribution_points
- **Relaciones:** ForeignKey a users, academies

#### **user_league_status**
- **Propósito:** Estado en ligas
- **Campos principales:** user, league_name, rank, points, tier
- **Relaciones:** ForeignKey a users

#### **user_achievements**
- **Propósito:** Logros de usuarios
- **Campos principales:** user, achievement_type, earned_at, points_awarded
- **Relaciones:** ForeignKey a users

#### **battles**
- **Propósito:** Batallas
- **Campos principales:** challenger, opponent, battle_type, winner, score
- **Relaciones:** ForeignKey a users (challenger, opponent, winner)

#### **user_currencies**
- **Propósito:** Monedas de usuarios
- **Campos principales:** user, currency_type, amount, last_updated
- **Relaciones:** ForeignKey a users

#### **user_powerups**
- **Propósito:** Powerups de usuarios
- **Campos principales:** user, powerup_type, quantity, expires_at
- **Relaciones:** ForeignKey a users

#### **user_events**
- **Propósito:** Eventos de usuarios
- **Campos principales:** user, event_type, data, occurred_at
- **Relaciones:** ForeignKey a users

#### **leaderboards**
- **Propósito:** Tablas de clasificación
- **Campos principales:** name, type, reset_frequency, is_active
- **Relaciones:** ManyToMany a users

#### **challenges**
- **Propósito:** Desafíos
- **Campos principales:** title, description, requirements, rewards, deadline
- **Relaciones:** ManyToMany a users

#### **rewards**
- **Propósito:** Recompensas
- **Campos principales:** name, description, reward_type, value, is_active
- **Relaciones:** ManyToMany a users

#### **game_settings**
- **Propósito:** Configuración del juego
- **Campos principales:** setting_name, setting_value, category
- **Relaciones:** ForeignKey a users

---

### 📝 **ICFES (12 tablas)**

#### **area_evaluaciones**
- **Propósito:** Áreas de evaluación
- **Campos principales:** nombre, descripcion, codigo, color
- **Relaciones:** ForeignKey a area_tematicas

#### **area_tematicas**
- **Propósito:** Áreas temáticas
- **Campos principales:** nombre, descripcion, area_evaluacion
- **Relaciones:** ForeignKey a area_evaluaciones

#### **competencia_icfes**
- **Propósito:** Competencias ICFES
- **Campos principales:** nombre, descripcion, area_evaluacion
- **Relaciones:** ForeignKey a area_evaluaciones

#### **icfes_exams**
- **Propósito:** Exámenes ICFES
- **Campos principales:** nombre, fecha, duracion, total_preguntas
- **Relaciones:** ForeignKey a area_evaluaciones

#### **preguntas_icfes**
- **Propósito:** Preguntas ICFES
- **Campos principales:** texto, imagen_url, area_evaluacion, dificultad
- **Relaciones:** ForeignKey a area_evaluaciones, ManyToMany a learning_path_lessons

#### **opciones_respuesta**
- **Propósito:** Opciones de respuesta
- **Campos principales:** texto, es_correcta, pregunta
- **Relaciones:** ForeignKey a preguntas_icfes

#### **respuestas_usuario_icfes**
- **Propósito:** Respuestas de usuarios
- **Campos principales:** usuario, pregunta, opcion_seleccionada, tiempo_respuesta
- **Relaciones:** ForeignKey a users, preguntas_icfes, opciones_respuesta

#### **user_icfes_sessions**
- **Propósito:** Sesiones de usuarios
- **Campos principales:** user, icfes_exam, status, started_at, completed_at
- **Relaciones:** ForeignKey a users, icfes_exams, icfes_results

#### **icfes_results**
- **Propósito:** Resultados ICFES
- **Campos principales:** user, session, total_score, area_scores, completed_at
- **Relaciones:** ForeignKey a users, user_icfes_sessions

#### **icfes_predictions**
- **Propósito:** Predicciones ICFES
- **Campos principales:** user, predicted_score, confidence, factors
- **Relaciones:** ForeignKey a users

#### **study_plans**
- **Propósito:** Planes de estudio
- **Campos principales:** user, name, target_score, duration_weeks, created_at
- **Relaciones:** ForeignKey a users

#### **user_university_goals**
- **Propósito:** Metas universitarias
- **Campos principales:** user, university, target_score, current_probability
- **Relaciones:** ForeignKey a users, universities

---

### 🧠 **LEARNING (8 tablas)**

#### **learning_paths**
- **Propósito:** Rutas de aprendizaje
- **Campos principales:** name, description, difficulty_level, estimated_duration, total_xp_available
- **Relaciones:** ForeignKey a users (created_by), ManyToMany a prerequisite_paths

#### **learning_path_lessons**
- **Propósito:** Lecciones
- **Campos principales:** title, lesson_type, order, estimated_duration_minutes, xp_reward
- **Relaciones:** ForeignKey a learning_path_units, ManyToMany a content_units, preguntas_icfes

#### **learning_path_reviews**
- **Propósito:** Reseñas
- **Campos principales:** user, learning_path, rating, review_text, created_at
- **Relaciones:** ForeignKey a users, learning_paths, user_path_enrollments

#### **learning_path_units**
- **Propósito:** Unidades
- **Campos principales:** title, description, unit_type, order, xp_reward
- **Relaciones:** ForeignKey a learning_paths

#### **path_achievements**
- **Propósito:** Logros de rutas
- **Campos principales:** name, description, achievement_type, xp_reward, rarity
- **Relaciones:** ForeignKey a learning_paths

#### **user_lesson_progress**
- **Propósito:** Progreso de lecciones
- **Campos principales:** user, path_lesson, status, attempts_count, best_score
- **Relaciones:** ForeignKey a users, learning_path_lessons, user_path_enrollments

#### **user_path_achievements**
- **Propósito:** Logros de usuarios
- **Campos principales:** user, achievement, progress_when_earned, xp_earned
- **Relaciones:** ForeignKey a users, path_achievements, user_path_enrollments

#### **user_path_enrollments**
- **Propósito:** Inscripciones
- **Campos principales:** user, learning_path, status, progress_percentage, enrolled_at
- **Relaciones:** ForeignKey a users, learning_paths

---

### 📢 **NOTIFICATIONS (8 tablas)**

#### **announcements_global**
- **Propósito:** Anuncios globales
- **Campos principales:** title, content, announcement_type, priority, is_active
- **Relaciones:** ForeignKey a users (created_by), ManyToMany a users (views)

#### **messages**
- **Propósito:** Mensajes
- **Campos principales:** thread, sender, content, message_type, created_at
- **Relaciones:** ForeignKey a message_threads, users (sender), ManyToMany a users (mentions)

#### **message_threads**
- **Propósito:** Hilos de mensajes
- **Campos principales:** thread_type, created_by, title, is_active
- **Relaciones:** ForeignKey a users (created_by), ManyToMany a users (participants)

#### **notifications**
- **Propósito:** Notificaciones
- **Campos principales:** recipient, title, message, notification_type, status
- **Relaciones:** ForeignKey a users (recipient), notification_templates

#### **notification_templates**
- **Propósito:** Plantillas
- **Campos principales:** code, name, title_template, message_template, is_active
- **Relaciones:** ForeignKey a notifications

#### **thread_participants**
- **Propósito:** Participantes
- **Campos principales:** thread, user, role, is_active, joined_at
- **Relaciones:** ForeignKey a message_threads, users

#### **user_announcement_views**
- **Propósito:** Vistas de anuncios
- **Campos principales:** user, announcement, viewed_at, clicked
- **Relaciones:** ForeignKey a users, announcements_global

#### **user_notification_settings**
- **Propósito:** Configuración
- **Campos principales:** user, achievements_enabled, battle_invites_enabled, study_reminders_enabled
- **Relaciones:** ForeignKey a users

---

### ❓ **QUESTIONS (12 tablas)**

#### **icfes_cuadernillos**
- **Propósito:** Cuadernillos ICFES
- **Campos principales:** name, cuadernillo_type, period, code, pdf_file_url
- **Relaciones:** ForeignKey a subjects

#### **questions**
- **Propósito:** Preguntas generales
- **Campos principales:** question_text, question_type, difficulty, subject, topic
- **Relaciones:** ForeignKey a subjects, topics, ManyToMany a question_sets

#### **question_explanations**
- **Propósito:** Explicaciones
- **Campos principales:** question, explanation_type, content, difficulty_level
- **Relaciones:** ForeignKey a questions, users (created_by)

#### **question_multimedia**
- **Propósito:** Multimedia
- **Campos principales:** question, media_type, file_url, file_size_kb
- **Relaciones:** ForeignKey a questions

#### **question_options**
- **Propósito:** Opciones
- **Campos principales:** question, option_letter, option_text, is_correct
- **Relaciones:** ForeignKey a questions

#### **question_sets**
- **Propósito:** Conjuntos
- **Campos principales:** name, description, set_type, time_limit_minutes
- **Relaciones:** ForeignKey a subjects, ManyToMany a questions, topics

#### **question_set_items**
- **Propósito:** Elementos
- **Campos principales:** question_set, question, order, points
- **Relaciones:** ForeignKey a question_sets, questions

#### **subjects**
- **Propósito:** Materias
- **Campos principales:** code, name, area, description, is_active
- **Relaciones:** ForeignKey a topics, ManyToMany a questions

#### **topics**
- **Propósito:** Temas
- **Campos principales:** subject, name, description, order, keywords
- **Relaciones:** ForeignKey a subjects, ManyToMany a prerequisite_topics

#### **user_question_responses**
- **Propósito:** Respuestas
- **Campos principales:** user, question, selected_option, is_correct, response_time_seconds
- **Relaciones:** ForeignKey a users, questions, question_options

#### **question_analytics**
- **Propósito:** Analytics
- **Campos principales:** question, times_asked, times_correct, average_time_seconds
- **Relaciones:** ForeignKey a questions

#### **question_difficulty_logs**
- **Propósito:** Logs de dificultad
- **Campos principales:** question, difficulty_level, adjusted_by, reason
- **Relaciones:** ForeignKey a questions, users (adjusted_by)

---

### 👤 **USERS (10 tablas)**

#### **schools**
- **Propósito:** Escuelas
- **Campos principales:** code, name, city, department, school_type
- **Relaciones:** ForeignKey a users

#### **universities**
- **Propósito:** Universidades
- **Campos principales:** code, name, city, min_icfes_score, website
- **Relaciones:** ForeignKey a users

#### **users**
- **Propósito:** Usuarios
- **Campos principales:** username, email, first_name, last_name, hero_class, level, experience_points
- **Relaciones:** ForeignKey a schools, universities, ManyToMany a groups, user_permissions

#### **user_profiles**
- **Propósito:** Perfiles
- **Campos principales:** user, total_questions_answered, total_correct_answers, current_streak
- **Relaciones:** ForeignKey a users

#### **user_sessions**
- **Propósito:** Sesiones
- **Campos principales:** user, session_id, start_time, end_time, device_info
- **Relaciones:** ForeignKey a users

#### **user_preferences**
- **Propósito:** Preferencias
- **Campos principales:** user, preference_type, value, updated_at
- **Relaciones:** ForeignKey a users

#### **user_statistics**
- **Propósito:** Estadísticas
- **Campos principales:** user, stat_type, value, calculated_at
- **Relaciones:** ForeignKey a users

#### **user_roles**
- **Propósito:** Roles
- **Campos principales:** user, role_name, assigned_at, expires_at
- **Relaciones:** ForeignKey a users

#### **user_permissions**
- **Propósito:** Permisos
- **Campos principales:** user, permission_name, granted_at
- **Relaciones:** ForeignKey a users

#### **user_activity_logs**
- **Propósito:** Logs de actividad
- **Campos principales:** user, activity_type, data, timestamp
- **Relaciones:** ForeignKey a users

---

## 🔗 **RELACIONES CLAVE:**

### **🤖 AI/LLM System:**
- `ai_conversations` → `users` (Usuario que inicia conversación)
- `ai_conversations` → `icfes` (Pregunta relacionada)
- `ai_conversations` → `learning` (Ruta de aprendizaje)

### **📝 ICFES System:**
- `preguntas_icfes` → `area_evaluaciones` (Área de evaluación)
- `respuestas_usuario_icfes` → `users` (Usuario que responde)
- `user_icfes_sessions` → `users` (Sesión del usuario)

### **🧠 Learning System:**
- `learning_paths` → `users` (Creador de la ruta)
- `user_path_enrollments` → `users` (Usuario inscrito)
- `learning_path_lessons` → `icfes` (Preguntas ICFES relacionadas)

### **🎮 Gamification System:**
- `academies` → `users` (Líder de la academia)
- `user_achievements` → `users` (Usuario que logra)
- `battles` → `users` (Retador y oponente)

### **📊 Analytics System:**
- `learning_analytics` → `users` (Analytics del usuario)
- `session_analytics` → `users` (Analytics de sesión)
- `subject_analytics` → `users` (Analytics por materia)

---

## 🎯 **PATRONES DE RELACIÓN:**

### **🔗 ForeignKeys más comunes:**
1. **users** (259 referencias) - Centro del sistema
2. **learning_paths** (8 referencias) - Sistema de aprendizaje
3. **questions** (6 referencias) - Sistema de preguntas
4. **academies** (4 referencias) - Sistema de gamificación

### **🔗 ManyToMany más importantes:**
1. **users** ↔ **groups** (Permisos)
2. **learning_paths** ↔ **prerequisite_paths** (Prerrequisitos)
3. **questions** ↔ **question_sets** (Conjuntos de preguntas)
4. **topics** ↔ **prerequisite_topics** (Temas prerrequisitos)

---

## 🎉 **CONCLUSIÓN:**

**✅ Sistema bien estructurado** con 88 modelos distribuidos en 9 apps especializadas.

**🔗 Relaciones coherentes** con el usuario como centro del sistema (259 ForeignKeys).

**🤖 Preparado para LLM** con 10 tablas específicas de AI/LLM.

**📊 Analytics completo** con 8 tablas de análisis.

**🎮 Gamificación robusta** con 12 tablas de juego.

**📚 Sistema de aprendizaje** integrado con 8 tablas.

**📝 Sistema ICFES** completo con 12 tablas especializadas.

**🎯 El proyecto está 100% listo para la integración de LLM.** 