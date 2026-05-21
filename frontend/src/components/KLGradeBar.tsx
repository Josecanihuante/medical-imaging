import React from 'react';

interface KLGradeBarProps {
  grade: number; // 0-4
  value: number; // 0-1
  label: string;
}

const KLGradeBar: React.FC<KLGradeBarProps> = ({ grade, value, label }) => {
  // Define colors for each KL grade as per frontend.md
  const KL_COLORS = {
    0: "bg-green-100 text-green-800 border-green-300",   // Normal
    1: "bg-yellow-100 text-yellow-800 border-yellow-300", // Dudoso
    2: "bg-orange-100 text-orange-800 border-orange-300", // Mínimo
    3: "bg-red-100 text-red-800 border-red-300",          // Moderado
    4: "bg-red-200 text-red-900 border-red-400",          // Severo
  };

  const getColorForGrade = (g: number) => {
    return KL_COLORS[g] || KL_COLORS[0]; // default to grade 0 if out of range
  };

  const barWidth = `${Math.min(Math.max(value, 0), 1) * 100}%`;

  return (
    <div className="flex flex-col space-y-2">
      <div className="flex justify-between text-sm font-medium">
        <span>{label}</span>
        <span>{grade}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`${getColorForGrade(grade)} h-2.5 rounded-full`}
          style={{ width: barWidth }}
        ></div>
      </div>
    </div>
  );
};

export default KLGradeBar;