# 🎯 Sistema de Quiz Real - ICFES Quest

## 📋 Resumen

Sistema completo para importar, gestionar y utilizar **preguntas reales del ICFES** en la plataforma ICFES Quest. Incluye análisis automático de PDFs, importación de preguntas, gestión avanzada y sistema de quiz gamificado.

## 🗃️ Estructura de Base de Datos

### 📚 **Tablas Principales**

#### **1. ICFESCuadernillo**
Gestiona los cuadernillos ICFES oficiales.
```sql
- name: "Matemáticas 11° Cuadernillo 1"
- cuadernillo_type: SABER_11, SABER_PRO, SIMULACRO
- period: 2024-1, 2024-2, etc.
- pdf_file_url: URL del archivo PDF original
- total_questions: Número total de preguntas
- is_processed: Si ya se extrajeron las preguntas
```

#### **2. Question (Extendida)**
Modelo principal de preguntas con metadatos ICFES específicos.
```sql
- question_text: Texto de la pregunta
- content_type: TEXT_ONLY, WITH_IMAGE, WITH_GRAPH, WITH_TABLE
- has_diagram/has_graph/has_table: Flags de multimedia
- cuadernillo: Referencia al cuadernillo origen
- question_number: Número original en el cuadernillo
- mathematical_notation: Contiene notación matemática
- extraction_confidence: Confianza del análisis automático
- manual_review_required: Requiere revisión manual
```

#### **3. QuestionOption (Mejorada)**
Opciones con metadatos de extracción.
```sql
- option_letter: A, B, C, D
- option_text: Texto de la opción
- has_mathematical_notation: Contiene fórmulas
- extraction_confidence: Confianza de extracción
```

#### **4. QuestionExplanation (Con Roles)**
Explicaciones personalizadas por rol de batalla.
```sql
- explanation_type: SOLUTION, HINT, THEORY, ROLE_BASED
- target_role: ALL, TANK, DPS, SUPPORT, SPECIALIST
- content: Explicación específica para el rol
```

#### **5. QuestionMultimedia**
Archivos multimedia asociados a preguntas.
```sql
- media_type: IMAGE, DIAGRAM, GRAPH, TABLE, CHART
- file_url: URL del archivo multimedia
- alt_text: Texto alternativo
- is_primary: Si es la imagen principal
```

#### **6. UserQuestionResponse (Gamificada)**
Respuestas con gamificación específica por rol.
```sql
- xp_gained: XP obtenido por la respuesta
- role_bonus_applied: Si se aplicó bonus por rol
- strategy_hint_used: Si usó pista estratégica
```

## 🔧 Sistema de Importación

### **Comando Django**
```bash
# Importar preguntas desde el análisis del PDF
python manage.py import_icfes_questions --pdf-analysis pdf_analysis_result.json

# Opciones adicionales
python manage.py import_icfes_questions \
    --pdf-analysis pdf_analysis_result.json \
    --cuadernillo-name "Matemáticas 11° Cuadernillo 1" \
    --period "2024-1" \
    --dry-run  # Simular sin guardar
```

### **Proceso de Importación**

1. **Análisis del PDF** ✅ (Ya realizado)
   - Extracción de texto y metadatos
   - Detección de preguntas y opciones
   - Análisis de dificultad y temas

2. **Creación de Estructura**
   - Materia: Matemáticas
   - Temas: Álgebra, Geometría, Trigonometría, Estadística, Cálculo
   - Cuadernillo: Con metadatos del PDF

3. **Importación de Preguntas**
   - Filtrado de contenido válido
   - Detección automática de temas
   - Creación de opciones placeholder
   - Marcado para revisión manual

4. **Control de Calidad**
   - Confianza de extracción
   - Flags de revisión manual
   - Verificación pendiente

## 📊 Características del Sistema

### **🎮 Gamificación por Roles**

#### **TANK (Guardián)** 🛡️
- **Estrategia**: Enfoque en consolidar conocimientos base
- **Bonificación**: +20% XP por consistencia en respuestas
- **Explicaciones**: Enfoque en fundamentos y repetición

#### **DPS (Atacante)** ⚔️
- **Estrategia**: Velocidad y precisión en resolución
- **Bonificación**: +30% XP por respuestas rápidas y correctas
- **Explicaciones**: Métodos directos y eficientes

#### **SUPPORT (Colaborativo)** 💫
- **Estrategia**: Gestión del tiempo y organización
- **Bonificación**: +25% XP por completar sets completos
- **Explicaciones**: Enfoque en planificación y métodos

#### **SPECIALIST (Analítico)** 🎯
- **Estrategia**: Análisis profundo y patrones
- **Bonificación**: +35% XP por explicaciones solicitadas
- **Explicaciones**: Análisis detallado y técnicas avanzadas

### **📈 Sistema Adaptativo**

- **Dificultad Dinámica**: Ajuste según rendimiento del usuario
- **Modificadores por Rol**: Cada rol tiene modificadores específicos
- **Análisis de Patrones**: Detección de fortalezas y debilidades
- **Feedback Personalizado**: Explicaciones según el estilo de aprendizaje

