const FACTS = [
  {
    figure: "3",
    label: "languages in the safety screen",
    detail: "English, Kiswahili and Sheng. Every message is screened before anything else happens.",
  },
  {
    figure: "0",
    label: "model calls on an imminent-risk message",
    detail: "A fixed crisis protocol replies instead, with emergency contacts and a direct question about safety.",
  },
  {
    figure: "1",
    label: "safety check before any model sees a transcript",
    detail: "Voice is transcribed, then screened exactly like typed text. The model only receives what passed.",
  },
  {
    figure: "5 min",
    label: "wait before escalating to the next counsellor",
    detail: "The on-call counsellor is paged first. If they do not acknowledge, the secondary counsellor is paged, then the duty officer.",
  },
  {
    figure: "0",
    label: "audio kept by default",
    detail: "Raw audio is discarded after transcription. Keeping it needs an explicit opt-in.",
  },
  {
    figure: "1",
    label: "university boundary per account",
    detail: "Students register with their own university email. Counsellors only see their own campus, and only students who consented.",
  },
  {
    figure: "Every",
    label: "record read or write is audited",
    detail: "Each access to a student record writes an audit event, and the audit log is append-only.",
  },
  {
    figure: "1",
    label: "model behind one adapter",
    detail: "The conversation model can change without rewriting the safety logic, so the vendor choice stays open.",
  },
];

export default function SystemFacts() {
  return (
    <section id="facts" className="section scroll-mt-20">
      <div className="container">
        <h2 className="section-title">Built to keep students safe</h2>
        <p className="section-subtitle">
          A few facts about how the companion works, taken from its technical specification.
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FACTS.map((f) => (
            <div key={f.label} className="panel">
              <p className="text-3xl font-bold text-[#6FC8FF]">{f.figure}</p>
              <p className="font-semibold mt-2 leading-snug">{f.label}</p>
              <p className="text-sm text-[rgba(238,243,255,0.6)] mt-2 leading-relaxed">{f.detail}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
