import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { 
  ChevronLeft, 
  ChevronRight, 
  Home, 
  FileText, 
  Users, 
  Settings, 
  HelpCircle,
  Menu,
  X
} from "lucide-react"
import { cn } from "@/utils"
import { Button } from "@/components/ui/button"
import { Dropdown, type DropdownItem } from "@/components/ui/dropdown"

const sidebarVariants = cva(
  "flex h-full flex-col border-r bg-background transition-all duration-300",
  {
    variants: {
      variant: {
        default: "border-border",
        floating: "border-border shadow-lg rounded-lg m-4",
        glass: "border-border/20 bg-background/80 backdrop-blur-md",
      },
      size: {
        sm: "w-16",
        default: "w-64",
        lg: "w-80",
      },
      collapsed: {
        true: "w-16",
        false: "",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      collapsed: false,
    },
  }
)

const sidebarItemVariants = cva(
  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
  {
    variants: {
      active: {
        true: "bg-accent text-accent-foreground",
        false: "text-muted-foreground",
      },
      collapsed: {
        true: "justify-center px-2",
        false: "",
      },
    },
    defaultVariants: {
      active: false,
      collapsed: false,
    },
  }
)

export interface SidebarItem {
  id: string
  label: string
  icon?: React.ReactNode
  href?: string
  badge?: string | number
  children?: SidebarItem[]
  onClick?: () => void
}

export interface SidebarProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof sidebarVariants> {
  items: SidebarItem[]
  collapsed?: boolean
  onCollapseChange?: (collapsed: boolean) => void
  logo?: React.ReactNode
  title?: string
  user?: {
    name: string
    email?: string
    avatar?: string
  }
  footer?: React.ReactNode
  showCollapseButton?: boolean
  mobileOpen?: boolean
  onMobileClose?: () => void
}

const Sidebar = React.forwardRef<HTMLDivElement, SidebarProps>(
  ({
    className,
    variant,
    size,
    collapsed = false,
    onCollapseChange,
    logo,
    title,
    user,
    footer,
    showCollapseButton = true,
    mobileOpen = false,
    onMobileClose,
    items,
    ...props
  }, ref) => {
    const [expandedItems, setExpandedItems] = React.useState<Set<string>>(new Set())
    const [activeItem, setActiveItem] = React.useState<string | null>(null)

    const handleCollapseToggle = () => {
      onCollapseChange?.(!collapsed)
    }

    const handleItemClick = (item: SidebarItem) => {
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
    }

    const renderSidebarItem = (item: SidebarItem, level = 0) => {
      const isActive = activeItem === item.id
      const isExpanded = expandedItems.has(item.id)
      const hasChildren = item.children && item.children.length > 0

      return (
        <div key={item.id} className="w-full">
          <Button
            variant="ghost"
            className={cn(
              sidebarItemVariants({ active: isActive, collapsed }),
              "w-full justify-start"
            )}
            onClick={() => handleItemClick(item)}
          >
            {item.icon && (
              <span className="flex-shrink-0">
                {item.icon}
              </span>
            )}
            
            {!collapsed && (
              <>
                <span className="flex-1 truncate">{item.label}</span>
                {item.badge && (
                  <span className="ml-auto flex h-5 min-w-[20px] items-center justify-center rounded-full bg-primary text-primary-foreground text-xs px-1">
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
              </>
            )}
          </Button>

          {/* Submenu */}
          {hasChildren && !collapsed && isExpanded && (
            <div className="mt-1 space-y-1 pl-6">
              {item.children?.map(child => renderSidebarItem(child, level + 1))}
            </div>
          )}
        </div>
      )
    }

    const sidebarContent = (
      <div className="flex h-full flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          {!collapsed ? (
            <div className="flex items-center gap-3">
              {logo && (
                <div className="flex-shrink-0">
                  {logo}
                </div>
              )}
              {title && (
                <h2 className="text-lg font-semibold truncate">
                  {title}
                </h2>
              )}
            </div>
          ) : (
            logo && (
              <div className="flex-shrink-0">
                {logo}
              </div>
            )
          )}
          
          {showCollapseButton && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCollapseToggle}
              className="hidden md:flex"
            >
              {collapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>

        {/* User Info */}
        {user && !collapsed && (
          <div className="p-4 border-b border-border">
            <div className="flex items-center gap-3">
              {user.avatar ? (
                <img
                  src={user.avatar}
                  alt={user.name}
                  className="h-8 w-8 rounded-full"
                />
              ) : (
                <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm font-medium">
                  {user.name.charAt(0).toUpperCase()}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="truncate font-medium">{user.name}</div>
                {user.email && (
                  <div className="truncate text-sm text-muted-foreground">
                    {user.email}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 overflow-auto p-4">
          <div className="space-y-2">
            {items.map(item => renderSidebarItem(item))}
          </div>
        </nav>

        {/* Footer */}
        {footer && (
          <div className="p-4 border-t border-border">
            {footer}
          </div>
        )}
      </div>
    )

    return (
      <>
        {/* Desktop Sidebar */}
        <aside
          ref={ref}
          className={cn(
            sidebarVariants({ variant, size, collapsed }),
            "hidden md:flex",
            className
          )}
          {...props}
        >
          {sidebarContent}
        </aside>

        {/* Mobile Sidebar Overlay */}
        {mobileOpen && (
          <div className="md:hidden fixed inset-0 z-50 flex">
            <div
              className="fixed inset-0 bg-black/50"
              onClick={onMobileClose}
            />
            <aside
              className={cn(
                sidebarVariants({ variant, size, collapsed: false }),
                "relative h-full w-64 max-w-full"
              )}
            >
              <div className="absolute right-4 top-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onMobileClose}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              {sidebarContent}
            </aside>
          </div>
        )}
      </>
    )
  }
)
Sidebar.displayName = "Sidebar"

const SidebarHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center justify-between p-4 border-b border-border", className)}
    {...props}
  />
))
SidebarHeader.displayName = "SidebarHeader"

const SidebarContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex-1 overflow-auto p-4", className)}
    {...props}
  />
))
SidebarContent.displayName = "SidebarContent"

const SidebarFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("p-4 border-t border-border", className)}
    {...props}
  />
))
SidebarFooter.displayName = "SidebarFooter"

const SidebarMenu = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("space-y-2", className)}
    {...props}
  />
))
SidebarMenu.displayName = "SidebarMenu"

const SidebarMenuItem = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    active?: boolean
    collapsed?: boolean
    icon?: React.ReactNode
    badge?: string | number
  }
>(({ className, active = false, collapsed = false, icon, badge, children, ...props }, ref) => (
  <Button
    ref={ref}
    variant="ghost"
    className={cn(
      sidebarItemVariants({ active, collapsed }),
      "w-full justify-start",
      className
    )}
    {...props}
  >
    {icon && (
      <span className="flex-shrink-0">
        {icon}
      </span>
    )}
    
    {!collapsed && (
      <>
        <span className="flex-1 truncate">{children}</span>
        {badge && (
          <span className="ml-auto flex h-5 min-w-[20px] items-center justify-center rounded-full bg-primary text-primary-foreground text-xs px-1">
            {typeof badge === "number" && badge > 99 ? "99+" : badge}
          </span>
        )}
      </>
    )}
  </Button>
))
SidebarMenuItem.displayName = "SidebarMenuItem"

export {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuItem,
  sidebarVariants,
  sidebarItemVariants,
}