## 🖥️ Panel de Administración

### **Gestión de Preguntas**
- **Filtros Avanzados**: Por tema, dificultad, tipo de contenido
- **Editor Inline**: Opciones y explicaciones en la misma vista
- **Control de Calidad**: Marcado de verificación y revisión
- **Estadísticas**: Tasas de éxito y tiempos promedio

### **Acciones Masivas**
- Marcar como verificadas
- Marcar para revisión
- Activar/desactivar preguntas
- Exportar sets de preguntas

## 🔗 Integración con Frontend

### **APIs Necesarias**

#### **1. Obtener Preguntas**
```javascript
GET /api/questions/quiz/
?subject=MATHEMATICS
&difficulty=MEDIUM
&role=TANK
&count=10
```

#### **2. Enviar Respuesta**
```javascript
POST /api/questions/answer/
{
  "question_id": 123,
  "selected_option": "A",
  "response_time": 45.5,
  "confidence_level": 4,
  "session_id": "session_uuid"
}
```

#### **3. Obtener Explicación Personalizada**
```javascript
GET /api/questions/123/explanation/
?role=SPECIALIST
&explanation_type=SOLUTION
```

### **Componentes Frontend**

#### **QuestionCard Mejorada**
```tsx
<QuestionCard 
  question={question}
  userRole={user.assigned_role}
  showHints={userRole === 'TANK'}
  showAnalysis={userRole === 'SPECIALIST'}
  timeBonus={userRole === 'DPS'}
/>
```

#### **RoleBasedExplanation**
```tsx
<RoleBasedExplanation 
  question={question}
  userRole={user.assigned_role}
  explanationType="SOLUTION"
  difficulty={question.difficulty}
/>
```

## 🚀 Implementación Paso a Paso

### **Fase 1: Base de Datos** ✅
- [x] Modelos extendidos creados
- [x] Migraciones preparadas
- [x] Admin interface completo

### **Fase 2: Importación** 🔄
- [x] Comando de importación
- [ ] Ejecutar importación real
- [ ] Revisión manual de preguntas
- [ ] Verificación de opciones

### **Fase 3: APIs Backend**
- [ ] Endpoint de quiz personalizado
- [ ] Sistema de respuestas con gamificación
- [ ] Explicaciones dinámicas por rol
- [ ] Analytics de rendimiento

### **Fase 4: Frontend Integrado**
- [ ] Componente de pregunta multimedia
- [ ] Sistema de explicaciones por rol
- [ ] Feedback visual mejorado
- [ ] Analytics de usuario

### **Fase 5: Optimización**
- [ ] Sistema adaptativo de dificultad
- [ ] IA para explicaciones automáticas
- [ ] Análisis de patrones de aprendizaje
- [ ] Recomendaciones personalizadas

## 📝 Comandos Útiles

### **Ejecutar Importación**
```bash
# Navegar al directorio del proyecto
cd backend_django

# Ejecutar migraciones
python manage.py makemigrations questions
python manage.py migrate

# Importar preguntas (dry-run primero)
python manage.py import_icfes_questions --dry-run

# Importación real
python manage.py import_icfes_questions
```

### **Administración**
```bash
# Crear superusuario para admin
python manage.py createsuperuser

# Acceder a admin
# http://localhost:8000/admin/
```

### **Testing**
```bash
# Verificar que las preguntas se crearon
python manage.py shell
>>> from apps.questions.models import Question
>>> Question.objects.count()
>>> Question.objects.filter(manual_review_required=True).count()
```

## 🎯 Resultados Esperados

### **Después de la Importación**
- ✅ **~15-20 preguntas** de matemáticas importadas
- ✅ **Cuadernillo oficial** registrado en el sistema
- ✅ **Temas automáticamente** detectados y asignados
- ✅ **Opciones placeholder** para revisión manual
- ✅ **Metadatos completos** para cada pregunta

### **Beneficios del Sistema**
- 🎯 **Preguntas reales** del ICFES oficial
- 🎮 **Gamificación personalizada** por rol de batalla
- 📊 **Analytics detallados** de rendimiento
- 🤖 **IA adaptativa** para dificultad
- 📚 **Explicaciones personalizadas** por estilo de aprendizaje

## 🔧 Próximos Pasos

1. **Ejecutar la importación** de preguntas
2. **Revisar manualmente** las preguntas importadas
3. **Completar opciones** y respuestas correctas
4. **Crear explicaciones** personalizadas por rol
5. **Integrar con frontend** del sistema de quiz
6. **Implementar analytics** avanzados
7. **Agregar más cuadernillos** ICFES

---

## 🎉 ¡Sistema Listo para Implementar!

El sistema está **completamente diseñado** y listo para importar las preguntas reales del ICFES. Solo falta ejecutar la importación y comenzar con la revisión manual de las preguntas para tener un sistema de quiz épico y real. 🚀 