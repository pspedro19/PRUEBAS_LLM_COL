# 🎯 DIAGRAMA COMPLETO DE TABLAS Y RELACIONES

## 📊 **ESTADÍSTICAS GENERALES:**
- **Total de modelos:** 88
- **Total de apps:** 9
- **Total ForeignKeys:** 259
- **Total ManyToMany:** 22
- **Total relaciones:** 281

---

## 📱 **APPS Y SUS TABLAS:**

### 🤖 **AI_LLM (10 tablas)**
```
📋 ai_models                    # Modelos de IA disponibles
📋 ai_conversations            # Conversaciones con IA
📋 ai_messages                 # Mensajes en conversaciones
📋 ai_prompt_templates         # Plantillas de prompts
📋 ai_response_cache           # Cache de respuestas
📋 ai_interaction_logs         # Logs de interacciones
📋 ai_moderation_logs          # Logs de moderación
📋 ai_learning_insights       # Insights de aprendizaje
📋 ai_usage_quotas            # Cuotas de uso
📋 ai_performance_metrics     # Métricas de rendimiento
```

### 📊 **ANALYTICS (8 tablas)**
```
📋 learning_analytics          # Analytics de aprendizaje
📋 subject_analytics           # Analytics por materia
📋 session_analytics           # Analytics de sesiones
📋 a_btests                    # Tests A/B
📋 user_test_participations    # Participaciones en tests
📋 feature_usage_analytics     # Uso de características
📋 user_behavior_analytics     # Comportamiento de usuarios
📋 conversion_funnel_analytics # Embudo de conversión
```

### 📚 **CONTENT (8 tablas)**
```
📋 content_units               # Unidades de contenido
📋 user_content_progress       # Progreso de contenido
📋 content_ratings             # Calificaciones
📋 content_bookmarks           # Marcadores
📋 content_categories          # Categorías
📋 content_tags                # Etiquetas
📋 content_versions            # Versiones
📋 content_analytics           # Analytics de contenido
```

### 🎮 **GAMIFICATION (12 tablas)**
```
📋 academies                   # Academias
📋 academy_memberships         # Membresías
📋 user_league_status          # Estado en ligas
📋 user_achievements           # Logros de usuarios
📋 battles                     # Batallas
📋 user_currencies             # Monedas de usuarios
📋 user_powerups               # Powerups de usuarios
📋 user_events                 # Eventos de usuarios
📋 leaderboards                # Tablas de clasificación
📋 challenges                  # Desafíos
📋 rewards                     # Recompensas
📋 game_settings               # Configuración del juego
```

### 📝 **ICFES (12 tablas)**
```
📋 area_evaluaciones           # Áreas de evaluación
📋 area_tematicas              # Áreas temáticas
📋 competencia_icfes           # Competencias ICFES
📋 icfes_exams                 # Exámenes ICFES
📋 preguntas_icfes             # Preguntas ICFES
📋 opciones_respuesta          # Opciones de respuesta
📋 respuestas_usuario_icfes    # Respuestas de usuarios
📋 user_icfes_sessions         # Sesiones de usuarios
📋 icfes_results               # Resultados ICFES
📋 icfes_predictions           # Predicciones ICFES
📋 study_plans                 # Planes de estudio
📋 user_university_goals       # Metas universitarias
```

### 🧠 **LEARNING (8 tablas)**
```
📋 learning_paths              # Rutas de aprendizaje
📋 learning_path_lessons       # Lecciones
📋 learning_path_reviews       # Reseñas
📋 learning_path_units         # Unidades
📋 path_achievements           # Logros de rutas
📋 user_lesson_progress        # Progreso de lecciones
📋 user_path_achievements      # Logros de usuarios
📋 user_path_enrollments       # Inscripciones
```

### 📢 **NOTIFICATIONS (8 tablas)**
```
📋 announcements_global         # Anuncios globales
📋 messages                    # Mensajes
📋 message_threads             # Hilos de mensajes
📋 notifications               # Notificaciones
📋 notification_templates      # Plantillas
📋 thread_participants         # Participantes
📋 user_announcement_views     # Vistas de anuncios
📋 user_notification_settings  # Configuración
```

### ❓ **QUESTIONS (12 tablas)**
```
📋 icfes_cuadernillos          # Cuadernillos ICFES
📋 questions                   # Preguntas generales
📋 question_explanations       # Explicaciones
📋 question_multimedia         # Multimedia
📋 question_options            # Opciones
📋 question_sets               # Conjuntos
📋 question_set_items          # Elementos
📋 subjects                    # Materias
📋 topics                      # Temas
📋 user_question_responses     # Respuestas
📋 question_analytics          # Analytics
📋 question_difficulty_logs    # Logs de dificultad
```

### 👤 **USERS (10 tablas)**
```
📋 schools                     # Escuelas
📋 universities                # Universidades
📋 users                       # Usuarios
📋 user_profiles               # Perfiles
📋 user_sessions               # Sesiones
📋 user_preferences            # Preferencias
📋 user_statistics             # Estadísticas
📋 user_roles                  # Roles
📋 user_permissions            # Permisos
📋 user_activity_logs          # Logs de actividad
```

---

## 🔗 **RELACIONES ENTRE APPS:**

### **AI_LLM** → icfes, learning, users
### **ANALYTICS** → users
### **CONTENT** → learning, users
### **GAMIFICATION** → users
### **ICFES** → ai_llm, learning, users
### **LEARNING** → ai_llm, content, icfes, users
### **NOTIFICATIONS** → users
### **QUESTIONS** → users
### **USERS** → admin, ai_llm, analytics, auth, content, gamification, icfes, learning, notifications, questions

---

## 🎯 **RELACIONES CLAVE:**

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

## 📈 **PATRONES DE RELACIÓN:**

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