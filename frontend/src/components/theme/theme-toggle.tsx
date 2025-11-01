import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Sun, Moon, Monitor, Palette } from "lucide-react"
import { cn } from "@/utils"
import { Button } from "@/components/ui/button"
import { Dropdown, type DropdownItem } from "@/components/ui/dropdown"
import { useTheme } from "./theme-provider"

const themeToggleVariants = cva(
  "",
  {
    variants: {
      variant: {
        default: "",
        dropdown: "",
        toggle: "",
      },
      size: {
        sm: "h-8 w-8",
        default: "h-10 w-10",
        lg: "h-12 w-12",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ThemeToggleProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof themeToggleVariants> {
  showLabel?: boolean
  variant?: "default" | "dropdown" | "toggle"
}

const ThemeToggle = React.forwardRef<HTMLButtonElement, ThemeToggleProps>(
  ({
    className,
    size,
    variant: toggleVariant = "default",
    showLabel = false,
    ...props
  }, ref) => {
    const { theme, setTheme, systemTheme, themes } = useTheme()

    const getThemeIcon = (themeName: string) => {
      switch (themeName) {
        case "light":
          return <Sun className="h-4 w-4" />
        case "dark":
          return <Moon className="h-4 w-4" />
        case "system":
          return <Monitor className="h-4 w-4" />
        default:
          return <Palette className="h-4 w-4" />
      }
    }

    const getThemeLabel = (themeName: string) => {
      if (themeName === "system") {
        return `系统 (${systemTheme === "dark" ? "深色" : "浅色"})`
      }
      return themes[themeName]?.name || themeName
    }

    const handleToggle = () => {
      if (theme === "light") {
        setTheme("dark")
      } else if (theme === "dark") {
        setTheme("system")
      } else {
        setTheme("light")
      }
    }

    if (toggleVariant === "dropdown") {
      const dropdownItems: DropdownItem[] = [
        {
          value: "light",
          label: "浅色",
          icon: <Sun className="h-4 w-4" />,
          onClick: () => setTheme("light"),
        },
        {
          value: "dark",
          label: "深色",
          icon: <Moon className="h-4 w-4" />,
          onClick: () => setTheme("dark"),
        },
        {
          value: "system",
          label: `系统 (${systemTheme === "dark" ? "深色" : "浅色"})`,
          icon: <Monitor className="h-4 w-4" />,
          onClick: () => setTheme("system"),
        },
        ...Object.entries(themes)
          .filter(([key]) => !["light", "dark", "system"].includes(key))
          .map(([key, theme]) => ({
            value: key,
            label: theme.name,
            icon: <Palette className="h-4 w-4" />,
            onClick: () => setTheme(key),
          })),
      ]

      return (
        <Dropdown
          items={dropdownItems}
          value={theme}
          onValueChange={setTheme}
          className={cn(themeToggleVariants({ size }), className)}
          {...props}
        >
          <Button
            ref={ref}
            variant="outline"
            size={size}
            className={cn("w-full justify-start", className)}
            {...props}
          >
            {getThemeIcon(theme || "system")}
            {showLabel && (
              <span className="ml-2">
                {getThemeLabel(theme || "system")}
              </span>
            )}
          </Button>
        </Dropdown>
      )
    }

    if (toggleVariant === "toggle") {
      return (
        <Button
          ref={ref}
          variant="outline"
          size={size}
          onClick={handleToggle}
          className={cn(themeToggleVariants({ variant: "toggle", size }), className)}
          title={`当前主题: ${getThemeLabel(theme || "system")}`}
          {...props}
        >
          {getThemeIcon(theme || "system")}
        </Button>
      )
    }

    // Default variant
    return (
      <Button
        ref={ref}
        variant="ghost"
        size={size}
        onClick={handleToggle}
        className={cn(themeToggleVariants({ size }), className)}
        title={`当前主题: ${getThemeLabel(theme || "system")}`}
        {...props}
      >
        {getThemeIcon(theme || "system")}
        {showLabel && (
          <span className="ml-2">
            {getThemeLabel(theme || "system")}
          </span>
        )}
      </Button>
    )
  }
)
ThemeToggle.displayName = "ThemeToggle"

const ThemeToggleGroup = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    value?: string
    onValueChange?: (value: string) => void
    size?: VariantProps<typeof themeToggleVariants>["size"]
  }
>(({ className, value, onValueChange, size = "default", ...props }, ref) => {
  const { theme, setTheme, themes } = useTheme()

  const handleThemeChange = (newTheme: string) => {
    setTheme(newTheme)
    onValueChange?.(newTheme)
  }

  const currentTheme = value || theme

  const themeOptions = [
    { value: "light", label: "浅色", icon: <Sun className="h-4 w-4" /> },
    { value: "dark", label: "深色", icon: <Moon className="h-4 w-4" /> },
    { value: "system", label: "系统", icon: <Monitor className="h-4 w-4" /> },
    ...Object.entries(themes)
      .filter(([key]) => !["light", "dark", "system"].includes(key))
      .map(([key, theme]) => ({
        value: key,
        label: theme.name,
        icon: <Palette className="h-4 w-4" />,
      })),
  ]

  return (
    <div
      ref={ref}
      className={cn("inline-flex rounded-lg border border-input p-1", className)}
      {...props}
    >
      {themeOptions.map((option) => (
        <Button
          key={option.value}
          variant={currentTheme === option.value ? "default" : "ghost"}
          size={size}
          onClick={() => handleThemeChange(option.value)}
          className={cn(
            "flex items-center gap-2",
            currentTheme === option.value && "bg-primary text-primary-foreground"
          )}
        >
          {option.icon}
          <span className="hidden sm:inline">{option.label}</span>
        </Button>
      ))}
    </div>
  )
})
ThemeToggleGroup.displayName = "ThemeToggleGroup"

const ThemePreview = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    themeName: string
    size?: "sm" | "default" | "lg"
    showName?: boolean
    onClick?: () => void
  }
>(({ className, themeName, size = "default", showName = true, onClick, ...props }, ref) => {
  const { themes, theme: currentTheme } = useTheme()
  const theme = themes[themeName]

  if (!theme) return null

  const sizeClasses = {
    sm: "h-16 w-16",
    default: "h-20 w-20",
    lg: "h-24 w-24",
  }

  const isActive = currentTheme === themeName

  return (
    <div
      ref={ref}
      className={cn(
        "relative cursor-pointer rounded-lg border-2 transition-all hover:scale-105",
        isActive ? "border-primary shadow-lg" : "border-border",
        sizeClasses[size],
        className
      )}
      onClick={onClick}
      {...props}
    >
      <div
        className="absolute inset-1 rounded-md overflow-hidden"
        style={{
          background: `hsl(${theme.colors.background})`,
        }}
      >
        <div className="absolute top-2 left-2 right-2 h-4 rounded-sm" 
          style={{ backgroundColor: `hsl(${theme.colors.primary})` }} />
        <div className="absolute bottom-2 left-2 right-2 h-2 rounded-sm" 
          style={{ backgroundColor: `hsl(${theme.colors.muted})` }} />
      </div>
      {isActive && (
        <div className="absolute -top-1 -right-1 h-4 w-4 bg-primary rounded-full flex items-center justify-center">
          <div className="h-2 w-2 bg-primary-foreground rounded-full" />
        </div>
      )}
      {showName && (
        <div className="absolute -bottom-6 left-0 right-0 text-center text-xs text-muted-foreground">
          {theme.name}
        </div>
      )}
    </div>
  )
})
ThemePreview.displayName = "ThemePreview"

const ThemeCustomizer = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
  const { currentTheme, addCustomTheme } = useTheme()
  const [customTheme, setCustomTheme] = React.useState({
    name: "",
    colors: currentTheme?.colors || {},
    borderRadius: currentTheme?.borderRadius || "0.5rem",
    fontFamily: currentTheme?.fontFamily || "Inter, system-ui, sans-serif",
  })

  const handleSaveCustomTheme = () => {
    if (customTheme.name && customTheme.colors) {
      addCustomTheme({
        name: customTheme.name,
        colors: customTheme.colors,
        borderRadius: customTheme.borderRadius,
        fontFamily: customTheme.fontFamily,
      })
    }
  }

  return (
    <div
      ref={ref}
      className={cn("space-y-6 p-6 border rounded-lg", className)}
      {...props}
    >
      <div>
        <h3 className="text-lg font-semibold mb-4">自定义主题</h3>
        
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">主题名称</label>
            <input
              type="text"
              value={customTheme.name}
              onChange={(e) => setCustomTheme(prev => ({ ...prev, name: e.target.value }))}
              className="w-full mt-1 px-3 py-2 border rounded-md"
              placeholder="输入主题名称"
            />
          </div>

          <div>
            <label className="text-sm font-medium">主色调</label>
            <input
              type="color"
              value={`hsl(${customTheme.colors.primary})`}
              onChange={(e) => {
                const hsl = e.target.value
                setCustomTheme(prev => ({
                  ...prev,
                  colors: { ...prev.colors, primary: hsl }
                }))
              }}
              className="w-full mt-1 h-10 border rounded-md"
            />
          </div>

          <div>
            <label className="text-sm font-medium">背景色</label>
            <input
              type="color"
              value={`hsl(${customTheme.colors.background})`}
              onChange={(e) => {
                const hsl = e.target.value
                setCustomTheme(prev => ({
                  ...prev,
                  colors: { ...prev.colors, background: hsl }
                }))
              }}
              className="w-full mt-1 h-10 border rounded-md"
            />
          </div>

          <div>
            <label className="text-sm font-medium">边框圆角</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={parseFloat(customTheme.borderRadius)}
              onChange={(e) => {
                setCustomTheme(prev => ({
                  ...prev,
                  borderRadius: `${e.target.value}rem`
                }))
              }}
              className="w-full mt-1"
            />
          </div>
        </div>

        <Button
          onClick={handleSaveCustomTheme}
          className="mt-6 w-full"
          disabled={!customTheme.name}
        >
          保存自定义主题
        </Button>
      </div>
    </div>
  )
})
ThemeCustomizer.displayName = "ThemeCustomizer"

export {
  ThemeToggle,
  ThemeToggleGroup,
  ThemePreview,
  ThemeCustomizer,
  themeToggleVariants,
}