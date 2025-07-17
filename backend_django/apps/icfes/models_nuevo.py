"""
Modelos ICFES mejorados basados en la estructura del archivo ICFES.xlsx
Sistema completo de taxonomía educativa y preguntas reales
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
import uuid

User = get_user_model()


class AreaEvaluacion(models.Model):
    """Áreas de evaluación ICFES (Matemáticas, Lectura Crítica, etc.)"""
    
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    color_tema = models.CharField(max_length=7, default='#3B82F6')
    icono_url = models.URLField(max_length=500, blank=True, null=True)
    orden_visualizacion = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'areas_evaluacion'
        ordering = ['orden_visualizacion', 'nombre']
        verbose_name = 'Área de Evaluación'
        verbose_name_plural = 'Áreas de Evaluación'
    
    def __str__(self):
        return self.nombre


class CompetenciaICFES(models.Model):
    """Competencias específicas del ICFES por área"""
    
    area_evaluacion = models.ForeignKey(AreaEvaluacion, on_delete=models.CASCADE, related_name='competencias')
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'competencias_icfes'
        ordering = ['area_evaluacion', 'orden', 'nombre']
        verbose_name = 'Competencia ICFES'
        verbose_name_plural = 'Competencias ICFES'
    
    def __str__(self):
        return f"{self.area_evaluacion.nombre} - {self.nombre}"


class ComponenteConocimiento(models.Model):
    """Componentes de conocimiento por competencia"""
    
    competencia = models.ForeignKey(CompetenciaICFES, on_delete=models.CASCADE, related_name='componentes')
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'componentes_conocimiento'
        ordering = ['competencia', 'orden']
        verbose_name = 'Componente de Conocimiento'
        verbose_name_plural = 'Componentes de Conocimiento'
    
    def __str__(self):
        return f"{self.competencia.nombre} - {self.nombre}"


class ProcesoCognitivo(models.Model):
    """Procesos cognitivos según taxonomía de Bloom"""
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    nivel_bloom = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text="Nivel según taxonomía de Bloom (1-6)"
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'procesos_cognitivos'
        ordering = ['nivel_bloom', 'nombre']
        verbose_name = 'Proceso Cognitivo'
        verbose_name_plural = 'Procesos Cognitivos'
    
    def __str__(self):
        return f"{self.nombre} (Bloom {self.nivel_bloom})"


class TipoConocimiento(models.Model):
    """Tipos de conocimiento (Genérico, Específico)"""
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_conocimiento'
        ordering = ['nombre']
        verbose_name = 'Tipo de Conocimiento'
        verbose_name_plural = 'Tipos de Conocimiento'
    
    def __str__(self):
        return self.nombre


class ContextoAplicacion(models.Model):
    """Contextos de aplicación del conocimiento"""
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'contextos_aplicacion'
        ordering = ['orden', 'nombre']
        verbose_name = 'Contexto de Aplicación'
        verbose_name_plural = 'Contextos de Aplicación'
    
    def __str__(self):
        return self.nombre


class AreaTematica(models.Model):
    """Áreas temáticas específicas dentro de cada área de evaluación"""
    
    area_evaluacion = models.ForeignKey(AreaEvaluacion, on_delete=models.CASCADE, related_name='areas_tematicas')
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    keywords = models.JSONField(default=list, blank=True)
    color_tema = models.CharField(max_length=7, blank=True, null=True)
    icono_url = models.URLField(max_length=500, blank=True, null=True)
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'areas_tematicas'
        ordering = ['area_evaluacion', 'orden', 'nombre']
        verbose_name = 'Área Temática'
        verbose_name_plural = 'Áreas Temáticas'
    
    def __str__(self):
        return f"{self.area_evaluacion.nombre} - {self.nombre}"


class TemaEspecifico(models.Model):
    """Temas específicos dentro de cada área temática"""
    
    area_tematica = models.ForeignKey(AreaTematica, on_delete=models.CASCADE, related_name='temas')
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True, null=True)
    keywords = models.JSONField(default=list, blank=True)
    prerequisitos_ids = ArrayField(models.IntegerField(), default=list, blank=True)
    nivel_dificultad = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'temas_especificos'
        ordering = ['area_tematica', 'nivel_dificultad', 'nombre']
        verbose_name = 'Tema Específico'
        verbose_name_plural = 'Temas Específicos'
    
    def __str__(self):
        return self.nombre


class PeriodoAplicacion(models.Model):
    """Períodos de aplicación de exámenes ICFES"""
    
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'periodos_aplicacion'
        ordering = ['-fecha_inicio']
        verbose_name = 'Período de Aplicación'
        verbose_name_plural = 'Períodos de Aplicación'
    
    def __str__(self):
        return self.nombre


class CuadernilloICFES(models.Model):
    """Cuadernillos oficiales del ICFES"""
    
    TIPOS_CUADERNILLO = [
        ('SABER_11', 'Saber 11'),
        ('SABER_PRO', 'Saber Pro'),
        ('SIMULACRO', 'Simulacro'),
        ('PRACTICA', 'Práctica'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    area_evaluacion = models.ForeignKey(AreaEvaluacion, on_delete=models.CASCADE, related_name='cuadernillos')
    periodo_aplicacion = models.ForeignKey(PeriodoAplicacion, on_delete=models.CASCADE, related_name='cuadernillos')
    tipo_cuadernillo = models.CharField(max_length=20, choices=TIPOS_CUADERNILLO, default='SABER_11')
    grado_escolar = models.IntegerField()
    total_preguntas = models.IntegerField(default=0)
    archivo_fuente_url = models.URLField(max_length=500, blank=True, null=True)
    procesado = models.BooleanField(default=False)
    notas_procesamiento = models.TextField(blank=True, null=True)
    metadatos = models.JSONField(default=dict, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cuadernillos_icfes'
        ordering = ['-periodo_aplicacion__fecha_inicio', 'area_evaluacion', 'nombre']
        verbose_name = 'Cuadernillo ICFES'
        verbose_name_plural = 'Cuadernillos ICFES'
    
    def __str__(self):
        return f"{self.nombre} ({self.periodo_aplicacion.codigo})"


class PreguntaICFES(models.Model):
    """Pregunta principal del sistema ICFES"""
    
    NIVELES_DESEMPENO = [
        ('INSUFICIENTE', 'Insuficiente'),
        ('MINIMO', 'Mínimo'),
        ('SATISFACTORIO', 'Satisfactorio'),
        ('AVANZADO', 'Avanzado'),
    ]
    
    RESPUESTAS_VALIDAS = [
        ('A', 'Opción A'),
        ('B', 'Opción B'),
        ('C', 'Opción C'),
        ('D', 'Opción D'),
    ]
    
    # Identificación
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    id_pregunta_original = models.IntegerField(help_text="ID del archivo Excel original")
    cuadernillo = models.ForeignKey(CuadernilloICFES, on_delete=models.CASCADE, related_name='preguntas')
    numero_pregunta = models.CharField(max_length=10, blank=True, null=True)
    
    # Clasificación taxonómica
    area_evaluacion = models.ForeignKey(AreaEvaluacion, on_delete=models.CASCADE, related_name='preguntas')
    competencia = models.ForeignKey(CompetenciaICFES, on_delete=models.CASCADE, related_name='preguntas', blank=True, null=True)
    componente = models.ForeignKey(ComponenteConocimiento, on_delete=models.CASCADE, related_name='preguntas', blank=True, null=True)
    proceso_cognitivo = models.ForeignKey(ProcesoCognitivo, on_delete=models.CASCADE, related_name='preguntas', blank=True, null=True)
    tipo_conocimiento = models.ForeignKey(TipoConocimiento, on_delete=models.CASCADE, related_name='preguntas', blank=True, null=True)
    contexto_aplicacion = models.ForeignKey(ContextoAplicacion, on_delete=models.CASCADE, related_name='preguntas', blank=True, null=True)
    
    # Contenido principal
    pregunta_texto = models.TextField(help_text="Texto completo de la pregunta")
    afirmacion = models.TextField(blank=True, null=True, help_text="Lo que se evalúa específicamente")
    evidencia = models.TextField(blank=True, null=True, help_text="Evidencia de aprendizaje")
    
    # Metadatos de dificultad
    nivel_dificultad = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Nivel de dificultad del 1 al 5"
    )
    nivel_desempeno_esperado = models.CharField(max_length=50, choices=NIVELES_DESEMPENO, blank=True, null=True)
    tiempo_estimado_segundos = models.IntegerField(help_text="Tiempo estimado de respuesta en segundos")
    
    # Clasificación temática
    area_tematica = models.ForeignKey(AreaTematica, on_delete=models.CASCADE, related_name='preguntas', blank=True, null=True)
    tema_especifico = models.ForeignKey(TemaEspecifico, on_delete=models.CASCADE, related_name='preguntas', blank=True, null=True)
    grado_escolar = models.IntegerField(validators=[MinValueValidator(9), MaxValueValidator(11)])
    
    # Respuesta correcta
    respuesta_correcta = models.CharField(max_length=1, choices=RESPUESTAS_VALIDAS)
    
    # Gamificación
    puntos_xp = models.IntegerField(default=20, validators=[MinValueValidator(1)])
    
    # Multimedia
    requiere_imagen = models.BooleanField(default=False)
    imagen_pregunta_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Estado y metadatos
    verificada = models.BooleanField(default=False)
    activa = models.BooleanField(default=True)
    
    # Estadísticas de uso
    veces_preguntada = models.IntegerField(default=0)
    veces_correcta = models.IntegerField(default=0)
    tiempo_promedio_respuesta = models.FloatField(default=0.0)
    
    # Timestamps
    fecha_aplicacion = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'preguntas_icfes'
        ordering = ['cuadernillo', 'numero_pregunta']
        indexes = [
            models.Index(fields=['area_evaluacion', 'nivel_dificultad']),
            models.Index(fields=['competencia']),
            models.Index(fields=['activa', 'verificada']),
            models.Index(fields=['grado_escolar']),
        ]
        verbose_name = 'Pregunta ICFES'
        verbose_name_plural = 'Preguntas ICFES'
    
    def __str__(self):
        return f"P{self.id_pregunta_original} - {self.area_evaluacion.nombre}"
    
    @property
    def porcentaje_acierto(self):
        """Calcula el porcentaje de acierto de la pregunta"""
        if self.veces_preguntada == 0:
            return 0.0
        return (self.veces_correcta / self.veces_preguntada) * 100
    
    def actualizar_estadisticas(self, es_correcta, tiempo_respuesta):
        """Actualiza las estadísticas de la pregunta"""
        self.veces_preguntada += 1
        if es_correcta:
            self.veces_correcta += 1
        
        # Actualizar tiempo promedio
        if self.tiempo_promedio_respuesta == 0:
            self.tiempo_promedio_respuesta = tiempo_respuesta
        else:
            self.tiempo_promedio_respuesta = (
                (self.tiempo_promedio_respuesta * (self.veces_preguntada - 1) + tiempo_respuesta) 
                / self.veces_preguntada
            )
        
        self.save(update_fields=['veces_preguntada', 'veces_correcta', 'tiempo_promedio_respuesta'])


class OpcionRespuesta(models.Model):
    """Opciones de respuesta para preguntas ICFES"""
    
    LETRAS_OPCIONES = [
        ('A', 'Opción A'),
        ('B', 'Opción B'),
        ('C', 'Opción C'),
        ('D', 'Opción D'),
    ]
    
    pregunta = models.ForeignKey(PreguntaICFES, on_delete=models.CASCADE, related_name='opciones')
    letra_opcion = models.CharField(max_length=1, choices=LETRAS_OPCIONES)
    texto_opcion = models.TextField()
    es_correcta = models.BooleanField()
    imagen_opcion_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Metadatos de análisis
    tipo_distractor = models.CharField(max_length=50, blank=True, null=True)
    explicacion_opcion = models.TextField(blank=True, null=True)
    
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'opciones_respuesta'
        ordering = ['pregunta', 'orden', 'letra_opcion']
        unique_together = ['pregunta', 'letra_opcion']
        verbose_name = 'Opción de Respuesta'
        verbose_name_plural = 'Opciones de Respuesta'
    
    def __str__(self):
        return f"{self.pregunta.id_pregunta_original} - Opción {self.letra_opcion}"


class PistaPregunta(models.Model):
    """Pistas graduales para las preguntas"""
    
    TIPOS_PISTA = [
        ('CONCEPTUAL', 'Conceptual'),
        ('PROCEDIMENTAL', 'Procedimental'),
        ('ESTRATEGICA', 'Estratégica'),
        ('CONTEXTO', 'De Contexto'),
    ]
    
    ROLES_OBJETIVO = [
        ('ALL', 'Todos'),
        ('TANK', 'Tanque'),
        ('DPS', 'Atacante'),
        ('SUPPORT', 'Soporte'),
        ('SPECIALIST', 'Especialista'),
    ]
    
    pregunta = models.ForeignKey(PreguntaICFES, on_delete=models.CASCADE, related_name='pistas')
    numero_pista = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    texto_pista = models.TextField()
    tipo_pista = models.CharField(max_length=50, choices=TIPOS_PISTA, default='CONCEPTUAL')
    rol_objetivo = models.CharField(max_length=20, choices=ROLES_OBJETIVO, default='ALL')
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pistas_pregunta'
        ordering = ['pregunta', 'numero_pista']
        unique_together = ['pregunta', 'numero_pista']
        verbose_name = 'Pista de Pregunta'
        verbose_name_plural = 'Pistas de Preguntas'
    
    def __str__(self):
        return f"P{self.pregunta.id_pregunta_original} - Pista {self.numero_pista}"


class ExplicacionRespuesta(models.Model):
    """Explicaciones detalladas de respuestas"""
    
    TIPOS_EXPLICACION = [
        ('SOLUCION', 'Solución'),
        ('TEORIA', 'Teoría'),
        ('ESTRATEGIA', 'Estrategia'),
        ('CONTEXTO', 'Contexto'),
    ]
    
    ROLES_OBJETIVO = [
        ('ALL', 'Todos'),
        ('TANK', 'Tanque'),
        ('DPS', 'Atacante'),
        ('SUPPORT', 'Soporte'),
        ('SPECIALIST', 'Especialista'),
    ]
    
    NIVELES_DETALLE = [
        ('BASICO', 'Básico'),
        ('MEDIO', 'Medio'),
        ('AVANZADO', 'Avanzado'),
    ]
    
    pregunta = models.ForeignKey(PreguntaICFES, on_delete=models.CASCADE, related_name='explicaciones')
    tipo_explicacion = models.CharField(max_length=50, choices=TIPOS_EXPLICACION)
    titulo = models.CharField(max_length=200, blank=True, null=True)
    contenido = models.TextField()
    
    # Personalización por rol
    rol_objetivo = models.CharField(max_length=20, choices=ROLES_OBJETIVO, default='ALL')
    nivel_detalle = models.CharField(max_length=20, choices=NIVELES_DETALLE, default='MEDIO')
    
    # Multimedia
    imagen_explicacion_url = models.URLField(max_length=500, blank=True, null=True)
    video_explicacion_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Metadatos
    dificultad_explicacion = models.IntegerField(default=2, validators=[MinValueValidator(1), MaxValueValidator(5)])
    tiempo_lectura_estimado = models.IntegerField(help_text="Tiempo estimado de lectura en segundos", blank=True, null=True)
    
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'explicaciones_respuesta'
        ordering = ['pregunta', 'orden', 'tipo_explicacion']
        verbose_name = 'Explicación de Respuesta'
        verbose_name_plural = 'Explicaciones de Respuestas'
    
    def __str__(self):
        return f"P{self.pregunta.id_pregunta_original} - {self.get_tipo_explicacion_display()}"


class ErrorComun(models.Model):
    """Errores comunes que cometen los estudiantes"""
    
    OPCIONES_ELEGIDAS = [
        ('A', 'Opción A'),
        ('B', 'Opción B'),
        ('C', 'Opción C'),
        ('D', 'Opción D'),
    ]
    
    pregunta = models.ForeignKey(PreguntaICFES, on_delete=models.CASCADE, related_name='errores_comunes')
    descripcion_error = models.TextField()
    opcion_elegida = models.CharField(max_length=1, choices=OPCIONES_ELEGIDAS, blank=True, null=True)
    frecuencia_error = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Porcentaje de estudiantes que cometen este error"
    )
    explicacion_error = models.TextField(blank=True, null=True)
    sugerencia_correccion = models.TextField(blank=True, null=True)
    
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'errores_comunes'
        ordering = ['pregunta', '-frecuencia_error']
        verbose_name = 'Error Común'
        verbose_name_plural = 'Errores Comunes'
    
    def __str__(self):
        return f"P{self.pregunta.id_pregunta_original} - Error en {self.opcion_elegida}"


class RespuestaUsuarioICFES(models.Model):
    """Respuestas de usuarios a preguntas ICFES"""
    
    TIPOS_EVALUACION = [
        ('PRACTICA', 'Práctica'),
        ('SIMULACRO', 'Simulacro'),
        ('BATALLA', 'Batalla'),
        ('DIAGNOSTICO', 'Diagnóstico'),
        ('EXAMEN', 'Examen'),
    ]
    
    DISPOSITIVOS = [
        ('MOBILE', 'Móvil'),
        ('DESKTOP', 'Escritorio'),
        ('TABLET', 'Tablet'),
    ]
    
    # Identificación
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='respuestas_icfes')
    pregunta = models.ForeignKey(PreguntaICFES, on_delete=models.CASCADE, related_name='respuestas_usuarios')
    
    # Respuesta del usuario
    opcion_seleccionada = models.CharField(max_length=1, choices=PreguntaICFES.RESPUESTAS_VALIDAS, blank=True, null=True)
    es_correcta = models.BooleanField()
    tiempo_respuesta_segundos = models.IntegerField(validators=[MinValueValidator(1)])
    nivel_confianza = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Nivel de confianza del 1 al 5",
        blank=True, null=True
    )
    
    # Contexto de la sesión
    session_id = models.CharField(max_length=100, blank=True, null=True)
    tipo_evaluacion = models.CharField(max_length=50, choices=TIPOS_EVALUACION, default='PRACTICA')
    dispositivo = models.CharField(max_length=50, choices=DISPOSITIVOS, blank=True, null=True)
    
    # Ayudas utilizadas
    pistas_usadas = ArrayField(models.IntegerField(), default=list, blank=True)
    explicacion_solicitada = models.BooleanField(default=False)
    tiempo_en_explicacion = models.IntegerField(default=0)
    
    # Gamificación
    xp_ganado = models.IntegerField(default=0)
    bonus_aplicado = models.CharField(max_length=100, blank=True, null=True)
    
    # Análisis de comportamiento
    intentos_respuesta = models.IntegerField(default=1)
    cambio_respuesta = models.BooleanField(default=False)
    patron_respuesta = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'respuestas_usuarios_icfes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['pregunta']),
            models.Index(fields=['session_id']),
            models.Index(fields=['tipo_evaluacion']),
        ]
        verbose_name = 'Respuesta Usuario ICFES'
        verbose_name_plural = 'Respuestas Usuarios ICFES'
    
    def __str__(self):
        return f"{self.user.username} - P{self.pregunta.id_pregunta_original} ({'✓' if self.es_correcta else '✗'})"
    
    def save(self, *args, **kwargs):
        """Override para actualizar estadísticas de la pregunta"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Actualizar estadísticas de la pregunta
            self.pregunta.actualizar_estadisticas(self.es_correcta, self.tiempo_respuesta_segundos) 