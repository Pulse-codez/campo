"use client";

import Link from "next/link";

const conditions = [
  {
    id: "stress-anxiety",
    label: "Stress & anxiety",
    description: "Managing pressure, overwhelm, and anxious thoughts.",
  },
  {
    id: "low-mood",
    label: "Low mood",
    description: "When everything feels heavy or nothing feels like much.",
  },
  {
    id: "sleep",
    label: "Sleep & rest",
    description: "Trouble falling asleep, staying asleep, or feeling rested.",
  },
  {
    id: "academic-pressure",
    label: "Academic pressure",
    description: "Exams, deadlines, and keeping up with coursework.",
  },
  {
    id: "relationships",
    label: "Relationships",
    description: "Friends, family, dating, and boundaries.",
  },
  {
    id: "grief-loss",
    label: "Grief & loss",
    description: "Coping with death, breakups, and big changes.",
  },
];

export default function ConditionCards() {
  return (
    <section className="section bg-[rgb(255,255,255)]">
      <div className="container">
        <h2 className="section-title">Start with what you are feeling</h2>
        <p className="section-subtitle">
          Tap any area below to see relevant resources and next steps.
        </p>
        <div className="grid md:grid-cols-3 gap-3">
          {conditions.map((c) => (
            <Link
              key={c.id}
              href={`/conditions/${c.id}`}
              className="card text-center hover:border-[rgb(20,137,103)] group"
            >
              <h3 className="font-semibold text-base mb-1 group-hover:text-[rgb(20,137,103)] transition-colors">
                {c.label}
              </h3>
              <p className="text-xs text-[rgb(107,114,128)]">
                {c.description}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
