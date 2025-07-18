"""
Admin de Django para la app de Learning Paths - Versión mejorada
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import TextInput, Textarea
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Avg, Count, Sum
from django.utils import timezone

from .models import (
    LearningPath, LearningPathUnit, LearningPathLesson,
    UserPathEnrollment, UserLessonProgress, PathAchievement,
    UserPathAchievement, LearningPathReview
)


class AdminTextareaWidget(Textarea):
    def __init__(self, attrs=None):
        default_attrs = {'rows': 4, 'cols': 80}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class LearningPathUnitInline(admin.StackedInline):
    model = LearningPathUnit
    extra = 1
    fields = [
        ('title', 'unit_type', 'order'),
        'description',
        ('estimated_duration_minutes', 'xp_reward', 'hearts_required'),
        ('is_bonus', 'is_optional', 'is_active')
    ]
    ordering = ['order']
    
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1


class LearningPathLessonInline(admin.TabularInline):
    model = LearningPathLesson
    extra = 1
    fields = [
        'title', 'lesson_type', 'order', 'duration_display',
        'xp_reward', 'passing_score_display', 'assessment_badge'
    ]
    readonly_fields = ['duration_display', 'passing_score_display', 'assessment_badge']
    ordering = ['order']
    
    def duration_display(self, obj):
        if obj.estimated_duration_minutes:
            return f"⏱️ {obj.estimated_duration_minutes} min"
        return "-"
    duration_display.short_description = 'Duración'
    
    def passing_score_display(self, obj):
        if obj.passing_score:
            color = 'green' if obj.passing_score >= 80 else 'orange' if obj.passing_score >= 60 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.0f}%</span>',
                color, obj.passing_score
            )
        return "-"
    passing_score_display.short_description = 'Puntaje Min.'
    
    def assessment_badge(self, obj):
        if obj.is_assessment:
            return format_html('<span style="color: #ff5722; font-weight: bold;">📊 Evaluación</span>')
        return format_html('<span style="color: #4caf50;">📚 Lección</span>')
    assessment_badge.short_description = 'Tipo'


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'path_type_badge', 'difficulty_badge', 'status_badge',
        'completion_rate_display', 'rating_display', 'enrollments_display', 
        'features_summary', 'ai_status'
    ]
    list_filter = [
        'path_type', 'difficulty_level', 'status', 'is_featured', 
        'is_premium', 'has_adaptive_difficulty', 'is_ai_enhanced',
        'required_hero_class', 'target_icfes_areas',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = ['name', 'description', 'learning_outcomes', 'tags', 'short_description']
    ordering = ['-is_featured', 'difficulty_level', 'name']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['prerequisite_paths']
    
    inlines = [LearningPathUnitInline]
    
    fieldsets = (
        ('📚 Información Principal', {
            'fields': ('name', 'slug', 'description', 'short_description'),
            'description': 'Información básica del recorrido de aprendizaje'
        }),
        ('🎯 Clasificación y Dificultad', {
            'fields': ('path_type', 'status', 'difficulty_level'),
            'description': 'Categorización y nivel de dificultad del path'
        }),
        ('🎓 Configuración Educativa', {
            'fields': (
                'target_icfes_areas', 'estimated_duration_hours', 
                'recommended_weekly_hours', 'min_grade_level', 'max_grade_level'
            ),
            'description': 'Configuración académica y recomendaciones'
        }),
        ('🔗 Prerrequisitos y Acceso', {
            'fields': ('prerequisite_paths', 'required_hero_class', 'required_level'),
            'description': 'Requisitos para acceder a este path'
        }),
        ('🎮 Sistema de Gamificación', {
            'fields': ('completion_xp_bonus', 'mastery_xp_bonus'),
            'description': 'Bonificaciones de experiencia por completar o dominar'
        }),
        ('🎨 Contenido Visual y Multimedia', {
            'fields': ('thumbnail_url', 'cover_image_url', 'intro_video_url'),
            'description': 'Recursos visuales para la presentación del path'
        }),
        ('🌈 Personalización Visual', {
            'fields': ('primary_color', 'secondary_color', 'icon_emoji'),
            'description': 'Colores y emoji característicos del path'
        }),
        ('✨ Características Especiales', {
            'fields': (
                ('has_adaptive_difficulty', 'has_peer_comparison'),
                ('has_leaderboards', 'has_streaks'),
                'has_certificates'
            ),
            'description': 'Funcionalidades especiales disponibles'
        }),
        ('💎 Estado y Acceso Premium', {
            'fields': ('is_premium', 'is_featured'),
            'description': 'Control de acceso y destacado'
        }),
        ('🤖 Configuración de Inteligencia Artificial', {
            'fields': (
                'is_ai_enhanced',
                ('ai_recommendations_enabled', 'adaptive_sequencing_enabled'),
                'personalized_feedback_enabled'
            ),
            'classes': ['collapse'],
            'description': 'Configuraciones avanzadas de IA para personalización'
        }),
        ('📝 Objetivos y Metadatos', {
            'fields': ('learning_outcomes', 'tags', 'metadata'),
            'classes': ['collapse'],
            'description': 'Objetivos de aprendizaje e información complementaria'
        }),
        ('📊 Métricas de Rendimiento (Solo Lectura)', {
            'fields': (
                'metrics_summary', 'performance_analysis'
            ),
            'classes': ['collapse'],
            'description': 'Estadísticas detalladas de uso y efectividad'
        }),
    )
    
    readonly_fields = [
        'total_enrollments', 'total_completions', 
        'average_completion_time_hours', 'average_rating', 'total_xp_available', 'uuid',
        'metrics_summary', 'performance_analysis'
    ]
    
    formfield_overrides = {
        models.TextField: {'widget': AdminTextareaWidget()},
    }
    
    actions = [
        'publish_paths', 'draft_paths', 'feature_paths', 'unfeature_paths',
        'activate_ai_enhancement', 'make_premium', 'make_free', 'duplicate_paths'
    ]
    
    def path_type_badge(self, obj):
        colors = {
            'STRUCTURED': '#2196f3',
            'FLEXIBLE': '#4caf50',
            'ADAPTIVE': '#9c27b0',
            'CHALLENGE': '#ff5722'
        }
        icons = {
            'STRUCTURED': '📋',
            'FLEXIBLE': '🎯',
            'ADAPTIVE': '🧠',
            'CHALLENGE': '🏆'
        }
        color = colors.get(obj.path_type, '#9e9e9e')
        icon = icons.get(obj.path_type, '📚')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_path_type_display()
        )
    path_type_badge.short_description = '📚 Tipo de Path'
    
    def difficulty_badge(self, obj):
        colors = {
            'BEGINNER': '#4caf50',
            'INTERMEDIATE': '#ff9800',
            'ADVANCED': '#f44336',
            'EXPERT': '#9c27b0'
        }
        icons = {
            'BEGINNER': '🟢',
            'INTERMEDIATE': '🟡',
            'ADVANCED': '🟠',
            'EXPERT': '🔴'
        }
        color = colors.get(obj.difficulty_level, '#9e9e9e')
        icon = icons.get(obj.difficulty_level, '⚪')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_difficulty_level_display()
        )
    difficulty_badge.short_description = '📊 Dificultad'
    
    def status_badge(self, obj):
        colors = {
            'DRAFT': '#9e9e9e',
            'ACTIVE': '#4caf50',
            'PAUSED': '#ff9800',
            'ARCHIVED': '#616161'
        }
        icons = {
            'DRAFT': '✏️',
            'ACTIVE': '🟢',
            'PAUSED': '⏸️',
            'ARCHIVED': '📦'
        }
        color = colors.get(obj.status, '#9e9e9e')
        icon = icons.get(obj.status, '❓')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = '🔄 Estado'
    
    def completion_rate_display(self, obj):
        rate = obj.completion_rate
        if rate >= 80:
            color, icon = '#4caf50', '🏆'
        elif rate >= 60:
            color, icon = '#8bc34a', '🥇'
        elif rate >= 40:
            color, icon = '#ff9800', '🥈'
        elif rate >= 20:
            color, icon = '#ff5722', '🥉'
        else:
            color, icon = '#f44336', '📉'
            
        return format_html(
            '<div style="display: flex; align-items: center; gap: 5px;">'
            '<div style="width: 60px; background: #eee; border-radius: 10px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; height: 15px;"></div></div>'
            '<span style="font-size: 11px;">{} {:.1f}%</span></div>',
            rate, color, icon, rate
        )
    completion_rate_display.short_description = '📈 Tasa Éxito'
    
    def rating_display(self, obj):
        rating = obj.average_rating
        stars = '⭐' * int(rating) + '☆' * (5 - int(rating))
        
        # Color basado en rating
        if rating >= 4.5:
            color = '#4caf50'
        elif rating >= 3.5:
            color = '#8bc34a'
        elif rating >= 2.5:
            color = '#ff9800'
        else:
            color = '#f44336'
            
        return format_html(
            '<div style="display: flex; align-items: center; gap: 3px;">'
            '<span style="font-size: 14px;" title="{:.1f}/5">{}</span>'
            '<small style="color: {};">({:.1f})</small></div>',
            rating, stars, color, rating
        )
    rating_display.short_description = '⭐ Rating'
    
    def enrollments_display(self, obj):
        count = obj.total_enrollments
        if count >= 1000:
            display = f"{count/1000:.1f}K"
            color = '#4caf50'
        elif count >= 100:
            display = f"{count}"
            color = '#8bc34a'
        elif count >= 10:
            display = f"{count}"
            color = '#ff9800'
        else:
            display = f"{count}"
            color = '#9e9e9e'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">👥 {}</span>',
            color, display
        )
    enrollments_display.short_description = '👥 Inscripciones'
    
    def features_summary(self, obj):
        features = []
        if obj.is_premium:
            features.append('<span style="background: #ffd700; color: #333; padding: 1px 3px; border-radius: 3px; font-size: 8px;">💎</span>')
        if obj.is_featured:
            features.append('<span style="background: #ff5722; color: white; padding: 1px 3px; border-radius: 3px; font-size: 8px;">⭐</span>')
        if obj.has_certificates:
            features.append('<span style="background: #2196f3; color: white; padding: 1px 3px; border-radius: 3px; font-size: 8px;">🏆</span>')
        if obj.has_leaderboards:
            features.append('<span style="background: #9c27b0; color: white; padding: 1px 3px; border-radius: 3px; font-size: 8px;">🏅</span>')
        return format_html(' '.join(features) if features else '-')
    features_summary.short_description = '✨ Características'
    
    def ai_status(self, obj):
        if obj.is_ai_enhanced:
            ai_features = []
            if obj.ai_recommendations_enabled:
                ai_features.append('Rec')
            if obj.adaptive_sequencing_enabled:
                ai_features.append('Seq')
            if obj.personalized_feedback_enabled:
                ai_features.append('Feed')
            
            features_text = '+'.join(ai_features) if ai_features else 'Basic'
            return format_html(
                '<span style="background: #00bcd4; color: white; padding: 2px 6px; '
                'border-radius: 8px; font-size: 9px; font-weight: bold;">🤖 {}</span>',
                features_text
            )
        return format_html('<span style="color: #ccc;">➖</span>')
    ai_status.short_description = '🤖 IA'
    
    def metrics_summary(self, obj):
        return format_html(
            '📊 <strong>Inscripciones:</strong> {:,}<br/>'
            '✅ <strong>Completados:</strong> {:,}<br/>'
            '⏱️ <strong>Tiempo promedio:</strong> {:.1f}h<br/>'
            '⭐ <strong>Rating promedio:</strong> {:.1f}/5<br/>'
            '🎮 <strong>XP total disponible:</strong> {:,}',
            obj.total_enrollments, obj.total_completions,
            obj.average_completion_time_hours, obj.average_rating, obj.total_xp_available
        )
    metrics_summary.short_description = 'Resumen de Métricas'
    
    def performance_analysis(self, obj):
        completion_rate = obj.completion_rate
        rating = obj.average_rating
        
        # Análisis de rendimiento
        if completion_rate >= 80 and rating >= 4.0:
            analysis = "🟢 <strong>Excelente:</strong> Alto completamiento y satisfacción"
        elif completion_rate >= 60 and rating >= 3.5:
            analysis = "🟡 <strong>Bueno:</strong> Rendimiento satisfactorio"
        elif completion_rate >= 40 or rating >= 3.0:
            analysis = "🟠 <strong>Regular:</strong> Necesita optimización"
        else:
            analysis = "🔴 <strong>Crítico:</strong> Requiere revisión urgente"
            
        return format_html(analysis)
    performance_analysis.short_description = 'Análisis de Rendimiento'
    
    def publish_paths(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f"🟢 {updated} rutas publicadas y activadas.", messages.SUCCESS)
    publish_paths.short_description = "🟢 Publicar rutas seleccionadas"
    
    def draft_paths(self, request, queryset):
        updated = queryset.update(status='DRAFT')
        self.message_user(request, f"✏️ {updated} rutas movidas a borrador.", messages.INFO)
    draft_paths.short_description = "✏️ Mover a borrador"
    
    def feature_paths(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"⭐ {updated} rutas destacadas.", messages.SUCCESS)
    feature_paths.short_description = "⭐ Destacar rutas"
    
    def unfeature_paths(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"📝 {updated} rutas ya no están destacadas.", messages.INFO)
    unfeature_paths.short_description = "📝 Quitar de destacadas"
    
    def activate_ai_enhancement(self, request, queryset):
        updated = queryset.update(
            is_ai_enhanced=True,
            ai_recommendations_enabled=True,
            adaptive_sequencing_enabled=True,
            personalized_feedback_enabled=True
        )
        self.message_user(request, f"🤖 IA completa activada en {updated} rutas.", messages.SUCCESS)
    activate_ai_enhancement.short_description = "🤖 Activar IA completa"
    
    def make_premium(self, request, queryset):
        updated = queryset.update(is_premium=True)
        self.message_user(request, f"💎 {updated} rutas marcadas como premium.", messages.SUCCESS)
    make_premium.short_description = "💎 Marcar como premium"
    
    def make_free(self, request, queryset):
        updated = queryset.update(is_premium=False)
        self.message_user(request, f"🆓 {updated} rutas marcadas como gratuitas.", messages.SUCCESS)
    make_free.short_description = "🆓 Marcar como gratuitas"
    
    def duplicate_paths(self, request, queryset):
        duplicated = 0
        for path in queryset:
            # Duplicar el path principal
            original_units = path.learningpathunit_set.all()
            path.pk = None
            path.name = f"Copia de {path.name}"
            path.slug = f"{path.slug}-copia"
            path.status = 'DRAFT'
            path.is_featured = False
            path.save()
            
            # Duplicar unidades relacionadas
            for unit in original_units:
                original_lessons = unit.learningpathlesson_set.all()
                unit.pk = None
                unit.learning_path = path
                unit.save()
                
                # Duplicar lecciones relacionadas
                for lesson in original_lessons:
                    lesson.pk = None
                    lesson.path_unit = unit
                    lesson.save()
            
            duplicated += 1
        
        self.message_user(request, f"📋 {duplicated} rutas duplicadas como borradores.", messages.SUCCESS)
    duplicate_paths.short_description = "📋 Duplicar rutas completas"


@admin.register(LearningPathUnit)
class LearningPathUnitAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'learning_path', 'unit_type_badge', 'order',
        'duration_display', 'xp_reward', 'special_badges', 'lessons_count'
    ]
    list_filter = [
        'unit_type', 'is_bonus', 'is_optional', 'is_active',
        'learning_path__path_type', 'learning_path__difficulty_level'
    ]
    search_fields = ['title', 'description', 'learning_path__name']
    ordering = ['learning_path', 'order']
    
    inlines = [LearningPathLessonInline]
    
    fieldsets = (
        ('📚 Información Básica', {
            'fields': ('learning_path', 'title', 'unit_type', 'order'),
            'description': 'Información principal de la unidad del path'
        }),
        ('📝 Descripción y Contenido', {
            'fields': ('description',),
            'description': 'Descripción detallada de la unidad'
        }),
        ('⏱️ Duración y Esfuerzo', {
            'fields': ('estimated_duration_minutes',),
            'description': 'Tiempo estimado para completar la unidad'
        }),
        ('🎮 Gamificación', {
            'fields': ('xp_reward', 'hearts_required'),
            'description': 'Recompensas y costos en el sistema de juego'
        }),
        ('✨ Características Especiales', {
            'fields': ('is_bonus', 'is_optional', 'is_active'),
            'description': 'Configuraciones especiales de la unidad'
        }),
        ('🔧 Metadatos', {
            'fields': ('metadata',),
            'classes': ['collapse'],
            'description': 'Información adicional en formato JSON'
        }),
    )
    
    actions = ['activate_units', 'make_bonus', 'make_optional', 'adjust_order']
    
    def unit_type_badge(self, obj):
        colors = {
            'THEORY': '#2196f3',
            'PRACTICE': '#4caf50',
            'ASSESSMENT': '#ff5722',
            'PROJECT': '#9c27b0',
            'REVIEW': '#607d8b'
        }
        icons = {
            'THEORY': '📚',
            'PRACTICE': '💪',
            'ASSESSMENT': '📊',
            'PROJECT': '🛠️',
            'REVIEW': '🔍'
        }
        color = colors.get(obj.unit_type, '#9e9e9e')
        icon = icons.get(obj.unit_type, '📄')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_unit_type_display()
        )
    unit_type_badge.short_description = '📚 Tipo'
    
    def duration_display(self, obj):
        if obj.estimated_duration_minutes:
            hours = obj.estimated_duration_minutes // 60
            minutes = obj.estimated_duration_minutes % 60
            if hours > 0:
                return format_html('⏱️ {}h {:02d}m', hours, minutes)
            else:
                return format_html('⏱️ {}m', minutes)
        return '-'
    duration_display.short_description = '⏱️ Duración'
    
    def special_badges(self, obj):
        badges = []
        if obj.is_bonus:
            badges.append('<span style="background: #ffd700; color: #333; padding: 1px 4px; border-radius: 3px; font-size: 9px;">🌟 BONUS</span>')
        if obj.is_optional:
            badges.append('<span style="background: #00bcd4; color: white; padding: 1px 4px; border-radius: 3px; font-size: 9px;">📋 OPCIONAL</span>')
        if not obj.is_active:
            badges.append('<span style="background: #9e9e9e; color: white; padding: 1px 4px; border-radius: 3px; font-size: 9px;">❌ INACTIVA</span>')
        return format_html(' '.join(badges) if badges else 
                         '<span style="color: #4caf50;">✅ Normal</span>')
    special_badges.short_description = '🏷️ Especiales'
    
    def lessons_count(self, obj):
        count = obj.learningpathlesson_set.count()
        color = '#4caf50' if count >= 5 else '#ff9800' if count >= 3 else '#f44336'
        return format_html(
            '<span style="color: {}; font-weight: bold;">📖 {}</span>',
            color, count
        )
    lessons_count.short_description = '📖 Lecciones'
    
    def activate_units(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ {updated} unidades activadas.", messages.SUCCESS)
    activate_units.short_description = "✅ Activar unidades"
    
    def make_bonus(self, request, queryset):
        updated = queryset.update(is_bonus=True)
        self.message_user(request, f"🌟 {updated} unidades marcadas como bonus.", messages.SUCCESS)
    make_bonus.short_description = "🌟 Marcar como bonus"
    
    def make_optional(self, request, queryset):
        updated = queryset.update(is_optional=True)
        self.message_user(request, f"📋 {updated} unidades marcadas como opcionales.", messages.INFO)
    make_optional.short_description = "📋 Marcar como opcionales"
    
    def adjust_order(self, request, queryset):
        # Reordenar automáticamente
        for i, unit in enumerate(queryset.order_by('order'), 1):
            unit.order = i * 10  # Dejar espacio entre elementos
            unit.save()
        self.message_user(request, f"🔢 Orden ajustado para {queryset.count()} unidades.", messages.INFO)
    adjust_order.short_description = "🔢 Reordenar automáticamente"


@admin.register(LearningPathLesson)
class LearningPathLessonAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'path_unit', 'lesson_type_badge', 'order',
        'duration_display', 'xp_reward', 'difficulty_indicator', 
        'assessment_info', 'content_summary'
    ]
    list_filter = [
        'lesson_type', 'is_assessment', 'is_active', 'difficulty_level',
        'path_unit__learning_path__path_type'
    ]
    search_fields = ['title', 'path_unit__title', 'path_unit__learning_path__name']
    ordering = ['path_unit', 'order']
    filter_horizontal = ['content_units', 'icfes_questions']
    
    fieldsets = (
        ('📚 Información Básica', {
            'fields': ('path_unit', 'title', 'lesson_type', 'order'),
            'description': 'Información principal de la lección'
        }),
        ('🔗 Contenido Relacionado', {
            'fields': ('content_units', 'icfes_questions'),
            'description': 'Unidades de contenido y preguntas ICFES asociadas'
        }),
        ('⚙️ Configuración de Lección', {
            'fields': (
                'estimated_duration_minutes', 'difficulty_level', 
                'max_attempts', 'passing_score'
            ),
            'description': 'Parámetros de duración, dificultad y evaluación'
        }),
        ('🎮 Gamificación y Recompensas', {
            'fields': ('xp_reward', 'perfect_score_bonus'),
            'description': 'Sistema de puntos y bonificaciones'
        }),
        ('🆘 Sistema de Ayudas', {
            'fields': ('hints_enabled', 'explanations_enabled', 'skip_enabled'),
            'description': 'Configuración de ayudas disponibles para estudiantes'
        }),
        ('🎯 Estado y Evaluación', {
            'fields': ('is_active', 'is_assessment'),
            'description': 'Control de activación y tipo de actividad'
        }),
        ('🔧 Metadatos Técnicos', {
            'fields': ('metadata',),
            'classes': ['collapse'],
            'description': 'Información técnica adicional'
        }),
    )
    
    actions = [
        'activate_lessons', 'enable_all_hints', 'set_as_assessment', 
        'adjust_difficulty', 'bulk_update_xp'
    ]
    
    def lesson_type_badge(self, obj):
        colors = {
            'THEORY': '#2196f3',
            'PRACTICE': '#4caf50',
            'ASSESSMENT': '#ff5722',
            'VIDEO': '#9c27b0',
            'INTERACTIVE': '#ff9800'
        }
        icons = {
            'THEORY': '📚',
            'PRACTICE': '💪', 
            'ASSESSMENT': '📊',
            'VIDEO': '🎥',
            'INTERACTIVE': '🎮'
        }
        color = colors.get(obj.lesson_type, '#9e9e9e')
        icon = icons.get(obj.lesson_type, '📄')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_lesson_type_display()
        )
    lesson_type_badge.short_description = '📚 Tipo'
    
    def duration_display(self, obj):
        if obj.estimated_duration_minutes:
            if obj.estimated_duration_minutes >= 60:
                hours = obj.estimated_duration_minutes // 60
                minutes = obj.estimated_duration_minutes % 60
                return format_html('⏱️ {}h {}m', hours, minutes)
            else:
                return format_html('⏱️ {} min', obj.estimated_duration_minutes)
        return '-'
    duration_display.short_description = '⏱️ Duración'
    
    def difficulty_indicator(self, obj):
        colors = {
            'BEGINNER': '#4caf50',
            'INTERMEDIATE': '#ff9800',
            'ADVANCED': '#f44336',
            'EXPERT': '#9c27b0'
        }
        indicators = {
            'BEGINNER': '●',
            'INTERMEDIATE': '●●',
            'ADVANCED': '●●●',
            'EXPERT': '●●●●'
        }
        color = colors.get(obj.difficulty_level, '#9e9e9e')
        indicator = indicators.get(obj.difficulty_level, '○')
        return format_html(
            '<span style="color: {}; font-weight: bold;" title="{}">{}</span>',
            color, obj.get_difficulty_level_display(), indicator
        )
    difficulty_indicator.short_description = '📊 Dificultad'
    
    def assessment_info(self, obj):
        if obj.is_assessment:
            score_color = 'green' if obj.passing_score >= 80 else 'orange' if obj.passing_score >= 60 else 'red'
            return format_html(
                '<div style="font-size: 10px;">'
                '<span style="color: #ff5722; font-weight: bold;">📊 Evaluación</span><br/>'
                '<span style="color: {};">Min: {:.0f}%</span></div>',
                score_color, obj.passing_score or 0
            )
        return format_html('<span style="color: #4caf50;">📚 Lección</span>')
    assessment_info.short_description = '🎯 Evaluación'
    
    def content_summary(self, obj):
        content_count = obj.content_units.count()
        icfes_count = obj.icfes_questions.count()
        
        summary = []
        if content_count > 0:
            summary.append(f'📦 {content_count}')
        if icfes_count > 0:
            summary.append(f'❓ {icfes_count}')
            
        if summary:
            return format_html(
                '<div style="font-size: 10px; color: #666;">{}</div>',
                ' | '.join(summary)
            )
        return format_html('<span style="color: #ccc;">Sin contenido</span>')
    content_summary.short_description = '📋 Contenido'
    
    def activate_lessons(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ {updated} lecciones activadas.", messages.SUCCESS)
    activate_lessons.short_description = "✅ Activar lecciones"
    
    def enable_all_hints(self, request, queryset):
        updated = queryset.update(
            hints_enabled=True,
            explanations_enabled=True,
            skip_enabled=True
        )
        self.message_user(request, f"🆘 Todas las ayudas habilitadas en {updated} lecciones.", messages.SUCCESS)
    enable_all_hints.short_description = "🆘 Habilitar todas las ayudas"
    
    def set_as_assessment(self, request, queryset):
        updated = queryset.update(is_assessment=True, lesson_type='ASSESSMENT')
        self.message_user(request, f"📊 {updated} lecciones convertidas en evaluaciones.", messages.INFO)
    set_as_assessment.short_description = "📊 Convertir en evaluaciones"
    
    def adjust_difficulty(self, request, queryset):
        # Ajustar dificultad basado en XP reward
        for lesson in queryset:
            if lesson.xp_reward <= 25:
                lesson.difficulty_level = 'BEGINNER'
            elif lesson.xp_reward <= 50:
                lesson.difficulty_level = 'INTERMEDIATE'
            elif lesson.xp_reward <= 75:
                lesson.difficulty_level = 'ADVANCED'
            else:
                lesson.difficulty_level = 'EXPERT'
            lesson.save()
        self.message_user(request, f"📊 Dificultad ajustada automáticamente en {queryset.count()} lecciones.", messages.INFO)
    adjust_difficulty.short_description = "📊 Ajustar dificultad automáticamente"
    
    def bulk_update_xp(self, request, queryset):
        # Actualizar XP basado en duración y tipo
        for lesson in queryset:
            base_xp = lesson.estimated_duration_minutes or 15
            
            # Multiplicadores por tipo
            multipliers = {
                'THEORY': 1.0,
                'PRACTICE': 1.2,
                'ASSESSMENT': 1.5,
                'VIDEO': 0.8,
                'INTERACTIVE': 1.3
            }
            
            multiplier = multipliers.get(lesson.lesson_type, 1.0)
            new_xp = int(base_xp * multiplier)
            lesson.xp_reward = max(10, new_xp)  # Mínimo 10 XP
            lesson.save()
            
        self.message_user(request, f"🎮 XP actualizado automáticamente en {queryset.count()} lecciones.", messages.SUCCESS)
    bulk_update_xp.short_description = "🎮 Actualizar XP automáticamente"


@admin.register(UserPathEnrollment)
class UserPathEnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'learning_path', 'status_badge', 'progress_visual',
        'streak_display', 'total_xp_earned', 'performance_summary', 'enrollment_date'
    ]
    list_filter = [
        'status', 'learning_path__path_type', 'learning_path__difficulty_level',
        'adaptive_difficulty_enabled', 
        ('enrolled_at', admin.DateFieldListFilter),
        ('completed_at', admin.DateFieldListFilter),
    ]
    search_fields = ['user__username', 'user__email', 'learning_path__name']
    ordering = ['-enrolled_at']
    date_hierarchy = 'enrolled_at'
    
    fieldsets = (
        ('👤 Usuario y Ruta de Aprendizaje', {
            'fields': ('user', 'learning_path', 'status'),
            'description': 'Información del estudiante y ruta inscrita'
        }),
        ('📊 Progreso Actual', {
            'fields': (
                'current_unit_order', 'current_lesson_order', 'progress_percentage',
                'total_lessons_completed'
            ),
            'description': 'Estado actual de avance en la ruta'
        }),
        ('📈 Estadísticas de Rendimiento', {
            'fields': (
                'total_xp_earned', 'total_time_minutes', 'average_score'
            ),
            'description': 'Métricas de desempeño acumuladas'
        }),
        ('🎯 Configuración Personal', {
            'fields': ('daily_goal_minutes', 'reminder_time'),
            'description': 'Metas y recordatorios personalizados'
        }),
        ('🔥 Sistema de Rachas', {
            'fields': ('current_streak_days', 'max_streak_days', 'last_activity_date'),
            'description': 'Seguimiento de consistencia en el estudio'
        }),
        ('📅 Cronología de Inscripción', {
            'fields': ('enrolled_at', 'started_at', 'completed_at', 'paused_at'),
            'description': 'Fechas importantes del proceso de aprendizaje'
        }),
        ('🧠 Adaptación Inteligente', {
            'fields': ('adaptive_difficulty_enabled', 'current_difficulty_modifier'),
            'description': 'Configuración de dificultad adaptativa'
        }),
        ('🔧 Metadatos de Inscripción', {
            'fields': ('enrollment_metadata',),
            'classes': ['collapse'],
            'description': 'Información técnica adicional de la inscripción'
        }),
    )
    
    readonly_fields = ['enrolled_at']
    
    actions = [
        'reset_progress', 'award_streak_bonus', 'enable_adaptive_difficulty',
        'mark_as_completed', 'pause_enrollments', 'resume_enrollments'
    ]
    
    def status_badge(self, obj):
        colors = {
            'ENROLLED': '#2196f3',
            'IN_PROGRESS': '#ff9800',
            'COMPLETED': '#4caf50',
            'PAUSED': '#9e9e9e',
            'DROPPED': '#f44336'
        }
        icons = {
            'ENROLLED': '📝',
            'IN_PROGRESS': '🎯',
            'COMPLETED': '🏆',
            'PAUSED': '⏸️',
            'DROPPED': '❌'
        }
        color = colors.get(obj.status, '#9e9e9e')
        icon = icons.get(obj.status, '❓')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = '📊 Estado'
    
    def progress_visual(self, obj):
        percentage = obj.progress_percentage
        
        if percentage >= 100:
            color = '#4caf50'
            icon = '🏆'
        elif percentage >= 75:
            color = '#8bc34a'
            icon = '🥇'
        elif percentage >= 50:
            color = '#ff9800'
            icon = '🥈'
        elif percentage >= 25:
            color = '#ff5722'
            icon = '🥉'
        else:
            color = '#f44336'
            icon = '🎯'
            
        return format_html(
            '<div style="display: flex; align-items: center; gap: 5px;">'
            '<div style="width: 100px; background: #eee; border-radius: 10px; overflow: hidden; position: relative;">'
            '<div style="width: {}%; background: {}; height: 18px; transition: width 0.3s;"></div>'
            '<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; '
            'display: flex; align-items: center; justify-content: center; '
            'font-size: 10px; font-weight: bold; color: #333;">{:.0f}%</div></div>'
            '<span style="font-size: 14px;">{}</span></div>',
            percentage, color, percentage, icon
        )
    progress_visual.short_description = '📈 Progreso'
    
    def streak_display(self, obj):
        current = obj.current_streak_days
        max_streak = obj.max_streak_days
        
        if current >= 30:
            color, icon = '#ff5722', '🔥🔥🔥'
        elif current >= 14:
            color, icon = '#ff9800', '🔥🔥'
        elif current >= 7:
            color, icon = '#ffd700', '🔥'
        elif current >= 3:
            color, icon = '#8bc34a', '⭐'
        else:
            color, icon = '#9e9e9e', '💤'
            
        return format_html(
            '<div style="text-align: center; font-size: 10px;">'
            '<div style="color: {}; font-size: 12px;">{}</div>'
            '<div style="color: #666;">{} días</div>'
            '<div style="color: #999;">(máx: {})</div></div>',
            color, icon, current, max_streak
        )
    streak_display.short_description = '🔥 Racha'
    
    def performance_summary(self, obj):
        score = obj.average_score
        time_hours = obj.total_time_minutes / 60 if obj.total_time_minutes else 0
        
        if score >= 90:
            performance = '🏆 Excelente'
            color = '#4caf50'
        elif score >= 80:
            performance = '🥇 Muy Bueno'
            color = '#8bc34a'
        elif score >= 70:
            performance = '🥈 Bueno'
            color = '#ff9800'
        elif score >= 60:
            performance = '🥉 Regular'
            color = '#ff5722'
        else:
            performance = '📈 En Progreso'
            color = '#9e9e9e'
            
        return format_html(
            '<div style="font-size: 10px; text-align: center;">'
            '<div style="color: {}; font-weight: bold;">{}</div>'
            '<div style="color: #666;">{:.1f}h estudiadas</div></div>',
            color, performance, time_hours
        )
    performance_summary.short_description = '📊 Rendimiento'
    
    def enrollment_date(self, obj):
        return format_html(
            '<div style="font-size: 10px; color: #666;">'
            '📅 {}<br/>🕐 {}</div>',
            obj.enrolled_at.strftime('%d/%m/%Y'),
            obj.enrolled_at.strftime('%H:%M')
        )
    enrollment_date.short_description = '📅 Inscripción'
    
    def reset_progress(self, request, queryset):
        for enrollment in queryset:
            enrollment.current_unit_order = 1
            enrollment.current_lesson_order = 1
            enrollment.progress_percentage = 0
            enrollment.total_lessons_completed = 0
            enrollment.total_xp_earned = 0
            enrollment.total_time_minutes = 0
            enrollment.average_score = 0
            enrollment.status = 'ENROLLED'
            enrollment.save()
        self.message_user(request, f"🔄 Progreso reiniciado para {queryset.count()} inscripciones.", messages.WARNING)
    reset_progress.short_description = "🔄 Reiniciar progreso"
    
    def award_streak_bonus(self, request, queryset):
        bonus_xp = 100
        for enrollment in queryset:
            if enrollment.current_streak_days >= 7:
                enrollment.total_xp_earned += bonus_xp
                enrollment.save()
        self.message_user(request, f"🏆 Bonus de racha (+{bonus_xp} XP) otorgado a usuarios con 7+ días.", messages.SUCCESS)
    award_streak_bonus.short_description = "🏆 Bonus por racha (7+ días)"
    
    def enable_adaptive_difficulty(self, request, queryset):
        updated = queryset.update(adaptive_difficulty_enabled=True)
        self.message_user(request, f"🧠 Dificultad adaptativa habilitada en {updated} inscripciones.", messages.SUCCESS)
    enable_adaptive_difficulty.short_description = "🧠 Habilitar dificultad adaptativa"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(
            status='COMPLETED',
            progress_percentage=100,
            completed_at=timezone.now()
        )
        self.message_user(request, f"🏆 {updated} inscripciones marcadas como completadas.", messages.SUCCESS)
    mark_as_completed.short_description = "🏆 Marcar como completadas"
    
    def pause_enrollments(self, request, queryset):
        updated = queryset.update(status='PAUSED', paused_at=timezone.now())
        self.message_user(request, f"⏸️ {updated} inscripciones pausadas.", messages.INFO)
    pause_enrollments.short_description = "⏸️ Pausar inscripciones"
    
    def resume_enrollments(self, request, queryset):
        updated = queryset.update(status='IN_PROGRESS', paused_at=None)
        self.message_user(request, f"▶️ {updated} inscripciones reanudadas.", messages.SUCCESS)
    resume_enrollments.short_description = "▶️ Reanudar inscripciones"


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'path_lesson', 'status_badge', 'score_performance',
        'attempts_info', 'xp_earned', 'time_summary'
    ]
    list_filter = [
        'status', 'path_lesson__lesson_type', 'path_lesson__is_assessment',
        'path_lesson__path_unit__learning_path__path_type',
        ('completed_at', admin.DateFieldListFilter),
    ]
    search_fields = ['user__username', 'path_lesson__title']
    ordering = ['-updated_at']
    date_hierarchy = 'created_at'
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['reset_lesson_progress', 'award_perfect_bonus', 'mark_as_mastered']
    
    def status_badge(self, obj):
        colors = {
            'NOT_STARTED': '#9e9e9e',
            'IN_PROGRESS': '#ff9800',
            'COMPLETED': '#4caf50',
            'FAILED': '#f44336'
        }
        icons = {
            'NOT_STARTED': '⚪',
            'IN_PROGRESS': '🟡',
            'COMPLETED': '🟢',
            'FAILED': '🔴'
        }
        color = colors.get(obj.status, '#9e9e9e')
        icon = icons.get(obj.status, '❓')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = '📊 Estado'
    
    def score_performance(self, obj):
        score = obj.best_score
        
        if score >= 95:
            icon, color = '🏆', '#ffd700'
            label = 'Perfecto'
        elif score >= 90:
            icon, color = '🥇', '#4caf50'
            label = 'Excelente'
        elif score >= 80:
            icon, color = '🥈', '#8bc34a'
            label = 'Muy Bueno'
        elif score >= 70:
            icon, color = '🥉', '#ff9800'
            label = 'Bueno'
        elif score >= 60:
            icon, color = '📈', '#ff5722'
            label = 'Aprobado'
        else:
            icon, color = '❌', '#f44336'
            label = 'Necesita Mejorar'
            
        return format_html(
            '<div style="text-align: center; font-size: 10px;">'
            '<div style="font-size: 14px;">{}</div>'
            '<div style="color: {}; font-weight: bold;">{:.1f}%</div>'
            '<div style="color: #666;">{}</div></div>',
            icon, color, score, label
        )
    score_performance.short_description = '🎯 Puntuación'
    
    def attempts_info(self, obj):
        attempts = obj.attempts_count
        if attempts == 1:
            color, icon = '#4caf50', '✨'
            label = 'Primer intento'
        elif attempts <= 3:
            color, icon = '#8bc34a', '👍'
            label = f'{attempts} intentos'
        elif attempts <= 5:
            color, icon = '#ff9800', '⚠️'
            label = f'{attempts} intentos'
        else:
            color, icon = '#f44336', '🔄'
            label = f'{attempts} intentos'
            
        return format_html(
            '<div style="text-align: center; font-size: 10px;">'
            '<div style="color: {}; font-size: 12px;">{}</div>'
            '<div style="color: {};">{}</div></div>',
            color, icon, color, label
        )
    attempts_info.short_description = '🔄 Intentos'
    
    def time_summary(self, obj):
        if obj.completed_at:
            days_ago = (timezone.now().date() - obj.completed_at.date()).days
            if days_ago == 0:
                time_label = 'Hoy'
                color = '#4caf50'
            elif days_ago == 1:
                time_label = 'Ayer'
                color = '#8bc34a'
            elif days_ago <= 7:
                time_label = f'{days_ago} días'
                color = '#ff9800'
            else:
                time_label = obj.completed_at.strftime('%d/%m')
                color = '#9e9e9e'
                
            return format_html(
                '<div style="font-size: 10px; text-align: center;">'
                '<div>✅ Completado</div>'
                '<div style="color: {};">{}</div></div>',
                color, time_label
            )
        else:
            return format_html(
                '<div style="font-size: 10px; text-align: center; color: #9e9e9e;">'
                '<div>⏳ En progreso</div></div>'
            )
    time_summary.short_description = '📅 Estado Temporal'
    
    def reset_lesson_progress(self, request, queryset):
        for progress in queryset:
            progress.status = 'NOT_STARTED'
            progress.attempts_count = 0
            progress.best_score = 0
            progress.xp_earned = 0
            progress.completed_at = None
            progress.save()
        self.message_user(request, f"🔄 Progreso reiniciado para {queryset.count()} lecciones.", messages.WARNING)
    reset_lesson_progress.short_description = "🔄 Reiniciar progreso de lecciones"
    
    def award_perfect_bonus(self, request, queryset):
        bonus_xp = 25
        count = 0
        for progress in queryset:
            if progress.best_score >= 95:
                progress.xp_earned += bonus_xp
                progress.save()
                count += 1
        self.message_user(request, f"🏆 Bonus perfecto (+{bonus_xp} XP) otorgado a {count} lecciones con 95%+.", messages.SUCCESS)
    award_perfect_bonus.short_description = "🏆 Bonus por puntuación perfecta (95%+)"
    
    def mark_as_mastered(self, request, queryset):
        updated = queryset.update(status='COMPLETED', best_score=100)
        self.message_user(request, f"🎓 {updated} lecciones marcadas como dominadas.", messages.SUCCESS)
    mark_as_mastered.short_description = "🎓 Marcar como dominadas"


@admin.register(PathAchievement)
class PathAchievementAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'achievement_type_badge', 'learning_path', 'rarity_display',
        'xp_reward', 'earned_count', 'status_info'
    ]
    list_filter = [
        'achievement_type', 'rarity', 'is_active', 'is_secret',
        'learning_path__path_type'
    ]
    search_fields = ['name', 'description', 'learning_path__name']
    ordering = ['learning_path', 'achievement_type', 'rarity', 'name']
    
    fieldsets = (
        ('🏆 Información del Logro', {
            'fields': ('name', 'description', 'achievement_type', 'learning_path'),
            'description': 'Información principal del achievement'
        }),
        ('🎨 Visualización', {
            'fields': ('icon_emoji', 'badge_color', 'rarity'),
            'description': 'Elementos visuales del logro'
        }),
        ('📋 Criterios de Obtención', {
            'fields': ('criteria',),
            'description': 'Condiciones que deben cumplirse para obtener el logro'
        }),
        ('🎁 Recompensas', {
            'fields': ('xp_reward', 'special_rewards'),
            'description': 'Beneficios otorgados al conseguir el achievement'
        }),
        ('⚙️ Configuración', {
            'fields': ('is_active', 'is_secret'),
            'description': 'Control de visibilidad y activación'
        }),
    )
    
    actions = ['activate_achievements', 'make_secret', 'adjust_xp_rewards']
    
    def achievement_type_badge(self, obj):
        colors = {
            'COMPLETION': '#4caf50',
            'MASTERY': '#2196f3',
            'STREAK': '#ff9800',
            'SPEED': '#9c27b0',
            'SCORE': '#ffd700',
            'SPECIAL': '#f44336'
        }
        icons = {
            'COMPLETION': '✅',
            'MASTERY': '🎓',
            'STREAK': '🔥',
            'SPEED': '⚡',
            'SCORE': '🎯',
            'SPECIAL': '⭐'
        }
        color = colors.get(obj.achievement_type, '#9e9e9e')
        icon = icons.get(obj.achievement_type, '🏆')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_achievement_type_display()
        )
    achievement_type_badge.short_description = '🏆 Tipo'
    
    def rarity_display(self, obj):
        colors = {
            'COMMON': '#9e9e9e',
            'RARE': '#2196f3',
            'EPIC': '#9c27b0',
            'LEGENDARY': '#ffd700'
        }
        icons = {
            'COMMON': '⚪',
            'RARE': '🔵',
            'EPIC': '🟣',
            'LEGENDARY': '🟡'
        }
        color = colors.get(obj.rarity, '#9e9e9e')
        icon = icons.get(obj.rarity, '⚪')
        return format_html(
            '<span style="background: {}; color: {}; padding: 2px 8px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold; '
            'text-shadow: 1px 1px 1px rgba(0,0,0,0.5);">{} {}</span>',
            color, 'white' if obj.rarity != 'LEGENDARY' else 'black',
            icon, obj.rarity
        )
    rarity_display.short_description = '💎 Rareza'
    
    def earned_count(self, obj):
        count = obj.userpathachievement_set.count()
        if count >= 100:
            color, icon = '#4caf50', '🔥'
        elif count >= 50:
            color, icon = '#8bc34a', '💪'
        elif count >= 10:
            color, icon = '#ff9800', '👍'
        elif count > 0:
            color, icon = '#2196f3', '🎯'
        else:
            color, icon = '#9e9e9e', '❓'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, count
        )
    earned_count.short_description = '👥 Obtenido por'
    
    def status_info(self, obj):
        badges = []
        if obj.is_active:
            badges.append('<span style="background: #4caf50; color: white; padding: 1px 4px; border-radius: 3px; font-size: 9px;">✅ ACTIVO</span>')
        else:
            badges.append('<span style="background: #f44336; color: white; padding: 1px 4px; border-radius: 3px; font-size: 9px;">❌ INACTIVO</span>')
            
        if obj.is_secret:
            badges.append('<span style="background: #9c27b0; color: white; padding: 1px 4px; border-radius: 3px; font-size: 9px;">🔒 SECRETO</span>')
            
        return format_html(' '.join(badges))
    status_info.short_description = '🏷️ Estado'
    
    def activate_achievements(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ {updated} logros activados.", messages.SUCCESS)
    activate_achievements.short_description = "✅ Activar logros"
    
    def make_secret(self, request, queryset):
        updated = queryset.update(is_secret=True)
        self.message_user(request, f"🔒 {updated} logros marcados como secretos.", messages.INFO)
    make_secret.short_description = "🔒 Marcar como secretos"
    
    def adjust_xp_rewards(self, request, queryset):
        rarity_multipliers = {
            'COMMON': 1.0,
            'RARE': 1.5,
            'EPIC': 2.0,
            'LEGENDARY': 3.0
        }
        
        for achievement in queryset:
            base_xp = 50  # XP base
            multiplier = rarity_multipliers.get(achievement.rarity, 1.0)
            achievement.xp_reward = int(base_xp * multiplier)
            achievement.save()
            
        self.message_user(request, f"🎮 XP ajustado por rareza en {queryset.count()} logros.", messages.INFO)
    adjust_xp_rewards.short_description = "🎮 Ajustar XP por rareza"


@admin.register(UserPathAchievement)
class UserPathAchievementAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'achievement', 'rarity_badge', 'progress_when_earned', 
        'xp_earned', 'earned_time'
    ]
    list_filter = [
        'achievement__achievement_type', 'achievement__rarity',
        'achievement__learning_path__path_type',
        ('earned_at', admin.DateFieldListFilter),
    ]
    search_fields = ['user__username', 'achievement__name']
    ordering = ['-earned_at']
    date_hierarchy = 'earned_at'
    readonly_fields = ['earned_at']
    
    def rarity_badge(self, obj):
        colors = {
            'COMMON': '#9e9e9e',
            'RARE': '#2196f3',
            'EPIC': '#9c27b0',
            'LEGENDARY': '#ffd700'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px; font-weight: bold;">{}</span>',
            colors.get(obj.achievement.rarity, '#9e9e9e'),
            obj.achievement.rarity
        )
    rarity_badge.short_description = '💎 Rareza'
    
    def earned_time(self, obj):
        days_ago = (timezone.now().date() - obj.earned_at.date()).days
        if days_ago == 0:
            return format_html('<span style="color: #4caf50;">🎉 Hoy</span>')
        elif days_ago == 1:
            return format_html('<span style="color: #8bc34a;">✨ Ayer</span>')
        elif days_ago <= 7:
            return format_html('<span style="color: #ff9800;">📅 {} días</span>', days_ago)
        else:
            return format_html('<span style="color: #9e9e9e;">📅 {}</span>', 
                             obj.earned_at.strftime('%d/%m/%Y'))
    earned_time.short_description = '📅 Obtenido'


@admin.register(LearningPathReview)
class LearningPathReviewAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'learning_path', 'rating_display', 'aspects_summary',
        'recommend_badge', 'helpful_votes', 'review_date'
    ]
    list_filter = [
        'rating', 'would_recommend', 'learning_path__path_type',
        'learning_path__difficulty_level',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = ['user__username', 'learning_path__name', 'review_text']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('👤 Usuario y Ruta', {
            'fields': ('user', 'learning_path'),
        }),
        ('⭐ Calificación Principal', {
            'fields': ('rating', 'review_text'),
        }),
        ('📊 Evaluación por Aspectos', {
            'fields': ('content_quality', 'difficulty_appropriate', 'instructor_quality'),
        }),
        ('💭 Recomendación y Utilidad', {
            'fields': ('would_recommend', 'helpful_votes'),
        }),
        ('📅 Información Temporal', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    actions = ['feature_reviews', 'mark_helpful', 'moderate_reviews']
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        
        if obj.rating >= 4:
            color = '#4caf50'
        elif obj.rating >= 3:
            color = '#ff9800'
        else:
            color = '#f44336'
            
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 14px;">{}</div>'
            '<div style="color: {}; font-weight: bold;">{}/5</div></div>',
            stars, color, obj.rating
        )
    rating_display.short_description = '⭐ Calificación'
    
    def aspects_summary(self, obj):
        aspects = []
        
        if obj.content_quality:
            color = '#4caf50' if obj.content_quality >= 4 else '#ff9800' if obj.content_quality >= 3 else '#f44336'
            aspects.append(f'<span style="color: {color};">📚 {obj.content_quality}</span>')
            
        if obj.difficulty_appropriate:
            color = '#4caf50' if obj.difficulty_appropriate >= 4 else '#ff9800' if obj.difficulty_appropriate >= 3 else '#f44336'
            aspects.append(f'<span style="color: {color};">📊 {obj.difficulty_appropriate}</span>')
            
        if obj.instructor_quality:
            color = '#4caf50' if obj.instructor_quality >= 4 else '#ff9800' if obj.instructor_quality >= 3 else '#f44336'
            aspects.append(f'<span style="color: {color};">👨‍🏫 {obj.instructor_quality}</span>')
            
        return format_html('<div style="font-size: 10px;">{}</div>', '<br/>'.join(aspects))
    aspects_summary.short_description = '📊 Aspectos'
    
    def recommend_badge(self, obj):
        if obj.would_recommend:
            return format_html(
                '<span style="background: #4caf50; color: white; padding: 2px 6px; '
                'border-radius: 8px; font-size: 10px; font-weight: bold;">👍 SÍ</span>'
            )
        return format_html(
            '<span style="background: #f44336; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px; font-weight: bold;">👎 NO</span>'
        )
    recommend_badge.short_description = '💭 Recomienda'
    
    def review_date(self, obj):
        return format_html(
            '<div style="font-size: 10px; color: #666;">{}</div>',
            obj.created_at.strftime('%d/%m/%Y %H:%M')
        )
    review_date.short_description = '📅 Fecha'
    
    def feature_reviews(self, request, queryset):
        # Función para destacar reseñas (implementación futura)
        high_quality_reviews = queryset.filter(rating__gte=4, would_recommend=True)
        count = high_quality_reviews.count()
        self.message_user(request, f"⭐ {count} reseñas de alta calidad identificadas para destacar.", messages.INFO)
    feature_reviews.short_description = "⭐ Identificar reseñas destacadas"
    
    def mark_helpful(self, request, queryset):
        # Incrementar votos útiles para reseñas de alta calidad
        for review in queryset.filter(rating__gte=4):
            review.helpful_votes += 1
            review.save()
        self.message_user(request, f"👍 Votos útiles incrementados para reseñas de calidad.", messages.SUCCESS)
    mark_helpful.short_description = "👍 Incrementar utilidad"
    
    def moderate_reviews(self, request, queryset):
        # Marcar reseñas que podrían necesitar moderación
        problematic = queryset.filter(rating__lte=2, would_recommend=False)
        count = problematic.count()
        self.message_user(request, f"⚠️ {count} reseñas marcadas para revisión manual.", messages.WARNING)
    moderate_reviews.short_description = "⚠️ Marcar para moderación" 