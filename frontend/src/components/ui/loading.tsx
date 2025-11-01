"use client"

import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Loader2 } from "lucide-react"
import { cn } from "@/utils"

const loadingVariants = cva(
  "inline-flex items-center justify-center",
  {
    variants: {
      size: {
        sm: "h-4 w-4",
        default: "h-6 w-6",
        lg: "h-8 w-8",
        xl: "h-12 w-12",
      },
      variant: {
        default: "text-primary",
        destructive: "text-destructive",
        muted: "text-muted-foreground",
        secondary: "text-secondary-foreground",
        success: "text-green-600 dark:text-green-400",
        warning: "text-yellow-600 dark:text-yellow-400",
        info: "text-blue-600 dark:text-blue-400",
      },
    },
    defaultVariants: {
      size: "default",
      variant: "default",
    },
  }
)

const loadingContainerVariants = cva(
  "flex items-center justify-center",
  {
    variants: {
      layout: {
        inline: "inline-flex",
        block: "flex",
        fullscreen: "fixed inset-0 z-50 bg-background/80 backdrop-blur-sm",
        overlay: "absolute inset-0 z-50 bg-background/80 backdrop-blur-sm",
        centered: "min-h-[200px] flex",
      },
      spacing: {
        none: "",
        sm: "gap-2",
        default: "gap-3",
        lg: "gap-4",
      },
    },
    defaultVariants: {
      layout: "inline",
      spacing: "default",
    },
  }
)

export interface LoadingProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof loadingVariants> {
  text?: string
  showText?: boolean
  layout?: VariantProps<typeof loadingContainerVariants>["layout"]
  spacing?: VariantProps<typeof loadingContainerVariants>["spacing"]
  overlay?: boolean
  fullscreen?: boolean
  centered?: boolean
}

const Loading = React.forwardRef<HTMLDivElement, LoadingProps>(
  ({
    className,
    size,
    variant,
    text,
    showText = true,
    layout,
    spacing,
    overlay,
    fullscreen,
    centered,
    children,
    ...props
  }, ref) => {
    // Handle deprecated props
    const actualLayout = React.useMemo(() => {
      if (fullscreen) return "fullscreen"
      if (overlay) return "overlay"
      if (centered) return "centered"
      return layout || "inline"
    }, [fullscreen, overlay, centered, layout])

    const actualSpacing = spacing || (text ? "default" : "none")

    return (
      <div
        ref={ref}
        className={cn(
          loadingContainerVariants({ layout: actualLayout, spacing: actualSpacing }),
          className
        )}
        {...props}
      >
        <Loader2
          className={cn(
            loadingVariants({ size, variant }),
            "animate-spin"
          )}
        />
        {(text || children) && showText && (
          <div className="flex flex-col items-center gap-1">
            {text && (
              <span className="text-sm text-muted-foreground animate-pulse">
                {text}
              </span>
            )}
            {children}
          </div>
        )}
      </div>
    )
  }
)
Loading.displayName = "Loading"

const LoadingSpinner = React.forwardRef<
  HTMLDivElement,
  Omit<LoadingProps, "text" | "showText" | "layout" | "spacing">
>(({ className, size = "default", variant = "default", ...props }, ref) => (
  <div
    ref={ref}
    className={cn(loadingVariants({ size, variant }), "animate-spin", className)}
    {...props}
  >
    <Loader2 className="h-full w-full" />
  </div>
))
LoadingSpinner.displayName = "LoadingSpinner"

const LoadingDots = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    size?: VariantProps<typeof loadingVariants>["size"]
    variant?: VariantProps<typeof loadingVariants>["variant"]
  }
