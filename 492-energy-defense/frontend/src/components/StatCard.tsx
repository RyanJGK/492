/**
 * Stat Card Component
 * Displays key metrics with visual indicators
 */
import React from 'react';
import { LucideIcon } from 'lucide-react';
import clsx from 'clsx';

interface StatCardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'primary' | 'danger' | 'warning' | 'success';
}

export function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  color = 'primary',
}: StatCardProps) {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600 border-primary-200',
    danger: 'bg-danger-50 text-danger-600 border-danger-200',
    warning: 'bg-warning-50 text-warning-600 border-warning-200',
    success: 'bg-success-50 text-success-600 border-success-200',
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>

          {trend && (
            <div className="flex items-center mt-2">
              <span
                className={clsx(
                  'text-sm font-medium',
                  trend.isPositive ? 'text-success-600' : 'text-danger-600'
                )}
              >
                {trend.isPositive ? '+' : ''}
                {trend.value}%
              </span>
              <span className="text-sm text-gray-500 ml-2">vs last week</span>
            </div>
          )}
        </div>

        <div
          className={clsx(
            'w-14 h-14 rounded-lg flex items-center justify-center border',
            colorClasses[color]
          )}
        >
          <Icon className="w-7 h-7" />
        </div>
      </div>
    </div>
  );
}
