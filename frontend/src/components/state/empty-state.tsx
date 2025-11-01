import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { 
  FileX, 
  Search, 
  Inbox, 
  Package, 
  Users, 
  FolderOpen, 
  Database,
  AlertCircle,
  Plus,
  RefreshCw
} from "lucide-react"
import { cn } from "@/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const emptyStateVariants = cva(
  "flex flex-col items-center justify-center p-8 text-center",
  {
    variants: {
      variant: {
        default: "",
        minimal: "p-4",
        compact: "p-6",
        card: "p-0",
      },
      size: {
        sm: "min-h-[200px]",
        default: "min-h-[300px]",
        lg: "min-h-[400px]",
        xl: "min-h-[500px]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const emptyStateIconVariants = cva(
  "text-muted-foreground",
  {
    variants: {
      variant: {
        default: "h-12 w-12",
        minimal: "h-8 w-8",
        compact: "h-10 w-10",
        card: "h-16 w-16",
      },
      color: {
        default: "text-muted-foreground",
        primary: "text-primary",
        secondary: "text-secondary-foreground",
        destructive: "text-destructive",
        warning: "text-yellow-600 dark:text-yellow-400",
      },
    },
    defaultVariants: {
      variant: "default",
      color: "default",
    },
  }
)

export interface EmptyStateProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof emptyStateVariants> {
  icon?: React.ReactNode
  title?: string
  description?: string
  action?: {
    label: string
    onClick: () => void
    variant?: "default" | "outline" | "secondary" | "ghost" | "destructive"
    icon?: React.ReactNode
  }
  secondaryAction?: {
    label: string
    onClick: () => void
    variant?: "default" | "outline" | "secondary" | "ghost" | "destructive"
    icon?: React.ReactNode
  }
  illustration?: React.ReactNode
  type?: "default" | "search" | "data" | "error" | "folder" | "users" | "package" | "inbox"
  className?: string
}

const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  ({
    className,
    variant,
    size,
    icon,
    title,
    description,
    action,
    secondaryAction,
    illustration,
    type = "default",
    ...props
  }, ref) => {
    // Get default icon based on type
    const getDefaultIcon = () => {
      switch (type) {
        case "search":
          return <Search className="h-12 w-12" />
        case "data":
          return <Database className="h-12 w-12" />
        case "error":
          return <AlertCircle className="h-12 w-12" />
        case "folder":
          return <FolderOpen className="h-12 w-12" />
        case "users":
          return <Users className="h-12 w-12" />
        case "package":
          return <Package className="h-12 w-12" />
        case "inbox":
          return <Inbox className="h-12 w-12" />
        default:
          return <FileX className="h-12 w-12" />
      }
    }

    const renderContent = () => {
      if (variant === "card") {
        return (
          <Card className="w-full max-w-md">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center justify-center">
                {icon || getDefaultIcon()}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-center">
              {title && (
                <h3 className="text-lg font-medium">
                  {title}
                </h3>
              )}
              {description && (
                <p className="text-muted-foreground">
                  {description}
                </p>
              )}
              {(action || secondaryAction) && (
                <div className="flex flex-col gap-2 pt-2">
                  {action && (
                    <Button
                      onClick={action.onClick}
                      variant={action.variant || "default"}
                      className="w-full"
                    >
                      {action.icon && <span className="mr-2">{action.icon}</span>}
                      {action.label}
                    </Button>
                  )}
                  {secondaryAction && (
                    <Button
                      onClick={secondaryAction.onClick}
                      variant={secondaryAction.variant || "outline"}
                      className="w-full"
                    >
                      {secondaryAction.icon && <span className="mr-2">{secondaryAction.icon}</span>}
                      {secondaryAction.label}
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )
      }

      return (
        <>
          {illustration || (
            <div className={cn(emptyStateIconVariants({ variant, color: "default" }))}>
              {icon || getDefaultIcon()}
            </div>
          )}
          
          {title && (
            <h3 className="mt-4 text-lg font-medium">
              {title}
            </h3>
          )}
          
          {description && (
            <p className="mt-2 text-muted-foreground max-w-md">
              {description}
            </p>
          )}
          
          {(action || secondaryAction) && (
            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              {action && (
                <Button
                  onClick={action.onClick}
                  variant={action.variant || "default"}
                  className="w-full sm:w-auto"
                >
                  {action.icon && <span className="mr-2">{action.icon}</span>}
                  {action.label}
                </Button>
              )}
              {secondaryAction && (
                <Button
                  onClick={secondaryAction.onClick}
                  variant={secondaryAction.variant || "outline"}
                  className="w-full sm:w-auto"
                >
                  {secondaryAction.icon && <span className="mr-2">{secondaryAction.icon}</span>}
                  {secondaryAction.label}
                </Button>
              )}
            </div>
          )}
        </>
      )
    }

    return (
      <div
        ref={ref}
        className={cn(emptyStateVariants({ variant, size }), className)}
        {...props}
      >
        {renderContent()}
      </div>
    )
  }
)
EmptyState.displayName = "EmptyState"

const EmptyStateIllustration = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("mb-6", className)}
    {...props}
  />
))
EmptyStateIllustration.displayName = "EmptyStateIllustration"

const EmptyStateIcon = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    variant?: "default" | "minimal" | "compact" | "card"
    color?: "default" | "primary" | "secondary" | "destructive" | "warning"
  }
>(({ className, variant = "default", color = "default", ...props }, ref) => (
  <div
    ref={ref}
    className={cn(emptyStateIconVariants({ variant, color }), className)}
    {...props}
  />
))
EmptyStateIcon.displayName = "EmptyStateIcon"

const EmptyStateTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn("mt-4 text-lg font-medium", className)}
    {...props}
  />
))
EmptyStateTitle.displayName = "EmptyStateTitle"

const EmptyStateDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("mt-2 text-muted-foreground max-w-md", className)}
    {...props}
  />
))
EmptyStateDescription.displayName = "EmptyStateDescription"

const EmptyStateActions = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("mt-6 flex flex-col gap-3 sm:flex-row", className)}
    {...props}
  />
))
EmptyStateActions.displayName = "EmptyStateActions"

// Predefined empty states for common scenarios
const EmptyStateSearch = React.forwardRef<HTMLDivElement, Omit<EmptyStateProps, "type">>(
  (props, ref) => (
    <EmptyState
      ref={ref}
      type="search"
      title="没有找到结果"
      description="尝试调整搜索条件或关键词"
      action={{
        label: "清除搜索",
        onClick: () => {},
        icon: <RefreshCw className="h-4 w-4" />,
      }}
      {...props}
    />
  )
)
EmptyStateSearch.displayName = "EmptyStateSearch"

const EmptyStateData = React.forwardRef<HTMLDivElement, Omit<EmptyStateProps, "type">>(
  (props, ref) => (
    <EmptyState
      ref={ref}
      type="data"
      title="暂无数据"
      description="当前没有可显示的数据"
      action={{
        label: "刷新",
        onClick: () => {},
        icon: <RefreshCw className="h-4 w-4" />,
      }}
      {...props}
    />
  )
)
EmptyStateData.displayName = "EmptyStateData"

const EmptyStateError = React.forwardRef<HTMLDivElement, Omit<EmptyStateProps, "type">>(
  (props, ref) => (
    <EmptyState
      ref={ref}
      type="error"
      title="加载失败"
      description="无法加载数据，请稍后重试"
      action={{
        label: "重试",
        onClick: () => {},
        icon: <RefreshCw className="h-4 w-4" />,
      }}
      {...props}
    />
  )
)
EmptyStateError.displayName = "EmptyStateError"

const EmptyStateFolder = React.forwardRef<HTMLDivElement, Omit<EmptyStateProps, "type">>(
  (props, ref) => (
    <EmptyState
      ref={ref}
      type="folder"
      title="文件夹为空"
      description="此文件夹中没有文件或子文件夹"
      action={{
        label: "创建文件",
        onClick: () => {},
        icon: <Plus className="h-4 w-4" />,
      }}
      {...props}
    />
  )
)
EmptyStateFolder.displayName = "EmptyStateFolder"

const EmptyStateUsers = React.forwardRef<HTMLDivElement, Omit<EmptyStateProps, "type">>(
  (props, ref) => (
    <EmptyState
      ref={ref}
      type="users"
      title="没有用户"
      description="当前没有用户可显示"
      action={{
        label: "添加用户",
        onClick: () => {},
        icon: <Plus className="h-4 w-4" />,
      }}
      {...props}
    />
  )
)
EmptyStateUsers.displayName = "EmptyStateUsers"

export {
  EmptyState,
  EmptyStateIllustration,
  EmptyStateIcon,
  EmptyStateTitle,
  EmptyStateDescription,
  EmptyStateActions,
  EmptyStateSearch,
  EmptyStateData,
  EmptyStateError,
  EmptyStateFolder,
  EmptyStateUsers,
  emptyStateVariants,
  emptyStateIconVariants,
}