// Threat timeline chart component
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ThreatTimelineProps {
  data: Array<{
    timestamp: string;
    threat_level: string;
    confidence: number;
  }>;
}

const threatLevelToValue: Record<string, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
  info: 0,
};

export function ThreatTimeline({ data }: ThreatTimelineProps) {
  const chartData = data.map((item) => ({
    time: new Date(item.timestamp).toLocaleTimeString(),
    value: threatLevelToValue[item.threat_level] || 0,
    confidence: item.confidence * 100,
  }));

  return (
    <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
      <h3 className="text-lg font-semibold text-white mb-4">
        Threat Timeline (Last 24 Hours)
      </h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="time" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" domain={[0, 4]} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#F3F4F6' }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#EF4444"
            strokeWidth={2}
            name="Threat Level"
          />
          <Line
            type="monotone"
            dataKey="confidence"
            stroke="#3B82F6"
            strokeWidth={2}
            name="Confidence %"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
