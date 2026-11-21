import React from 'react';

export default function ProgressBar({ value = 0, max = 100, label = '', showPercentage = true, height = 'h-2.5' }) {
  const percentage = Math.min(100, Math.max(0, Math.round((value / max) * 100)));

  let colorClass = 'bg-rose-500';
  if (percentage >= 75) {
    colorClass = 'bg-emerald-500';
  } else if (percentage >= 50) {
    colorClass = 'bg-amber-500';
  }

  return (
    <div className="w-full">
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-1 text-xs font-semibold text-slate-700">
          <span>{label}</span>
          {showPercentage && <span className="font-mono">{percentage}%</span>}
        </div>
      )}
      <div className={`w-full bg-slate-200 rounded-full overflow-hidden ${height}`}>
        <div
          className={`${colorClass} ${height} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
