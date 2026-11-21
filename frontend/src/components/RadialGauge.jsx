import React from 'react';

export default function RadialGauge({ value = 0, size = 120, strokeWidth = 10, label = '', subtitle = '' }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.min(100, Math.max(0, value));
  const offset = circumference - (clamped / 100) * circumference;

  let strokeColor = '#f43f5e'; // Rose-500
  if (clamped >= 75) {
    strokeColor = '#10b981'; // Emerald-500
  } else if (clamped >= 50) {
    strokeColor = '#f59e0b'; // Amber-500
  }

  return (
    <div className="flex flex-col items-center justify-center p-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#e2e8f0"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-2xl font-extrabold text-slate-800 tracking-tight font-mono">
            {Math.round(clamped)}%
          </span>
          {subtitle && <span className="text-[10px] uppercase font-bold text-slate-600">{subtitle}</span>}
        </div>
      </div>
      {label && <p className="mt-2 text-xs font-semibold text-slate-700 text-center">{label}</p>}
    </div>
  );
}
