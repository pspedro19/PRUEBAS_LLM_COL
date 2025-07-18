"""
Comando Django para crear Learning Paths de demostración
Conecta con las 49 preguntas ICFES existentes
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.learning.models import (
    LearningPath, LearningPathUnit, LearningPathLesson,
    PathAchievement, UserPathEnrollment
)
from apps.content.models import ContentCategory
from apps.icfes.models import PreguntaICFES, AreaEvaluacion

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea Learning Paths de demostración conectados con preguntas ICFES'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Limpiar learning paths existentes antes de crear nuevos'
        )
        parser.add_argument(
            '--create-users',
            action='store_true',
            help='Crear usuarios de prueba con progreso'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Iniciando configuración de Learning Paths demo...')
        )

        if options['clear_existing']:
            self.clear_existing_data()

        with transaction.atomic():
            # 1. Crear categorías de contenido
            categories = self.create_content_categories()
            
            # 2. Crear learning paths
            learning_paths = self.create_learning_paths(categories)
            
            # 3. Crear unidades y lecciones con preguntas ICFES
            self.create_units_and_lessons(learning_paths)
            
            # 4. Crear achievements
            self.create_achievements(learning_paths)
            
            # 5. Crear usuarios de prueba si se solicita
            if options['create_users']:
                self.create_demo_users(learning_paths)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Learning Paths demo configurados exitosamente!\n"
                f"📊 Paths creados: {len(learning_paths)}\n"
                f"🎯 Conectados con {PreguntaICFES.objects.count()} preguntas ICFES\n"
                f"🚀 Sistema listo para testing!"
            )
        )

    def clear_existing_data(self):
        """Limpiar datos existentes"""
        self.stdout.write("🧹 Limpiando datos existentes...")
        
        # Eliminar en orden para evitar problemas de FK
        UserPathEnrollment.objects.all().delete()
        PathAchievement.objects.all().delete()
        LearningPathLesson.objects.all().delete()
        LearningPathUnit.objects.all().delete()
        LearningPath.objects.all().delete()
        ContentCategory.objects.all().delete()
        
        self.stdout.write("✅ Datos existentes eliminados")

    def create_content_categories(self):
        """Crear categorías de contenido"""
        self.stdout.write("📚 Creando categorías de contenido...")
        
        categories_data = [
            {
                'name': 'Matemáticas ICFES',
                'slug': 'matematicas-icfes',
                'description': 'Preparación completa para matemáticas del examen ICFES',
                'icon': '🔢',
                'color_theme': '#FF6B35',
                'category_type': 'EXAM_PREP',
                'is_featured': True
            },
            {
                'name': 'Álgebra Fundamental',
                'slug': 'algebra-fundamental',
                'description': 'Conceptos fundamentales de álgebra para ICFES',
                'icon': '📐',
                'color_theme': '#4ECDC4',
                'category_type': 'ACADEMIC',
                'is_featured': True
            },
            {
                'name': 'Geometría y Trigonometría',
                'slug': 'geometria-trigonometria',
                'description': 'Geometría plana, espacial y trigonometría básica',
                'icon': '📏',
                'color_theme': '#45B7D1',
                'category_type': 'ACADEMIC',
                'is_featured': True
            },
            {
                'name': 'Estadística y Probabilidad',
                'slug': 'estadistica-probabilidad',
                'description': 'Análisis de datos y conceptos de probabilidad',
                'icon': '📊',
                'color_theme': '#96CEB4',
                'category_type': 'ACADEMIC',
                'is_featured': True
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = ContentCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f"  ✅ Categoría creada: {category.name}")
        
        return categories

    def create_learning_paths(self, categories):
        """Crear learning paths principales"""
        self.stdout.write("🎯 Creando Learning Paths...")
        
        # Obtener área de matemáticas de ICFES
        try:
            area_matematicas = AreaEvaluacion.objects.get(codigo='MATEMATICAS')
        except AreaEvaluacion.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("⚠️ Área de matemáticas ICFES no encontrada")
            )
            area_matematicas = None
        
        paths_data = [
            {
                'name': 'Maestría Matemática ICFES',
                'slug': 'maestria-matematica-icfes',
                'description': 'Ruta completa de preparación matemática para el examen ICFES. Domina todos los temas evaluados con preguntas reales.',
                'difficulty_level': 3,
                'path_type': 'SEQUENTIAL',
                'status': 'ACTIVE',
                'category': categories[0],  # Matemáticas ICFES
                'estimated_duration_hours': 40,
                'minimum_level': 5,
                'is_featured': True,
                'is_premium': False,
                'has_certificate': True,
                'tags': 'matemáticas,icfes,examen,preparación,álgebra,geometría',
                'total_xp_available': 2450,  # 49 preguntas * 50 XP promedio
                'vitality_cost': 2
            },
            {
                'name': 'Álgebra desde Cero',
                'slug': 'algebra-desde-cero',
                'description': 'Aprende álgebra paso a paso, desde conceptos básicos hasta ecuaciones complejas.',
                'difficulty_level': 2,
                'path_type': 'ADAPTIVE',
                'status': 'ACTIVE',
                'category': categories[1],  # Álgebra Fundamental
                'estimated_duration_hours': 25,
                'minimum_level': 3,
                'is_featured': True,
                'is_premium': False,
                'has_certificate': True,
                'tags': 'álgebra,ecuaciones,básico,fundamentos',
                'total_xp_available': 1250,
                'vitality_cost': 1
            },
            {
                'name': 'Geometría Espacial Avanzada',
                'slug': 'geometria-espacial-avanzada',
                'description': 'Domina la geometría en 3D y trigonometría avanzada para el ICFES.',
                'difficulty_level': 4,
                'path_type': 'MASTERY',
                'status': 'ACTIVE',
                'category': categories[2],  # Geometría y Trigonometría
                'estimated_duration_hours': 30,
                'minimum_level': 8,
                'is_featured': False,
                'is_premium': True,
                'has_certificate': True,
                'tags': 'geometría,trigonometría,3d,espacial,avanzado',
                'total_xp_available': 1800,
                'vitality_cost': 3
            },
            {
                'name': 'Estadística en Acción',
                'slug': 'estadistica-en-accion',
                'description': 'Aprende estadística aplicada y probabilidad con casos reales del ICFES.',
                'difficulty_level': 3,
                'path_type': 'PROJECT_BASED',
                'status': 'ACTIVE',
                'category': categories[3],  # Estadística y Probabilidad
                'estimated_duration_hours': 20,
                'minimum_level': 6,
                'is_featured': False,
                'is_premium': False,
                'has_certificate': False,
                'tags': 'estadística,probabilidad,datos,análisis',
                'total_xp_available': 1000,
                'vitality_cost': 2
            }
        ]
        
        learning_paths = []
        for path_data in paths_data:
            learning_path, created = LearningPath.objects.get_or_create(
                slug=path_data['slug'],
                defaults=path_data
            )
            learning_paths.append(learning_path)
            if created:
                self.stdout.write(f"  ✅ Learning Path creado: {learning_path.name}")
        
        return learning_paths

    def create_units_and_lessons(self, learning_paths):
        """Crear unidades y lecciones conectadas con preguntas ICFES"""
        self.stdout.write("📝 Creando unidades y lecciones con preguntas ICFES...")
        
        # Obtener todas las preguntas ICFES disponibles
        preguntas_icfes = list(PreguntaICFES.objects.filter(
            activa=True,
            verificada=True
        ).select_related('area_tematica'))
        
        if not preguntas_icfes:
            self.stdout.write(
                self.style.WARNING("⚠️ No se encontraron preguntas ICFES activas")
            )
            return
        
        self.stdout.write(f"📊 Encontradas {len(preguntas_icfes)} preguntas ICFES")
        
        # Agrupar preguntas por área temática
        preguntas_por_area = {}
        for pregunta in preguntas_icfes:
            area_key = pregunta.area_tematica.codigo if pregunta.area_tematica else 'GENERAL'
            if area_key not in preguntas_por_area:
                preguntas_por_area[area_key] = []
            preguntas_por_area[area_key].append(pregunta)
        
        # Configuración de unidades por learning path
        unidades_config = {
            'maestria-matematica-icfes': [
                {
                    'title': 'Aritmética y Operaciones',
                    'description': 'Operaciones básicas, fracciones, decimales y porcentajes',
                    'area_filter': 'ARITMETICA_OPERACIONES',
                    'xp_reward': 150,
                    'order': 1
                },
                {
                    'title': 'Álgebra y Ecuaciones',
                    'description': 'Ecuaciones lineales, cuadráticas y sistemas',
                    'area_filter': 'ALGEBRA_FUNCIONES',
                    'xp_reward': 200,
                    'order': 2
                },
                {
                    'title': 'Geometría y Medidas',
                    'description': 'Figuras planas, volúmenes y trigonometría',
                    'area_filter': 'GEOMETRIA_TRIGONOMETRIA',
                    'xp_reward': 200,
                    'order': 3
                },
                {
                    'title': 'Estadística y Probabilidad',
                    'description': 'Análisis de datos, gráficas y probabilidad',
                    'area_filter': 'ESTADISTICA_PROBABILIDAD',
                    'xp_reward': 150,
                    'order': 4
                },
                {
                    'title': 'Problemas Aplicados',
                    'description': 'Problemas contextualizados y aplicaciones',
                    'area_filter': 'PROBLEMAS_APLICADOS',
                    'xp_reward': 180,
                    'order': 5
                }
            ],
            'algebra-desde-cero': [
                {
                    'title': 'Fundamentos Algebraicos',
                    'description': 'Variables, expresiones y operaciones básicas',
                    'area_filter': 'ALGEBRA_FUNCIONES',
                    'xp_reward': 100,
                    'order': 1
                },
                {
                    'title': 'Ecuaciones Lineales',
                    'description': 'Resolución de ecuaciones de primer grado',
                    'area_filter': 'ALGEBRA_FUNCIONES',
                    'xp_reward': 120,
                    'order': 2
                },
                {
                    'title': 'Sistemas de Ecuaciones',
                    'description': 'Métodos de solución para sistemas lineales',
                    'area_filter': 'ALGEBRA_FUNCIONES',
                    'xp_reward': 150,
                    'order': 3
                }
            ]
        }
        
        # Crear unidades para los paths principales
        for learning_path in learning_paths[:2]:  # Solo para los primeros 2 paths
            if learning_path.slug not in unidades_config:
                continue
            
            unidades_data = unidades_config[learning_path.slug]
            
            for unidad_data in unidades_data:
                # Crear unidad
                unit = LearningPathUnit.objects.create(
                    learning_path=learning_path,
                    title=unidad_data['title'],
                    description=unidad_data['description'],
                    order_index=unidad_data['order'],
                    xp_reward=unidad_data['xp_reward']
                )
                
                # Filtrar preguntas para esta unidad
                area_key = unidad_data['area_filter']
                preguntas_unidad = preguntas_por_area.get(area_key, [])
                
                # Crear lecciones con preguntas
                for i, pregunta in enumerate(preguntas_unidad[:8]):  # Máximo 8 preguntas por unidad
                    lesson = LearningPathLesson.objects.create(
                        path_unit=unit,
                        icfes_question=pregunta,
                        title=f"Problema {i+1}: {pregunta.pregunta_texto[:50]}...",
                        description=f"Resuelve este problema de {pregunta.area_tematica.nombre if pregunta.area_tematica else 'matemáticas'}",
                        order_index=i + 1,
                        is_mandatory=True,
                        xp_reward=pregunta.puntos_xp,
                        time_limit_minutes=pregunta.tiempo_estimado_segundos // 60,
                        retry_limit=3
                    )
                
                self.stdout.write(f"  ✅ Unidad creada: {unit.title} ({len(preguntas_unidad[:8])} lecciones)")

    def create_achievements(self, learning_paths):
        """Crear achievements para los learning paths"""
        self.stdout.write("🏆 Creando achievements...")
        
        achievements_data = [
            {
                'name': 'Primer Paso',
                'description': 'Completa tu primera lección',
                'achievement_type': 'COMPLETION',
                'rarity_level': 'COMMON',
                'icon_emoji': '👶',
                'required_lessons_completed': 1,
                'required_progress_percentage': 0,
                'xp_reward': 50,
                'is_hidden': False
            },
            {
                'name': 'En Marcha',
                'description': 'Alcanza 25% de progreso en el path',
                'achievement_type': 'COMPLETION',
                'rarity_level': 'COMMON',
                'icon_emoji': '🚶',
                'required_lessons_completed': 0,
                'required_progress_percentage': 25,
                'xp_reward': 100,
                'is_hidden': False
            },
            {
                'name': 'A Medio Camino',
                'description': 'Completa el 50% del learning path',
                'achievement_type': 'COMPLETION',
                'rarity_level': 'UNCOMMON',
                'icon_emoji': '🏃',
                'required_lessons_completed': 0,
                'required_progress_percentage': 50,
                'xp_reward': 200,
                'is_hidden': False
            },
            {
                'name': 'Casi Listo',
                'description': 'Alcanza 75% de progreso',
                'achievement_type': 'COMPLETION',
                'rarity_level': 'RARE',
                'icon_emoji': '💪',
                'required_lessons_completed': 0,
                'required_progress_percentage': 75,
                'xp_reward': 300,
                'is_hidden': False
            },
            {
                'name': 'Maestro Matemático',
                'description': 'Completa todo el learning path',
                'achievement_type': 'COMPLETION',
                'rarity_level': 'EPIC',
                'icon_emoji': '🎓',
                'required_lessons_completed': 0,
                'required_progress_percentage': 100,
                'xp_reward': 500,
                'is_hidden': False
            },
            {
                'name': 'Racha de Fuego',
                'description': 'Mantén una racha de 7 días',
                'achievement_type': 'STREAK',
                'rarity_level': 'RARE',
                'icon_emoji': '🔥',
                'required_streak_days': 7,
                'xp_reward': 250,
                'is_hidden': False
            },
            {
                'name': 'Perfeccionista',
                'description': 'Obtén puntuación perfecta en 5 lecciones',
                'achievement_type': 'SCORE',
                'rarity_level': 'EPIC',
                'icon_emoji': '⭐',
                'required_score': 100,
                'required_lessons_completed': 5,
                'xp_reward': 400,
                'is_hidden': False
            },
            {
                'name': 'Leyenda Matemática',
                'description': 'Logro secreto para verdaderos maestros',
                'achievement_type': 'COMPLETION',
                'rarity_level': 'LEGENDARY',
                'icon_emoji': '👑',
                'required_progress_percentage': 100,
                'required_score': 95,
                'xp_reward': 1000,
                'is_hidden': True
            }
        ]
        
        for learning_path in learning_paths:
            for achievement_data in achievements_data:
                achievement, created = PathAchievement.objects.get_or_create(
                    learning_path=learning_path,
                    name=achievement_data['name'],
                    defaults=achievement_data
                )
                if created:
                    self.stdout.write(f"  ✅ Achievement creado: {achievement.name}")

    def create_demo_users(self, learning_paths):
        """Crear usuarios de demostración con progreso"""
        self.stdout.write("👥 Creando usuarios de demostración...")
        
        demo_users_data = [
            {
                'username': 'demo_estudiante',
                'email': 'estudiante@demo.com',
                'first_name': 'Ana',
                'last_name': 'Estudiante',
                'level': 3,
                'hero_class': 'D',
                'experience_points': 450
            },
            {
                'username': 'demo_avanzado',
                'email': 'avanzado@demo.com',
                'first_name': 'Carlos',
                'last_name': 'Avanzado',
                'level': 8,
                'hero_class': 'A',
                'experience_points': 2100
            },
            {
                'username': 'demo_principiante',
                'email': 'principiante@demo.com',
                'first_name': 'María',
                'last_name': 'Principiante',
                'level': 1,
                'hero_class': 'F',
                'experience_points': 50
            }
        ]
        
        created_users = []
        for user_data in demo_users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={**user_data, 'password': 'demopass123'}
            )
            if created:
                user.set_password('demopass123')
                user.save()
                created_users.append(user)
                self.stdout.write(f"  ✅ Usuario creado: {user.username}")
        
        # Crear inscripciones y progreso para usuarios demo
        for i, user in enumerate(created_users):
            # Inscribir en el path principal
            main_path = learning_paths[0]  # Maestría Matemática ICFES
            
            enrollment = UserPathEnrollment.objects.create(
                user=user,
                learning_path=main_path,
                status='ACTIVE',
                overall_progress_percentage=min(85, (i + 1) * 25),  # Progreso variable
                current_streak_days=i + 1,
                total_xp_earned=(i + 1) * 200,
                daily_goal_minutes=30 + (i * 15)
            )
            
            self.stdout.write(f"  ✅ Inscripción creada: {user.username} -> {main_path.name}")
        
        self.stdout.write(f"🎉 {len(created_users)} usuarios demo creados con progreso") 