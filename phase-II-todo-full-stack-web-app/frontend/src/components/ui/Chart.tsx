import React from 'react';

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string[];
    borderColor?: string[];
    borderWidth?: number;
  }[];
}

interface ChartProps {
  type: 'bar' | 'line' | 'pie';
  data: ChartData;
  width?: number;
  height?: number;
  className?: string;
}

const Chart: React.FC<ChartProps> = ({ type, data, width = 400, height = 200, className = '' }) => {
  // This is a simplified implementation of a chart component
  // In a real application, you would use a library like Chart.js or Recharts

  const maxValue = Math.max(...data.datasets.flatMap(dataset => dataset.data));

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-4 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">{data.datasets[0]?.label || 'Chart'}</h3>
      </div>
      <div
        className="relative border border-gray-200 dark:border-gray-700 rounded"
        style={{ width: `${width}px`, height: `${height}px` }}
      >
        {type === 'bar' && (
          <div className="absolute inset-0 flex items-end p-4 space-x-2">
            {data.labels.map((label, index) => {
              const value = data.datasets[0]?.data[index] || 0;
              const barHeight = maxValue > 0 ? (value / maxValue) * (height - 40) : 0;

              return (
                <div key={index} className="flex flex-col items-center flex-1">
                  <div
                    className="w-3/4 bg-blue-500 rounded-t hover:bg-blue-600 transition-colors"
                    style={{ height: `${barHeight}px` }}
                  ></div>
                  <div className="mt-2 text-xs text-gray-600 dark:text-gray-400 truncate w-full text-center">
                    {label}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {type === 'pie' && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className="relative rounded-full border-2 border-gray-200 dark:border-gray-700"
              style={{ width: `${Math.min(width, height) - 40}px`, height: `${Math.min(width, height) - 40}px` }}
            >
              {data.datasets[0]?.data.map((value, index) => {
                const percentage = (value / data.datasets[0].data.reduce((a, b) => a + b, 0)) * 100;
                const color = data.datasets[0].backgroundColor[index];

                return (
                  <div
                    key={index}
                    className="absolute top-0 left-0 w-full h-full"
                    style={{
                      clipPath: `conic-gradient(from ${(index * 360 / data.datasets[0].data.length) - 90}deg, ${color} ${percentage}%, transparent ${percentage}%)`
                    }}
                  ></div>
                );
              })}
            </div>
          </div>
        )}

        {type === 'line' && (
          <div className="absolute inset-0 p-4">
            <svg
              width={width - 40}
              height={height - 40}
              viewBox={`0 0 ${width - 40} ${height - 40}`}
              className="w-full h-full"
            >
              {data.datasets.map((dataset, dsIndex) => {
                const points = dataset.data.map((value, index) => {
                  const x = ((width - 40) / (data.labels.length - 1)) * index;
                  const y = height - 40 - ((value / maxValue) * (height - 60));
                  return `${x},${y}`;
                }).join(' ');

                return (
                  <g key={dsIndex}>
                    <polyline
                      fill="none"
                      stroke={dataset.backgroundColor[0]}
                      strokeWidth="2"
                      points={points}
                    />
                    {dataset.data.map((value, index) => {
                      const x = ((width - 40) / (data.labels.length - 1)) * index;
                      const y = height - 40 - ((value / maxValue) * (height - 60));

                      return (
                        <circle
                          key={index}
                          cx={x}
                          cy={y}
                          r="4"
                          fill={dataset.backgroundColor[0]}
                        />
                      );
                    })}
                  </g>
                );
              })}
            </svg>
          </div>
        )}
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {data.labels.map((label, index) => (
          <div key={index} className="flex items-center">
            <div
              className="w-3 h-3 rounded-full mr-1"
              style={{ backgroundColor: data.datasets[0]?.backgroundColor[index] }}
            ></div>
            <span className="text-xs text-gray-600 dark:text-gray-400">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Chart;