import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils"
import { Navbar, type NavbarProps } from "@/components/navigation"
import { Sidebar, type SidebarProps } from "@/components/navigation"
import { MobileNav, type MobileNavProps } from "@/components/navigation"
import { ToastProviderWithContainer } from "@/components/ui/toast"
import { ThemeProvider } from "@/components/theme"
import { PerformanceMonitor } from "@/components/performance/performance-monitor"

const appLayoutVariants = cva(
  "min-h-screen bg-background",
  {
    variants: {
      variant: {
        default: "",
        fluid: "",
        contained: "container mx-auto",
        centered: "flex items-center justify-center",
      },
      sidebar: {
        none: "",
        left: "",
        right: "",
        collapsible: "",
      },
    },
    defaultVariants: {
      variant: "default",
      sidebar: "none",
    },
  }
)

export interface AppLayoutProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof appLayoutVariants> {
  navbar?: React.ReactNode | NavbarProps
  sidebar?: React.ReactNode | SidebarProps
  mobileNav?: React.ReactNode | MobileNavProps
  children: React.ReactNode
  showNavbar?: boolean
  showSidebar?: boolean
  showMobileNav?: boolean
  sidebarPosition?: "left" | "right"
  sidebarCollapsed?: boolean
  onSidebarCollapseChange?: (collapsed: boolean) => void
  mobileNavOpen?: boolean
  onMobileNavToggle?: (open: boolean) => void
  themeProvider?: boolean
  toastProvider?: boolean
  performanceMonitor?: boolean
  className?: string
}

