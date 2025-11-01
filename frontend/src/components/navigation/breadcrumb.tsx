import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { ChevronRight, Home, MoreHorizontal } from "lucide-react"
import { cn } from "@/utils"

const breadcrumbVariants = cva(
  "flex flex-wrap items-center gap-2 text-sm text-muted-foreground",
  {
    variants: {
      variant: {
        default: "",
        separated: "gap-1",
        pills: "gap-1",
      },
      size: {
        sm: "text-xs",
        default: "text-sm",
        lg: "text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const breadcrumbItemVariants = cva(
  "transition-colors hover:text-foreground",
  {
    variants: {
      variant: {
        default: "",
        link: "hover:text-foreground",
        active: "text-foreground font-medium",
        pill: "rounded-md bg-muted px-2 py-1 hover:bg-accent hover:text-accent-foreground",
        activePill: "rounded-md bg-primary text-primary-foreground px-2 py-1",
      },
      size: {
        sm: "text-xs",
        default: "text-sm",
        lg: "text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface BreadcrumbItem {
  label: string
  href?: string
  icon?: React.ReactNode
  active?: boolean
  disabled?: boolean
  onClick?: () => void
}

export interface BreadcrumbProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof breadcrumbVariants> {
  items: BreadcrumbItem[]
  separator?: React.ReactNode
  maxItems?: number
  showHome?: boolean
  homeLabel?: string
  homeHref?: string
  homeIcon?: React.ReactNode
}

const Breadcrumb = React.forwardRef<HTMLDivElement, BreadcrumbProps>(
  ({
    className,
    variant,
    size,
    items,
    separator,
    maxItems,
    showHome = true,
    homeLabel = "首页",
    homeHref = "/",
    homeIcon = <Home className="h-4 w-4" />,
    ...props
  }, ref) => {
    const [expanded, setExpanded] = React.useState(false)

    // Add home item if enabled
    const allItems = React.useMemo(() => {
      const homeItem: BreadcrumbItem = {
        label: homeLabel,
        href: homeHref,
        icon: homeIcon,
        active: items.length === 0,
      }
      
      return showHome ? [homeItem, ...items] : items
    }, [items, showHome, homeLabel, homeHref, homeIcon])

    // Handle max items and truncation
    const displayItems = React.useMemo(() => {
      if (!maxItems || allItems.length <= maxItems) {
        return allItems
      }

      const activeIndex = allItems.findIndex(item => item.active)
      const beforeActive = allItems.slice(0, activeIndex)
      const afterActive = allItems.slice(activeIndex + 1)

      // Keep active item and some items around it
      const keepBefore = Math.max(0, Math.floor((maxItems - 1) / 2))
      const keepAfter = Math.max(0, Math.ceil((maxItems - 1) / 2))

      const truncatedBefore = beforeActive.length > keepBefore
        ? [
            ...beforeActive.slice(0, keepBefore - 1),
            { label: "...", disabled: true } as BreadcrumbItem
          ]
        : beforeActive

      const truncatedAfter = afterActive.length > keepAfter
        ? [
            { label: "...", disabled: true } as BreadcrumbItem,
            ...afterActive.slice(-keepAfter)
          ]
        : afterActive

      return [
        ...truncatedBefore,
        allItems[activeIndex],
        ...truncatedAfter
      ]
    }, [allItems, maxItems])

    const defaultSeparator = <ChevronRight className="h-4 w-4" />

    const renderBreadcrumbItem = (item: BreadcrumbItem, index: number) => {
      const isLast = index === displayItems.length - 1
      const isActive = item.active || isLast

      const itemVariant = React.useMemo(() => {
        if (variant === "pills") {
          return isActive ? "activePill" : "pill"
        }
        return isActive ? "active" : item.href ? "link" : "default"
      }, [variant, isActive, item.href])

      const content = (
        <>
          {item.icon && (
            <span className="mr-1 flex-shrink-0">
              {item.icon}
            </span>
          )}
          <span className="truncate">{item.label}</span>
        </>
      )

      if (item.href && !item.disabled) {
        return (
          <a
            key={index}
            href={item.href}
            className={cn(breadcrumbItemVariants({ variant: itemVariant, size }))}
            onClick={item.onClick}
          >
            {content}
          </a>
        )
      }

      return (
        <span
          key={index}
          className={cn(
            breadcrumbItemVariants({ variant: itemVariant, size }),
            item.disabled && "opacity-50 cursor-not-allowed"
          )}
          onClick={!item.disabled ? item.onClick : undefined}
        >
          {content}
        </span>
      )
    }

    const renderSeparator = (index: number) => {
      if (variant === "separated") {
        return (
          <span key={`separator-${index}`} className="mx-1 text-muted-foreground/60">
            {separator || "/"}
          </span>
        )
      }

      if (variant === "pills") {
        return null // Pills don't need separators
      }

      return (
        <span key={`separator-${index}`} className="text-muted-foreground/60">
          {separator || defaultSeparator}
        </span>
      )
    }

    return (
      <nav
        ref={ref}
        className={cn(breadcrumbVariants({ variant, size }), className)}
        aria-label="面包屑导航"
        {...props}
      >
        {displayItems.map((item, index) => (
          <React.Fragment key={index}>
            {renderBreadcrumbItem(item, index)}
            {index < displayItems.length - 1 && renderSeparator(index)}
          </React.Fragment>
        ))}
      </nav>
    )
  }
)
Breadcrumb.displayName = "Breadcrumb"

const BreadcrumbList = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-wrap items-center gap-2", className)}
    {...props}
  />
))
BreadcrumbList.displayName = "BreadcrumbList"

const BreadcrumbItem = React.forwardRef<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement> & {
    href?: string
    active?: boolean
    disabled?: boolean
  }
>(({ className, href, active = false, disabled = false, ...props }, ref) => {
    const Component = href && !disabled ? "a" : "span"
  
    return (
      <Component
        ref={ref as any}
        href={href}
        className={cn(
          "transition-colors hover:text-foreground",
          active && "text-foreground font-medium",
          !active && href && "hover:text-foreground",
          disabled && "opacity-50 cursor-not-allowed",
          className
        )}
        {...props}
      />
    )
  }
)
BreadcrumbItem.displayName = "BreadcrumbItem"

const BreadcrumbSeparator = React.forwardRef<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement>
>(({ className, children = "/", ...props }, ref) => (
  <span
    ref={ref}
    className={cn("mx-1 text-muted-foreground/60", className)}
    role="presentation"
    {...props}
  >
    {children}
  </span>
))
BreadcrumbSeparator.displayName = "BreadcrumbSeparator"

const BreadcrumbEllipsis = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    items: BreadcrumbItem[]
    expanded?: boolean
    onExpandedChange?: (expanded: boolean) => void
  }
>(({ className, items, expanded = false, onExpandedChange, ...props }, ref) => {
  const [isExpanded, setIsExpanded] = React.useState(expanded)

  const handleToggle = () => {
    const newExpanded = !isExpanded
    setIsExpanded(newExpanded)
    onExpandedChange?.(newExpanded)
  }

  return (
    <div className="relative">
      <button
        ref={ref}
        type="button"
        className={cn(
          "flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground",
          className
        )}
        onClick={handleToggle}
        {...props}
      >
        <MoreHorizontal className="h-4 w-4" />
      </button>
      
      {isExpanded && (
        <div className="absolute top-full left-0 z-10 mt-1 min-w-[200px] rounded-md border bg-popover p-2 shadow-lg">
          <div className="space-y-1">
            {items.map((item, index) => (
              <a
                key={index}
                href={item.href}
                className="block rounded px-2 py-1 text-sm hover:bg-accent hover:text-accent-foreground"
                onClick={item.onClick}
              >
                {item.icon && (
                  <span className="mr-2 inline-flex">
                    {item.icon}
                  </span>
                )}
                {item.label}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
})
BreadcrumbEllipsis.displayName = "BreadcrumbEllipsis"

export {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbSeparator,
  BreadcrumbEllipsis,
  breadcrumbVariants,
  breadcrumbItemVariants,
}