import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { ChevronLeft, ChevronRight, MoreHorizontal } from "lucide-react"
import { cn } from "@/utils"
import { Button } from "./button"

const paginationVariants = cva(
  "flex items-center gap-1",
  {
    variants: {
      size: {
        sm: "text-xs",
        default: "text-sm",
        lg: "text-base",
      },
      variant: {
        default: "",
        compact: "gap-0",
      },
    },
    defaultVariants: {
      size: "default",
      variant: "default",
    },
  }
)

const paginationItemVariants = cva(
  "inline-flex items-center justify-center rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "hover:bg-accent hover:text-accent-foreground",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        ghost: "hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        sm: "h-8 w-8",
        default: "h-10 w-10",
        lg: "h-12 w-12",
      },
      active: {
        true: "bg-primary text-primary-foreground hover:bg-primary/90",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      active: false,
    },
  }
)

export interface PaginationProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof paginationVariants> {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  showFirstLast?: boolean
  showPrevNext?: boolean
  showPageNumbers?: boolean
  maxVisiblePages?: number
  disabled?: boolean
  itemVariant?: VariantProps<typeof paginationItemVariants>["variant"]
  itemSize?: VariantProps<typeof paginationItemVariants>["size"]
  className?: string
}

const Pagination = React.forwardRef<HTMLDivElement, PaginationProps>(
  ({
    className,
    size,
    variant,
    currentPage,
    totalPages,
    onPageChange,
    showFirstLast = true,
    showPrevNext = true,
    showPageNumbers = true,
    maxVisiblePages = 5,
    disabled = false,
    itemVariant = "default",
    itemSize = "default",
    ...props
  }, ref) => {
    const handlePageChange = (page: number) => {
      if (page < 1 || page > totalPages || disabled) return
      onPageChange(page)
    }

    const getVisiblePages = () => {
      if (totalPages <= maxVisiblePages) {
        return Array.from({ length: totalPages }, (_, i) => i + 1)
      }

      const halfVisible = Math.floor(maxVisiblePages / 2)
      let start = Math.max(1, currentPage - halfVisible)
      let end = Math.min(totalPages, start + maxVisiblePages - 1)

      if (end - start + 1 < maxVisiblePages) {
        start = Math.max(1, end - maxVisiblePages + 1)
      }

      const pages = []
      
      if (start > 1) {
        pages.push(1)
        if (start > 2) {
          pages.push("ellipsis")
        }
      }

      for (let i = start; i <= end; i++) {
        pages.push(i)
      }

      if (end < totalPages) {
        if (end < totalPages - 1) {
          pages.push("ellipsis")
        }
        pages.push(totalPages)
      }

      return pages
    }

    const visiblePages = getVisiblePages()

    return (
      <div
        ref={ref}
        className={cn(paginationVariants({ size, variant }), className)}
        {...props}
      >
        {showFirstLast && (
          <Button
            variant={itemVariant}
            size={itemSize}
            onClick={() => handlePageChange(1)}
            disabled={disabled || currentPage === 1}
            aria-label="第一页"
          >
            <ChevronLeft className="h-4 w-4" />
            <ChevronLeft className="h-4 w-4 -ml-3" />
          </Button>
        )}

        {showPrevNext && (
          <Button
            variant={itemVariant}
            size={itemSize}
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={disabled || currentPage === 1}
            aria-label="上一页"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        )}

        {showPageNumbers && (
          <div className="flex items-center gap-1">
            {visiblePages.map((page, index) => (
              <React.Fragment key={index}>
                {page === "ellipsis" ? (
                  <div
                    className={cn(
                      paginationItemVariants({ variant: itemVariant, size: itemSize }),
                      "cursor-default"
                    )}
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </div>
                ) : (
                  <Button
                    variant={itemVariant}
                    size={itemSize}
                    onClick={() => handlePageChange(page as number)}
                    disabled={disabled}
                    className={cn(
                      paginationItemVariants({
                        variant: itemVariant,
                        size: itemSize,
                        active: currentPage === page,
                      })
                    )}
                    aria-label={`第${page}页`}
                    aria-current={currentPage === page ? "page" : undefined}
                  >
                    {page}
                  </Button>
                )}
              </React.Fragment>
            ))}
          </div>
        )}

        {showPrevNext && (
          <Button
            variant={itemVariant}
            size={itemSize}
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={disabled || currentPage === totalPages}
            aria-label="下一页"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        )}

        {showFirstLast && (
          <Button
            variant={itemVariant}
            size={itemSize}
            onClick={() => handlePageChange(totalPages)}
            disabled={disabled || currentPage === totalPages}
            aria-label="最后一页"
          >
            <ChevronRight className="h-4 w-4" />
            <ChevronRight className="h-4 w-4 -ml-3" />
          </Button>
        )}
      </div>
    )
  }
)
Pagination.displayName = "Pagination"

const PaginationContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center gap-1", className)}
    {...props}
  />
))
PaginationContent.displayName = "PaginationContent"

const PaginationItem = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    active?: boolean
    variant?: VariantProps<typeof paginationItemVariants>["variant"]
    size?: VariantProps<typeof paginationItemVariants>["size"]
  }
>(({ className, active, variant = "default", size = "default", ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      paginationItemVariants({ variant, size, active }),
      className
    )}
    {...props}
  />
))
PaginationItem.displayName = "PaginationItem"

const PaginationLink = React.forwardRef<
  HTMLAnchorElement,
  React.AnchorHTMLAttributes<HTMLAnchorElement> & {
    active?: boolean
    variant?: VariantProps<typeof paginationItemVariants>["variant"]
    size?: VariantProps<typeof paginationItemVariants>["size"]
  }
>(({ className, active, variant = "default", size = "default", ...props }, ref) => (
  <a
    ref={ref}
    className={cn(
      paginationItemVariants({ variant, size, active }),
      className
    )}
    {...props}
  />
))
PaginationLink.displayName = "PaginationLink"

const PaginationPrevious = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: VariantProps<typeof paginationItemVariants>["variant"]
    size?: VariantProps<typeof paginationItemVariants>["size"]
  }
>(({ className, variant = "default", size = "default", ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      paginationItemVariants({ variant, size }),
      className
    )}
    {...props}
  >
    <ChevronLeft className="h-4 w-4" />
    <span className="sr-only">上一页</span>
  </button>
))
PaginationPrevious.displayName = "PaginationPrevious"

const PaginationNext = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: VariantProps<typeof paginationItemVariants>["variant"]
    size?: VariantProps<typeof paginationItemVariants>["size"]
  }
>(({ className, variant = "default", size = "default", ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      paginationItemVariants({ variant, size }),
      className
    )}
    {...props}
  >
    <span className="sr-only">下一页</span>
    <ChevronRight className="h-4 w-4" />
  </button>
))
PaginationNext.displayName = "PaginationNext"

const PaginationEllipsis = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    size?: VariantProps<typeof paginationItemVariants>["size"]
  }
>(({ className, size = "default", ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      paginationItemVariants({ variant: "ghost", size }),
      "cursor-default",
      className
    )}
    {...props}
  >
    <MoreHorizontal className="h-4 w-4" />
    <span className="sr-only">更多页面</span>
  </div>
))
PaginationEllipsis.displayName = "PaginationEllipsis"

export {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
  PaginationEllipsis,
  paginationVariants,
  paginationItemVariants,
}