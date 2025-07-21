export default function ContainerFilters({ children, extraContent = null }) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
      <div className="flex flex-wrap gap-4">{children}</div>
      {extraContent && <div>{extraContent}</div>}
    </div>
  );
}
