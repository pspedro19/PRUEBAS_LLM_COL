export interface LearningPath {
  id: string
  name: string
  description: string
  progress: number
  estimatedHours: number
  units: Unit[]
  targetAreas: string[]
  weeklyGoal: number
  pathType: 'ICFES_PREP' | 'SUBJECT_MASTERY' | 'SKILL_DEVELOPMENT' | 'CUSTOM'
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT' | 'ADAPTIVE'
}

export interface Unit {
  id: string
  position: number
  title: string
  type: 'foundation' | 'core' | 'practice' | 'advanced' | 'assessment'
  progress: number
  lessons: Lesson[]
  locked: boolean
  xpReward: number
  estimatedDuration: number
  description?: string
}

export interface Lesson {
  id: string
  title: string
  type: 'INTRO' | 'CONCEPT' | 'PRACTICE' | 'QUIZ' | 'STORY' | 'CHALLENGE'
  duration: number
  completed: boolean
  score?: number
  xpReward: number
  passingScore: number
  maxAttempts: number
  contentTypes: ContentType[]
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