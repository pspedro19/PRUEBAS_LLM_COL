# MathQuest - Solo Leveling Edition 🎮📚

Una plataforma educativa inmersiva que fusiona la preparación para el ICFES con la narrativa épica de "Solo Leveling". Domina las matemáticas a través de batallas épicas, sistemas de nivelación y un árbol de talentos único.

## ✨ Características Principales

### 🎯 **Diseño Visual Mejorado**
- **Tipografía Dual**: Cinzel para títulos épicos, Inter para legibilidad
- **Paleta de Colores Optimizada**: Azul cian para marca, grises para texto, acentos dorados
- **Efectos Visuales Moderados**: Neon-glow equilibrado sin sacrificar contraste
- **Navegación Responsiva**: Sticky navbar en desktop, bottom nav en móvil

### 🏗️ **Arquitectura de Información**
- **Hero Section Mejorado**: Sub-headline claro + teaser interactivo
- **Panel de Estadísticas Avanzado**: Barras de progreso circulares con tooltips
- **Jerarquía Visual Clara**: Información organizada por importancia

### ⚔️ **Sistema de Gamificación**
- **Árbol de Talentos**: Habilidades matemáticas como nodos desbloqueables
- **Misiones Diarias**: Recompensas variables para inducir hábito
- **Sistema de Ranking**: Tablas responsivas con filtros (global, amigos, colegio)
- **Logros Sociales**: Compartir progreso en redes sociales

### 📊 **Componentes Nuevos**
- `EpicStatsPanel`: Estadísticas con barras circulares y microinteracciones
- `SkillTree`: Árbol de talentos con conexiones visuales
- `EpicRanking`: Ranking con filtros y funcionalidad social
- Páginas especializadas: `/practice`, `/dashboard`

## 🚀 Tecnologías

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python, PostgreSQL
- **Diseño**: Componentes modulares, CSS Grid, Flexbox
- **Accesibilidad**: WCAG AA, lectores de pantalla, modo alto contraste

## 🎨 Mejoras de UX Implementadas

### 1. **Legibilidad y Accesibilidad**
- Contraste mejorado (WCAG AA 4.5:1)
- Soporte para `prefers-reduced-motion`
- Etiquetas ARIA para lectores de pantalla
- Indicadores de foco visibles

### 2. **Interactividad**
- Hover states informativos
- Tooltips contextuales
- Animaciones suaves y responsivas
- Microinteracciones para feedback

### 3. **Gamificación Educativa**
- Progreso visual claro
- Recompensas inmediatas
- Sistema de rachas
- Logros desbloqueables

### 4. **Responsividad**
- Diseño mobile-first
- Navegación adaptativa
- Tablas responsivas
- Componentes flexibles

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Página principal mejorada
│   │   ├── practice/page.tsx     # Árbol de talentos y misiones
│   │   ├── dashboard/page.tsx    # Perfil y analíticas
│   │   └── globals.css           # Estilos mejorados
│   ├── components/
│   │   ├── EpicStatsPanel.tsx    # Estadísticas circulares
│   │   ├── SkillTree.tsx         # Árbol de talentos
│   │   ├── EpicRanking.tsx       # Ranking con filtros
│   │   └── EpicNavigation.tsx    # Navegación mejorada
│   └── lib/
└── tailwind.config.js            # Configuración extendida
```

## 🎯 Métricas de Éxito

- **TTST (Time to Solve First Task)**: < 30 segundos
- **NPS (Net Promoter Score)**: Objetivo > 50
- **Retención**: 7 días consecutivos
- **Accesibilidad**: WCAG AA compliance

## 🔧 Instalación

```bash
# Clonar repositorio
git clone [url-del-repositorio]

# Instalar dependencias frontend
cd frontend
npm install

# Configurar variables de entorno
cp .env.example .env.local

# Ejecutar en desarrollo
npm run dev
```

## 🎮 Uso

1. **Registro/Login**: Accede con tu cuenta
2. **Explorar Habilidades**: Visita el árbol de talentos
3. **Completar Misiones**: Gana XP y recompensas
4. **Competir**: Sube en el ranking global
5. **Compartir**: Muestra tu progreso en redes

## 🎨 Personalización

### Colores
```css
--neonSystem: #00D9FF;    /* Color principal */
--levelUp: #FFD700;       /* Acentos dorados */
--brightPurple: #9333EA;  /* Púrpura monarca */
--neonGreen: #39FF14;     /* Verde éxito */
```

### Tipografías
```css
font-epicTitle: Cinzel    /* Títulos épicos */
font-body: Inter          /* Texto legible */
font-display: Orbitron    /* Elementos UI */
```

## 📈 Roadmap

- [ ] **Sistema de Clanes**: Cooperación entre estudiantes
- [ ] **Eventos Temporales**: Competencias especiales
- [ ] **Analíticas Avanzadas**: Machine Learning para personalización
- [ ] **Modo Offline**: Sincronización con IndexedDB
- [ ] **Integración ICFES**: Contenido oficial actualizado

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Agradecimientos

- Inspiración en "Solo Leveling" de Chugong
- Comunidad educativa colombiana
- Estudiantes beta-testers
- Críticos de diseño educativo

---

**¡Conviértete en el más fuerte de las matemáticas!** ⚔️📚 