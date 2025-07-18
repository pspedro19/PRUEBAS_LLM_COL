"""
Tests unitarios para Learning Paths APIs optimizadas
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    LearningPath, LearningPathUnit, LearningPathLesson,
    UserPathEnrollment, UserLessonProgress, PathAchievement
)
from apps.content.models import ContentCategory
from apps.icfes.models import AreaEvaluacion

User = get_user_model()


class LearningPathModelTests(TestCase):
    """Tests para modelos de Learning Paths"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear categoría de prueba
        self.category = ContentCategory.objects.create(
            name='Matemáticas Básicas',
            slug='matematicas-basicas',
            description='Categoría de prueba',
            is_active=True
        )
        
        # Crear learning path de prueba
        self.learning_path = LearningPath.objects.create(
            name='Álgebra Básica',
            slug='algebra-basica',
            description='Path de prueba para álgebra',
            difficulty_level=2,
            path_type='SEQUENTIAL',
            status='ACTIVE',
            category=self.category,
            estimated_duration_hours=10,
            minimum_level=1,
            total_xp_available=500
        )
        
        # Crear unidad de prueba
        self.unit = LearningPathUnit.objects.create(
            learning_path=self.learning_path,
            title='Ecuaciones Lineales',
            description='Unidad de prueba',
            order_index=1,
            xp_reward=100
        )
        
        # Crear lección de prueba
        self.lesson = LearningPathLesson.objects.create(
            path_unit=self.unit,
            title='Resolver ecuaciones simples',
            description='Lección de prueba',
            order_index=1,
            xp_reward=50
        )
    
    def test_learning_path_creation(self):
        """Test creación de learning path"""
        self.assertEqual(self.learning_path.name, 'Álgebra Básica')
        self.assertEqual(self.learning_path.slug, 'algebra-basica')
        self.assertEqual(self.learning_path.status, 'ACTIVE')
        self.assertTrue(self.learning_path.uuid)
    
    def test_learning_path_str_representation(self):
        """Test representación string"""
        expected = f"{self.learning_path.name} ({self.learning_path.difficulty_level})"
        self.assertEqual(str(self.learning_path), expected)
    
    def test_user_enrollment_creation(self):
        """Test creación de inscripción"""
        enrollment = UserPathEnrollment.objects.create(
            user=self.user,
            learning_path=self.learning_path,
            status='ACTIVE'
        )
        
        self.assertEqual(enrollment.user, self.user)
        self.assertEqual(enrollment.learning_path, self.learning_path)
        self.assertEqual(enrollment.status, 'ACTIVE')
        self.assertEqual(enrollment.overall_progress_percentage, 0.0)
    
    def test_user_lesson_progress_creation(self):
        """Test creación de progreso de lección"""
        enrollment = UserPathEnrollment.objects.create(
            user=self.user,
            learning_path=self.learning_path
        )
        
        progress = UserLessonProgress.objects.create(
            user=self.user,
            path_lesson=self.lesson,
            status='COMPLETED',
            final_score=85,
            time_spent_seconds=300,
            attempts_count=1
        )
        
        self.assertEqual(progress.user, self.user)
        self.assertEqual(progress.path_lesson, self.lesson)
        self.assertEqual(progress.status, 'COMPLETED')
        self.assertEqual(progress.final_score, 85)


