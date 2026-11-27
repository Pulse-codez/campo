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
    <section id="conditions" className="section scroll-mt-20">
      <div className="container">
        <h2 className="section-title">Start with what you are feeling</h2>
        <p className="section-subtitle">
          Tap any area below to see relevant resources and next steps.
        </p>
        <div className="grid md:grid-cols-3 gap-3">
          {conditions.map((c) => (
            <Link
              key={c.id}
              href="/talk"
              className="card text-center hover:border-[rgba(111,200,255,0.45)] group"
            >
              <h3 className="font-semibold text-base mb-1 group-hover:text-[#6FC8FF] transition-colors">
                {c.label}
              </h3>
              <p className="text-xs text-[rgba(238,243,255,0.62)]">
                {c.description}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
