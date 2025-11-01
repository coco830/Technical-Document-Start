import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { 
  Menu, 
  X, 
  Home, 
  FileText, 
  Users, 
  Settings, 
  HelpCircle,
  ChevronRight,
  LogOut,
  User
} from "lucide-react"
import { cn } from "@/utils"
import { Button } from "@/components/ui/button"
import { Dropdown, type DropdownItem } from "@/components/ui/dropdown"

const mobileNavVariants = cva(
  "fixed inset-0 z-50 flex flex-col bg-background",
  {
    variants: {
      variant: {
        default: "",
        slide: "transition-transform duration-300 ease-in-out",
        overlay: "bg-black/50 backdrop-blur-sm",
      },
      position: {
        bottom: "flex-col-reverse",
        top: "",
      },
    },
    defaultVariants: {
      variant: "default",
      position: "bottom",
    },
  }
)

const mobileNavItemVariants = cva(
  "flex items-center justify-between py-3 px-4 border-b border-border transition-colors hover:bg-accent",
  {
    variants: {
      active: {
        true: "bg-accent text-accent-foreground",
        false: "",
      },
    },
    defaultVariants: {
      active: false,
    },
  }
)

export interface MobileNavItem {
  id: string
  label: string
  icon?: React.ReactNode
  href?: string
  badge?: string | number
  children?: MobileNavItem[]
  onClick?: () => void
}

export interface MobileNavProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof mobileNavVariants> {
  isOpen: boolean
  onClose: () => void
  items: MobileNavItem[]
  title?: string
  user?: {
    name: string
    email?: string
    avatar?: string
  }
  showUser?: boolean
  userItems?: DropdownItem[]
  onUserItemClick?: (action: string) => void
}

