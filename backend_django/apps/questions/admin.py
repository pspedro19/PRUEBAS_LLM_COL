"""
Administración Django para el sistema de preguntas ICFES
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import TextInput, Textarea
from .models import (
    Subject, Topic, ICFESCuadernillo, Question, QuestionOption, 
    QuestionExplanation, QuestionSet, QuestionSetItem, 
    UserQuestionResponse, QuestionMultimedia
)


# Configuración de widgets para campos largos
class AdminTextareaWidget(Textarea):
    def __init__(self, attrs=None):
        default_attrs = {'rows': 4, 'cols': 80}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'area', 'code', 'color_preview', 'is_active', 'created_at']
    list_filter = ['area', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['area', 'name']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
            obj.color_theme
        )
    color_preview.short_description = 'Color'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'order', 'is_active', 'created_at']
    list_filter = ['subject', 'is_active']
    search_fields = ['name', 'description', 'keywords']
    ordering = ['subject', 'order', 'name']
    filter_horizontal = ['prerequisite_topics']


@admin.register(ICFESCuadernillo)
class ICFESCuadernilloAdmin(admin.ModelAdmin):
    list_display = ['name', 'cuadernillo_type', 'period', 'subject', 'total_questions', 'is_processed', 'created_at']
    list_filter = ['cuadernillo_type', 'period', 'subject', 'is_processed', 'is_active']
    search_fields = ['name', 'code', 'processing_notes']
    ordering = ['-period', 'subject', 'name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'cuadernillo_type', 'period', 'code', 'subject', 'grade_level')
        }),
        ('Archivos', {
            'fields': ('pdf_file_url', 'pdf_file_path', 'total_pages')
        }),
        ('Estado', {
            'fields': ('total_questions', 'is_processed', 'is_active', 'processing_notes')
        }),
    )


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4
    fields = ['option_letter', 'option_text', 'is_correct', 'explanation', 'extraction_confidence']
    formfield_overrides = {
        models.TextField: {'widget': AdminTextareaWidget(attrs={'rows': 2, 'cols': 50})},
    }


class QuestionExplanationInline(admin.TabularInline):
    model = QuestionExplanation
    extra = 1
    fields = ['explanation_type', 'target_role', 'title', 'content', 'difficulty_level', 'order']
    formfield_overrides = {
        models.TextField: {'widget': AdminTextareaWidget(attrs={'rows': 3, 'cols': 50})},
    }


class QuestionMultimediaInline(admin.TabularInline):
    model = QuestionMultimedia
    extra = 1
    fields = ['media_type', 'file_url', 'alt_text', 'is_primary', 'order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'question_preview', 'subject', 'topic', 'difficulty', 
        'content_type', 'cuadernillo', 'question_number', 'success_rate_display',
        'is_verified', 'manual_review_required'
    ]
    list_filter = [
        'subject', 'topic', 'difficulty', 'content_type', 'source_type',
        'is_verified', 'manual_review_required', 'is_active',
        'mathematical_notation', 'has_diagram', 'has_graph', 'has_table'
    ]
    search_fields = ['question_text', 'question_number', 'source_reference', 'tags']
    ordering = ['-created_at']
    
    inlines = [QuestionOptionInline, QuestionExplanationInline, QuestionMultimediaInline]
    
    fieldsets = (
        ('Contenido de la Pregunta', {
            'fields': ('question_text', 'question_image_url', 'question_audio_url')
        }),
        ('Multimedia ICFES', {
            'fields': ('content_type', 'has_diagram', 'has_graph', 'has_table',
                      'diagram_image_url', 'graph_image_url', 'table_image_url'),
            'classes': ['collapse']
        }),
        ('Clasificación', {
            'fields': ('subject', 'topic', 'difficulty', 'question_type')
        }),
        ('Origen ICFES', {
            'fields': ('cuadernillo', 'question_number', 'page_number', 
                      'source_type', 'source_reference', 'official_answer_key')
        }),
        ('Análisis Automático', {
            'fields': ('mathematical_notation', 'geometric_figures', 'statistical_data', 
                      'word_problem', 'detected_topics', 'tags'),
            'classes': ['collapse']
        }),
        ('Control de Calidad', {
            'fields': ('extraction_confidence', 'extraction_notes', 'manual_review_required',
                      'is_verified', 'verification_notes', 'is_active')
        }),
        ('Estadísticas', {
            'fields': ('times_asked', 'times_correct', 'average_time_seconds'),
            'classes': ['collapse']
        }),
        ('IA', {
            'fields': ('ai_explanation_prompt',),
            'classes': ['collapse']
        }),
    )
    
    formfield_overrides = {
        models.TextField: {'widget': AdminTextareaWidget()},
    }
    
    def question_preview(self, obj):
        preview = obj.question_text[:100]
        if len(obj.question_text) > 100:
            preview += "..."
        return preview
    question_preview.short_description = 'Pregunta'
    
    def success_rate_display(self, obj):
        rate = obj.success_rate
        color = 'green' if rate > 70 else 'orange' if rate > 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    success_rate_display.short_description = 'Éxito'
    
    actions = ['mark_as_verified', 'mark_for_review', 'mark_as_active']
    
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True, manual_review_required=False)
        self.message_user(request, f"{queryset.count()} preguntas marcadas como verificadas.")
    mark_as_verified.short_description = "Marcar como verificadas"
    
    def mark_for_review(self, request, queryset):
        queryset.update(manual_review_required=True, is_verified=False)
        self.message_user(request, f"{queryset.count()} preguntas marcadas para revisión.")
    mark_for_review.short_description = "Marcar para revisión"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} preguntas activadas.")
    mark_as_active.short_description = "Activar preguntas"


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['question_id', 'option_letter', 'option_preview', 'is_correct', 'extraction_confidence']
    list_filter = ['is_correct', 'has_image', 'has_mathematical_notation']
    search_fields = ['question__question_text', 'option_text']
    ordering = ['question', 'order']
    
    def question_id(self, obj):
        return f"Q{obj.question.id}"
    question_id.short_description = 'Pregunta'
    
    def option_preview(self, obj):
        preview = obj.option_text[:50]
        if len(obj.option_text) > 50:
            preview += "..."
        return preview
    option_preview.short_description = 'Opción'


@admin.register(QuestionExplanation)
class QuestionExplanationAdmin(admin.ModelAdmin):
    list_display = ['question_id', 'explanation_type', 'target_role', 'title', 'difficulty_level']
    list_filter = ['explanation_type', 'target_role', 'difficulty_level', 'is_active']
    search_fields = ['question__question_text', 'title', 'content']
    ordering = ['question', 'order']
    
    def question_id(self, obj):
        return f"Q{obj.question.id}"
    question_id.short_description = 'Pregunta'


class QuestionSetItemInline(admin.TabularInline):
    model = QuestionSetItem
    extra = 0
    fields = ['question', 'order', 'points', 'tank_difficulty_modifier', 
              'dps_difficulty_modifier', 'support_difficulty_modifier', 'specialist_difficulty_modifier']


@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'set_type', 'question_count', 'subject_filter', 'difficulty_filter', 'is_active']
    list_filter = ['set_type', 'subject_filter', 'difficulty_filter', 'is_active', 'is_public']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    inlines = [QuestionSetItemInline]
    
    filter_horizontal = ['topic_filters']
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Preguntas'


@admin.register(UserQuestionResponse)
class UserQuestionResponseAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'question_id', 'is_correct', 'response_time_seconds', 
        'confidence_level', 'quiz_type', 'xp_gained', 'created_at'
    ]
    list_filter = [
        'is_correct', 'quiz_type', 'confidence_level', 'role_bonus_applied',
        'ai_explanation_requested', 'difficulty_perceived'
    ]
    search_fields = ['user__username', 'question__question_text', 'session_id']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def question_id(self, obj):
        return f"Q{obj.question.id}"
    question_id.short_description = 'Pregunta'
    
    readonly_fields = ['created_at']


@admin.register(QuestionMultimedia)
class QuestionMultimediaAdmin(admin.ModelAdmin):
    list_display = ['question_id', 'media_type', 'file_preview', 'is_primary', 'file_size_display']
    list_filter = ['media_type', 'is_primary', 'is_active']
    search_fields = ['question__question_text', 'alt_text']
    ordering = ['question', 'order']
    
    def question_id(self, obj):
        return f"Q{obj.question.id}"
    question_id.short_description = 'Pregunta'
    
    def file_preview(self, obj):
        if obj.file_url:
            return format_html('<a href="{}" target="_blank">Ver archivo</a>', obj.file_url)
        return "Sin archivo"
    file_preview.short_description = 'Archivo'
    
    def file_size_display(self, obj):
        if obj.file_size_kb > 0:
            return f"{obj.file_size_kb} KB"
        return "N/A"
    file_size_display.short_description = 'Tamaño'


# Configuración del admin site
admin.site.site_header = "ICFES Quest - Administración"
admin.site.site_title = "ICFES Quest Admin"
admin.site.index_title = "Panel de Administración del Sistema de Preguntas" 