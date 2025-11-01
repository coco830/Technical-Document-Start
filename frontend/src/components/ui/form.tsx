import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils"
import { Input } from "./input"
import { Button } from "./button"

const formVariants = cva(
  "space-y-6",
  {
    variants: {
      layout: {
        default: "flex flex-col",
        inline: "flex flex-row flex-wrap items-center gap-4",
        horizontal: "grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3",
        compact: "space-y-4",
      },
      spacing: {
        none: "space-y-0",
        sm: "space-y-2",
        default: "space-y-6",
        lg: "space-y-8",
      },
    },
    defaultVariants: {
      layout: "default",
      spacing: "default",
    },
  }
)

const formFieldVariants = cva(
  "space-y-2",
  {
    variants: {
      layout: {
        default: "flex flex-col",
        inline: "flex items-center gap-2",
        horizontal: "flex flex-col sm:flex-row sm:items-center sm:gap-2",
        compact: "space-y-1",
      },
      size: {
        sm: "text-sm",
        default: "text-sm",
        lg: "text-base",
      },
      state: {
        default: "",
        error: "text-destructive",
        success: "text-green-600 dark:text-green-400",
        warning: "text-yellow-600 dark:text-yellow-400",
      },
    },
    defaultVariants: {
      layout: "default",
      size: "default",
      state: "default",
    },
  }
)

const formLabelVariants = cva(
  "font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
  {
    variants: {
      size: {
        sm: "text-xs",
        default: "text-sm",
        lg: "text-base",
      },
      required: {
        true: "after:content-['*'] after:ml-0.5 after:text-destructive",
      },
    },
    defaultVariants: {
      size: "default",
      required: false,
    },
  }
)

const formInputVariants = cva(
  "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      size: {
        sm: "h-8 px-2 text-xs",
        default: "h-10 px-3 text-sm",
        lg: "h-12 px-4 text-base",
      },
      state: {
        default: "border-input",
        error: "border-destructive focus-visible:ring-destructive",
        success: "border-green-600 focus-visible:ring-green-600",
        warning: "border-yellow-600 focus-visible:ring-yellow-600",
      },
    },
    defaultVariants: {
      size: "default",
      state: "default",
    },
  }
)

const formErrorVariants = cva(
  "text-sm",
  {
    variants: {
      state: {
        default: "text-muted-foreground",
        error: "text-destructive",
        success: "text-green-600 dark:text-green-400",
        warning: "text-yellow-600 dark:text-yellow-400",
      },
    },
    defaultVariants: {
      state: "default",
    },
  }
)

export interface FormFieldProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof formFieldVariants> {
  label?: string
  description?: string
  error?: string
  required?: boolean
  children: React.ReactNode
}

const FormField = React.forwardRef<HTMLDivElement, FormFieldProps>(
  ({
    className,
    layout,
    size,
    state,
    label,
    description,
    error,
    required,
    children,
    ...props
  }, ref) => {
    const actualState = error ? "error" : state

    return (
      <div
        ref={ref}
        className={cn(formFieldVariants({ layout, size, state: actualState }), className)}
        {...props}
      >
        {label && (
          <label className={cn(formLabelVariants({ size, required }))}>
            {label}
          </label>
        )}
        {children}
        {description && (
          <p className={cn(formErrorVariants({ state: "default" }), "text-xs")}>
            {description}
          </p>
        )}
        {error && (
          <p className={cn(formErrorVariants({ state: "error" }), "text-xs")}>
            {error}
          </p>
        )}
      </div>
    )
  }
)
FormField.displayName = "FormField"

export interface FormInputProps
  extends React.InputHTMLAttributes<HTMLInputElement>,
    VariantProps<typeof formInputVariants> {
  error?: boolean
  success?: boolean
  warning?: boolean
}

const FormInput = React.forwardRef<HTMLInputElement, FormInputProps>(
  ({ className, size, state, error, success, warning, ...props }, ref) => {
    const actualState = error ? "error" : success ? "success" : warning ? "warning" : state

    return (
      <Input
        ref={ref}
        className={cn(formInputVariants({ size, state: actualState }), className)}
        {...props}
      />
    )
  }
)
FormInput.displayName = "FormInput"

export interface FormTextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement>,
    VariantProps<typeof formInputVariants> {
  error?: boolean
  success?: boolean
  warning?: boolean
}

const FormTextarea = React.forwardRef<HTMLTextAreaElement, FormTextareaProps>(
  ({ className, size, state, error, success, warning, ...props }, ref) => {
    const actualState = error ? "error" : success ? "success" : warning ? "warning" : state

    return (
      <textarea
        ref={ref}
        className={cn(
          formInputVariants({ size, state: actualState }),
          "min-h-[80px] resize-y",
          className
        )}
        {...props}
      />
    )
  }
)
FormTextarea.displayName = "FormTextarea"

