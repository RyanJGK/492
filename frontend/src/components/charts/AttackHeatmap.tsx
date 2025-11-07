// Attack heatmap component
import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface AttackHeatmapProps {
  threatCounts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

export function AttackHeatmap({ threatCounts }: AttackHeatmapProps) {
  const data = [
    { name: 'Critical', count: threatCounts.critical, fill: '#DC2626' },
    { name: 'High', count: threatCounts.high, fill: '#F59E0B' },
    { name: 'Medium', count: threatCounts.medium, fill: '#FCD34D' },
    { name: 'Low', count: threatCounts.low, fill: '#10B981' },
  ];

  return (
    <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
      <h3 className="text-lg font-semibold text-white mb-4">
        Active Threats by Severity
      </h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="name" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#F3F4F6' }}
          />
          <Bar dataKey="count" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
