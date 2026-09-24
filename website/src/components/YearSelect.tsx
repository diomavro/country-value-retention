'use client';
export default function YearSelect({ years, value, onChange, label = 'Year' }: { years: number[]; value: number; onChange: (y: number) => void; label?: string }) {
  return (
    <label>
      {label}
      <select value={value} onChange={(e) => onChange(Number(e.target.value))}>
        {years.map((y) => (
          <option key={y} value={y}>
            {y}
          </option>
        ))}
      </select>
    </label>
  );
}
