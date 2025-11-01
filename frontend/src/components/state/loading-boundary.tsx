"use client"

import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Loader2 } from "lucide-react"
import { cn } from "@/utils"
import { Loading, type LoadingProps } from "@/components/ui/loading"

const loadingBoundaryVariants = cva(
  "flex items-center justify-center min-h-[200px] p-6",
  {
    variants: {
      variant: {
        default: "",
        overlay: "fixed inset-0 z-50 bg-background/80 backdrop-blur-sm",
        inline: "min-h-[100px]",
        minimal: "min-h-[50px]",
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

const loadingContentVariants = cva(
  "flex flex-col items-center justify-center gap-4",
  {
    variants: {
      variant: {
        default: "",
        centered: "",
        minimal: "gap-2",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface LoadingBoundaryState {
  isLoading: boolean
  loadingText?: string
  loadingId?: string
  startTime?: number
  delay?: number
  timeout?: number
  timedOut?: boolean
}

export interface LoadingBoundaryProps
  extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  isLoading?: boolean
  fallback?: React.ComponentType<LoadingBoundaryState>
  loadingText?: string
  delay?: number
  timeout?: number
  onTimeout?: () => void
  variant?: "default" | "spinner" | "skeleton" | "dots" | "progress"
  loadingProps?: Partial<LoadingProps>
  showProgress?: boolean
  progress?: number
  minDuration?: number
}

const initialState: LoadingBoundaryState = {
  isLoading: false,
  loadingText: undefined,
  loadingId: undefined,
  startTime: undefined,
  delay: 0,
  timeout: undefined,
  timedOut: false,
}

class LoadingBoundary extends React.Component<LoadingBoundaryProps, LoadingBoundaryState> {
  private timeoutId: NodeJS.Timeout | null = null
  private delayId: NodeJS.Timeout | null = null
  private minDurationId: NodeJS.Timeout | null = null
  private minDurationStartTime: number | null = null

  constructor(props: LoadingBoundaryProps) {
    super(props)
    this.state = initialState
  }

  static getDerivedStateFromProps(props: LoadingBoundaryProps): Partial<LoadingBoundaryState> {
    return {
      isLoading: props.isLoading || false,
      delay: props.delay || 0,
      timeout: props.timeout,
    }
  }

  componentDidMount() {
    if (this.state.isLoading) {
      this.startLoading()
    }
  }

  componentDidUpdate(prevProps: LoadingBoundaryProps, prevState: LoadingBoundaryState) {
    const { isLoading, delay, timeout, minDuration } = this.props
    const { isLoading: wasLoading } = prevState

    // Handle loading state changes
    if (isLoading !== wasLoading) {
      if (isLoading) {
        this.startLoading()
      } else {
        this.stopLoading()
      }
    }

    // Handle delay changes
    if (delay !== prevState.delay) {
      this.setState({ delay })
    }

    // Handle timeout changes
    if (timeout !== prevState.timeout) {
      this.setState({ timeout })
    }
  }

  componentWillUnmount() {
    this.clearAllTimeouts()
  }

  startLoading = () => {
    const { delay, timeout, minDuration } = this.props
    const loadingId = Math.random().toString(36).substring(2, 9)
    const startTime = Date.now()

    this.clearAllTimeouts()

    // Set minimum duration if specified
    if (minDuration) {
      this.minDurationStartTime = startTime
      this.minDurationId = setTimeout(() => {
        this.minDurationStartTime = null
      }, minDuration)
    }

    // Handle delay
    if (delay && delay > 0) {
      this.delayId = setTimeout(() => {
        this.setState({
          isLoading: true,
          loadingId,
          startTime,
        })
        this.setupTimeout(timeout)
      }, delay)
    } else {
      this.setState({
        isLoading: true,
        loadingId,
        startTime,
      })
      this.setupTimeout(timeout)
    }
  }

  stopLoading = () => {
    this.clearAllTimeouts()

    // Check if we need to wait for minimum duration
    if (this.minDurationStartTime) {
      const elapsed = Date.now() - this.minDurationStartTime
      const { minDuration } = this.props
      
      if (minDuration && elapsed < minDuration) {
        // Wait for the remaining time
        this.timeoutId = setTimeout(() => {
          this.setState({
            isLoading: false,
            loadingId: undefined,
            startTime: undefined,
            timedOut: false,
          })
        }, minDuration - elapsed)
        return
      }
    }

    this.setState({
      isLoading: false,
      loadingId: undefined,
      startTime: undefined,
      timedOut: false,
    })
  }

  setupTimeout = (timeout?: number) => {
    if (timeout && timeout > 0) {
      this.timeoutId = setTimeout(() => {
        this.setState({ timedOut: true })
        this.props.onTimeout?.()
      }, timeout)
    }
  }

  clearAllTimeouts = () => {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
      this.timeoutId = null
    }

    if (this.delayId) {
      clearTimeout(this.delayId)
      this.delayId = null
    }

    if (this.minDurationId) {
      clearTimeout(this.minDurationId)
      this.minDurationId = null
    }
  }

  render() {
    const { 
      children, 
      fallback, 
      loadingText, 
      variant = "default",
      loadingProps = {},
      showProgress = false,
      progress = 0,
      minDuration,
      ...props 
    } = this.props

    const { isLoading, timedOut, startTime } = this.state

    // Custom fallback component
    if (isLoading && fallback) {
      const FallbackComponent = fallback
      return (
        <div className={cn(loadingBoundaryVariants({ variant: variant as any }), props.className)}>
          <FallbackComponent
            isLoading
            loadingText={loadingText || this.state.loadingText}
            loadingId={this.state.loadingId}
            startTime={startTime}
            delay={this.state.delay}
            timeout={this.state.timeout}
            timedOut={timedOut}
          />
        </div>
      )
    }

    // Default loading UI
    if (isLoading) {
      const actualLoadingText = loadingText || this.state.loadingText || "加载中..."
      const elapsed = startTime ? Date.now() - startTime : 0

      return (
        <div className={cn(loadingBoundaryVariants({ variant: variant as any }), props.className)}>
          <div className={cn(loadingContentVariants({ variant: variant as any }))}>
            {variant === "spinner" && (
              <Loading
                {...loadingProps}
                text={actualLoadingText}
                variant="default"
              />
            )}
            
            {variant === "skeleton" && (
              <div className="w-full space-y-3">
                <div className="h-4 w-full bg-muted rounded animate-pulse" />
                <div className="h-4 w-3/4 bg-muted rounded animate-pulse" />
                <div className="h-4 w-1/2 bg-muted rounded animate-pulse" />
              </div>
            )}
            
            {variant === "dots" && (
              <Loading
                {...loadingProps}
                text={actualLoadingText}
                variant="default"
              />
            )}
            
            {variant === "progress" && (
              <div className="w-full max-w-md space-y-3">
                <Loading
                  {...loadingProps}
                  text={actualLoadingText}
                  variant="default"
                  {...(showProgress ? { value: progress } : {})}
                />
                {showProgress && (
                  <div className="text-xs text-muted-foreground">
                    {Math.round(progress)}% · {elapsed > 0 ? `${Math.round(elapsed / 1000)}秒` : ""}
                  </div>
                )}
              </div>
            )}
            
            {variant === "default" && (
              <>
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
                <span className="text-sm text-muted-foreground">
                  {actualLoadingText}
                </span>
                {timedOut && (
                  <div className="text-xs text-destructive mt-2">
                    加载超时，请重试
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )
    }

    return children
  }
}

const LoadingBoundaryFallback = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    text?: string
    variant?: "default" | "spinner" | "skeleton" | "dots" | "progress"
    loadingProps?: Partial<LoadingProps>
  }
>(({ 
  className, 
  text = "加载中...", 
  variant = "default",
  loadingProps = {},
  ...props 
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn(loadingBoundaryVariants(), className)}
      {...props}
    >
      <div className={cn(loadingContentVariants())}>
        {variant === "spinner" && (
          <Loading
            {...loadingProps}
            text={text}
            variant="default"
          />
        )}
        
        {variant === "skeleton" && (
          <div className="w-full space-y-3">
            <div className="h-4 w-full bg-muted rounded animate-pulse" />
            <div className="h-4 w-3/4 bg-muted rounded animate-pulse" />
            <div className="h-4 w-1/2 bg-muted rounded animate-pulse" />
          </div>
        )}
        
        {variant === "dots" && (
          <Loading
            {...loadingProps}
            text={text}
            variant="default"
          />
        )}
        
        {variant === "progress" && (
          <Loading
            {...loadingProps}
            text={text}
            variant="default"
          />
        )}
        
        {variant === "default" && (
          <>
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
            <span className="text-sm text-muted-foreground">
              {text}
            </span>
          </>
        )}
      </div>
    </div>
  )
})
LoadingBoundaryFallback.displayName = "LoadingBoundaryFallback"

const LoadingBoundaryMinimal = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    text?: string
  }
>(({ 
  className, 
  text = "加载中...", 
  ...props 
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn(loadingBoundaryVariants({ variant: "minimal" }), className)}
      {...props}
    >
      <div className={cn(loadingContentVariants({ variant: "minimal" }))}>
        <Loader2 className="h-4 w-4 animate-spin text-primary" />
        <span className="text-xs text-muted-foreground">
          {text}
        </span>
      </div>
    </div>
  )
})
LoadingBoundaryMinimal.displayName = "LoadingBoundaryMinimal"

export {
  LoadingBoundary,
  LoadingBoundaryFallback,
  LoadingBoundaryMinimal,
  loadingBoundaryVariants,
  loadingContentVariants,
}