>(({ className, size = "default", variant = "default", ...props }, ref) => {
  const dotSize = React.useMemo(() => {
    switch (size) {
      case "sm":
        return "h-1 w-1"
      case "default":
        return "h-2 w-2"
      case "lg":
        return "h-3 w-3"
      case "xl":
        return "h-4 w-4"
      default:
        return "h-2 w-2"
    }
  }, [size])

  return (
    <div
      ref={ref}
      className={cn("flex items-center gap-1", className)}
      {...props}
    >
      {[0, 1, 2].map((index) => (
        <div
          key={index}
          className={cn(
            dotSize,
            "rounded-full",
            loadingVariants({ variant }),
            "animate-bounce"
          )}
          style={{
            animationDelay: `${index * 0.1}s`,
            animationDuration: "1.4s",
          }}
        />
      ))}
    </div>
  )
})
LoadingDots.displayName = "LoadingDots"

const LoadingBar = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    variant?: VariantProps<typeof loadingVariants>["variant"]
    height?: "sm" | "default" | "lg"
    progress?: number
  }
>(({ className, variant = "default", height = "default", progress, ...props }, ref) => {
  const heightClass = React.useMemo(() => {
    switch (height) {
      case "sm":
        return "h-1"
      case "default":
        return "h-2"
      case "lg":
        return "h-3"
      default:
        return "h-2"
    }
  }, [height])

  return (
    <div
      ref={ref}
      className={cn(
        "w-full overflow-hidden rounded-full bg-muted",
        heightClass,
        className
      )}
      {...props}
    >
      <div
        className={cn(
          "h-full rounded-full bg-primary transition-all duration-300 ease-out",
          loadingVariants({ variant })
        )}
        style={{
          width: progress !== undefined ? `${progress}%` : "100%",
          animation: progress === undefined ? "loading-bar 1.5s ease-in-out infinite" : undefined,
        }}
      />
    </div>
  )
})
LoadingBar.displayName = "LoadingBar"

const LoadingSkeleton = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    width?: string | number
    height?: string | number
    variant?: "default" | "text" | "circular" | "rectangular"
    animation?: "pulse" | "wave" | "none"
  }
>(({ className, width, height, variant = "default", animation = "pulse", ...props }, ref) => {
  const variantClass = React.useMemo(() => {
    switch (variant) {
      case "text":
        return "h-4 rounded"
      case "circular":
        return "rounded-full"
      case "rectangular":
        return "rounded-md"
      default:
        return "rounded-md"
    }
  }, [variant])

  const animationClass = React.useMemo(() => {
    switch (animation) {
      case "pulse":
        return "animate-pulse"
      case "wave":
        return "animate-shimmer"
      case "none":
        return ""
      default:
        return "animate-pulse"
    }
  }, [animation])

  return (
    <div
      ref={ref}
      className={cn(
        "bg-muted",
        variantClass,
        animationClass,
        className
      )}
      style={{ width, height }}
      {...props}
    />
  )
})
LoadingSkeleton.displayName = "LoadingSkeleton"

const LoadingProgress = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    value: number
    max?: number
    showLabel?: boolean
    variant?: VariantProps<typeof loadingVariants>["variant"]
    size?: "sm" | "default" | "lg"
  }
>(({ className, value, max = 100, showLabel = true, variant = "default", size = "default", ...props }, ref) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  
  const sizeClass = React.useMemo(() => {
    switch (size) {
      case "sm":
        return "h-1"
      case "default":
        return "h-2"
      case "lg":
        return "h-3"
      default:
        return "h-2"
    }
  }, [size])

  return (
    <div className={cn("w-full space-y-2", className)} {...props}>
      {showLabel && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">进度</span>
          <span className="font-medium">{Math.round(percentage)}%</span>
        </div>
      )}
      <div
        ref={ref}
        className={cn(
          "w-full overflow-hidden rounded-full bg-muted",
          sizeClass
        )}
      >
        <div
          className={cn(
            "h-full rounded-full transition-all duration-300 ease-out",
            loadingVariants({ variant })
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
})
LoadingProgress.displayName = "LoadingProgress"

export {
  Loading,
  LoadingSpinner,
  LoadingDots,
  LoadingBar,
  LoadingSkeleton,
  LoadingProgress,
  loadingVariants,
  loadingContainerVariants,
}