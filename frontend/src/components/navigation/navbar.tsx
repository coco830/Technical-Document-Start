import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Menu, X, Search, Bell, User, Settings } from "lucide-react"
import { cn } from "@/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ThemeToggle } from "@/components/theme"
import { Dropdown, type DropdownItem } from "@/components/ui/dropdown"

const navbarVariants = cva(
  "sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60",
  {
    variants: {
      variant: {
        default: "border-border",
        transparent: "border-transparent bg-transparent",
        floating: "border-border shadow-lg rounded-lg mx-4 mt-4",
      },
      size: {
        sm: "h-12",
        default: "h-16",
        lg: "h-20",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface NavbarProps
  extends React.HTMLAttributes<HTMLElement>,
    VariantProps<typeof navbarVariants> {
  logo?: React.ReactNode
  title?: string
  menuItems?: DropdownItem[]
  userItems?: DropdownItem[]
  showSearch?: boolean
  searchPlaceholder?: string
  onSearch?: (query: string) => void
  showThemeToggle?: boolean
  showNotifications?: boolean
  notificationCount?: number
  onNotificationClick?: () => void
  user?: {
    name: string
    email?: string
    avatar?: string
  }
  onUserMenuClick?: (action: string) => void
  mobileMenuOpen?: boolean
  onMobileMenuToggle?: (open: boolean) => void
}

const Navbar = React.forwardRef<HTMLElement, NavbarProps>(
  ({
    className,
    variant,
    size,
    logo,
    title,
    menuItems = [],
    userItems = [],
    showSearch = false,
    searchPlaceholder = "搜索...",
    onSearch,
    showThemeToggle = true,
    showNotifications = true,
    notificationCount = 0,
    onNotificationClick,
    user,
    onUserMenuClick,
    mobileMenuOpen = false,
    onMobileMenuToggle,
    ...props
  }, ref) => {
    const [searchQuery, setSearchQuery] = React.useState("")
    const [isScrolled, setIsScrolled] = React.useState(false)

    React.useEffect(() => {
      const handleScroll = () => {
        setIsScrolled(window.scrollY > 10)
      }

      window.addEventListener("scroll", handleScroll)
      return () => window.removeEventListener("scroll", handleScroll)
    }, [])

    const handleSearch = (e: React.FormEvent) => {
      e.preventDefault()
      onSearch?.(searchQuery)
    }

    const defaultUserItems: DropdownItem[] = [
      {
        value: "profile",
        label: "个人资料",
        icon: <User className="h-4 w-4" />,
        onClick: () => onUserMenuClick?.("profile"),
      },
      {
        value: "settings",
        label: "设置",
        icon: <Settings className="h-4 w-4" />,
        onClick: () => onUserMenuClick?.("settings"),
      },
      ...userItems,
    ]

    const sizeClasses = {
      sm: "h-12",
      default: "h-16",
      lg: "h-20",
    }

    const shouldShowBackground = variant === "default" || 
      (variant === "transparent" && isScrolled) ||
      variant === "floating"

    return (
      <header
        ref={ref}
        className={cn(
          navbarVariants({ variant, size }),
          shouldShowBackground && "bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60",
          variant === "transparent" && !isScrolled && "bg-transparent",
          className
        )}
        {...props}
      >
        <div className="container mx-auto flex h-full items-center justify-between px-4">
          {/* Logo and Title */}
          <div className="flex items-center gap-4">
            {/* Mobile Menu Toggle */}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
              onClick={() => onMobileMenuToggle?.(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>

            {logo && (
              <div className="flex items-center gap-2">
                {logo}
              </div>
            )}
            
            {title && (
              <h1 className="text-xl font-semibold hidden sm:block">
                {title}
              </h1>
            )}
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            {menuItems.map((item) => (
              <Button
                key={item.value}
                variant="ghost"
                size="sm"
                onClick={() => item.onClick?.()}
                className="h-9"
              >
                {item.icon && <span className="mr-2">{item.icon}</span>}
                {item.label}
              </Button>
            ))}
          </nav>

          {/* Right Side Actions */}
          <div className="flex items-center gap-2">
            {/* Search */}
            {showSearch && (
              <form onSubmit={handleSearch} className="hidden sm:block">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="search"
                    placeholder={searchPlaceholder}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 w-64 lg:w-80"
                  />
                </div>
              </form>
            )}

            {/* Theme Toggle */}
            {showThemeToggle && (
              <ThemeToggle
                variant="toggle"
                size="sm"
                className="hidden sm:flex"
              />
            )}

            {/* Notifications */}
            {showNotifications && (
              <Button
                variant="ghost"
                size="sm"
                className="relative"
                onClick={onNotificationClick}
              >
                <Bell className="h-4 w-4" />
                {notificationCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-destructive text-destructive-foreground text-xs flex items-center justify-center">
                    {notificationCount > 99 ? "99+" : notificationCount}
                  </span>
                )}
              </Button>
            )}

            {/* User Menu */}
            {user ? (
              <Dropdown
                items={defaultUserItems}
                className="hidden sm:flex"
              >
                <Button variant="ghost" size="sm" className="flex items-center gap-2">
                  {user.avatar ? (
                    <img
                      src={user.avatar}
                      alt={user.name}
                      className="h-6 w-6 rounded-full"
                    />
                  ) : (
                    <User className="h-4 w-4" />
                  )}
                  <span className="hidden lg:block">{user.name}</span>
                </Button>
              </Dropdown>
            ) : (
              <div className="hidden sm:flex items-center gap-2">
                <Button variant="ghost" size="sm">
                  登录
                </Button>
                <Button size="sm">
                  注册
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 right-0 bg-background border-b border-border shadow-lg">
            <nav className="container mx-auto px-4 py-4 space-y-2">
              {menuItems.map((item) => (
                <Button
                  key={item.value}
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    item.onClick?.()
                    onMobileMenuToggle?.(false)
                  }}
                  className="w-full justify-start"
                >
                  {item.icon && <span className="mr-2">{item.icon}</span>}
                  {item.label}
                </Button>
              ))}
              
              {/* Mobile Search */}
              {showSearch && (
                <form onSubmit={handleSearch} className="pt-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      type="search"
                      placeholder={searchPlaceholder}
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 w-full"
                    />
                  </div>
                </form>
              )}

              {/* Mobile Theme Toggle */}
              {showThemeToggle && (
                <div className="pt-2">
                  <ThemeToggle
                    variant="dropdown"
                    showLabel={true}
                  />
                </div>
              )}

              {/* Mobile User Menu */}
              {user ? (
                <div className="pt-2 border-t border-border">
                  <div className="flex items-center gap-2 py-2">
                    {user.avatar ? (
                      <img
                        src={user.avatar}
                        alt={user.name}
                        className="h-8 w-8 rounded-full"
                      />
                    ) : (
                      <User className="h-6 w-6" />
                    )}
                    <div>
                      <div className="font-medium">{user.name}</div>
                      {user.email && (
                        <div className="text-sm text-muted-foreground">{user.email}</div>
                      )}
                    </div>
                  </div>
                  {defaultUserItems.map((item) => (
                    <Button
                      key={item.value}
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        item.onClick?.()
                        onMobileMenuToggle?.(false)
                      }}
                      className="w-full justify-start"
                    >
                      {item.icon && <span className="mr-2">{item.icon}</span>}
                      {item.label}
                    </Button>
                  ))}
                </div>
              ) : (
                <div className="pt-2 border-t border-border space-y-2">
                  <Button variant="ghost" size="sm" className="w-full">
                    登录
                  </Button>
                  <Button size="sm" className="w-full">
                    注册
                  </Button>
                </div>
              )}
            </nav>
          </div>
        )}
      </header>
    )
  }
)
Navbar.displayName = "Navbar"

const NavbarBrand = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center gap-2", className)}
    {...props}
  />
))
NavbarBrand.displayName = "NavbarBrand"

const NavbarNav = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <nav
    ref={ref}
    className={cn("hidden md:flex items-center gap-6", className)}
    {...props}
  />
))
NavbarNav.displayName = "NavbarNav"

const NavbarActions = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center gap-2", className)}
    {...props}
  />
))
NavbarActions.displayName = "NavbarActions"

export {
  Navbar,
  NavbarBrand,
  NavbarNav,
  NavbarActions,
  navbarVariants,
}