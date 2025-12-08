import * as React from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

interface AlertDialogProps {
  open: boolean
  onClose: () => void
  title: string
  description: string
  type?: "error" | "warning" | "info"
}

export function AlertDialog({ open, onClose, title, description, type = "warning" }: AlertDialogProps) {
  if (!open) return null

  const bgColor = {
    error: "bg-red-50 border-red-200",
    warning: "bg-yellow-50 border-yellow-200",
    info: "bg-blue-50 border-blue-200"
  }

  const textColor = {
    error: "text-red-800",
    warning: "text-yellow-800",
    info: "text-blue-800"
  }

  const iconColor = {
    error: "bg-red-100 text-red-600",
    warning: "bg-yellow-100 text-yellow-600",
    info: "bg-blue-100 text-blue-600"
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 animate-in fade-in duration-200">
      <div className={cn(
        "relative w-full max-w-md rounded-lg border-2 p-6 shadow-lg animate-in zoom-in-95 duration-200",
        bgColor[type]
      )}>
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 transition-opacity"
        >
          <X className="h-4 w-4" />
          <span className="sr-only">Close</span>
        </button>

        <div className="flex gap-4">
          <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-full", iconColor[type])}>
            {type === "error" && (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
            {type === "warning" && (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            )}
            {type === "info" && (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
          </div>

          <div className="flex-1 space-y-2">
            <h3 className={cn("text-lg font-semibold", textColor[type])}>
              {title}
            </h3>
            <p className={cn("text-sm", textColor[type])}>
              {description}
            </p>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className={cn(
              "rounded-md px-4 py-2 text-sm font-medium transition-colors",
              type === "error" && "bg-red-600 text-white hover:bg-red-700",
              type === "warning" && "bg-yellow-600 text-white hover:bg-yellow-700",
              type === "info" && "bg-blue-600 text-white hover:bg-blue-700"
            )}
          >
            OK
          </button>
        </div>
      </div>
    </div>
  )
}
