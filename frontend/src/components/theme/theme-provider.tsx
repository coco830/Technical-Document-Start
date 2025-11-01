"use client"

import React from "react"

export interface CustomTheme {
  name: string
  colors: {
    background: string
    foreground: string
    primary: string
    primaryForeground: string
    secondary: string
    secondaryForeground: string
    muted: string
    mutedForeground: string
    accent: string
    accentForeground: string
    destructive: string
    destructiveForeground: string
    border: string
    input: string
    ring: string
    card: string
    cardForeground: string
    popover: string
    popoverForeground: string
  }
  borderRadius: string
  fontFamily: string
}

const defaultThemes: Record<string, CustomTheme> = {
  light: {
    name: "浅色",
    colors: {
      background: "0 0% 100%",
      foreground: "222.2 84% 4.9%",
      primary: "221.2 83.2% 53.3%",
      primaryForeground: "210 40% 98%",
      secondary: "210 40% 96%",
      secondaryForeground: "222.2 84% 4.9%",
      muted: "210 40% 96%",
      mutedForeground: "215.4 16.3% 46.9%",
      accent: "210 40% 96%",
      accentForeground: "222.2 84% 4.9%",
      destructive: "0 84.2% 60.2%",
      destructiveForeground: "210 40% 98%",
      border: "214.3 31.8% 91.4%",
      input: "214.3 31.8% 91.4%",
      ring: "221.2 83.2% 53.3%",
      card: "0 0% 100%",
      cardForeground: "222.2 84% 4.9%",
      popover: "0 0% 100%",
      popoverForeground: "222.2 84% 4.9%",
    },
    borderRadius: "0.5rem",
    fontFamily: "Inter, system-ui, sans-serif",
  },
  dark: {
    name: "深色",
    colors: {
      background: "222.2 84% 4.9%",
      foreground: "210 40% 98%",
      primary: "217.2 91.2% 59.8%",
      primaryForeground: "222.2 84% 4.9%",
      secondary: "217.2 32.6% 17.5%",
      secondaryForeground: "210 40% 98%",
      muted: "217.2 32.6% 17.5%",
      mutedForeground: "215 20.2% 65.1%",
      accent: "217.2 32.6% 17.5%",
      accentForeground: "210 40% 98%",
      destructive: "0 62.8% 30.6%",
      destructiveForeground: "210 40% 98%",
      border: "217.2 32.6% 17.5%",
      input: "217.2 32.6% 17.5%",
      ring: "224.3 76.3% 94.1%",
      card: "222.2 84% 4.9%",
      cardForeground: "210 40% 98%",
      popover: "222.2 84% 4.9%",
      popoverForeground: "210 40% 98%",
    },
    borderRadius: "0.5rem",
    fontFamily: "Inter, system-ui, sans-serif",
  },
  blue: {
    name: "蓝色",
    colors: {
      background: "0 0% 100%",
      foreground: "222.2 84% 4.9%",
      primary: "210 100% 50%",
      primaryForeground: "0 0% 98%",
      secondary: "210 40% 96%",
      secondaryForeground: "222.2 84% 4.9%",
      muted: "210 40% 96%",
      mutedForeground: "215.4 16.3% 46.9%",
      accent: "210 40% 96%",
      accentForeground: "222.2 84% 4.9%",
      destructive: "0 84.2% 60.2%",
      destructiveForeground: "210 40% 98%",
      border: "214.3 31.8% 91.4%",
      input: "214.3 31.8% 91.4%",
      ring: "210 100% 50%",
      card: "0 0% 100%",
      cardForeground: "222.2 84% 4.9%",
      popover: "0 0% 100%",
      popoverForeground: "222.2 84% 4.9%",
    },
    borderRadius: "0.5rem",
    fontFamily: "Inter, system-ui, sans-serif",
  },
  green: {
    name: "绿色",
    colors: {
      background: "0 0% 100%",
      foreground: "222.2 84% 4.9%",
      primary: "142 76% 36%",
      primaryForeground: "0 0% 98%",
      secondary: "210 40% 96%",
      secondaryForeground: "222.2 84% 4.9%",
      muted: "210 40% 96%",
      mutedForeground: "215.4 16.3% 46.9%",
      accent: "210 40% 96%",
      accentForeground: "222.2 84% 4.9%",
      destructive: "0 84.2% 60.2%",
      destructiveForeground: "210 40% 98%",
      border: "214.3 31.8% 91.4%",
      input: "214.3 31.8% 91.4%",
      ring: "142 76% 36%",
      card: "0 0% 100%",
      cardForeground: "222.2 84% 4.9%",
      popover: "0 0% 100%",
      popoverForeground: "222.2 84% 4.9%",
    },
    borderRadius: "0.5rem",
    fontFamily: "Inter, system-ui, sans-serif",
  },
}

