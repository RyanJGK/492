// Generic event table component
import React from 'react';

interface Column<T> {
  key: keyof T | string;
  label: string;
  render?: (value: any, row: T) => React.ReactNode;
}

interface EventTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
}

export function EventTable<T extends { id: number }>({
  data,
  columns,
  loading = false,
}: EventTableProps<T>) {
  if (loading) {
    return (
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-dark-700 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <p className="text-gray-400 text-center">No data available</p>
      </div>
    );
  }

  return (
    <div className="bg-dark-800 rounded-lg border border-dark-700 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-dark-900">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key as string}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider"
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-700">
            {data.map((row) => (
              <tr key={row.id} className="hover:bg-dark-700/50 transition">
                {columns.map((column) => {
                  const value = column.key.includes('.')
                    ? column.key.split('.').reduce((obj: any, key) => obj?.[key], row)
                    : row[column.key as keyof T];
                  
                  return (
                    <td
                      key={column.key as string}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-300"
                    >
                      {column.render ? column.render(value, row) : String(value || '-')}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
