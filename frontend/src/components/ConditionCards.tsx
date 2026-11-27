import Link from "next/link";

const concerns = [
  {
    label: "Family issues",
    description: "Tension at home, boundaries, and hard conversations with family.",
  },
  {
    label: "Stress",
    description: "Overwhelm, study pressure, and feeling stretched too thin.",
  },
  {
    label: "Peer pressure",
    description: "Pressure to fit in, and learning to say no and trust your own choices.",
  },
  {
    label: "Thoughts of suicide",
    description: "If you are thinking about ending your life, reach a person now. Help is one tap away.",
  },
  {
    label: "Something else",
    description: "Anything else on your mind. You do not need a label to start.",
  },
];

export default function ConditionCards() {
  return (
    <section id="conditions" className="section scroll-mt-20">
      <div className="container">
        <h2 className="section-title">What is on your mind?</h2>
        <p className="section-subtitle">
          Choose what fits when you sign up. It helps us match you with the right virtual therapist.
        </p>
        <div className="grid md:grid-cols-3 gap-3">
          {concerns.map((c) => (
            <Link key={c.label} href="/login?tab=new" className="card text-center hover:border-[rgb(var(--link)/0.5)] group">
              <h3 className="font-semibold text-base mb-1 group-hover:text-[rgb(var(--link))] transition-colors">
                {c.label}
              </h3>
              <p className="text-xs text-[rgb(var(--fg)/0.62)]">{c.description}</p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
