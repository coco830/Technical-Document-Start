"use client"

import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { AlertTriangle, RefreshCw, Home } from "lucide-react"
import { cn } from "@/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const errorBoundaryVariants = cva(
  "flex items-center justify-center min-h-[400px] p-6",
  {
    variants: {
      variant: {
        default: "",
        minimal: "min-h-[200px] p-4",
        full: "min-h-screen",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

const errorCardVariants = cva(
  "w-full max-w-md",
  {
    variants: {
      variant: {
        default: "",
        destructive: "border-destructive",
        warning: "border-yellow-600 dark:border-yellow-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
  errorInfo?: React.ErrorInfo
  errorId?: string
  retryCount?: number
}

export interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<{ error: Error; errorInfo: React.ErrorInfo; resetError: () => void }>
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
  onReset?: () => void
  showRetry?: boolean
  showHome?: boolean
  resetButtonText?: string
  homeButtonText?: string
  homeHref?: string
  variant?: "default" | "destructive" | "warning"
  title?: string
  description?: string
  className?: string
}

const initialState: ErrorBoundaryState = {
  hasError: false,
  error: undefined,
  errorInfo: undefined,
  errorId: undefined,
  retryCount: 0,
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = initialState
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      errorId: Math.random().toString(36).substring(2, 9),
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ errorInfo })
    this.props.onError?.(error, errorInfo)
    
    // Log error to console in development
    if (process.env.NODE_ENV === "development") {
      console.error("ErrorBoundary caught an error:", error, errorInfo)
    }
  }

  resetError = () => {
    this.setState({
      ...initialState,
      retryCount: (this.state.retryCount || 0) + 1,
    })
    this.props.onReset?.()
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback component
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback
        return (
          <div className={cn(errorBoundaryVariants({ variant: this.props.variant as any }), this.props.className)}>
            <FallbackComponent
              error={this.state.error!}
              errorInfo={this.state.errorInfo!}
              resetError={this.resetError}
            />
          </div>
        )
      }

      // Default fallback UI
      const errorVariant = this.props.variant || "default"
      const title = this.props.title || "出现错误"
      const description = this.props.description || "抱歉，应用程序遇到了一个错误。"
      
      return (
        <div className={cn(errorBoundaryVariants({ variant: this.props.variant as any }), this.props.className)}>
          <Card className={cn(errorCardVariants({ variant: errorVariant }))}>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                {title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                {description}
              </p>
              
              {process.env.NODE_ENV === "development" && this.state.error && (
                <details className="mt-4">
                  <summary className="cursor-pointer text-sm font-medium">
                    错误详情 (仅开发环境可见)
                  </summary>
                  <div className="mt-2 p-3 bg-muted rounded-md text-xs overflow-auto">
                    <div className="mb-2">
                      <strong>错误ID:</strong> {this.state.errorId}
                    </div>
                    <div className="mb-2">
                      <strong>重试次数:</strong> {this.state.retryCount}
                    </div>
                    <div className="mb-2">
                      <strong>错误消息:</strong>
                      <pre className="mt-1 whitespace-pre-wrap">
                        {this.state.error.toString()}
                      </pre>
                    </div>
                    {this.state.errorInfo && (
                      <div>
                        <strong>组件堆栈:</strong>
                        <pre className="mt-1 whitespace-pre-wrap">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}
              
              <div className="flex flex-col gap-2 pt-2">
                {this.props.showRetry !== false && (
                  <Button
                    onClick={this.resetError}
                    className="w-full"
                    variant={errorVariant === "destructive" ? "default" : (errorVariant as any)}
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    {this.props.resetButtonText || "重试"}
                  </Button>
                )}
                
                {this.props.showHome && (
                  <Button
                    variant="outline"
                    className="w-full"
                    asChild
                  >
                    <a href={this.props.homeHref || "/"}>
                      <Home className="mr-2 h-4 w-4" />
                      {this.props.homeButtonText || "返回首页"}
                    </a>
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

const ErrorBoundaryFallback = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    title?: string
    description?: string
    variant?: "default" | "destructive" | "warning"
    showRetry?: boolean
    showHome?: boolean
    resetButtonText?: string
    homeButtonText?: string
    homeHref?: string
    onRetry?: () => void
  }
>(({ 
  className, 
  title = "出现错误", 
  description = "抱歉，应用程序遇到了一个错误。",
  variant = "default",
  showRetry = true,
  showHome = true,
  resetButtonText = "重试",
  homeButtonText = "返回首页",
  homeHref = "/",
  onRetry,
  ...props 
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn(errorBoundaryVariants(), className)}
      {...props}
    >
      <Card className={cn(errorCardVariants({ variant }))}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            {description}
          </p>
          
          <div className="flex flex-col gap-2 pt-2">
            {showRetry && (
              <Button
                onClick={onRetry}
                className="w-full"
                variant={variant === "destructive" ? "default" : (variant as any)}
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                {resetButtonText}
              </Button>
            )}
            
            {showHome && (
              <Button
                variant="outline"
                className="w-full"
                asChild
              >
                <a href={homeHref}>
                  <Home className="mr-2 h-4 w-4" />
                  {homeButtonText}
                </a>
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
})
ErrorBoundaryFallback.displayName = "ErrorBoundaryFallback"

const ErrorBoundaryMinimal = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    title?: string
    description?: string
    onRetry?: () => void
  }
>(({ 
  className, 
  title = "出现错误", 
  description = "抱歉，应用程序遇到了一个错误。",
  onRetry,
  ...props 
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn(errorBoundaryVariants({ variant: "minimal" }), className)}
      {...props}
    >
      <div className="text-center space-y-4">
        <AlertTriangle className="mx-auto h-12 w-12 text-destructive" />
        <h3 className="text-lg font-medium">{title}</h3>
        <p className="text-muted-foreground max-w-md">{description}</p>
        {onRetry && (
          <Button onClick={onRetry} variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            重试
          </Button>
        )}
      </div>
    </div>
  )
})
ErrorBoundaryMinimal.displayName = "ErrorBoundaryMinimal"

export {
  ErrorBoundary,
  ErrorBoundaryFallback,
  ErrorBoundaryMinimal,
  errorBoundaryVariants,
  errorCardVariants,
}