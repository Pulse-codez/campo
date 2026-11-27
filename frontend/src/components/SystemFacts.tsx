const FACTS = [
  {
    figure: "0",
    label: "AI calls on a crisis message",
    detail: "A fixed safety message with helpline numbers replies instead. The AI is never asked.",
  },
  {
    figure: "1",
    label: "safety check before the AI sees anything",
    detail: "Typed and spoken messages are screened first. The AI only receives what passed the check.",
  },
  {
    figure: "English",
    label: "safety screen language today",
    detail: "Kiswahili and Sheng screening is planned and not built yet.",
  },
  {
    figure: "0",
    label: "voice recordings kept",
    detail: "Your voice is turned into text, and the recording is not saved.",
  },
  {
    figure: "1",
    label: "check-in per month, private to you",
    detail: "Your monthly check-in is visible only to you. Counsellors cannot open it.",
  },
  {
    figure: "Consent",
    label: "gates what counsellors see",
    detail: "A counsellor only sees a request if you have chosen to share counselling with them. Withdrawing takes effect straight away.",
  },
  {
    figure: "1",
    label: "AI model behind one adapter",
    detail: "The conversation model can change without rewriting the safety logic.",
  },
  {
    figure: "Logged",
    label: "sign-ins, consent, and counselling changes",
    detail: "These actions are written to an audit log. Reading records is not logged yet.",
  },
];

export default function SystemFacts() {
  return (
    <section id="facts" className="section scroll-mt-20">
      <div className="container">
        <h2 className="section-title">How it keeps you safe</h2>
        <p className="section-subtitle">
          A few facts about how the companion works today. Items still being built are marked as planned.
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FACTS.map((f) => (
            <div key={f.label} className="panel">
              <p className="text-3xl font-bold text-[rgb(var(--link))]">{f.figure}</p>
              <p className="font-semibold mt-2 leading-snug">{f.label}</p>
              <p className="text-sm text-[rgb(var(--fg)/0.62)] mt-2 leading-relaxed">{f.detail}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
