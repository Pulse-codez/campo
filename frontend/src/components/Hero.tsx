"use client";

export default function Hero() {
  return (
    <section className="px-4 py-12 md:py-20 text-center">
      <div className="max-w-3xl mx-auto">
        <span className="badge mb-6 block">Confidential · Student-led · Free</span>
        <h1 className="text-4xl md:text-5xl font-bold text-balance mb-6">
          Support that meets you where you are.
        </h1>
        <p className="text-lg text-[rgb(107,114,128)] mb-10 max-w-2xl mx-auto leading-relaxed">
          A private space for university students in Kenya to find campus
          resources, plan around your energy, and reach a human when you need
          one — no judgment, no waiting.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <a href="/find-support" className="btn btn-primary flex-1 sm:flex-none">
            Get support
          </a>
          <a href="/resources" className="btn btn-outline flex-1 sm:flex-none">
            Browse resources
          </a>
        </div>
      </div>
    </section>
  );
}
