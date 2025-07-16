/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Base Oscura
        abyss: '#000000',
        carbon: '#0A0A0A',
        dungeon: '#141414',
        shadow: '#1C1C1C',
        
        // Sistema Azul
        neonSystem: '#00D9FF',
        systemMedium: '#0099CC',
        systemDark: '#006699',
        cyanAwaken: '#00FFD1',
        royalBlue: '#4169E1',
        
        // Púrpura Monarca
        shadowPurple: '#6B46C1',
        brightPurple: '#9333EA',
        deepPurple: '#4C1D95',
        neonPurple: '#A855F7',
        darkPurple: '#2E1065',
        
        // Acentos de Poder
        levelUp: '#FFD700',
        ascension: '#FFA500',
        bloodRed: '#DC143C',
        portalRed: '#FF0000',
        neonGreen: '#39FF14',
        
        // Rareza de Items
        common: '#FFFFFF',
        uncommon: '#00FF00',
        rare: '#0080FF',
        epic: '#AA00FF',
        legendary: '#FF8800',
        mythical: '#FF0044',
        divine: '#FF00FF',
      },
      fontFamily: {
        epicTitle: ['Cinzel', 'UnifrakturMaguntia', 'serif'],
        epicUI: ['Orbitron', 'Rajdhani', 'sans-serif'],
        epicStats: ['Fira Code', 'JetBrains Mono', 'monospace'],
        epicNarration: ['Crimson Text', 'Playfair Display', 'serif'],
        body: ['Inter', 'Poppins', 'sans-serif'],
        display: ['Orbitron', 'Rajdhani', 'sans-serif'],
      },
      backgroundImage: {
        'epic-tower': "url('/assets/bg-tower.jpg')",
        'epic-dungeon': "url('/assets/bg-dungeon.jpg')",
        'epic-portal': "url('/assets/bg-portal.jpg')",
        'epic-ruins': "url('/assets/bg-ruins.jpg')",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} 