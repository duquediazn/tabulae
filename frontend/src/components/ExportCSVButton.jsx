export default function ExportCSVButton({ onExport, label = "Export CSV" }) {
  return (
    <button
      role="button"
      onClick={onExport}
      className="h-[36px] bg-indigo-600 hover:bg-indigo-500 text-white px-4 rounded text-sm"
    >
      {label}
    </button>
  );
}
