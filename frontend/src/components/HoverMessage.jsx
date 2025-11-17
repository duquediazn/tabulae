import { useState } from "react";

export default function HoverMessage({ text, icon = "ℹ️", className = "" }) {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div
      className={`absolute top-4 right-4 w-64 p-3 bg-indigo-50 border border-indigo-300 rounded text-sm text-indigo-900 shadow-md
                  opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 ${className}`}
    >
      <div className="flex justify-between items-start">
        <span>
          {icon} {text}
        </span>
        <button
          role="button"
          onClick={() => setIsVisible(false)}
          className="ml-2 text-indigo-500 hover:text-indigo-700"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
