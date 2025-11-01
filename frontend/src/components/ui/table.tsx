import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils"
import { ChevronUp, ChevronDown, MoreHorizontal } from "lucide-react"

const tableVariants = cva(
  "w-full caption-bottom text-sm",
  {
    variants: {
      variant: {
        default: "border-separate border-spacing-0",
        striped: "border-separate border-spacing-0",
        bordered: "border-collapse border border-border",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

const tableCellVariants = cva(
  "px-4 py-2 align-middle [&:has([role=checkbox])]:pr-0",
  {
    variants: {
      variant: {
        default: "",
        striped: "",
        bordered: "border border-border",
      },
      header: {
        true: "font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0",
      },
    },
    defaultVariants: {
      variant: "default",
      header: false,
    },
  }
)

export interface TableColumn<T = any> {
  key: string
  title: string
  dataIndex?: string
  render?: (value: any, record: T, index: number) => React.ReactNode
  sortable?: boolean
  width?: string | number
  align?: "left" | "center" | "right"
  className?: string
  headerClassName?: string
}

export interface TableProps<T = any>
  extends React.HTMLAttributes<HTMLTableElement>,
    VariantProps<typeof tableVariants> {
  columns: TableColumn<T>[]
  data: T[]
  loading?: boolean
  empty?: React.ReactNode
  rowKey?: string | ((record: T) => string)
  onRowClick?: (record: T, index: number) => void
  onSort?: (key: string, direction: "asc" | "desc") => void
  sortKey?: string
  sortDirection?: "asc" | "desc"
  rowClassName?: string | ((record: T, index: number) => string)
  striped?: boolean
  hoverable?: boolean
  compact?: boolean
}

const Table = <T extends Record<string, any>>({
  className,
  variant,
  columns,
  data,
  loading = false,
  empty,
  rowKey = "id",
  onRowClick,
  onSort,
  sortKey,
  sortDirection,
  rowClassName,
  striped = false,
  hoverable = true,
  compact = false,
  ...props
}: TableProps<T>) => {
  const [localSortKey, setLocalSortKey] = React.useState<string | null>(null)
  const [localSortDirection, setLocalSortDirection] = React.useState<"asc" | "desc">("asc")

  const currentSortKey = sortKey || localSortKey
  const currentSortDirection = sortDirection || localSortDirection

  const handleSort = (key: string) => {
    if (!onSort) {
      if (currentSortKey === key) {
        setLocalSortDirection(currentSortDirection === "asc" ? "desc" : "asc")
      } else {
        setLocalSortKey(key)
        setLocalSortDirection("asc")
      }
    } else {
      const direction = currentSortKey === key && currentSortDirection === "asc" ? "desc" : "asc"
      onSort(key, direction)
    }
  }

  const getSortedData = () => {
    if (!currentSortKey) return data

    return [...data].sort((a, b) => {
      const aValue = a[currentSortKey]
      const bValue = b[currentSortKey]

      if (aValue === undefined || aValue === null) return 1
      if (bValue === undefined || bValue === null) return -1

      if (typeof aValue === "string" && typeof bValue === "string") {
        return currentSortDirection === "asc"
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      if (aValue < bValue) return currentSortDirection === "asc" ? -1 : 1
      if (aValue > bValue) return currentSortDirection === "asc" ? 1 : -1
      return 0
    })
  }

  const getRowKey = (record: T, index: number) => {
    if (typeof rowKey === "function") {
      return rowKey(record)
    }
    return record[rowKey] || index.toString()
  }

  const getRowClassName = (record: T, index: number) => {
    if (typeof rowClassName === "function") {
      return rowClassName(record, index)
    }
    return rowClassName || ""
  }

  const getCellValue = (column: TableColumn<T>, record: T, index: number) => {
    const value = column.dataIndex ? record[column.dataIndex] : record[column.key]
    return column.render ? column.render(value, record, index) : value
  }

  const getCellAlignment = (align?: "left" | "center" | "right") => {
    switch (align) {
      case "center":
        return "text-center"
      case "right":
        return "text-right"
      default:
        return "text-left"
    }
  }

  const sortedData = getSortedData()

  return (
    <div className="relative w-full overflow-auto">
      <table
        className={cn(
          tableVariants({ variant }),
          compact && "text-xs",
          className
        )}
        {...props}
      >
        <thead>
          <tr className="border-b border-border transition-colors hover:bg-muted/50">
            {columns.map((column) => (
              <th
                key={column.key}
                className={cn(
                  tableCellVariants({ variant, header: true }),
                  column.headerClassName,
                  getCellAlignment(column.align),
                  column.sortable && "cursor-pointer select-none hover:bg-muted/50",
                  compact && "px-2 py-1"
                )}
                style={{ width: column.width }}
                onClick={() => column.sortable && handleSort(column.key)}
              >
                <div className="flex items-center gap-1">
                  <span>{column.title}</span>
                  {column.sortable && currentSortKey === column.key && (
                    <span className="inline-flex">
                      {currentSortDirection === "asc" ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr>
              <td colSpan={columns.length} className="text-center py-8">
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                  <span className="ml-2">加载中...</span>
                </div>
              </td>
            </tr>
          ) : sortedData.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="text-center py-8">
                {empty || <div className="text-muted-foreground">暂无数据</div>}
              </td>
            </tr>
          ) : (
            sortedData.map((record, index) => (
              <tr
                key={getRowKey(record, index)}
                className={cn(
                  "border-b border-border transition-colors",
                  striped && index % 2 === 1 && "bg-muted/25",
                  hoverable && "hover:bg-muted/50",
                  onRowClick && "cursor-pointer",
                  getRowClassName(record, index),
                  compact && "text-xs"
                )}
                onClick={() => onRowClick?.(record, index)}
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={cn(
                      tableCellVariants({ variant }),
                      column.className,
                      getCellAlignment(column.align),
                      compact && "px-2 py-1"
                    )}
                    style={{ width: column.width }}
                  >
                    {getCellValue(column, record, index)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
Table.displayName = "Table"

const TableHeader = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <thead ref={ref} className={cn("[&_tr]:border-b", className)} {...props} />
))
TableHeader.displayName = "TableHeader"

const TableBody = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tbody
    ref={ref}
    className={cn("[&_tr:last-child]:border-0", className)}
    {...props}
  />
))
TableBody.displayName = "TableBody"

const TableFooter = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tfoot
    ref={ref}
    className={cn(
      "border-t bg-muted/50 font-medium [&>tr]:last:border-b-0",
      className
    )}
    {...props}
  />
))
TableFooter.displayName = "TableFooter"

const TableRow = React.forwardRef<
  HTMLTableRowElement,
  React.HTMLAttributes<HTMLTableRowElement>
>(({ className, ...props }, ref) => (
  <tr
    ref={ref}
    className={cn(
      "border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted",
      className
    )}
    {...props}
  />
))
TableRow.displayName = "TableRow"

const TableHead = React.forwardRef<
  HTMLTableCellElement,
  React.ThHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <th
    ref={ref}
    className={cn(
      "h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0",
      className
    )}
    {...props}
  />
))
TableHead.displayName = "TableHead"

const TableCell = React.forwardRef<
  HTMLTableCellElement,
  React.TdHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <td
    ref={ref}
    className={cn("p-4 align-middle [&:has([role=checkbox])]:pr-0", className)}
    {...props}
  />
))
TableCell.displayName = "TableCell"

const TableCaption = React.forwardRef<
  HTMLTableCaptionElement,
  React.HTMLAttributes<HTMLTableCaptionElement>
>(({ className, ...props }, ref) => (
  <caption
    ref={ref}
    className={cn("mt-4 text-sm text-muted-foreground", className)}
    {...props}
  />
))
TableCaption.displayName = "TableCaption"

export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
  tableVariants,
  tableCellVariants,
}