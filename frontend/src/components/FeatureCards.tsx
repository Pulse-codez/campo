"use client";

const features = [
  {
    title: "Find campus resources",
    description:
      "Counselling, health clinic, peer support, legal aid, and emergency contacts — all in one place.",
  },
  {
    title: "Study planner",
    description:
      "Build a weekly study plan that paces load by your energy and upcoming exams.",
  },
  {
    title: "Decision support",
    description:
      "Weigh options against what matters to you, with crisis-aware guardrails.",
  },
  {
    title: "Policy lookup",
    description:
      "Search mental health leave, academic accommodation, and other campus policies.",
  },
];

export default function FeatureCards() {
  return (
    <section className="section">
      <div className="container">
        <h2 className="section-title">What you can do here</h2>
        <p className="section-subtitle">
          Tools designed around how student life actually feels — not how it looks on a brochure.
        </p>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((f) => (
            <div key={f.title} className="card">
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-sm text-[rgb(107,114,128)] leading-relaxed">
                {f.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
