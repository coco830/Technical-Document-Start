import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { ChevronDown, Check } from "lucide-react"
import { cn } from "@/utils"

const dropdownVariants = cva(
  "relative inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-9 px-3 rounded-md",
        lg: "h-11 px-8 rounded-md",
      },
    },
    defaultVariants: {
      variant: "outline",
      size: "default",
    },
  }
)

const dropdownContentVariants = cva(
  "absolute z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95",
  {
    variants: {
      position: {
        top: "bottom-full mb-2",
        bottom: "top-full mt-2",
        left: "right-full mr-2",
        right: "left-full ml-2",
      },
      align: {
        start: "left-0",
        center: "left-1/2 transform -translate-x-1/2",
        end: "right-0",
      },
    },
    defaultVariants: {
      position: "bottom",
      align: "start",
    },
  }
)

export interface DropdownItem {
  value: string
  label: string
  icon?: React.ReactNode
  disabled?: boolean
  description?: string
  onClick?: () => void
}

export interface DropdownProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof dropdownVariants> {
  items: DropdownItem[]
  placeholder?: string
  value?: string
  onValueChange?: (value: string) => void
  contentClassName?: string
  position?: "top" | "bottom" | "left" | "right"
  align?: "start" | "center" | "end"
}

const Dropdown = React.forwardRef<HTMLButtonElement, DropdownProps>(
  ({
    className,
    variant,
    size,
    items,
    placeholder = "选择选项",
    value,
    onValueChange,
    contentClassName,
    position = "bottom",
    align = "start",
    disabled,
    ...props
  }, ref) => {
    const [isOpen, setIsOpen] = React.useState(false)
    const [selectedItem, setSelectedItem] = React.useState<DropdownItem | null>(
      items.find(item => item.value === value) || null
    )
    const dropdownRef = React.useRef<HTMLDivElement>(null)

    React.useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
          setIsOpen(false)
        }
      }

      const handleEscapeKey = (event: KeyboardEvent) => {
        if (event.key === 'Escape') {
          setIsOpen(false)
        }
      }

      if (isOpen) {
        document.addEventListener('mousedown', handleClickOutside)
        document.addEventListener('keydown', handleEscapeKey)
      }

      return () => {
        document.removeEventListener('mousedown', handleClickOutside)
        document.removeEventListener('keydown', handleEscapeKey)
      }
    }, [isOpen])

    React.useEffect(() => {
      if (value !== undefined) {
        const item = items.find(item => item.value === value)
        setSelectedItem(item || null)
      }
    }, [value, items])

    const handleItemClick = (item: DropdownItem) => {
      if (item.disabled) return
      
      setSelectedItem(item)
      setIsOpen(false)
      
      if (onValueChange) {
        onValueChange(item.value)
      }
      
      if (item.onClick) {
        item.onClick()
      }
    }

    const displayText = selectedItem ? selectedItem.label : placeholder

    return (
      <div ref={dropdownRef} className="relative">
        <button
          ref={ref}
          type="button"
          className={cn(dropdownVariants({ variant, size }), "w-full justify-between", className)}
          onClick={() => setIsOpen(!isOpen)}
          disabled={disabled}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          {...props}
        >
          <span className="truncate">{displayText}</span>
          <ChevronDown className={cn("h-4 w-4 transition-transform", isOpen && "rotate-180")} />
        </button>
        
        {isOpen && (
          <div
            className={cn(
              dropdownContentVariants({ position, align }),
              "w-full",
              contentClassName
            )}
            role="listbox"
          >
            <div className="p-1">
              {items.map((item) => (
                <div
                  key={item.value}
                  className={cn(
                    "relative flex cursor-default select-none items-center rounded-sm py-1.5 px-2 text-sm outline-none transition-colors",
                    item.disabled
                      ? "pointer-events-none opacity-50"
                      : "focus:bg-accent focus:text-accent-foreground hover:bg-accent hover:text-accent-foreground",
                    selectedItem?.value === item.value && "bg-accent text-accent-foreground"
                  )}
                  role="option"
                  aria-selected={selectedItem?.value === item.value}
                  onClick={() => handleItemClick(item)}
                >
                  {item.icon && (
                    <span className="mr-2 h-4 w-4">{item.icon}</span>
                  )}
                  <div className="flex flex-col flex-1">
                    <span>{item.label}</span>
                    {item.description && (
                      <span className="text-xs text-muted-foreground">
                        {item.description}
                      </span>
                    )}
                  </div>
                  {selectedItem?.value === item.value && (
                    <Check className="ml-2 h-4 w-4" />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }
)
Dropdown.displayName = "Dropdown"

const DropdownSeparator = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("my-1 h-px bg-muted", className)}
    {...props}
  />
))
DropdownSeparator.displayName = "DropdownSeparator"

const DropdownLabel = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("px-2 py-1.5 text-sm font-semibold", className)}
    {...props}
  />
))
DropdownLabel.displayName = "DropdownLabel"

export {
  Dropdown,
  DropdownSeparator,
  DropdownLabel,
  dropdownVariants,
  dropdownContentVariants,
}