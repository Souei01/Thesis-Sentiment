'use client';

import React from 'react';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface RatingInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  required?: boolean;
}

export const RatingInput: React.FC<RatingInputProps> = ({
  label,
  value,
  onChange,
  required = true
}) => {
  const ratings = [
    { value: 1, label: 'Poor' },
    { value: 2, label: 'Fair' },
    { value: 3, label: 'Satisfactory' },
    { value: 4, label: 'Very Satisfactory' },
    { value: 5, label: 'Outstanding' }
  ];

  return (
    <div className="space-y-2 sm:space-y-3">
      <Label className="text-xs sm:text-sm font-medium text-gray-700 block">
        {label} {required && <span className="text-red-500">*</span>}
      </Label>
      <div className="grid grid-cols-5 gap-1 sm:gap-2">
        {ratings.map((rating) => (
          <button
            key={rating.value}
            type="button"
            onClick={() => onChange(rating.value)}
            className={cn(
              "p-2 sm:p-3 rounded-lg border-2 transition-all text-center",
              "hover:border-[#8E1B1B] hover:bg-[#8E1B1B]/5",
              "focus:outline-none focus:ring-2 focus:ring-[#8E1B1B] focus:ring-offset-1",
              value === rating.value
                ? "border-[#8E1B1B] bg-[#8E1B1B] text-white"
                : "border-gray-200 bg-white text-gray-700"
            )}
          >
            <div className="text-base sm:text-lg font-bold">{rating.value}</div>
            <div className="text-[10px] sm:text-xs mt-0.5 sm:mt-1 leading-tight">{rating.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
};
