# 📁 Estructura MVP - ICFES Math Tutor

```
icfes-math-mvp/
├── docker-compose.yml
├── .env
├── README.md
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── app/
│       │   ├── page.tsx         # Landing/Register
│       │   ├── session/page.tsx # Study session
│       │   ├── dashboard/page.tsx # Metrics
│       │   └── layout.tsx
│       ├── components/
│       │   ├── QuestionCard.tsx
│       │   ├── StreakDisplay.tsx
│       │   ├── XPBar.tsx
│       │   └── MetricsChart.tsx
│       └── lib/
│           └── api.ts
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── app/
│       ├── models.py
│       ├── schemas.py
│       ├── database.py
│       ├── crud.py
│       └── llm_service.py
│
└── database/
    └── init.sql  # DB schema + sample data
```