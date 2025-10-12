'use client';

import React from 'react';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface YesNoInputProps {
  label: string;
  value: boolean | null;
  onChange: (value: boolean) => void;
  required?: boolean;
}

export const YesNoInput: React.FC<YesNoInputProps> = ({
  label,
  value,
  onChange,
  required = true
}) => {
  return (
    <div className="space-y-2 sm:space-y-3">
      <Label className="text-xs sm:text-sm font-medium text-gray-700 block">
        {label} {required && <span className="text-red-500">*</span>}
      </Label>
      <div className="flex gap-2 sm:gap-3">
        <button
          type="button"
          onClick={() => onChange(true)}
          className={cn(
            "flex-1 p-2 sm:p-3 rounded-lg border-2 transition-all font-medium text-sm sm:text-base",
            "hover:border-green-500 hover:bg-green-50",
            "focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-1",
            value === true
              ? "border-green-500 bg-green-500 text-white"
              : "border-gray-200 bg-white text-gray-700"
          )}
        >
          Yes
        </button>
        <button
          type="button"
          onClick={() => onChange(false)}
          className={cn(
            "flex-1 p-2 sm:p-3 rounded-lg border-2 transition-all font-medium text-sm sm:text-base",
            "hover:border-red-500 hover:bg-red-50",
            "focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1",
            value === false
              ? "border-red-500 bg-red-500 text-white"
              : "border-gray-200 bg-white text-gray-700"
          )}
        >
          No
        </button>
      </div>
    </div>
  );
};
