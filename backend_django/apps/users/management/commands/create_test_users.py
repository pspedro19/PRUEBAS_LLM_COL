"""
Comando Django para crear usuarios de prueba con datos completos
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import date

from apps.users.models import User, UserProfile, School, University


class Command(BaseCommand):
    help = 'Crear usuarios de prueba con datos completos para testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Eliminar usuarios de prueba existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️ Eliminando usuarios de prueba existentes...')
            User.objects.filter(email__in=[
                'admin@icfesquest.com',
                'profesor@icfesquest.com', 
                'estudiante@icfesquest.com'
            ]).delete()

        self.stdout.write('🏫 Creando instituciones educativas...')
        school1, _ = School.objects.get_or_create(
            code='IE001',
            defaults={
                'name': 'Colegio San José',
                'city': 'Bogotá',
                'department': 'Cundinamarca',
                'school_type': 'PRIVATE'
            }
        )

        school2, _ = School.objects.get_or_create(
            code='IE002',
            defaults={
                'name': 'IED República de Colombia',
                'city': 'Medellín',
                'department': 'Antioquia',
                'school_type': 'PUBLIC'
            }
        )

        self.stdout.write('🎓 Creando universidades...')
        uni_nacional, _ = University.objects.get_or_create(
            code='UN',
            defaults={
                'name': 'Universidad Nacional de Colombia',
                'city': 'Bogotá',
                'min_icfes_score': 350
            }
        )

        uni_andes, _ = University.objects.get_or_create(
            code='UNIANDES',
            defaults={
                'name': 'Universidad de los Andes',
                'city': 'Bogotá',
                'min_icfes_score': 380
            }
        )

        uni_antioquia, _ = University.objects.get_or_create(
            code='UDEA',
            defaults={
                'name': 'Universidad de Antioquia',
                'city': 'Medellín',
                'min_icfes_score': 320
            }
        )

        with transaction.atomic():
            self.stdout.write('👨‍💼 Creando Admin - Usuario Administrador...')
            
            # 1. ADMIN - Usuario administrador con acceso completo
            admin_user, created = User.objects.get_or_create(
                email='admin@icfesquest.com',
                defaults={
                    'username': 'admin_icfes',
                    'first_name': 'Carlos',
                    'last_name': 'Administrador',
                    'identification_number': '1234567890',
                    'phone_number': '+573001234567',
                    'birth_date': date(1985, 5, 15),
                    'is_staff': True,
                    'is_superuser': True,
                    'hero_class': 'S+',
                    'level': 25,
                    'experience_points': 50000,
                    'initial_assessment_completed': True,
                    'vocational_test_completed': True,
                    'assigned_role': 'SPECIALIST',
                    'avatar_evolution_stage': 5,
                    'last_activity': timezone.now(),
                }
            )
            
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
                
                # Crear perfil avanzado
                admin_profile = UserProfile.objects.create(
                    user=admin_user,
                    total_questions_answered=1500,
                    total_correct_answers=1350,
                    total_study_minutes=12000,
                    current_streak=45,
                    max_streak=67,
                    current_vitality=100,
                    learning_style='Visual',
                    difficulty_preference='adaptive',
                    average_response_time=25.5,
                    improvement_rate=15.2
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Admin creado: {admin_user.email} / admin123'
                    )
                )

            # 2. PROFESOR - Usuario profesor/tutor
            teacher_user, created = User.objects.get_or_create(
                email='profesor@icfesquest.com',
                defaults={
                    'username': 'prof_martinez',
                    'first_name': 'María',
                    'last_name': 'Martínez',
                    'identification_number': '9876543210',
                    'phone_number': '+573019876543',
                    'birth_date': date(1990, 8, 22),
                    'school': school1,
                    'target_university': uni_andes,
                    'target_career': 'Licenciatura en Matemáticas',
                    'is_staff': True,
                    'hero_class': 'A',
                    'level': 18,
                    'experience_points': 25000,
                    'initial_assessment_completed': True,
                    'vocational_test_completed': True,
                    'assigned_role': 'SUPPORT',
                    'avatar_evolution_stage': 3,
                    'last_activity': timezone.now(),
                }
            )
            
            if created:
                teacher_user.set_password('profesor123')
                teacher_user.save()
                
                teacher_profile = UserProfile.objects.create(
                    user=teacher_user,
                    total_questions_answered=800,
                    total_correct_answers=720,
                    total_study_minutes=6000,
                    current_streak=23,
                    max_streak=35,
                    current_vitality=85,
                    learning_style='Auditivo',
                    difficulty_preference='hard',
                    average_response_time=18.3,
                    improvement_rate=12.8
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Profesor creado: {teacher_user.email} / profesor123'
                    )
                )

            # 3. ESTUDIANTE - Usuario estudiante típico
            student_user, created = User.objects.get_or_create(
                email='estudiante@icfesquest.com',
                defaults={
                    'username': 'ana_rodriguez',
                    'first_name': 'Ana',
                    'last_name': 'Rodríguez',
                    'identification_number': '1122334455',
                    'phone_number': '+573205551234',
                    'birth_date': date(2006, 3, 10),
                    'school': school2,
                    'grade': 11,
                    'target_university': uni_nacional,
                    'target_career': 'Ingeniería de Sistemas',
                    'hero_class': 'C',
                    'level': 8,
                    'experience_points': 3500,
                    'initial_assessment_completed': True,
                    'vocational_test_completed': False,
                    'assigned_role': 'DPS',
                    'avatar_evolution_stage': 2,
                    'last_activity': timezone.now(),
                }
            )
            
            if created:
                student_user.set_password('estudiante123')
                student_user.save()
                
                student_profile = UserProfile.objects.create(
                    user=student_user,
                    total_questions_answered=250,
                    total_correct_answers=175,
                    total_study_minutes=1200,
                    current_streak=7,
                    max_streak=12,
                    current_vitality=75,
                    learning_style='Kinestésico',
                    difficulty_preference='medium',
                    average_response_time=35.2,
                    improvement_rate=8.5
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Estudiante creado: {student_user.email} / estudiante123'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 ¡Usuarios de prueba creados exitosamente!\n'
            )
        )
        
        self.stdout.write('📋 RESUMEN DE USUARIOS CREADOS:')
        self.stdout.write('=' * 50)
        self.stdout.write('👨‍💼 ADMIN (Administrador):')
        self.stdout.write('   📧 Email: admin@icfesquest.com')
        self.stdout.write('   🔑 Password: admin123')
        self.stdout.write('   🎭 Rol: Super Admin (S+ Nivel 25)')
        self.stdout.write('   📊 Stats: 1500 preguntas, 90% precisión')
        self.stdout.write('')
        
        self.stdout.write('👩‍🏫 PROFESOR (Tutor):')
        self.stdout.write('   📧 Email: profesor@icfesquest.com')
        self.stdout.write('   🔑 Password: profesor123')
        self.stdout.write('   🎭 Rol: Staff (A Nivel 18)')
        self.stdout.write('   🏫 Escuela: Colegio San José')
        self.stdout.write('   📊 Stats: 800 preguntas, 90% precisión')
        self.stdout.write('')
        
        self.stdout.write('👩‍🎓 ESTUDIANTE (Grado 11):')
        self.stdout.write('   📧 Email: estudiante@icfesquest.com')
        self.stdout.write('   🔑 Password: estudiante123')
        self.stdout.write('   🎭 Rol: Estudiante (C Nivel 8)')
        self.stdout.write('   🏫 Escuela: IED República de Colombia')
        self.stdout.write('   🎯 Meta: Universidad Nacional - Sistemas')
        self.stdout.write('   📊 Stats: 250 preguntas, 70% precisión')
        self.stdout.write('')
        
        self.stdout.write('🔗 ENDPOINTS PARA PROBAR:')
        self.stdout.write('   Login: POST /api/v1/auth/login/')
        self.stdout.write('   Profile: GET /api/v1/auth/profile/')
        self.stdout.write('   Stats: GET /api/v1/auth/stats/')
        self.stdout.write('   Register: POST /api/v1/auth/register/')
        self.stdout.write('')
        
        self.stdout.write(
            self.style.WARNING(
                '⚠️  Recuerda: Estos son usuarios de PRUEBA. '
                'No uses en producción.'
            )
        ) 