export interface LearningPath {
  id: number // Backend devuelve number, no string
  name: string
  description: string
  difficulty_level: string // Backend usa difficulty_level
  estimated_duration_hours: number // Backend usa estimated_duration_hours
  total_units: number // Backend incluye total_units
  units: Unit[]
  progress?: {
    completed_units: number
    total_units: number
    completion_percentage: number
    current_week: number
    estimated_weeks: number
  }
  personalization?: {
    template_name: string
    color_theme: string
    focus_areas: string[]
  }
  // Propiedades opcionales para compatibilidad hacia atrás
  estimatedHours?: number
  targetAreas?: string[]
  weeklyGoal?: number
  pathType?: 'ICFES_PREP' | 'SUBJECT_MASTERY' | 'SKILL_DEVELOPMENT' | 'CUSTOM'
  difficulty?: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT' | 'ADAPTIVE'
}

export interface Unit {
  id: number // Backend devuelve number
  order?: number // Backend usa order, no position
  title: string
  description: string
  icon?: string // Backend incluye icon
  unit_type?: 'FOUNDATION' | 'CORE' | 'PRACTICE' | 'ASSESSMENT' // Backend usa estos valores
  xp_reward?: number // Backend usa xp_reward
  difficulty_modifier?: number // Backend incluye difficulty_modifier
  estimated_duration_minutes?: number // Backend usa estimated_duration_minutes
  lessons: Lesson[]
  metadata?: {
    color_theme?: string
    focus_topics?: string[]
    template_name?: string
    learning_style?: string
    difficulty_level?: string
    weak_areas_focus?: string[]
    practice_intensity?: string
    target_score_range?: number[]
    estimated_duration_original?: number
  }
  // Propiedades opcionales para compatibilidad hacia atrás
  position?: number
  type?: 'foundation' | 'core' | 'practice' | 'advanced' | 'assessment'
  progress?: number
  locked?: boolean
  xpReward?: number
  estimatedDuration?: number
}

export interface Lesson {
  id: number // Backend devuelve number
  title: string
  type: 'INTRO' | 'CONCEPT' | 'PRACTICE' | 'QUIZ' | 'STORY' | 'CHALLENGE'
  completed: boolean // Backend incluye completed
  duration_minutes?: number // Backend puede incluir duration_minutes
  order?: number // Backend incluye order
  
  // Propiedades opcionales para compatibilidad
  duration?: number
  score?: number
  xpReward?: number
  passingScore?: number
  maxAttempts?: number
  contentTypes?: ContentType[]
}

export type ContentType = 'video' | 'interactive' | 'practice' | 'reading' | 'quiz'

export interface UserMetrics {
  totalStudyTime: number
  currentStreak: number
  maxStreak: number
  averageAccuracy: number
  weeklyProgress: WeeklyProgress
  areaPerformance: AreaPerformance
  predictedScore: number
  improvementRate: number
}

export interface WeeklyProgress {
  targetMinutes: number
  completedMinutes: number
  daysActive: number
  lessonsCompleted: number
}

export interface AreaPerformance {
  mathematics: SubjectMetrics
  reading: SubjectMetrics
  naturalSciences: SubjectMetrics
  socialStudies: SubjectMetrics
  english: SubjectMetrics
}

export interface SubjectMetrics {
  score: number
  accuracy: number
  totalQuestions: number
  correctAnswers: number
  averageTime: number
  weakTopics: string[]
}

export interface ContentRecommendation {
  id: string
  type: ContentType
  provider: string
  title: string
  url: string
  duration?: number
  difficulty: string
  relevanceScore: number
}

export interface StudySession {
  id: string
  startTime: Date
  endTime?: Date
  unitId: string
  lessonId: string
  xpEarned: number
  questionsAnswered: number
  accuracy: number
} 