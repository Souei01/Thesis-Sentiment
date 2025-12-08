import * as React from "react"
import { cn } from "@/lib/utils"

interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg" | "xl"
  showMessage?: boolean
}

const sizeClasses = {
  sm: "h-4 w-4 border-2",
  md: "h-8 w-8 border-2",
  lg: "h-12 w-12 border-3",
  xl: "h-16 w-16 border-4",
}

const messages = [
  "Analyzing sentiment… please wait.",
  "Processing text for sentiment insights…",
  "Running sentiment analysis… almost there.",
]

const Spinner = React.forwardRef<HTMLDivElement, SpinnerProps>(
  ({ className, size = "md", showMessage = false, ...props }, ref) => {
    const [messageIndex, setMessageIndex] = React.useState(0)

    React.useEffect(() => {
      if (showMessage) {
        const interval = setInterval(() => {
          setMessageIndex((prev) => (prev + 1) % messages.length)
        }, 3000)
        return () => clearInterval(interval)
      }
    }, [showMessage])

    if (showMessage) {
      return (
        <div className="flex flex-col items-center gap-4">
          <div
            ref={ref}
            className={cn(
              "animate-spin rounded-full border-primary border-t-transparent",
              sizeClasses[size],
              className
            )}
            {...props}
          />
          <p className="text-sm text-gray-600 animate-pulse">
            {messages[messageIndex]}
          </p>
        </div>
      )
    }

    return (
      <div
        ref={ref}
        className={cn(
          "animate-spin rounded-full border-primary border-t-transparent",
          sizeClasses[size],
          className
        )}
        {...props}
      />
    )
  }
)
Spinner.displayName = "Spinner"

export { Spinner }

// Usage example
<Spinner size="lg" showMessage />
