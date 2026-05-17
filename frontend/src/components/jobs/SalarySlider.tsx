"use client";

import { useTranslation } from "@/hooks/useTranslation";
import { Input } from "@/components/ui/input";

export function SalarySlider({
  value,
  onChange,
}: {
  value: [number, number];
  onChange: (value: [number, number]) => void;
}) {
  const { locale } = useTranslation();
  const isRu = locale === "ru";
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-sm">
        <span className="text-surface-500">{isRu ? "Мин" : "Min"}: ${value[0].toLocaleString()}</span>
        <span className="text-surface-500">{isRu ? "Макс" : "Maks"}: ${value[1].toLocaleString()}</span>
      </div>
      <div className="relative h-2 rounded-full bg-surface-200">
        <div
          className="absolute h-full rounded-full bg-gradient-to-r from-purple-500 to-indigo-600"
          style={{
            left: `${(value[0] / 10000) * 100}%`,
            right: `${100 - (value[1] / 10000) * 100}%`,
          }}
        />
        <input
          type="range"
          min={0}
          max={10000}
          step={100}
          value={value[0]}
          onChange={(e) => onChange([parseInt(e.target.value), value[1]])}
          className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
        />
        <input
          type="range"
          min={0}
          max={10000}
          step={100}
          value={value[1]}
          onChange={(e) => onChange([value[0], parseInt(e.target.value)])}
          className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
        />
      </div>
      <div className="flex gap-2">
        <Input
          type="number"
          value={value[0]}
          onChange={(e) => onChange([parseInt(e.target.value) || 0, value[1]])}
          className="text-center text-sm"
          placeholder={isRu ? "Мин" : "Min"}
        />
        <span className="flex items-center text-surface-400">-</span>
        <Input
          type="number"
          value={value[1]}
          onChange={(e) => onChange([value[0], parseInt(e.target.value) || 10000])}
          className="text-center text-sm"
          placeholder={isRu ? "Макс" : "Maks"}
        />
      </div>
    </div>
  );
}