export interface FormSelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement>,
    VariantProps<typeof formInputVariants> {
  error?: boolean
  success?: boolean
  warning?: boolean
  options: { value: string; label: string; disabled?: boolean }[]
  placeholder?: string
}

const FormSelect = React.forwardRef<HTMLSelectElement, FormSelectProps>(
  ({
    className,
    size,
    state,
    error,
    success,
    warning,
    options,
    placeholder,
    ...props
  }, ref) => {
    const actualState = error ? "error" : success ? "success" : warning ? "warning" : state

    return (
      <select
        ref={ref}
        className={cn(formInputVariants({ size, state: actualState }), className)}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </option>
        ))}
      </select>
    )
  }
)
FormSelect.displayName = "FormSelect"

export interface FormCheckboxProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  description?: string
  error?: string
}

const FormCheckbox = React.forwardRef<HTMLInputElement, FormCheckboxProps>(
  ({ className, label, description, error, ...props }, ref) => {
    return (
      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <input
            ref={ref}
            type="checkbox"
            className={cn(
              "h-4 w-4 rounded border border-input bg-background text-primary focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
              error && "border-destructive focus:ring-destructive",
              className
            )}
            {...props}
          />
          {label && (
            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
              {label}
            </label>
          )}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground ml-6">
            {description}
          </p>
        )}
        {error && (
          <p className="text-xs text-destructive ml-6">
            {error}
          </p>
        )}
      </div>
    )
  }
)
FormCheckbox.displayName = "FormCheckbox"

export interface FormRadioProps {
  name: string
  options: { value: string; label: string; disabled?: boolean }[]
  value?: string
  onChange?: (value: string) => void
  error?: string
  orientation?: "horizontal" | "vertical"
  size?: "sm" | "default" | "lg"
}

const FormRadio = React.forwardRef<HTMLDivElement, FormRadioProps>(
  ({
    name,
    options,
    value,
    onChange,
    error,
    orientation = "vertical",
    size = "default",
    ...props
  }, ref) => {
    const sizeClasses = {
      sm: "h-3 w-3",
      default: "h-4 w-4",
      lg: "h-5 w-5",
    }

    const labelSizeClasses = {
      sm: "text-xs",
      default: "text-sm",
      lg: "text-base",
    }

    return (
      <div
        ref={ref}
        className={cn(
          "space-y-2",
          orientation === "horizontal" && "flex items-center space-x-4 space-y-0"
        )}
        {...props}
      >
        {options.map((option) => (
          <div key={option.value} className="flex items-center space-x-2">
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange?.(option.value)}
              disabled={option.disabled}
              className={cn(
                "border-input text-primary focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
                sizeClasses[size],
                error && "border-destructive focus:ring-destructive"
              )}
            />
            <label className={cn("font-medium leading-none", labelSizeClasses[size])}>
              {option.label}
            </label>
          </div>
        ))}
        {error && (
          <p className="text-xs text-destructive">
            {error}
          </p>
        )}
      </div>
    )
  }
)
FormRadio.displayName = "FormRadio"

export interface FormProps
  extends React.FormHTMLAttributes<HTMLFormElement>,
    VariantProps<typeof formVariants> {
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void
  loading?: boolean
  disabled?: boolean
}

const Form = React.forwardRef<HTMLFormElement, FormProps>(
  ({
    className,
    layout,
    spacing,
    onSubmit,
    loading = false,
    disabled = false,
    children,
    ...props
  }, ref) => {
    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault()
      if (!loading && !disabled) {
        onSubmit?.(e)
      }
    }

    return (
      <form
        ref={ref}
        className={cn(formVariants({ layout, spacing }), className)}
        onSubmit={handleSubmit}
        {...props}
      >
        <fieldset disabled={disabled || loading}>
          {children}
        </fieldset>
      </form>
    )
  }
)
Form.displayName = "Form"

export interface FormActionsProps extends React.HTMLAttributes<HTMLDivElement> {
  align?: "left" | "center" | "right" | "between"
  spacing?: "sm" | "default" | "lg"
}

const FormActions = React.forwardRef<HTMLDivElement, FormActionsProps>(
  ({ className, align = "right", spacing = "default", ...props }, ref) => {
    const alignClasses = {
      left: "justify-start",
      center: "justify-center",
      right: "justify-end",
      between: "justify-between",
    }

    const spacingClasses = {
      sm: "gap-2",
      default: "gap-3",
      lg: "gap-4",
    }

    return (
      <div
        ref={ref}
        className={cn(
          "flex items-center",
          alignClasses[align],
          spacingClasses[spacing],
          className
        )}
        {...props}
      />
    )
  }
)
FormActions.displayName = "FormActions"

export {
  Form,
  FormField,
  FormInput,
  FormTextarea,
  FormSelect,
  FormCheckbox,
  FormRadio,
  FormActions,
  formVariants,
  formFieldVariants,
  formLabelVariants,
  formInputVariants,
  formErrorVariants,
}