class LearningPathAPITests(APITestCase):
    """Tests para APIs de Learning Paths"""
    
    def setUp(self):
        """Configuración inicial para tests de API"""
        self.client = APIClient()
        
        # Crear usuarios de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            level=5
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        # Crear datos de prueba
        self.category = ContentCategory.objects.create(
            name='Matemáticas',
            slug='matematicas',
            is_active=True
        )
        
        self.learning_path = LearningPath.objects.create(
            name='Álgebra Básica',
            slug='algebra-basica',
            description='Path de álgebra básica',
            difficulty_level=2,
            path_type='SEQUENTIAL',
            status='ACTIVE',
            category=self.category,
            estimated_duration_hours=10,
            minimum_level=1,
            total_xp_available=500,
            is_featured=True
        )
        
        self.unit = LearningPathUnit.objects.create(
            learning_path=self.learning_path,
            title='Ecuaciones',
            order_index=1,
            xp_reward=100
        )
        
        # URLs para tests
        self.paths_url = reverse('learningpath-list')
        self.path_detail_url = reverse('learningpath-detail', kwargs={'slug': self.learning_path.slug})
    
    def test_learning_paths_list_authenticated(self):
        """Test listado de paths para usuario autenticado"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.paths_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Álgebra Básica')
    
    def test_learning_paths_list_unauthenticated(self):
        """Test listado de paths sin autenticación"""
        response = self.client.get(self.paths_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_learning_path_detail(self):
        """Test detalle de path específico"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.path_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Álgebra Básica')
        self.assertEqual(response.data['slug'], 'algebra-basica')
        self.assertIn('units', response.data)
        self.assertIn('user_can_enroll', response.data)
    
    def test_learning_path_filtering(self):
        """Test filtros de learning paths"""
        self.client.force_authenticate(user=self.user)
        
        # Test filtro por dificultad
        response = self.client.get(self.paths_url, {'difficulty': '2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtro por featured
        response = self.client.get(self.paths_url, {'is_featured': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtro que no debe encontrar resultados
        response = self.client.get(self.paths_url, {'difficulty': '5'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_learning_path_search(self):
        """Test búsqueda de learning paths"""
        self.client.force_authenticate(user=self.user)
        
        # Búsqueda por nombre
        response = self.client.get(self.paths_url, {'search': 'álgebra'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Búsqueda que no encuentra resultados
        response = self.client.get(self.paths_url, {'search': 'física'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_daily_challenge_endpoint(self):
        """Test endpoint de reto diario"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('learningpath-daily-challenge')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('challenge', response.data)
        self.assertIn('message', response.data)
        
        # Verificar estructura del challenge
        challenge = response.data['challenge']
        self.assertIn('type', challenge)
        self.assertIn('title', challenge)
        self.assertIn('description', challenge)
        self.assertIn('requirements', challenge)
        self.assertIn('rewards', challenge)
    
    def test_ai_recommendations_endpoint(self):
        """Test endpoint de recomendaciones IA"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('learningpath-recommended')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)
        self.assertIn('algorithm_version', response.data)
    
    def test_start_battle_endpoint_unenrolled(self):
        """Test iniciar batalla sin estar inscrito"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('learningpath-start-battle', kwargs={'slug': self.learning_path.slug})
        response = self.client.post(url)
        
        # Debe fallar porque el usuario no está inscrito
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_start_battle_endpoint_enrolled_insufficient_progress(self):
        """Test iniciar batalla con progreso insuficiente"""
        self.client.force_authenticate(user=self.user)
        
        # Inscribir usuario
        enrollment = UserPathEnrollment.objects.create(
            user=self.user,
            learning_path=self.learning_path,
            status='ACTIVE',
            overall_progress_percentage=50  # Insuficiente para batalla (necesita 70%)
        )
        
        url = reverse('learningpath-start-battle', kwargs={'slug': self.learning_path.slug})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_claim_rewards_no_rewards(self):
        """Test reclamar recompensas cuando no hay disponibles"""
        self.client.force_authenticate(user=self.user)
        
        # Inscribir usuario sin recompensas
        enrollment = UserPathEnrollment.objects.create(
            user=self.user,
            learning_path=self.learning_path,
            status='ACTIVE',
            unclaimed_rewards=0
        )
        
        url = reverse('learningpath-claim-rewards', kwargs={'slug': self.learning_path.slug})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class UserPathEnrollmentAPITests(APITestCase):
    """Tests para APIs de inscripciones de usuarios"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = ContentCategory.objects.create(
            name='Test Category',
            slug='test-category',
            is_active=True
        )
        
        self.learning_path = LearningPath.objects.create(
            name='Test Path',
            slug='test-path',
            path_type='SIMULACRO',
            status='ACTIVE',
            category=self.category,
            estimated_duration_hours=5
        )
        
        self.enrollment = UserPathEnrollment.objects.create(
            user=self.user,
            learning_path=self.learning_path,
            status='ACTIVE',
            overall_progress_percentage=75
        )
    
    def test_generate_questions_endpoint(self):
        """Test generación de preguntas para simulacro"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('userpathenfollment-generate-questions', kwargs={'uuid': self.enrollment.uuid})
        
        data = {
            'num_questions': 20,
            'difficulty_distribution': {
                'easy': 40,
                'medium': 40,
                'hard': 20
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('simulacro_config', response.data)
        self.assertIn('message', response.data)
        
        config = response.data['simulacro_config']
        self.assertIn('questions', config)
        self.assertIn('total_questions', config)
        self.assertIn('estimated_duration_minutes', config)
    
    def test_detailed_report_incomplete_simulacro(self):
        """Test reporte detallado de simulacro incompleto"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('userpathenfollment-detailed-report', kwargs={'uuid': self.enrollment.uuid})
        response = self.client.get(url)
        
        # Debe fallar porque el simulacro no está completado
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_compare_results_incomplete_simulacro(self):
        """Test comparación de resultados con simulacro incompleto"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('userpathenfollment-compare-results', kwargs={'uuid': self.enrollment.uuid})
        response = self.client.get(url)
        
        # Debe fallar porque el simulacro no está completado
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class CacheTests(TestCase):
    """Tests para funcionalidad de caché"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        cache.clear()  # Limpiar caché antes de cada test
    
    def test_cache_user_progress(self):
        """Test caché de progreso del usuario"""
        from .cache import LearningCacheManager
        
        # Test set y get
        progress_data = {
            'overall_progress': 75,
            'units': {
                '1': {'completed': True, 'score': 85}
            }
        }
        
        LearningCacheManager.set_user_progress(self.user.id, 1, progress_data)
        cached_data = LearningCacheManager.get_user_progress(self.user.id, 1)
        
        self.assertEqual(cached_data, progress_data)
    
    def test_cache_daily_challenge(self):
        """Test caché de reto diario"""
        from .cache import LearningCacheManager
        
        challenge_data = {
            'type': 'speed_run',
            'title': 'Test Challenge',
            'rewards': {'xp': 100}
        }
        
        LearningCacheManager.set_daily_challenge(challenge_data)
        cached_challenge = LearningCacheManager.get_daily_challenge()
        
        self.assertEqual(cached_challenge, challenge_data)
    
    def test_cache_ai_recommendations(self):
        """Test caché de recomendaciones IA"""
        from .cache import LearningCacheManager
        
        recommendations = [
            {'path_id': 1, 'score': 85, 'reason': 'Good fit'},
            {'path_id': 2, 'score': 70, 'reason': 'Alternative'}
        ]
        
        LearningCacheManager.set_ai_recommendations(self.user.id, recommendations)
        cached_recs = LearningCacheManager.get_ai_recommendations(self.user.id)
        
        self.assertEqual(cached_recs, recommendations)


class PermissionTests(APITestCase):
    """Tests para permisos personalizados"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        self.category = ContentCategory.objects.create(
            name='Test Category',
            slug='test-category',
            is_active=True
        )
        
        self.learning_path = LearningPath.objects.create(
            name='Test Path',
            slug='test-path',
            status='ACTIVE',
            category=self.category
        )
        
        self.enrollment_user1 = UserPathEnrollment.objects.create(
            user=self.user1,
            learning_path=self.learning_path
        )
    
    def test_owner_can_access_own_enrollment(self):
        """Test que el propietario puede acceder a su inscripción"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('userpathenfollment-detail', kwargs={'uuid': self.enrollment_user1.uuid})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_non_owner_cannot_access_enrollment(self):
        """Test que otros usuarios no pueden acceder a inscripciones ajenas"""
        self.client.force_authenticate(user=self.user2)
        
        url = reverse('userpathenfollment-detail', kwargs={'uuid': self.enrollment_user1.uuid})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ThrottleTests(APITestCase):
    """Tests básicos para throttling"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        cache.clear()  # Limpiar caché de throttling
    
    def test_daily_challenge_throttle(self):
        """Test que el throttle de reto diario funciona"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('learningpath-daily-challenge')
        
        # Primera request debe funcionar
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Segunda request inmediata debe fallar por throttling
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class FilterTests(APITestCase):
    """Tests para filtros avanzados"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            level=5
        )
        
        self.category = ContentCategory.objects.create(
            name='Mathematics',
            slug='mathematics',
            is_active=True
        )
        
        # Crear múltiples paths para testing
        self.path_easy = LearningPath.objects.create(
            name='Easy Math',
            slug='easy-math',
            difficulty_level=1,
            status='ACTIVE',
            category=self.category,
            minimum_level=1,
            is_featured=True
        )
        
        self.path_hard = LearningPath.objects.create(
            name='Advanced Math',
            slug='advanced-math',
            difficulty_level=4,
            status='ACTIVE',
            category=self.category,
            minimum_level=8,
            is_featured=False
        )
    
    def test_difficulty_filter(self):
        """Test filtro por dificultad"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('learningpath-list')
        
        # Filtrar solo fáciles
        response = self.client.get(url, {'difficulty': '1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Easy Math')
        
        # Filtrar solo difíciles
        response = self.client.get(url, {'difficulty': '4'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Advanced Math')
    
    def test_user_can_enroll_filter(self):
        """Test filtro de paths disponibles para inscripción"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('learningpath-list')
        response = self.client.get(url, {'user_can_enroll': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe mostrar el path fácil (el usuario es nivel 5, el difícil requiere nivel 8)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Easy Math')
    
    def test_featured_filter(self):
        """Test filtro de paths destacados"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('learningpath-list')
        response = self.client.get(url, {'is_featured': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Easy Math') 