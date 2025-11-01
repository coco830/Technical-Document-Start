"use client"

import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from "lucide-react"
import { cn } from "@/utils"

const toastVariants = cva(
  "group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full",
  {
    variants: {
      variant: {
        default: "border bg-background text-foreground",
        destructive:
          "destructive border-destructive bg-destructive text-destructive-foreground",
        success: "border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-900/20 dark:text-green-200",
        warning: "border-yellow-200 bg-yellow-50 text-yellow-800 dark:border-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200",
        info: "border-blue-200 bg-blue-50 text-blue-800 dark:border-blue-800 dark:bg-blue-900/20 dark:text-blue-200",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

const toastActionVariants = cva(
  "inline-flex h-8 shrink-0 items-center justify-center rounded-md border bg-transparent px-3 text-sm font-medium ring-offset-background transition-colors hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 group-[.destructive]:border-muted/40 group-[.destructive]:hover:border-destructive/30 group-[.destructive]:hover:bg-destructive group-[.destructive]:hover:text-destructive-foreground group-[.destructive]:focus:ring-destructive"
)

const toastCloseVariants = cva(
  "absolute right-2 top-2 rounded-md p-1 text-foreground/50 opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100 group-[.destructive]:text-red-300 group-[.destructive]:hover:text-red-50 group-[.destructive]:focus:ring-red-400 group-[.destructive]:focus:ring-offset-red-600"
)

export interface ToastProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof toastVariants> {
  title?: string
  description?: string
  action?: React.ReactNode
  actionAltText?: string
  duration?: number
  onOpenChange?: (open: boolean) => void
  showIcon?: boolean
  icon?: React.ReactNode
  closable?: boolean
  position?: "top-left" | "top-right" | "bottom-left" | "bottom-right" | "top-center" | "bottom-center"
}

const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({
    className,
    variant,
    title,
    description,
    action,
    actionAltText = "操作",
    duration = 5000,
    onOpenChange,
    showIcon = true,
    icon,
    closable = true,
    position = "bottom-right",
    ...props
  }, ref) => {
    const [open, setOpen] = React.useState(true)
    const timerRef = React.useRef<NodeJS.Timeout>()

    React.useEffect(() => {
      if (duration > 0) {
        timerRef.current = setTimeout(() => {
          setOpen(false)
        }, duration)
      }

      return () => {
        if (timerRef.current) {
          clearTimeout(timerRef.current)
        }
      }
    }, [duration])

    React.useEffect(() => {
      onOpenChange?.(open)
    }, [open, onOpenChange])

    const handleClose = () => {
      setOpen(false)
    }

    const getIcon = () => {
      if (icon) return icon
      
      switch (variant) {
        case "success":
          return <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />
        case "destructive":
          return <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
        case "warning":
          return <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
        case "info":
          return <Info className="h-5 w-5 text-blue-600 dark:text-blue-400" />
        default:
          return null
      }
    }

    if (!open) return null

    return (
      <div
        ref={ref}
        className={cn(toastVariants({ variant }), className)}
        {...props}
      >
        <div className="grid gap-1">
          {title && (
            <div className="flex items-center gap-2">
              {showIcon && getIcon()}
              <div className="text-sm font-semibold">{title}</div>
            </div>
          )}
          {description && (
            <div className={cn("text-sm opacity-90", title && "ml-7")}>
              {description}
            </div>
          )}
        </div>
        {action && (
          <div className={toastActionVariants()}>{action}</div>
        )}
        {closable && (
          <button
            className={toastCloseVariants()}
            onClick={handleClose}
            aria-label="关闭"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    )
  }
)
Toast.displayName = "Toast"

const ToastProvider = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>
}

const ToastViewport = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    position?: "top-left" | "top-right" | "bottom-left" | "bottom-right" | "top-center" | "bottom-center"
  }
>(({ className, position = "bottom-right", ...props }, ref) => {
  const getPositionClasses = () => {
    switch (position) {
      case "top-left":
        return "fixed top-0 left-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:top-auto sm:right-auto sm:flex-col md:max-w-[420px]"
      case "top-right":
        return "fixed top-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:top-auto sm:flex-col md:max-w-[420px]"
      case "bottom-left":
        return "fixed bottom-0 left-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:left-0 sm:top-auto sm:flex-col md:max-w-[420px]"
      case "bottom-right":
        return "fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:top-auto sm:flex-col md:max-w-[420px]"
      case "top-center":
        return "fixed top-0 left-1/2 z-[100] flex max-h-screen w-full -translate-x-1/2 flex-col-reverse p-4 sm:top-auto sm:flex-col md:max-w-[420px]"
      case "bottom-center":
        return "fixed bottom-0 left-1/2 z-[100] flex max-h-screen w-full -translate-x-1/2 flex-col-reverse p-4 sm:top-auto sm:flex-col md:max-w-[420px]"
      default:
        return "fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:top-auto sm:flex-col md:max-w-[420px]"
    }
  }

  return (
    <div
      ref={ref}
      className={cn(getPositionClasses(), className)}
      {...props}
    />
  )
})
ToastViewport.displayName = "ToastViewport"

const ToastTitle = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm font-semibold", className)}
    {...props}
  />
))
ToastTitle.displayName = "ToastTitle"

const ToastDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm opacity-90", className)}
    {...props}
  />
))
ToastDescription.displayName = "ToastDescription"

const ToastAction = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) => (
  <button
    ref={ref}
    className={cn(toastActionVariants(), className)}
    {...props}
  />
))
ToastAction.displayName = "ToastAction"

const ToastClose = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) => (
  <button
    ref={ref}
    className={cn(toastCloseVariants(), className)}
    {...props}
  />
))
ToastClose.displayName = "ToastClose"

// Toast context for managing toasts
interface ToastContextType {
  toasts: ToastProps[]
  addToast: (toast: Omit<ToastProps, "id">) => void
  removeToast: (id: string) => void
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined)

export const useToast = () => {
  const context = React.useContext(ToastContext)
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider")
  }
  return context
}

export const ToastContainer: React.FC<{ position?: ToastProps["position"] }> = ({ position }) => {
  const { toasts, removeToast } = useToast()

  return (
    <ToastViewport position={position}>
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          {...toast}
          onOpenChange={(open) => {
            if (!open) {
              removeToast(toast.id!)
            }
          }}
        />
      ))}
    </ToastViewport>
  )
}

export const ToastProviderWithContainer: React.FC<{
  children: React.ReactNode
  position?: ToastProps["position"]
}> = ({ children, position }) => {
  const [toasts, setToasts] = React.useState<ToastProps[]>([])

  const addToast = React.useCallback((toast: Omit<ToastProps, "id">) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { ...toast, id }])
  }, [])

  const removeToast = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer position={position} />
    </ToastContext.Provider>
  )
}

export {
  Toast,
  ToastProvider,
  ToastViewport,
  ToastTitle,
  ToastDescription,
  ToastAction,
  ToastClose,
  toastVariants,
  toastActionVariants,
  toastCloseVariants,
}