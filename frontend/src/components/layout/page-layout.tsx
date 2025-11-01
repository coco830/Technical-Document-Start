import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils"
import { Breadcrumb, type BreadcrumbProps } from "@/components/navigation"

const pageLayoutVariants = cva(
  "flex flex-col min-h-screen",
  {
    variants: {
      variant: {
        default: "",
        centered: "items-center justify-center",
        fluid: "",
        contained: "container mx-auto",
      },
      padding: {
        none: "",
        sm: "p-4",
        default: "p-6",
        lg: "p-8",
        xl: "p-12",
      },
    },
    defaultVariants: {
      variant: "default",
      padding: "default",
    },
  }
)

export interface PageLayoutProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof pageLayoutVariants> {
  title?: string
  subtitle?: string
  description?: string
  breadcrumb?: React.ReactNode | BreadcrumbProps
  header?: React.ReactNode
  footer?: React.ReactNode
  sidebar?: React.ReactNode
  actions?: React.ReactNode
  backHref?: string
  backLabel?: string
  className?: string
  contentClassName?: string
}

const PageLayout = React.forwardRef<HTMLDivElement, PageLayoutProps>(
  ({
    className,
    variant,
    padding,
    title,
    subtitle,
    description,
    breadcrumb,
    header,
    footer,
    sidebar,
    actions,
    backHref,
    backLabel = "返回",
    contentClassName,
    children,
    ...props
  }, ref) => {
    const renderHeader = () => {
      if (header) return header

      return (
        <div className="border-b border-border bg-background">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                {breadcrumb && (
                  <div className="mb-4">
                    {React.isValidElement(breadcrumb) ? (
                      breadcrumb
                    ) : (
                      <Breadcrumb {...(breadcrumb as BreadcrumbProps)} />
                    )}
                  </div>
                )}
                
                <div className="flex items-center gap-4">
                  {backHref && (
                    <a
                      href={backHref}
                      className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="h-4 w-4"
                      >
                        <path d="M19 12H5M12 19l-7-7 7-7" />
                      </svg>
                      {backLabel}
                    </a>
                  )}
                  
                  <div>
                    {title && (
                      <h1 className="text-2xl font-bold tracking-tight">
                        {title}
                      </h1>
                    )}
                    {subtitle && (
                      <p className="text-lg text-muted-foreground mt-1">
                        {subtitle}
                      </p>
                    )}
                    {description && (
                      <p className="text-sm text-muted-foreground mt-2 max-w-3xl">
                        {description}
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
              {actions && (
                <div className="flex items-center gap-2 ml-4">
                  {actions}
                </div>
              )}
            </div>
          </div>
        </div>
      )
    }

    const renderContent = () => {
      return (
        <div className={cn("flex-1", sidebar && "lg:flex")}>
          {sidebar && (
            <aside className="w-64 flex-shrink-0 hidden lg:block">
              {sidebar}
            </aside>
          )}
          
          <main className={cn(
            "flex-1",
            contentClassName,
            sidebar && "lg:ml-0"
          )}>
            {children}
          </main>
        </div>
      )
    }

    const renderFooter = () => {
      if (!footer) return null

      return (
        <footer className="border-t border-border bg-background mt-auto">
          <div className="container mx-auto px-4 py-6">
            {footer}
          </div>
        </footer>
      )
    }

    return (
      <div
        ref={ref}
        className={cn(pageLayoutVariants({ variant, padding }), className)}
        {...props}
      >
        {renderHeader()}
        {renderContent()}
        {renderFooter()}
      </div>
    )
  }
)
PageLayout.displayName = "PageLayout"

const PageLayoutHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    title?: string
    subtitle?: string
    description?: string
    breadcrumb?: React.ReactNode | BreadcrumbProps
    actions?: React.ReactNode
    backHref?: string
    backLabel?: string
  }
>(({ 
  className, 
  title, 
  subtitle, 
  description, 
  breadcrumb, 
  actions, 
  backHref, 
  backLabel = "返回",
  ...props 
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn("border-b border-border bg-background", className)}
      {...props}
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            {breadcrumb && (
              <div className="mb-4">
                {React.isValidElement(breadcrumb) ? (
                  breadcrumb
                ) : (
                  <Breadcrumb {...(breadcrumb as BreadcrumbProps)} />
                )}
              </div>
            )}
            
            <div className="flex items-center gap-4">
              {backHref && (
                <a
                  href={backHref}
                  className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-4 w-4"
                  >
                    <path d="M19 12H5M12 19l-7-7 7-7" />
                  </svg>
                  {backLabel}
                </a>
              )}
              
              <div>
                {title && (
                  <h1 className="text-2xl font-bold tracking-tight">
                    {title}
                  </h1>
                )}
                {subtitle && (
                  <p className="text-lg text-muted-foreground mt-1">
                    {subtitle}
                  </p>
                )}
                {description && (
                  <p className="text-sm text-muted-foreground mt-2 max-w-3xl">
                    {description}
                  </p>
                )}
              </div>
            </div>
          </div>
          
          {actions && (
            <div className="flex items-center gap-2 ml-4">
              {actions}
            </div>
          )}
        </div>
      </div>
    </div>
  )
})
PageLayoutHeader.displayName = "PageLayoutHeader"

const PageLayoutContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    sidebar?: React.ReactNode
  }
>(({ className, sidebar, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn("flex-1", sidebar && "lg:flex", className)}
      {...props}
    >
      {sidebar && (
        <aside className="w-64 flex-shrink-0 hidden lg:block">
          {sidebar}
        </aside>
      )}
      
      <main className={cn(
        "flex-1",
        sidebar && "lg:ml-0"
      )}>
        {props.children}
      </main>
    </div>
  )
})
PageLayoutContent.displayName = "PageLayoutContent"

const PageLayoutSidebar = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <aside
    ref={ref}
    className={cn("w-64 flex-shrink-0 hidden lg:block", className)}
    {...props}
  />
))
PageLayoutSidebar.displayName = "PageLayoutSidebar"

const PageLayoutFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <footer
    ref={ref}
    className={cn("border-t border-border bg-background mt-auto", className)}
    {...props}
  >
    <div className="container mx-auto px-4 py-6">
      {props.children}
    </div>
  </footer>
))
PageLayoutFooter.displayName = "PageLayoutFooter"

export {
  PageLayout,
  PageLayoutHeader,
  PageLayoutContent,
  PageLayoutSidebar,
  PageLayoutFooter,
  pageLayoutVariants,
}