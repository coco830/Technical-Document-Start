import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils"

const contentLayoutVariants = cva(
  "flex flex-col",
  {
    variants: {
      variant: {
        default: "",
        centered: "items-center justify-center",
        fluid: "",
        contained: "container mx-auto",
      },
      size: {
        sm: "max-w-2xl",
        default: "max-w-4xl",
        lg: "max-w-6xl",
        xl: "max-w-7xl",
        full: "max-w-full",
      },
      padding: {
        none: "",
        sm: "p-4",
        default: "p-6",
        lg: "p-8",
        xl: "p-12",
      },
      spacing: {
        none: "gap-0",
        sm: "gap-2",
        default: "gap-4",
        lg: "gap-6",
        xl: "gap-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      padding: "default",
      spacing: "default",
    },
  }
)

export interface ContentLayoutProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof contentLayoutVariants> {
  header?: React.ReactNode
  footer?: React.ReactNode
  sidebar?: React.ReactNode
  sidebarPosition?: "left" | "right"
  aside?: React.ReactNode
  asidePosition?: "left" | "right"
  className?: string
  contentClassName?: string
}

const ContentLayout = React.forwardRef<HTMLDivElement, ContentLayoutProps>(
  ({
    className,
    variant,
    size,
    padding,
    spacing,
    header,
    footer,
    sidebar,
    sidebarPosition = "left",
    aside,
    asidePosition = "right",
    contentClassName,
    children,
    ...props
  }, ref) => {
    const renderHeader = () => {
      if (!header) return null

      return (
        <header className="border-b border-border bg-background">
          <div className={cn(
            contentLayoutVariants({ variant, size, padding: "sm" }),
            "py-4"
          )}>
            {header}
          </div>
        </header>
      )
    }

    const renderSidebar = () => {
      if (!sidebar) return null

      return (
        <aside className={cn(
          "hidden lg:block w-64 flex-shrink-0 border-r border-border bg-background",
          sidebarPosition === "right" && "order-last border-r-0 border-l"
        )}>
          <div className={cn(
            contentLayoutVariants({ variant, padding: "sm" }),
            "py-4 h-full"
          )}>
            {sidebar}
          </div>
        </aside>
      )
    }

    const renderAside = () => {
      if (!aside) return null

      return (
        <aside className={cn(
          "hidden lg:block w-64 flex-shrink-0 border-l border-border bg-background",
          asidePosition === "left" && "order-first border-l-0 border-r"
        )}>
          <div className={cn(
            contentLayoutVariants({ variant, padding: "sm" }),
            "py-4 h-full"
          )}>
            {aside}
          </div>
        </aside>
      )
    }

    const renderFooter = () => {
      if (!footer) return null

      return (
        <footer className="border-t border-border bg-background mt-auto">
          <div className={cn(
            contentLayoutVariants({ variant, size, padding: "sm" }),
            "py-4"
          )}>
            {footer}
          </div>
        </footer>
      )
    }

    return (
      <div
        ref={ref}
        className={cn(
          contentLayoutVariants({ variant, size, padding, spacing }),
          "min-h-screen",
          className
        )}
        {...props}
      >
        {renderHeader()}
        
        <div className={cn(
          "flex flex-1 overflow-hidden",
          (sidebar || aside) && "lg:flex"
        )}>
          {renderSidebar()}
          
          <main className={cn(
            "flex-1 overflow-auto",
            contentClassName,
            sidebar && aside && "lg:max-w-none"
          )}>
            {children}
          </main>
          
          {renderAside()}
        </div>
        
        {renderFooter()}
      </div>
    )
  }
)
ContentLayout.displayName = "ContentLayout"

const ContentLayoutHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("border-b border-border bg-background", className)}
    {...props}
  />
))
ContentLayoutHeader.displayName = "ContentLayoutHeader"

const ContentLayoutMain = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    sidebar?: boolean
    aside?: boolean
  }
>(({ className, sidebar = false, aside = false, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex-1 overflow-auto",
      sidebar && aside && "lg:max-w-none",
      className
    )}
    {...props}
  />
))
ContentLayoutMain.displayName = "ContentLayoutMain"

const ContentLayoutSidebar = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    position?: "left" | "right"
  }
>(({ className, position = "left", ...props }, ref) => (
  <aside
    ref={ref}
    className={cn(
      "hidden lg:block w-64 flex-shrink-0 border-r border-border bg-background",
      position === "right" && "order-last border-r-0 border-l"
    )}
    {...props}
  />
))
ContentLayoutSidebar.displayName = "ContentLayoutSidebar"

const ContentLayoutAside = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    position?: "left" | "right"
  }
>(({ className, position = "right", ...props }, ref) => (
  <aside
    ref={ref}
    className={cn(
      "hidden lg:block w-64 flex-shrink-0 border-l border-border bg-background",
      position === "left" && "order-first border-l-0 border-r"
    )}
    {...props}
  />
))
ContentLayoutAside.displayName = "ContentLayoutAside"

const ContentLayoutFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <footer
    ref={ref}
    className={cn("border-t border-border bg-background mt-auto", className)}
    {...props}
  />
))
ContentLayoutFooter.displayName = "ContentLayoutFooter"

const ContentLayoutSection = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    variant?: "default" | "muted" | "accent"
    padding?: "none" | "sm" | "default" | "lg" | "xl"
  }
>(({ className, variant = "default", padding = "default", ...props }, ref) => {
  const variantClasses = {
    default: "",
    muted: "bg-muted/30",
    accent: "bg-accent/30",
  }

  const paddingClasses = {
    none: "",
    sm: "p-4",
    default: "p-6",
    lg: "p-8",
    xl: "p-12",
  }

  return (
    <section
      ref={ref}
      className={cn(
        "rounded-lg border",
        variantClasses[variant],
        paddingClasses[padding],
        className
      )}
      {...props}
    />
  )
})
ContentLayoutSection.displayName = "ContentLayoutSection"

const ContentLayoutGrid = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    cols?: 1 | 2 | 3 | 4 | 6 | 12
    gap?: "none" | "sm" | "default" | "lg" | "xl"
  }
>(({ className, cols = 1, gap = "default", ...props }, ref) => {
  const colsClasses = {
    1: "grid-cols-1",
    2: "grid-cols-2",
    3: "grid-cols-3",
    4: "grid-cols-4",
    6: "grid-cols-6",
    12: "grid-cols-12",
  }

  const gapClasses = {
    none: "gap-0",
    sm: "gap-2",
    default: "gap-4",
    lg: "gap-6",
    xl: "gap-8",
  }

  return (
    <div
      ref={ref}
      className={cn(
        "grid",
        colsClasses[cols],
        gapClasses[gap],
        className
      )}
      {...props}
    />
  )
})
ContentLayoutGrid.displayName = "ContentLayoutGrid"

export {
  ContentLayout,
  ContentLayoutHeader,
  ContentLayoutMain,
  ContentLayoutSidebar,
  ContentLayoutAside,
  ContentLayoutFooter,
  ContentLayoutSection,
  ContentLayoutGrid,
  contentLayoutVariants,
}