"""
Sample questions for ICFES areas - FOCUSED ON MATHEMATICS
"""

# No need to import enums anymore, using string values directly
# from app.models.question import ICFESArea, DifficultyLevel

SAMPLE_QUESTIONS = [
    # MATEMÁTICAS - PRINCIPIANTE (5 preguntas)
    {
        "title": "Operaciones básicas",
        "content": "Si Juan tiene 15 manzanas y le da 7 a su hermana, ¿cuántas manzanas le quedan?",
        "option_a": "8 manzanas",
        "option_b": "7 manzanas", 
        "option_c": "22 manzanas",
        "option_d": "9 manzanas",
        "correct_answer": "A",
        "explanation": "15 - 7 = 8. Juan le queda 8 manzanas después de dar 7 a su hermana.",
        "area": "matematicas",
        "topic": "Aritmética",
        "subtopic": "Resta",
        "difficulty": "principiante",
        "points_value": 10
    },
    {
        "title": "Fracciones básicas",
        "content": "¿Cuál es el resultado de 1/2 + 1/4?",
        "option_a": "2/6",
        "option_b": "3/4",
        "option_c": "1/6",
        "option_d": "2/4",
        "correct_answer": "B",
        "explanation": "Para sumar fracciones: 1/2 + 1/4 = 2/4 + 1/4 = 3/4",
        "area": "matematicas",
        "topic": "Fracciones",
        "subtopic": "Suma de fracciones",
        "difficulty": "principiante",
        "points_value": 15
    },
    {
        "title": "Multiplicación básica",
        "content": "¿Cuál es el resultado de 8 × 7?",
        "option_a": "54",
        "option_b": "56",
        "option_c": "48",
        "option_d": "64",
        "correct_answer": "B",
        "explanation": "8 × 7 = 56. Es la tabla de multiplicar del 8 o del 7.",
        "area": "matematicas",
        "topic": "Aritmética",
        "subtopic": "Multiplicación",
        "difficulty": "principiante",
        "points_value": 10
    },
    {
        "title": "Porcentajes simples",
        "content": "¿Cuál es el 50% de 80?",
        "option_a": "30",
        "option_b": "40",
        "option_c": "50",
        "option_d": "60",
        "correct_answer": "B",
        "explanation": "50% significa la mitad. 80 ÷ 2 = 40",
        "area": "matematicas",
        "topic": "Porcentajes",
        "subtopic": "Cálculo básico",
        "difficulty": "principiante",
        "points_value": 12
    },
    {
        "title": "Números pares e impares",
        "content": "¿Cuál de los siguientes números es par?",
        "option_a": "27",
        "option_b": "35",
        "option_c": "42",
        "option_d": "51",
        "correct_answer": "C",
        "explanation": "Un número par es divisible entre 2. 42 ÷ 2 = 21, por lo tanto 42 es par.",
        "area": "matematicas",
        "topic": "Números",
        "subtopic": "Paridad",
        "difficulty": "principiante",
        "points_value": 8
    },

    # MATEMÁTICAS - INTERMEDIO (5 preguntas)
    {
        "title": "Ecuaciones lineales",
        "content": "Resuelve la ecuación: 3x + 5 = 14",
        "option_a": "x = 3",
        "option_b": "x = 4",
        "option_c": "x = 2",
        "option_d": "x = 5",
        "correct_answer": "A",
        "explanation": "3x + 5 = 14 → 3x = 14 - 5 → 3x = 9 → x = 3",
        "area": "matematicas",
        "topic": "Álgebra",
        "subtopic": "Ecuaciones lineales",
        "difficulty": "intermedio",
        "points_value": 20
    },
    {
        "title": "Área de figuras",
        "content": "¿Cuál es el área de un rectángulo con base 6 cm y altura 4 cm?",
        "option_a": "10 cm²",
        "option_b": "20 cm²",
        "option_c": "24 cm²",
        "option_d": "30 cm²",
        "correct_answer": "C",
        "explanation": "El área de un rectángulo es base × altura = 6 × 4 = 24 cm²",
        "area": "matematicas",
        "topic": "Geometría",
        "subtopic": "Área de rectángulos",
        "difficulty": "intermedio",
        "points_value": 18
    },
    {
        "title": "Proporciones",
        "content": "Si 3 lápices cuestan $900, ¿cuánto cuestan 5 lápices?",
        "option_a": "$1200",
        "option_b": "$1500",
        "option_c": "$1800",
        "option_d": "$2100",
        "correct_answer": "B",
        "explanation": "Cada lápiz cuesta $900 ÷ 3 = $300. Entonces 5 lápices cuestan 5 × $300 = $1500",
        "area": "matematicas",
        "topic": "Proporciones",
        "subtopic": "Regla de tres",
        "difficulty": "intermedio",
        "points_value": 16
    },
    {
        "title": "Exponentes",
        "content": "¿Cuál es el valor de 2⁴?",
        "option_a": "8",
        "option_b": "12",
        "option_c": "16",
        "option_d": "32",
        "correct_answer": "C",
        "explanation": "2⁴ = 2 × 2 × 2 × 2 = 16",
        "area": "matematicas",
        "topic": "Exponentes",
        "subtopic": "Potencias básicas",
        "difficulty": "intermedio",
        "points_value": 15
    },
    {
        "title": "Sistemas de ecuaciones",
        "content": "Si x + y = 10 y x - y = 2, ¿cuál es el valor de x?",
        "option_a": "4",
        "option_b": "5",
        "option_c": "6",
        "option_d": "8",
        "correct_answer": "C",
        "explanation": "Sumando las ecuaciones: (x + y) + (x - y) = 10 + 2 → 2x = 12 → x = 6",
        "area": "matematicas",
        "topic": "Álgebra",
        "subtopic": "Sistemas de ecuaciones",
        "difficulty": "intermedio",
        "points_value": 22
    },

    # MATEMÁTICAS - AVANZADO (5 preguntas)
    {
        "title": "Funciones cuadráticas",
        "content": "¿Cuál es el vértice de la parábola y = x² - 4x + 3?",
        "option_a": "(2, -1)",
        "option_b": "(4, 3)",
        "option_c": "(-2, 15)",
        "option_d": "(1, 0)",
        "correct_answer": "A",
        "explanation": "Para y = ax² + bx + c, el vértice está en x = -b/2a = -(-4)/2(1) = 2. y(2) = 4 - 8 + 3 = -1",
        "area": "matematicas",
        "topic": "Funciones",
        "subtopic": "Funciones cuadráticas",
        "difficulty": "avanzado",
        "points_value": 30
    },
    {
        "title": "Trigonometría básica",
        "content": "En un triángulo rectángulo, si el ángulo A = 30° y la hipotenusa = 10, ¿cuál es el cateto opuesto?",
        "option_a": "5",
        "option_b": "5√3",
        "option_c": "10",
        "option_d": "8.66",
        "correct_answer": "A",
        "explanation": "sen(30°) = cateto opuesto / hipotenusa = cateto opuesto / 10. Como sen(30°) = 1/2, entonces cateto opuesto = 5",
        "area": "matematicas",
        "topic": "Trigonometría",
        "subtopic": "Razones trigonométricas",
        "difficulty": "avanzado",
        "points_value": 35
    },
    {
        "title": "Logaritmos",
        "content": "¿Cuál es el valor de log₂(8)?",
        "option_a": "2",
        "option_b": "3",
        "option_c": "4",
        "option_d": "16",
        "correct_answer": "B",
        "explanation": "log₂(8) pregunta: ¿2 elevado a qué potencia da 8? 2³ = 8, entonces log₂(8) = 3",
        "area": "matematicas",
        "topic": "Logaritmos",
        "subtopic": "Logaritmos básicos",
        "difficulty": "avanzado",
        "points_value": 25
    },
    {
        "title": "Derivadas básicas",
        "content": "¿Cuál es la derivada de f(x) = 3x² + 2x?",
        "option_a": "6x + 2",
        "option_b": "3x + 2",
        "option_c": "6x",
        "option_d": "x² + x",
        "correct_answer": "A",
        "explanation": "Aplicando las reglas: d/dx(3x²) = 6x y d/dx(2x) = 2, entonces f'(x) = 6x + 2",
        "area": "matematicas",
        "topic": "Cálculo",
        "subtopic": "Derivadas",
        "difficulty": "avanzado",
        "points_value": 30
    },
    {
        "title": "Matrices básicas",
        "content": "Si A = [2 1; 0 3] y B = [1 2; 1 0], ¿cuál es A + B?",
        "option_a": "[3 3; 1 3]",
        "option_b": "[2 2; 0 0]",
        "option_c": "[1 1; 1 1]",
        "option_d": "[3 1; 1 0]",
        "correct_answer": "A",
        "explanation": "Suma elemento por elemento: [2+1 1+2; 0+1 3+0] = [3 3; 1 3]",
        "area": "matematicas",
        "topic": "Álgebra lineal",
        "subtopic": "Operaciones con matrices",
        "difficulty": "avanzado",
        "points_value": 25
    },

    # Mantener algunas preguntas de otras áreas para diversidad
    # LECTURA CRÍTICA - Principiante
    {
        "title": "Comprensión textual",
        "content": "Texto: 'María estudia medicina en la universidad. Cada día se levanta temprano para asistir a clases.' Según el texto, ¿qué hace María?",
        "option_a": "Trabaja en un hospital",
        "option_b": "Estudia medicina",
        "option_c": "Es profesora",
        "option_d": "Vende medicinas",
        "correct_answer": "B",
        "explanation": "El texto claramente menciona que 'María estudia medicina en la universidad'.",
        "area": "lectura_critica",
        "topic": "Comprensión lectora",
        "subtopic": "Información explícita",
        "difficulty": "principiante",
        "points_value": 10
    },

    # CIENCIAS NATURALES - Principiante
    {
        "title": "Estados de la materia",
        "content": "¿Cuáles son los tres estados principales de la materia?",
        "option_a": "Sólido, líquido, plasma",
        "option_b": "Líquido, gaseoso, plasma",
        "option_c": "Sólido, líquido, gaseoso",
        "option_d": "Sólido, plasma, condensado",
        "correct_answer": "C",
        "explanation": "Los tres estados principales de la materia son: sólido, líquido y gaseoso.",
        "area": "ciencias_naturales",
        "topic": "Física",
        "subtopic": "Estados de la materia",
        "difficulty": "principiante",
        "points_value": 12
    },

    # INGLÉS - Principiante
    {
        "title": "Vocabulary - Colors",
        "content": "What color do you get when you mix red and yellow?",
        "option_a": "Green",
        "option_b": "Purple", 
        "option_c": "Orange",
        "option_d": "Blue",
        "correct_answer": "C",
        "explanation": "When you mix red and yellow, you get orange.",
        "area": "ingles",
        "topic": "Vocabulary",
        "subtopic": "Colors",
        "difficulty": "principiante",
        "points_value": 8
    }
] 