const MobileNav = React.forwardRef<HTMLDivElement, MobileNavProps>(
  ({
    className,
    variant,
    position,
    isOpen,
    onClose,
    items,
    title,
    user,
    showUser = true,
    userItems = [],
    onUserItemClick,
    ...props
  }, ref) => {
  const [expandedItems, setExpandedItems] = React.useState<Set<string>>(new Set())
  const [activeItem, setActiveItem] = React.useState<string | null>(null)

  React.useEffect(() => {
    // Prevent body scroll when mobile nav is open
    if (isOpen) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = ""
    }

    return () => {
      document.body.style.overflow = ""
    }
  }, [isOpen])

  const handleItemClick = (item: MobileNavItem) => {
    setActiveItem(item.id)
    
    if (item.children && item.children.length > 0) {
      setExpandedItems(prev => {
        const newSet = new Set(prev)
        if (newSet.has(item.id)) {
          newSet.delete(item.id)
        } else {
          newSet.add(item.id)
        }
        return newSet
      })
    }
    
    item.onClick?.()
    
    // Close mobile nav if item has href (navigation)
    if (item.href) {
      onClose()
    }
  }

  const renderMobileNavItem = (item: MobileNavItem, level = 0) => {
    const isActive = activeItem === item.id
    const isExpanded = expandedItems.has(item.id)
    const hasChildren = item.children && item.children.length > 0

    return (
      <div key={item.id} className="w-full">
        <Button
          variant="ghost"
          className={cn(
            mobileNavItemVariants({ active: isActive }),
            "w-full justify-start h-auto py-3"
          )}
          onClick={() => handleItemClick(item)}
        >
          <div className="flex items-center gap-3">
            {item.icon && (
              <span className="flex-shrink-0">
                {item.icon}
              </span>
            )}
            
            <span className="flex-1 text-left">{item.label}</span>
            
            {item.badge && (
              <span className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-primary text-primary-foreground text-xs px-1">
                {typeof item.badge === "number" && item.badge > 99 ? "99+" : item.badge}
              </span>
            )}
            
            {hasChildren && (
              <ChevronRight
                className={cn(
                  "h-4 w-4 transition-transform",
                  isExpanded && "rotate-90"
                )}
              />
            )}
          </div>
        </Button>

        {/* Submenu */}
        {hasChildren && isExpanded && (
          <div className="bg-muted/30">
            {item.children?.map(child => renderMobileNavItem(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  const defaultUserItems: DropdownItem[] = [
    {
      value: "profile",
      label: "个人资料",
      icon: <User className="h-4 w-4" />,
      onClick: () => onUserItemClick?.("profile"),
    },
    {
      value: "settings",
      label: "设置",
      icon: <Settings className="h-4 w-4" />,
      onClick: () => onUserItemClick?.("settings"),
    },
    {
      value: "help",
      label: "帮助",
      icon: <HelpCircle className="h-4 w-4" />,
      onClick: () => onUserItemClick?.("help"),
    },
    {
      value: "logout",
      label: "退出登录",
      icon: <LogOut className="h-4 w-4" />,
      onClick: () => onUserItemClick?.("logout"),
    },
    ...userItems,
  ]

  if (!isOpen) return null

  return (
    <div
      ref={ref}
      className={cn(
        mobileNavVariants({ variant, position }),
        variant === "slide" && (position === "bottom" ? "translate-y-full" : "-translate-y-full"),
        className
      )}
      {...props}
    >
      {/* Overlay for variant="overlay" */}
      {variant === "overlay" && (
        <div className="absolute inset-0" onClick={onClose} />
      )}

      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <h2 className="text-lg font-semibold">{title || "菜单"}</h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* User Info */}
      {showUser && user && (
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-3">
            {user.avatar ? (
              <img
                src={user.avatar}
                alt={user.name}
                className="h-10 w-10 rounded-full"
              />
            ) : (
              <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm font-medium">
                {user.name.charAt(0).toUpperCase()}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <div className="font-medium">{user.name}</div>
              {user.email && (
                <div className="text-sm text-muted-foreground">
                  {user.email}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex-1 overflow-auto">
        {items.map(item => renderMobileNavItem(item))}
      </div>

      {/* User Actions */}
      {showUser && user && (
        <div className="p-4 border-t border-border">
          <div className="space-y-2">
            {defaultUserItems.map((item) => (
              <Button
                key={item.value}
                variant="ghost"
                size="sm"
                onClick={() => {
                  item.onClick?.()
                  onClose()
                }}
                className="w-full justify-start"
              >
                {item.icon && <span className="mr-2">{item.icon}</span>}
                {item.label}
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
MobileNav.displayName = "MobileNav"

const MobileNavHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    title?: string
    onClose?: () => void
  }
>(({ className, title, onClose, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center justify-between p-4 border-b border-border", className)}
    {...props}
  >
    <h2 className="text-lg font-semibold">{title || "菜单"}</h2>
    <Button
      variant="ghost"
      size="sm"
      onClick={onClose}
    >
      <X className="h-5 w-5" />
    </Button>
  </div>
))
MobileNavHeader.displayName = "MobileNavHeader"

const MobileNavContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex-1 overflow-auto", className)}
    {...props}
  />
))
MobileNavContent.displayName = "MobileNavContent"

const MobileNavFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("p-4 border-t border-border", className)}
    {...props}
  />
))
MobileNavFooter.displayName = "MobileNavFooter"

const MobileNavToggle = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    isOpen?: boolean
  variant?: "default" | "outline" | "ghost"
    size?: "sm" | "default" | "lg"
  }
>(({ className, isOpen, variant = "outline", size = "default", ...props }, ref) => (
  <Button
    ref={ref}
    variant={variant}
    size={size}
    className={cn("md:hidden", className)}
    {...props}
  >
    {isOpen ? (
      <X className="h-5 w-5" />
    ) : (
      <Menu className="h-5 w-5" />
    )}
  </Button>
))
MobileNavToggle.displayName = "MobileNavToggle"

export {
  MobileNav,
  MobileNavHeader,
  MobileNavContent,
  MobileNavFooter,
  MobileNavToggle,
  mobileNavVariants,
  mobileNavItemVariants,
}