const TONE: Record<string, string> = {
  requested: "bg-[rgb(var(--link)/0.12)] text-[rgb(var(--link))]",
  booked: "bg-[rgb(var(--accent)/0.25)] text-[rgb(var(--fg))]",
  completed: "bg-[rgb(var(--fg)/0.08)] text-[rgb(var(--fg)/0.7)]",
  cancelled: "bg-[rgb(var(--danger)/0.12)] text-[rgb(var(--danger))]",
};

export default function StatusPill({ status }: { status: string }) {
  return (
    <span className={`text-xs font-semibold px-2.5 py-1 rounded-full capitalize ${TONE[status] ?? ""}`}>
      {status}
    </span>
  );
}
