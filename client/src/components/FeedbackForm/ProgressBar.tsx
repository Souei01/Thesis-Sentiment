'use client';

import React from 'react';
import { FORM_STEPS } from '@/types/feedback';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  currentStep: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ currentStep }) => {
  const progress = (currentStep / FORM_STEPS.length) * 100;

  return (
    <div className="mb-6 sm:mb-8">
      {/* Progress Bar */}
      <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden mb-4 sm:mb-6">
        <div
          className="absolute top-0 left-0 h-full bg-[#8E1B1B] transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Step Indicators */}
      <div className="flex justify-between items-start gap-1 sm:gap-2">
        {FORM_STEPS.map((step) => {
          const isCompleted = currentStep > step.id;
          const isCurrent = currentStep === step.id;

          return (
            <div key={step.id} className="flex flex-col items-center flex-1 min-w-0">
              <div
                className={cn(
                  "w-7 h-7 sm:w-10 sm:h-10 rounded-full flex items-center justify-center font-semibold transition-all mb-1 sm:mb-2 text-xs sm:text-base",
                  isCompleted && "bg-[#8E1B1B] text-white",
                  isCurrent && "bg-[#8E1B1B] text-white ring-2 sm:ring-4 ring-[#8E1B1B]/20",
                  !isCompleted && !isCurrent && "bg-gray-200 text-gray-500"
                )}
              >
                {isCompleted ? <Check className="w-3 h-3 sm:w-5 sm:h-5" /> : step.id}
              </div>
              <span
                className={cn(
                  "text-[9px] sm:text-xs text-center leading-tight px-1",
                  (isCompleted || isCurrent) ? "text-[#8E1B1B] font-medium" : "text-gray-400"
                )}
              >
                {step.title}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
