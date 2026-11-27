const TONE: Record<string, string> = {
  requested: "bg-[rgba(111,200,255,0.12)] text-[#6FC8FF]",
  booked: "bg-[rgba(27,79,216,0.25)] text-[#cfe0ff]",
  completed: "bg-[rgba(238,243,255,0.08)] text-[rgba(238,243,255,0.7)]",
  cancelled: "bg-[rgba(255,80,80,0.12)] text-[rgb(255,190,190)]",
};

export default function StatusPill({ status }: { status: string }) {
  return (
    <span className={`text-xs font-semibold px-2.5 py-1 rounded-full capitalize ${TONE[status] ?? ""}`}>
      {status}
    </span>
  );
}
