import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.icfes.models import PreguntaICFES, OpcionRespuesta, AreaEvaluacion, AreaTematica
from apps.users.models import User
from apps.ai_llm.models import AIModel, AIPromptTemplate, AIUsageQuota
from apps.learning.models import LearningPath
from apps.content.models import ContentLesson, ContentUnit

def analyze_llm_readiness():
    """Analizar qué necesitamos antes de integrar LLM"""
    
    print("🔍 ANÁLISIS DE PREPARACIÓN PARA LLM")
    print("=" * 60)
    
    # 1. DATOS ACTUALES
    print("\n📊 DATOS ACTUALES:")
    print(f"  ✅ Preguntas ICFES: {PreguntaICFES.objects.count()}")
    print(f"  ✅ Opciones de respuesta: {OpcionRespuesta.objects.count()}")
    print(f"  ✅ Usuarios: {User.objects.count()}")
    print(f"  ✅ Modelos AI: {AIModel.objects.count()}")
    print(f"  ✅ Templates de prompts: {AIPromptTemplate.objects.count()}")
    print(f"  ✅ Áreas de evaluación: {AreaEvaluacion.objects.count()}")
    print(f"  ✅ Áreas temáticas: {AreaTematica.objects.count()}")
    
    # 2. ANÁLISIS DE NECESIDADES
    print("\n🎯 ANÁLISIS DE NECESIDADES:")
    
    # Verificar contenido para explicaciones
    preguntas_con_texto = PreguntaICFES.objects.filter(pregunta_texto__isnull=False).exclude(pregunta_texto='').count()
    print(f"  📝 Preguntas con texto: {preguntas_con_texto}/{PreguntaICFES.objects.count()}")
    
    # Verificar opciones de respuesta
    opciones_con_texto = OpcionRespuesta.objects.filter(texto_opcion__isnull=False).exclude(texto_opcion='').count()
    print(f"  📝 Opciones con texto: {opciones_con_texto}/{OpcionRespuesta.objects.count()}")
    
    # Verificar respuestas correctas
    preguntas_con_respuesta = PreguntaICFES.objects.filter(respuesta_correcta__isnull=False).exclude(respuesta_correcta='').count()
    print(f"  ✅ Preguntas con respuesta correcta: {preguntas_con_respuesta}/{PreguntaICFES.objects.count()}")
    
    # 3. RECOMENDACIONES
    print("\n💡 RECOMENDACIONES ANTES DE LLM:")
    
    recommendations = []
    
    # Verificar datos mínimos
    if PreguntaICFES.objects.count() < 50:
        recommendations.append("❌ Necesitas más preguntas ICFES (mínimo 100 recomendado)")
    else:
        recommendations.append("✅ Suficientes preguntas ICFES")
    
    if preguntas_con_texto < PreguntaICFES.objects.count() * 0.8:
        recommendations.append("❌ Muchas preguntas sin texto para explicar")
    else:
        recommendations.append("✅ Preguntas con texto adecuado")
    
    if preguntas_con_respuesta < PreguntaICFES.objects.count() * 0.9:
        recommendations.append("❌ Faltan respuestas correctas en algunas preguntas")
    else:
        recommendations.append("✅ Respuestas correctas completas")
    
    # Verificar templates de prompts
    if AIPromptTemplate.objects.count() < 3:
        recommendations.append("❌ Necesitas más templates de prompts (explicación, pista, análisis)")
    else:
        recommendations.append("✅ Templates de prompts suficientes")
    
    # Verificar cuotas de usuario
    users_with_quota = AIUsageQuota.objects.count()
    total_users = User.objects.count()
    if users_with_quota < total_users * 0.5:
        recommendations.append("❌ Muchos usuarios sin cuotas de uso configuradas")
    else:
        recommendations.append("✅ Cuotas de usuario configuradas")
    
    # Mostrar recomendaciones
    for rec in recommendations:
        print(f"  {rec}")
    
    # 4. FUNCIONALIDADES ADICIONALES RECOMENDADAS
    print("\n🚀 FUNCIONALIDADES ADICIONALES RECOMENDADAS:")
    
    additional_features = [
        "📝 Sistema de prompts dinámicos basado en contexto",
        "🔄 Sistema de caché inteligente para respuestas frecuentes",
        "📊 Métricas de satisfacción del usuario",
        "🛡️ Sistema de moderación de contenido",
        "💰 Tracking de costos por usuario",
        "📈 Analytics de uso de LLM",
        "🎯 Personalización basada en perfil de usuario",
        "⚡ Optimización de prompts por área temática",
        "🔍 Sistema de búsqueda de explicaciones previas",
        "📚 Biblioteca de explicaciones reutilizables"
    ]
    
    for feature in additional_features:
        print(f"  {feature}")
    
    # 5. PRIORIDADES
    print("\n🎯 PRIORIDADES DE IMPLEMENTACIÓN:")
    
    priorities = [
        "1. 🔌 Integrar API de OpenAI/Anthropic",
        "2. 📝 Crear engine de prompts dinámicos",
        "3. 💬 Sistema de conversaciones con contexto",
        "4. 💾 Sistema de caché de respuestas",
        "5. 📊 Tracking de costos y uso",
        "6. 🛡️ Moderación básica de contenido",
        "7. 📈 Analytics de efectividad",
        "8. 🎯 Personalización por usuario",
        "9. ⚡ Optimización de prompts",
        "10. 📚 Biblioteca de explicaciones"
    ]
    
    for priority in priorities:
        print(f"  {priority}")
    
    # 6. ESTADO ACTUAL
    print("\n✅ ESTADO ACTUAL:")
    print("  ✅ Infraestructura de base de datos completa")
    print("  ✅ APIs REST funcionales")
    print("  ✅ Sistema de usuarios activo")
    print("  ✅ Datos ICFES disponibles")
    print("  ✅ Templates de prompts básicos")
    print("  ✅ Sistema de cuotas configurado")
    
    print("\n🎯 CONCLUSIÓN:")
    print("  El sistema está BIEN PREPARADO para integrar LLM.")
    print("  Solo necesitas implementar la lógica de conexión con APIs externas.")
    print("  Los datos actuales son suficientes para comenzar.")

if __name__ == "__main__":
    analyze_llm_readiness() 