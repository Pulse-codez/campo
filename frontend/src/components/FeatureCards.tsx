const features = [
  {
    title: "Talk, by text or voice",
    description:
      "Say what is on your mind. Replies are read aloud, and typing is always there as a fallback.",
  },
  {
    title: "Virtual therapists",
    description:
      "Choose a companion that fits what you are going through. They are AI companions, not licensed clinicians.",
  },
  {
    title: "Kind words",
    description:
      "Ask for a short encouraging message, or write a private note to someone who matters to you.",
  },
  {
    title: "Monthly check-in",
    description:
      "Once a month, write how you are feeling and where you are going in life. Only you can read it.",
  },
  {
    title: "Counselling requests",
    description:
      "Ask for time with a campus counsellor. Counsellors only see requests from students who chose to share them.",
  },
  {
    title: "Help now",
    description:
      "An SOS button and an urgent help page with the helpline and campus security, no account needed.",
  },
];

export default function FeatureCards() {
  return (
    <section id="features" className="section scroll-mt-20">
      <div className="container">
        <h2 className="section-title">What you can do here</h2>
        <p className="section-subtitle">
          Built around how student life actually feels, with a person one request away.
        </p>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f) => (
            <div key={f.title} className="card">
              <h3 className="font-semibold text-lg mb-2 text-[rgb(var(--fg))]">{f.title}</h3>
              <p className="text-sm text-[rgb(var(--fg)/0.62)] leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
