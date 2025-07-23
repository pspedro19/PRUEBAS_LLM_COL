"""
Comando Django para limpiar Learning Paths duplicados o con problemas
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.learning.models import LearningPath, UserPathEnrollment
from apps.icfes.models import ICFESResult

User = get_user_model()

class Command(BaseCommand):
    help = 'Limpiar Learning Paths duplicados y resolver problemas de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username específico para limpiar',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se haría sin ejecutar',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar limpieza sin confirmación',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧹 LIMPIANDO LEARNING PATHS'))
        self.stdout.write('=' * 60)
        
        dry_run = options['dry_run']
        force = options['force']
        username = options.get('user')
        
        if username:
            try:
                user = User.objects.get(username=username)
                self.cleanup_user_paths(user, dry_run, force)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"❌ Usuario '{username}' no encontrado")
                )
        else:
            self.cleanup_all_problematic_paths(dry_run, force)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Limpieza completada'))

    def cleanup_user_paths(self, user, dry_run=False, force=False):
        """Limpiar paths de un usuario específico"""
        self.stdout.write(f"\n👤 LIMPIANDO PATHS DE: {user.username}")
        
        # Encontrar enrollments activos
        active_enrollments = UserPathEnrollment.objects.filter(
            user=user,
            status='ACTIVE'
        )
        
        self.stdout.write(f"📊 Enrollments activos encontrados: {active_enrollments.count()}")
        
        if active_enrollments.count() > 1:
            self.stdout.write("⚠️ MÚLTIPLES ENROLLMENTS ACTIVOS DETECTADOS")
            
            # Mantener solo el más reciente
            latest_enrollment = active_enrollments.order_by('-created_at').first()
            duplicate_enrollments = active_enrollments.exclude(id=latest_enrollment.id)
            
            for enrollment in duplicate_enrollments:
                self.stdout.write(f"  🗑️ Eliminando enrollment duplicado: {enrollment.learning_path.name}")
                if not dry_run:
                    enrollment.status = 'CANCELLED'
                    enrollment.save()
        
        # Encontrar learning paths huérfanos (sin enrollments activos)
        user_paths = LearningPath.objects.filter(created_by=user)
        orphan_paths = []
        
        for path in user_paths:
            active_enrollments_for_path = UserPathEnrollment.objects.filter(
                learning_path=path,
                status='ACTIVE'
            )
            if not active_enrollments_for_path.exists():
                orphan_paths.append(path)
        
        if orphan_paths:
            self.stdout.write(f"🗑️ Paths huérfanos encontrados: {len(orphan_paths)}")
            for path in orphan_paths:
                self.stdout.write(f"  - {path.name}")
                if not dry_run and (force or self.confirm_deletion()):
                    path.delete()
        
        # Verificar integridad
        self.verify_user_integrity(user)

    def cleanup_all_problematic_paths(self, dry_run=False, force=False):
        """Limpiar todos los paths problemáticos"""
        self.stdout.write("\n🔍 BUSCANDO PATHS PROBLEMÁTICOS")
        
        # Encontrar duplicados por slug
        from django.db.models import Count
        duplicate_slugs = LearningPath.objects.values('slug').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicate_slugs:
            self.stdout.write(f"⚠️ Slugs duplicados encontrados: {duplicate_slugs.count()}")
            for slug_info in duplicate_slugs:
                slug = slug_info['slug']
                paths = LearningPath.objects.filter(slug=slug)
                self.stdout.write(f"  📋 Slug '{slug}' tiene {paths.count()} paths")
                
                # Mantener solo el más reciente
                latest_path = paths.order_by('-created_at').first()
                duplicate_paths = paths.exclude(id=latest_path.id)
                
                for path in duplicate_paths:
                    self.stdout.write(f"    🗑️ Eliminando duplicado: {path.name}")
                    if not dry_run and (force or self.confirm_deletion()):
                        path.delete()

    def verify_user_integrity(self, user):
        """Verificar integridad de datos del usuario"""
        self.stdout.write(f"\n🔍 VERIFICANDO INTEGRIDAD DE {user.username}")
        
        # Verificar enrollments activos
        active_enrollments = UserPathEnrollment.objects.filter(
            user=user,
            status='ACTIVE'
        ).count()
        
        # Verificar resultados ICFES
        icfes_results = ICFESResult.objects.filter(user=user).count()
        
        self.stdout.write(f"  ✅ Enrollments activos: {active_enrollments}")
        self.stdout.write(f"  ✅ Resultados ICFES: {icfes_results}")
        
        if active_enrollments > 1:
            self.stdout.write("  ⚠️ Múltiples enrollments activos - Necesita limpieza")
        elif active_enrollments == 0 and icfes_results > 0:
            self.stdout.write("  💡 Tiene resultados ICFES pero no enrollments - OK para generar nuevo path")
        elif active_enrollments == 1:
            self.stdout.write("  ✅ Estado normal - 1 enrollment activo")

    def confirm_deletion(self):
        """Confirmar eliminación interactiva"""
        response = input("¿Eliminar? (y/N): ")
        return response.lower() in ['y', 'yes', 'sí', 's']
    
    def reset_user_completely(self, user, dry_run=False):
        """Resetear completamente un usuario (usar con cuidado)"""
        self.stdout.write(f"\n🔄 RESET COMPLETO DE {user.username}")
        
        if not dry_run:
            # Cancelar todos los enrollments
            UserPathEnrollment.objects.filter(user=user).update(status='CANCELLED')
            
            # Eliminar todos los paths creados por el usuario
            LearningPath.objects.filter(created_by=user).delete()
            
            self.stdout.write("✅ Usuario reseteado completamente") 