const AppLayout = React.forwardRef<HTMLDivElement, AppLayoutProps>(
  (props, ref) => {
    const {
      className,
      variant,
      sidebar,
      sidebarPosition = "left",
      sidebarCollapsed = false,
      onSidebarCollapseChange,
      mobileNavOpen = false,
      onMobileNavToggle,
      showNavbar = true,
      showSidebar = true,
      showMobileNav = true,
      themeProvider = true,
      toastProvider = true,
      performanceMonitor = process.env.NODE_ENV === "production" || process.env.NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING === "true",
      navbar: navbarProps,
      sidebar: sidebarProps,
      mobileNav: mobileNavProps,
      children,
      ...layoutProps
    } = props

    const [isMobile, setIsMobile] = React.useState(false)
    const [localSidebarCollapsed, setLocalSidebarCollapsed] = React.useState(sidebarCollapsed)
    const [localMobileNavOpen, setLocalMobileNavOpen] = React.useState(mobileNavOpen)

    // Detect mobile screen size
    React.useEffect(() => {
      const checkMobile = () => {
        setIsMobile(window.innerWidth < 768)
      }

      checkMobile()
      window.addEventListener("resize", checkMobile)
      return () => window.removeEventListener("resize", checkMobile)
    }, [])

    // Handle sidebar collapse state
    React.useEffect(() => {
      setLocalSidebarCollapsed(sidebarCollapsed)
    }, [sidebarCollapsed])

    // Handle mobile nav state
    React.useEffect(() => {
      setLocalMobileNavOpen(mobileNavOpen)
    }, [mobileNavOpen])

    const handleSidebarCollapseChange = (collapsed: boolean) => {
      setLocalSidebarCollapsed(collapsed)
      onSidebarCollapseChange?.(collapsed)
    }

    const handleMobileNavToggle = (open: boolean) => {
      setLocalMobileNavOpen(open)
      onMobileNavToggle?.(open)
    }

    // Render navbar
    const renderNavbar = () => {
      if (!showNavbar) return null

      if (React.isValidElement(navbarProps)) {
        return React.cloneElement(navbarProps, {
          mobileOpen: localMobileNavOpen,
          onMobileClose: () => handleMobileNavToggle(false),
        } as any)
      }

      return (
        <Navbar
          {...(navbarProps as NavbarProps)}
          mobileOpen={localMobileNavOpen}
          onMobileClose={() => handleMobileNavToggle(false)}
        />
      )
    }

    // Render sidebar
    const renderSidebar = () => {
      if (!showSidebar || isMobile) return null

      if (React.isValidElement(sidebarProps)) {
        return React.cloneElement(sidebarProps, {
          collapsed: localSidebarCollapsed,
          onCollapseChange: handleSidebarCollapseChange,
        } as any)
      }

      return (
        <Sidebar
          {...(sidebarProps as SidebarProps)}
          collapsed={localSidebarCollapsed}
          onCollapseChange={handleSidebarCollapseChange}
        />
      )
    }

    // Render mobile nav
    const renderMobileNav = () => {
      if (!showMobileNav || !isMobile) return null

      if (React.isValidElement(mobileNavProps)) {
        return React.cloneElement(mobileNavProps, {
          isOpen: localMobileNavOpen,
          onClose: () => handleMobileNavToggle(false),
        } as any)
      }

      return (
        <MobileNav
          {...(mobileNavProps as MobileNavProps)}
          isOpen={localMobileNavOpen}
          onClose={() => handleMobileNavToggle(false)}
        />
      )
    }

    const layoutContent = (
      <>
        {renderNavbar()}
        
        <div className={cn("flex flex-1", sidebarPosition === "right" && "flex-row-reverse")}>
          {renderSidebar()}
          
          <main className={cn(
            "flex-1 overflow-auto",
            showSidebar && !isMobile && "md:ml-0",
            sidebarPosition === "right" && "md:mr-0"
          )}>
            {children}
          </main>
        </div>
        
        {renderMobileNav()}
      </>
    )

    // Wrap with theme provider if enabled
    if (themeProvider) {
      return (
        <ThemeProvider>
          {toastProvider ? (
            <ToastProviderWithContainer>
              <div
                ref={ref}
                className={cn(
                  appLayoutVariants({ variant, sidebar: showSidebar ? sidebarPosition : "none" }),
                  className
                )}
                {...layoutProps}
              >
                {layoutContent}
              </div>
              {performanceMonitor && <PerformanceMonitor />}
            </ToastProviderWithContainer>
          ) : (
            <div
              ref={ref}
              className={cn(
                appLayoutVariants({ variant, sidebar: showSidebar ? sidebarPosition : "none" }),
                className
              )}
              {...layoutProps}
            >
              {layoutContent}
              {performanceMonitor && <PerformanceMonitor />}
            </div>
          )}
        </ThemeProvider>
      )
    }

    // Wrap with toast provider if enabled
    if (toastProvider) {
      return (
        <ToastProviderWithContainer>
          <div
            ref={ref}
            className={cn(
              appLayoutVariants({ variant, sidebar: showSidebar ? sidebarPosition : "none" }),
              className
            )}
            {...layoutProps}
          >
            {layoutContent}
            {performanceMonitor && <PerformanceMonitor />}
          </div>
        </ToastProviderWithContainer>
      )
    }

    // Default layout without providers
    return (
      <div
        ref={ref}
        className={cn(
          appLayoutVariants({ variant, sidebar: showSidebar ? sidebarPosition : "none" }),
          className
        )}
        {...layoutProps}
      >
        {layoutContent}
        {performanceMonitor && <PerformanceMonitor />}
      </div>
    )
  }
)
AppLayout.displayName = "AppLayout"

const AppLayoutHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("sticky top-0 z-40", className)}
    {...props}
  />
))
AppLayoutHeader.displayName = "AppLayoutHeader"

const AppLayoutSidebar = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    position?: "left" | "right"
    collapsed?: boolean
  }
>(({ className, position = "left", collapsed = false, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "hidden md:block",
      position === "left" ? "order-first" : "order-last",
      collapsed && "md:w-16",
      className
    )}
    {...props}
  />
))
AppLayoutSidebar.displayName = "AppLayoutSidebar"

const AppLayoutContent = React.forwardRef<
  HTMLMainElement,
  React.HTMLAttributes<HTMLMainElement> & {
    sidebarPosition?: "left" | "right"
    hasSidebar?: boolean
  }
>(({ className, sidebarPosition = "left", hasSidebar = false, ...props }, ref) => (
  <main
    ref={ref}
    className={cn(
      "flex-1 overflow-auto",
      hasSidebar && "md:ml-0",
      sidebarPosition === "right" && "md:mr-0",
      className
    )}
    {...props}
  />
))
AppLayoutContent.displayName = "AppLayoutContent"

const AppLayoutFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("mt-auto", className)}
    {...props}
  />
))
AppLayoutFooter.displayName = "AppLayoutFooter"

export {
  AppLayout,
  AppLayoutHeader,
  AppLayoutSidebar,
  AppLayoutContent,
  AppLayoutFooter,
  appLayoutVariants,
}