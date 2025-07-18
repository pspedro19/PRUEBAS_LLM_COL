"""
Admin de Django para la app de contenido educativo - Versión mejorada
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
    ContentCategory, ContentUnit, ContentLesson, 
    UserContentProgress, ContentRating, ContentBookmark
)


class AdminTextareaWidget(Textarea):
    def __init__(self, attrs=None):
        default_attrs = {'rows': 4, 'cols': 80}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category_type', 'parent_category', 'order', 
        'color_preview', 'stats_display', 'featured_badge', 'status_badge'
    ]
    list_filter = [
        'category_type', 'is_active', 'is_featured', 'parent_category',
        'min_grade_level', 'max_grade_level'
    ]
    search_fields = ['name', 'description', 'tags']
    ordering = ['parent_category', 'order', 'name']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('📚 Información Básica', {
            'fields': ('name', 'slug', 'description', 'category_type'),
            'description': 'Información principal de la categoría'
        }),
        ('🏗️ Jerarquía y Organización', {
            'fields': ('parent_category', 'order'),
            'description': 'Define la estructura jerárquica y orden de visualización'
        }),
        ('🎨 Visualización y Diseño', {
            'fields': ('icon', 'color_theme', 'cover_image_url'),
            'description': 'Elementos visuales para la interfaz de usuario'
        }),
        ('🎓 Configuración Educativa', {
            'fields': ('min_grade_level', 'max_grade_level'),
            'description': 'Rangos de edad y grado recomendados'
        }),
        ('⚙️ Estado y Configuración', {
            'fields': ('is_active', 'is_featured'),
            'description': 'Control de visibilidad y destacado'
        }),
        ('🏷️ Metadatos y SEO', {
            'fields': ('tags', 'metadata'),
            'classes': ['collapse'],
            'description': 'Información adicional para búsquedas y categorización'
        }),
    )
    
    formfield_overrides = {
        models.TextField: {'widget': AdminTextareaWidget()},
    }
    
    actions = ['activate_categories', 'deactivate_categories', 'feature_categories', 'unfeature_categories']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; '
            'border-radius: 5px; display: inline-block; border: 1px solid #ccc; '
            'box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>',
            obj.color_theme or '#e0e0e0'
        )
    color_preview.short_description = '🎨 Color'
    
    def stats_display(self, obj):
        units_count = obj.contentunit_set.count()
        return format_html(
            '<span style="background: #f0f0f0; padding: 2px 8px; border-radius: 10px; '
            'font-size: 11px; color: #666;">📦 {} unidades</span>',
            units_count
        )
    stats_display.short_description = '📊 Estadísticas'
    
    def featured_badge(self, obj):
        if obj.is_featured:
            return format_html(
                '<span style="background: #ffd700; color: #333; padding: 2px 6px; '
                'border-radius: 8px; font-size: 10px; font-weight: bold;">⭐ DESTACADA</span>'
            )
        return '-'
    featured_badge.short_description = '⭐ Destacada'
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #4caf50; color: white; padding: 2px 6px; '
                'border-radius: 8px; font-size: 10px; font-weight: bold;">✅ ACTIVA</span>'
            )
        else:
            return format_html(
                '<span style="background: #f44336; color: white; padding: 2px 6px; '
                'border-radius: 8px; font-size: 10px; font-weight: bold;">❌ INACTIVA</span>'
            )
    status_badge.short_description = '🔄 Estado'
    
    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ {updated} categorías activadas exitosamente.", messages.SUCCESS)
    activate_categories.short_description = "✅ Activar categorías seleccionadas"
    
    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"❌ {updated} categorías desactivadas.", messages.WARNING)
    deactivate_categories.short_description = "❌ Desactivar categorías seleccionadas"
    
    def feature_categories(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"⭐ {updated} categorías marcadas como destacadas.", messages.SUCCESS)
    feature_categories.short_description = "⭐ Marcar como destacadas"
    
    def unfeature_categories(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"📝 {updated} categorías ya no están destacadas.", messages.INFO)
    unfeature_categories.short_description = "📝 Quitar de destacadas"


class ContentLessonInline(admin.TabularInline):
    model = ContentLesson
    extra = 1
    fields = [
        'title', 'lesson_type', 'content_format', 'order', 
        'duration_display', 'xp_reward', 'mandatory_badge'
    ]
    readonly_fields = ['duration_display', 'mandatory_badge']
    ordering = ['order']
    
    def duration_display(self, obj):
        if obj.estimated_duration_seconds:
            minutes = obj.estimated_duration_seconds // 60
            seconds = obj.estimated_duration_seconds % 60
            return f"⏱️ {minutes}:{seconds:02d}"
        return "-"
    duration_display.short_description = 'Duración'
    
    def mandatory_badge(self, obj):
        if obj.is_mandatory:
            return format_html('<span style="color: #d32f2f;">🔴 Obligatoria</span>')
        return format_html('<span style="color: #4caf50;">🟢 Opcional</span>')
    mandatory_badge.short_description = 'Tipo'


@admin.register(ContentUnit)
class ContentUnitAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'unit_type', 'difficulty_badge', 
        'completion_rate_display', 'rating_display', 'xp_reward', 
        'status_badges', 'stats_summary'
    ]
    list_filter = [
        'category', 'unit_type', 'difficulty_level', 'is_active', 
        'is_premium', 'is_featured', 'has_theory', 'has_practice',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = ['title', 'description', 'learning_objectives', 'tags']
    ordering = ['category', 'order', 'title']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['prerequisite_units']
    
    inlines = [ContentLessonInline]
    
    fieldsets = (
        ('📚 Información Básica', {
            'fields': ('title', 'slug', 'description', 'category', 'unit_type'),
            'description': 'Información principal de la unidad de contenido'
        }),
        ('🎯 Configuración Educativa', {
            'fields': (
                'difficulty_level', 'estimated_duration_minutes', 
                'recommended_age_min', 'recommended_age_max'
            ),
            'description': 'Configuración pedagógica y recomendaciones de edad'
        }),
        ('🔗 Prerrequisitos y Dependencias', {
            'fields': ('prerequisite_units',),
            'description': 'Unidades que deben completarse antes de esta'
        }),
        ('🎮 Gamificación y Recompensas', {
            'fields': ('xp_reward', 'hearts_required', 'completion_criteria'),
            'description': 'Sistema de puntos, vidas y criterios de finalización'
        }),
        ('🎬 Contenido Multimedia', {
            'fields': ('thumbnail_url', 'video_intro_url', 'audio_intro_url'),
            'description': 'Recursos audiovisuales y miniaturas'
        }),
        ('📋 Tipos de Contenido Incluido', {
            'fields': ('has_theory', 'has_examples', 'has_practice', 'has_assessment'),
            'description': 'Marcar los tipos de contenido que incluye esta unidad'
        }),
        ('⚙️ Estado y Configuración', {
            'fields': ('order', 'is_active', 'is_premium', 'is_featured'),
            'description': 'Control de visibilidad, orden y características especiales'
        }),
        ('🎯 Objetivos y Metadatos', {
            'fields': ('learning_objectives', 'tags', 'metadata'),
            'classes': ['collapse'],
            'description': 'Objetivos de aprendizaje y información adicional'
        }),
        ('📊 Métricas y Estadísticas (Solo Lectura)', {
            'fields': (
                'stats_display', 'performance_metrics'
            ),
            'classes': ['collapse'],
            'description': 'Estadísticas de uso y rendimiento'
        }),
    )
    
    readonly_fields = [
        'total_attempts', 'total_completions', 
        'average_completion_time', 'average_rating', 'uuid',
        'stats_display', 'performance_metrics'
    ]
    
    formfield_overrides = {
        models.TextField: {'widget': AdminTextareaWidget()},
    }
    
    actions = [
        'activate_units', 'deactivate_units', 'mark_as_featured', 
        'mark_as_premium', 'reset_statistics', 'duplicate_units'
    ]
    
    def difficulty_badge(self, obj):
        colors = {
            'BEGINNER': '#4caf50',
            'INTERMEDIATE': '#ff9800', 
            'ADVANCED': '#f44336',
            'EXPERT': '#9c27b0'
        }
        color = colors.get(obj.difficulty_level, '#9e9e9e')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_difficulty_level_display()
        )
    difficulty_badge.short_description = '📊 Dificultad'
    
    def completion_rate_display(self, obj):
        rate = obj.completion_rate
        if rate >= 80:
            color, icon = '#4caf50', '🟢'
        elif rate >= 60:
            color, icon = '#ff9800', '🟡'
        elif rate >= 40:
            color, icon = '#ff5722', '🟠'
        else:
            color, icon = '#f44336', '🔴'
            
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
        return format_html(
            '<span title="{:.1f}/5" style="font-size: 14px;">{}</span>',
            rating, stars
        )
    rating_display.short_description = '⭐ Rating'
    
    def status_badges(self, obj):
        badges = []
        if obj.is_active:
            badges.append('<span style="background: #4caf50; color: white; padding: 1px 4px; border-radius: 3px; font-size: 9px;">ACTIVA</span>')
        if obj.is_premium:
            badges.append('<span style="background: #ffd700; color: #333; padding: 1px 4px; border-radius: 3px; font-size: 9px;">💎 PREMIUM</span>')
        if obj.is_featured:
            badges.append('<span style="background: #ff5722; color: white; padding: 1px 4px; border-radius: 3px; font-size: 9px;">⭐ DESTACADA</span>')
        return format_html(' '.join(badges) if badges else '-')
    status_badges.short_description = '🏷️ Estado'
    
    def stats_summary(self, obj):
        return format_html(
            '<div style="font-size: 10px; color: #666;">'
            '👥 {} intentos<br/>✅ {} completados</div>',
            obj.total_attempts, obj.total_completions
        )
    stats_summary.short_description = '📊 Resumen'
    
    def stats_display(self, obj):
        return format_html(
            '📊 Intentos: {} | ✅ Completados: {} | ⏱️ Tiempo promedio: {:.1f}min | ⭐ Rating: {:.1f}/5',
            obj.total_attempts, obj.total_completions, 
            obj.average_completion_time, obj.average_rating
        )
    stats_display.short_description = 'Estadísticas Completas'
    
    def performance_metrics(self, obj):
        completion_rate = obj.completion_rate
        if completion_rate >= 80:
            performance = "🟢 Excelente"
        elif completion_rate >= 60:
            performance = "🟡 Bueno" 
        elif completion_rate >= 40:
            performance = "🟠 Regular"
        else:
            performance = "🔴 Necesita mejoras"
            
        return format_html(
            'Rendimiento: {} ({}% completitud)',
            performance, completion_rate
        )
    performance_metrics.short_description = 'Análisis de Rendimiento'
    
    def activate_units(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ {updated} unidades activadas.", messages.SUCCESS)
    activate_units.short_description = "✅ Activar unidades seleccionadas"
    
    def deactivate_units(self, request, queryset):
        updated = queryset.update(is_active=False) 
        self.message_user(request, f"❌ {updated} unidades desactivadas.", messages.WARNING)
    deactivate_units.short_description = "❌ Desactivar unidades seleccionadas"
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"⭐ {updated} unidades marcadas como destacadas.", messages.SUCCESS)
    mark_as_featured.short_description = "⭐ Marcar como destacadas"
    
    def mark_as_premium(self, request, queryset):
        updated = queryset.update(is_premium=True)
        self.message_user(request, f"💎 {updated} unidades marcadas como premium.", messages.SUCCESS)
    mark_as_premium.short_description = "💎 Marcar como premium"
    
    def reset_statistics(self, request, queryset):
        for unit in queryset:
            unit.total_attempts = 0
            unit.total_completions = 0
            unit.average_completion_time = 0
            unit.average_rating = 0
            unit.save()
        self.message_user(request, f"🔄 Estadísticas reiniciadas para {queryset.count()} unidades.", messages.INFO)
    reset_statistics.short_description = "🔄 Reiniciar estadísticas"
    
    def duplicate_units(self, request, queryset):
        duplicated = 0
        for unit in queryset:
            unit.pk = None
            unit.title = f"Copia de {unit.title}"
            unit.slug = f"{unit.slug}-copia"
            unit.is_active = False
            unit.save()
            duplicated += 1
        self.message_user(request, f"📋 {duplicated} unidades duplicadas (inactivas).", messages.SUCCESS)
    duplicate_units.short_description = "📋 Duplicar unidades seleccionadas"


@admin.register(ContentLesson)
class ContentLessonAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'content_unit', 'lesson_type_badge', 'content_format_badge', 
        'order', 'duration_display', 'xp_reward', 'mandatory_status'
    ]
    list_filter = [
        'lesson_type', 'content_format', 'is_mandatory', 'is_active',
        'content_unit__category', 'content_unit__difficulty_level'
    ]
    search_fields = ['title', 'content_text', 'content_unit__title']
    ordering = ['content_unit', 'order']
    
    fieldsets = (
        ('📚 Información Básica', {
            'fields': ('content_unit', 'title', 'lesson_type', 'content_format', 'order'),
            'description': 'Información principal de la lección'
        }),
        ('📝 Contenido Textual', {
            'fields': ('content_text', 'content_html'),
            'description': 'Contenido principal en texto plano y HTML'
        }),
        ('🎬 Contenido Multimedia', {
            'fields': ('video_url', 'audio_url', 'image_url', 'interactive_url'),
            'description': 'Enlaces a recursos multimedia'
        }),
        ('⚙️ Configuración de Lección', {
            'fields': ('estimated_duration_seconds', 'is_mandatory', 'is_active'),
            'description': 'Configuración de duración y requisitos'
        }),
        ('🎮 Gamificación', {
            'fields': ('xp_reward',),
            'description': 'Puntos de experiencia otorgados'
        }),
        ('🔧 Metadatos', {
            'fields': ('metadata',),
            'classes': ['collapse'],
            'description': 'Información adicional en formato JSON'
        }),
    )
    
    formfield_overrides = {
        models.TextField: {'widget': AdminTextareaWidget()},
    }
    
    actions = ['activate_lessons', 'make_mandatory', 'make_optional', 'adjust_xp_rewards']
    
    def lesson_type_badge(self, obj):
        colors = {
            'THEORY': '#2196f3',
            'PRACTICE': '#4caf50', 
            'ASSESSMENT': '#ff5722',
            'VIDEO': '#9c27b0',
            'INTERACTIVE': '#ff9800'
        }
        color = colors.get(obj.lesson_type, '#9e9e9e')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px; font-weight: bold;">{}</span>',
            color, obj.get_lesson_type_display()
        )
    lesson_type_badge.short_description = '📚 Tipo'
    
    def content_format_badge(self, obj):
        icons = {
            'TEXT': '📝',
            'VIDEO': '🎥',
            'AUDIO': '🎵',
            'IMAGE': '🖼️',
            'INTERACTIVE': '🎮',
            'MIXED': '🎯'
        }
        icon = icons.get(obj.content_format, '📄')
        return format_html(
            '<span style="font-size: 14px;" title="{}">{}</span>',
            obj.get_content_format_display(), icon
        )
    content_format_badge.short_description = '🎨 Formato'
    
    def duration_display(self, obj):
        if obj.estimated_duration_seconds:
            minutes = obj.estimated_duration_seconds // 60
            seconds = obj.estimated_duration_seconds % 60
            if minutes > 0:
                return format_html('⏱️ {}:{:02d}', minutes, seconds)
            else:
                return format_html('⏱️ {}s', seconds)
        return '-'
    duration_display.short_description = '⏱️ Duración'
    
    def mandatory_status(self, obj):
        if obj.is_mandatory:
            return format_html(
                '<span style="color: #d32f2f; font-weight: bold;">🔴 Obligatoria</span>'
            )
        return format_html(
            '<span style="color: #4caf50;">🟢 Opcional</span>'
        )
    mandatory_status.short_description = '🎯 Tipo'
    
    def activate_lessons(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ {updated} lecciones activadas.", messages.SUCCESS)
    activate_lessons.short_description = "✅ Activar lecciones seleccionadas"
    
    def make_mandatory(self, request, queryset):
        updated = queryset.update(is_mandatory=True)
        self.message_user(request, f"🔴 {updated} lecciones marcadas como obligatorias.", messages.WARNING)
    make_mandatory.short_description = "🔴 Marcar como obligatorias"
    
    def make_optional(self, request, queryset):
        updated = queryset.update(is_mandatory=False)
        self.message_user(request, f"🟢 {updated} lecciones marcadas como opcionales.", messages.SUCCESS)
    make_optional.short_description = "🟢 Marcar como opcionales"
    
    def adjust_xp_rewards(self, request, queryset):
        # Ejemplo: ajustar XP basado en duración
        for lesson in queryset:
            if lesson.estimated_duration_seconds:
                minutes = lesson.estimated_duration_seconds // 60
                new_xp = max(10, minutes * 5)  # Mínimo 10 XP, 5 XP por minuto
                lesson.xp_reward = new_xp
                lesson.save()
        self.message_user(request, f"🎮 XP ajustado para {queryset.count()} lecciones.", messages.INFO)
    adjust_xp_rewards.short_description = "🎮 Ajustar XP automáticamente"


@admin.register(UserContentProgress)
class UserContentProgressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'content_unit', 'status_badge', 'progress_bar',
        'attempts_count', 'score_display', 'xp_earned', 'time_info'
    ]
    list_filter = [
        'status', 'is_completed', 'is_mastered', 
        'content_unit__category', 'content_unit__difficulty_level',
        ('created_at', admin.DateFieldListFilter),
        ('completed_at', admin.DateFieldListFilter),
    ]
    search_fields = ['user__username', 'user__email', 'content_unit__title']
    ordering = ['-updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('👤 Usuario y Contenido', {
            'fields': ('user', 'content_unit', 'status'),
            'description': 'Información del estudiante y unidad de contenido'
        }),
        ('📊 Progreso y Completitud', {
            'fields': ('progress_percentage', 'is_completed', 'is_mastered'),
            'description': 'Estado de avance y dominio del contenido'
        }),
        ('🎯 Estadísticas de Rendimiento', {
            'fields': (
                'attempts_count', 'best_score', 'total_time_seconds',
                'completion_time_seconds'
            ),
            'description': 'Métricas de desempeño y tiempo invertido'
        }),
        ('📅 Cronología', {
            'fields': (
                'first_attempt_at', 'last_attempt_at', 
                'completed_at', 'mastered_at'
            ),
            'description': 'Fechas importantes del progreso'
        }),
        ('🎮 Gamificación', {
            'fields': ('xp_earned', 'hearts_spent'),
            'description': 'Puntos de experiencia y vidas utilizadas'
        }),
        ('📋 Información Detallada', {
            'fields': ('lesson_progress', 'mistakes_data', 'metadata'),
            'classes': ['collapse'],
            'description': 'Datos específicos de progreso por lección y errores'
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['reset_progress', 'mark_as_mastered', 'award_bonus_xp']
    
    def status_badge(self, obj):
        colors = {
            'NOT_STARTED': '#9e9e9e',
            'IN_PROGRESS': '#ff9800',
            'COMPLETED': '#4caf50',
            'MASTERED': '#2196f3'
        }
        icons = {
            'NOT_STARTED': '⚪',
            'IN_PROGRESS': '🟡', 
            'COMPLETED': '🟢',
            'MASTERED': '🔵'
        }
        color = colors.get(obj.status, '#9e9e9e')
        icon = icons.get(obj.status, '⚪')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = '📊 Estado'
    
    def progress_bar(self, obj):
        percentage = obj.progress_percentage
        if percentage >= 100:
            color = '#4caf50'
        elif percentage >= 80:
            color = '#8bc34a'
        elif percentage >= 50:
            color = '#ff9800'
        else:
            color = '#f44336'
            
        return format_html(
            '<div style="width: 120px; background: #eee; border-radius: 10px; overflow: hidden; position: relative;">'
            '<div style="width: {}%; background: {}; height: 20px; transition: width 0.3s;"></div>'
            '<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; '
            'display: flex; align-items: center; justify-content: center; '
            'font-size: 11px; font-weight: bold; color: #333;">{:.1f}%</div></div>',
            percentage, color, percentage
        )
    progress_bar.short_description = '📈 Progreso'
    
    def score_display(self, obj):
        score = obj.best_score
        if score >= 90:
            color, icon = '#4caf50', '🏆'
        elif score >= 80:
            color, icon = '#8bc34a', '🥇'
        elif score >= 70:
            color, icon = '#ff9800', '🥈'
        elif score >= 60:
            color, icon = '#ff5722', '🥉'
        else:
            color, icon = '#f44336', '❌'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {:.1f}%</span>',
            color, icon, score
        )
    score_display.short_description = '🎯 Mejor Puntuación'
    
    def time_info(self, obj):
        if obj.completed_at:
            return format_html(
                '<small style="color: #666;">✅ {}</small>',
                obj.completed_at.strftime('%d/%m/%y')
            )
        elif obj.last_attempt_at:
            return format_html(
                '<small style="color: #ff9800;">🕐 {}</small>',
                obj.last_attempt_at.strftime('%d/%m/%y')
            )
        return '-'
    time_info.short_description = '📅 Última Actividad'
    
    def reset_progress(self, request, queryset):
        count = 0
        for progress in queryset:
            progress.status = 'NOT_STARTED'
            progress.progress_percentage = 0
            progress.is_completed = False
            progress.is_mastered = False
            progress.attempts_count = 0
            progress.best_score = 0
            progress.xp_earned = 0
            progress.save()
            count += 1
        self.message_user(request, f"🔄 Progreso reiniciado para {count} registros.", messages.WARNING)
    reset_progress.short_description = "🔄 Reiniciar progreso seleccionado"
    
    def mark_as_mastered(self, request, queryset):
        updated = queryset.update(
            is_mastered=True, 
            is_completed=True,
            status='MASTERED',
            mastered_at=timezone.now()
        )
        self.message_user(request, f"🔵 {updated} registros marcados como dominados.", messages.SUCCESS)
    mark_as_mastered.short_description = "🔵 Marcar como dominado"
    
    def award_bonus_xp(self, request, queryset):
        bonus_xp = 50
        for progress in queryset:
            progress.xp_earned += bonus_xp
            progress.save()
        self.message_user(request, f"🎮 +{bonus_xp} XP otorgado a {queryset.count()} usuarios.", messages.SUCCESS)
    award_bonus_xp.short_description = "🎮 Otorgar XP bonus (+50)"


@admin.register(ContentRating)
class ContentRatingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'content_unit', 'rating_stars', 'quality_badge',
        'recommend_badge', 'helpful_badge', 'review_preview', 'created_at'
    ]
    list_filter = [
        'rating', 'content_quality', 'would_recommend', 'is_helpful',
        'content_unit__category', 'content_unit__difficulty_level',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = ['user__username', 'content_unit__title', 'review_text']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('👤 Usuario y Contenido', {
            'fields': ('user', 'content_unit'),
        }),
        ('⭐ Calificación Principal', {
            'fields': ('rating', 'review_text'),
        }),
        ('📊 Evaluación Detallada', {
            'fields': ('content_quality', 'difficulty_appropriate', 'clarity_rating'),
        }),
        ('💭 Opinión y Recomendación', {
            'fields': ('would_recommend', 'is_helpful'),
        }),
        ('📅 Información de Seguimiento', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_as_helpful', 'mark_as_not_helpful', 'feature_reviews']
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="font-size: 16px;" title="{}/5">{}</span>',
            obj.rating, stars
        )
    rating_stars.short_description = '⭐ Calificación'
    
    def quality_badge(self, obj):
        colors = {
            'EXCELLENT': '#4caf50',
            'GOOD': '#8bc34a',
            'AVERAGE': '#ff9800',
            'POOR': '#f44336'
        }
        color = colors.get(obj.content_quality, '#9e9e9e')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px; font-weight: bold;">{}</span>',
            color, obj.get_content_quality_display()
        )
    quality_badge.short_description = '📊 Calidad'
    
    def recommend_badge(self, obj):
        if obj.would_recommend:
            return format_html(
                '<span style="color: #4caf50; font-weight: bold;">👍 Recomienda</span>'
            )
        return format_html(
            '<span style="color: #f44336;">👎 No recomienda</span>'
        )
    recommend_badge.short_description = '👥 Recomendación'
    
    def helpful_badge(self, obj):
        if obj.is_helpful:
            return format_html(
                '<span style="color: #4caf50;">✅ Útil</span>'
            )
        return format_html(
            '<span style="color: #9e9e9e;">➖ Neutral</span>'
        )
    helpful_badge.short_description = '💡 Utilidad'
    
    def review_preview(self, obj):
        if obj.review_text:
            preview = obj.review_text[:100]
            if len(obj.review_text) > 100:
                preview += "..."
            return format_html(
                '<div style="max-width: 200px; font-size: 11px; color: #666;">{}</div>',
                preview
            )
        return format_html('<em style="color: #ccc;">Sin comentario</em>')
    review_preview.short_description = '💬 Comentario'
    
    def mark_as_helpful(self, request, queryset):
        updated = queryset.update(is_helpful=True)
        self.message_user(request, f"✅ {updated} reseñas marcadas como útiles.", messages.SUCCESS)
    mark_as_helpful.short_description = "✅ Marcar como útiles"
    
    def mark_as_not_helpful(self, request, queryset):
        updated = queryset.update(is_helpful=False)
        self.message_user(request, f"❌ {updated} reseñas marcadas como no útiles.", messages.INFO)
    mark_as_not_helpful.short_description = "❌ Marcar como no útiles"
    
    def feature_reviews(self, request, queryset):
        # Esta sería una funcionalidad para destacar reseñas
        self.message_user(request, f"⭐ {queryset.count()} reseñas destacadas (función por implementar).", messages.INFO)
    feature_reviews.short_description = "⭐ Destacar reseñas seleccionadas"


@admin.register(ContentBookmark)
class ContentBookmarkAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'content_unit', 'category_info', 'notes_preview', 
        'tags_display', 'created_at'
    ]
    list_filter = [
        'content_unit__category', 'content_unit__difficulty_level',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = ['user__username', 'content_unit__title', 'notes', 'tags']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('👤 Usuario y Contenido', {
            'fields': ('user', 'content_unit'),
        }),
        ('📝 Notas Personales', {
            'fields': ('notes',),
            'description': 'Notas privadas del usuario sobre este contenido'
        }),
        ('🏷️ Etiquetas', {
            'fields': ('tags',),
            'description': 'Etiquetas personalizadas para organizar favoritos'
        }),
        ('📅 Información de Fecha', {
            'fields': ('created_at',),
        }),
    )
    
    readonly_fields = ['created_at']
    
    actions = ['export_bookmarks', 'clear_notes', 'add_study_tag']
    
    def category_info(self, obj):
        category = obj.content_unit.category
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px; font-weight: bold;">{}</span>',
            category.color_theme or '#9e9e9e', category.name
        )
    category_info.short_description = '📚 Categoría'
    
    def notes_preview(self, obj):
        if obj.notes:
            preview = obj.notes[:80]
            if len(obj.notes) > 80:
                preview += "..."
            return format_html(
                '<div style="max-width: 200px; font-size: 11px; color: #333; '
                'background: #f5f5f5; padding: 3px 6px; border-radius: 5px;">{}</div>',
                preview
            )
        return format_html('<em style="color: #ccc;">📝 Sin notas</em>')
    notes_preview.short_description = '📝 Notas'
    
    def tags_display(self, obj):
        if obj.tags:
            tags = obj.tags.split(',')[:3]  # Mostrar solo primeras 3 etiquetas
            tag_html = []
            for tag in tags:
                tag_html.append(
                    f'<span style="background: #e3f2fd; color: #1976d2; '
                    f'padding: 1px 4px; border-radius: 3px; font-size: 9px; '
                    f'margin-right: 2px;">#{tag.strip()}</span>'
                )
            return format_html(''.join(tag_html))
        return '-'
    tags_display.short_description = '🏷️ Etiquetas'
    
    def export_bookmarks(self, request, queryset):
        # Función para exportar favoritos (implementación pendiente)
        self.message_user(
            request, 
            f"📤 Exportación de {queryset.count()} favoritos (función por implementar).", 
            messages.INFO
        )
    export_bookmarks.short_description = "📤 Exportar favoritos seleccionados"
    
    def clear_notes(self, request, queryset):
        updated = queryset.update(notes='')
        self.message_user(request, f"🗑️ Notas eliminadas de {updated} favoritos.", messages.WARNING)
    clear_notes.short_description = "🗑️ Limpiar notas"
    
    def add_study_tag(self, request, queryset):
        for bookmark in queryset:
            current_tags = bookmark.tags or ''
            if 'estudio' not in current_tags.lower():
                new_tags = f"{current_tags}, estudio" if current_tags else "estudio"
                bookmark.tags = new_tags
                bookmark.save()
        self.message_user(request, f"🏷️ Etiqueta 'estudio' añadida a {queryset.count()} favoritos.", messages.SUCCESS)
    add_study_tag.short_description = "🏷️ Añadir etiqueta 'estudio'" 