// Threat level gauge component
import React from 'react';
import type { ThreatLevel } from '../../types';

interface ThreatGaugeProps {
  level: ThreatLevel;
  confidence: number;
}

const levelColors: Record<ThreatLevel, string> = {
  critical: 'text-danger-500',
  high: 'text-warning-500',
  medium: 'text-warning-300',
  low: 'text-success-500',
  info: 'text-primary-500',
};

const levelBgColors: Record<ThreatLevel, string> = {
  critical: 'bg-danger-500',
  high: 'bg-warning-500',
  medium: 'bg-warning-300',
  low: 'bg-success-500',
  info: 'bg-primary-500',
};

export function ThreatGauge({ level, confidence }: ThreatGaugeProps) {
  const percentage = confidence * 100;

  return (
    <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
      <h3 className="text-lg font-semibold text-white mb-4">
        Current Threat Level
      </h3>
      
      <div className="flex flex-col items-center">
        <div className="relative w-48 h-48 mb-4">
          <svg className="transform -rotate-90 w-48 h-48">
            <circle
              cx="96"
              cy="96"
              r="80"
              stroke="currentColor"
              strokeWidth="16"
              fill="transparent"
              className="text-dark-700"
            />
            <circle
              cx="96"
              cy="96"
              r="80"
              stroke="currentColor"
              strokeWidth="16"
              fill="transparent"
              strokeDasharray={`${502.4 * percentage / 100} 502.4`}
              className={levelColors[level]}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className={`text-4xl font-bold ${levelColors[level]} uppercase`}>
              {level}
            </div>
            <div className="text-gray-400 text-sm mt-1">
              {percentage.toFixed(1)}% confidence
            </div>
          </div>
        </div>

        <div className="w-full space-y-2">
          <div className="flex justify-between text-xs text-gray-400">
            <span>Low</span>
            <span>High</span>
          </div>
          <div className="w-full bg-dark-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${levelBgColors[level]} transition-all duration-500`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