interface ThemeContextType {
  theme: string | undefined
  setTheme: (theme: string) => void
  systemTheme: string | undefined
  themes: Record<string, CustomTheme>
  currentTheme: CustomTheme | undefined
  addCustomTheme: (theme: CustomTheme) => void
  removeCustomTheme: (name: string) => void
}

const ThemeContext = React.createContext<ThemeContextType | undefined>(undefined)

export const useTheme = () => {
  const context = React.useContext(ThemeContext)
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider")
  }
  return context
}

export interface CustomThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: string
  storageKey?: string
  enableSystem?: boolean
  attribute?: string
  themes?: Record<string, CustomTheme>
}

export const ThemeProvider: React.FC<CustomThemeProviderProps> = ({
  children,
  defaultTheme = "system",
  storageKey = "ui-theme",
  enableSystem = true,
  attribute = "class",
  themes = defaultThemes,
}) => {
  const [theme, setThemeState] = React.useState<string | undefined>(defaultTheme)
  const [systemTheme, setSystemTheme] = React.useState<string | undefined>("light")
  const [customThemes, setCustomThemes] = React.useState<Record<string, CustomTheme>>({})

  React.useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    setSystemTheme(mediaQuery.matches ? "dark" : "light")

    const handleChange = (e: MediaQueryListEvent) => {
      setSystemTheme(e.matches ? "dark" : "light")
    }

    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [])

  const setTheme = React.useCallback((newTheme: string) => {
    setThemeState(newTheme)
    try {
      localStorage.setItem(storageKey, newTheme)
    } catch (error) {
      console.warn("Failed to save theme to localStorage:", error)
    }
  }, [storageKey])

  const addCustomTheme = React.useCallback((theme: CustomTheme) => {
    setCustomThemes(prev => ({
      ...prev,
      [theme.name]: theme,
    }))
  }, [])

  const removeCustomTheme = React.useCallback((name: string) => {
    setCustomThemes(prev => {
      const newThemes = { ...prev }
      delete newThemes[name]
      return newThemes
    })
  }, [])

  const allThemes = React.useMemo(() => ({
    ...themes,
    ...customThemes,
  }), [themes, customThemes])

  const currentTheme = React.useMemo(() => {
    const resolvedTheme = theme === "system" ? systemTheme : theme
    return resolvedTheme ? allThemes[resolvedTheme] : undefined
  }, [theme, systemTheme, allThemes])

  React.useEffect(() => {
    const savedTheme = localStorage.getItem(storageKey)
    if (savedTheme) {
      setThemeState(savedTheme)
    }
  }, [storageKey])

  React.useEffect(() => {
    if (currentTheme) {
      const root = document.documentElement
      
      // Apply CSS variables
      Object.entries(currentTheme.colors).forEach(([key, value]) => {
        root.style.setProperty(`--${key}`, value)
      })
      
      root.style.setProperty("--radius", currentTheme.borderRadius)
      root.style.setProperty("--font-family", currentTheme.fontFamily)
      
      // Apply theme class
      if (theme === "system") {
        root.classList.remove("light", "dark")
        root.classList.add(systemTheme || "light")
      } else {
        root.classList.remove("light", "dark", "blue", "green")
        if (theme) {
          root.classList.add(theme)
        }
      }
    }
  }, [currentTheme, theme, systemTheme])

  const contextValue: ThemeContextType = {
    theme,
    setTheme,
    systemTheme,
    themes: allThemes,
    currentTheme,
    addCustomTheme,
    removeCustomTheme,
  }

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  )
}

export { defaultThemes }