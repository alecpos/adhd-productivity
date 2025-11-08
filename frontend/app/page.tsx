import { CalendarIntegrationPanel } from "../components/CalendarIntegrationPanel";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-start px-6 pb-24 pt-24 text-slate-100">
      <section className="w-full max-w-4xl text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.4em] text-indigo-300">
          ADHD Productivity Platform
        </p>
        <h1 className="mt-6 text-4xl font-bold leading-tight sm:text-5xl">
          Calendar intelligence that respects your neurodivergent rhythms
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-300">
          Connect Outlook or Microsoft 365 calendars in seconds, then unlock adaptive reminders,
          mindful time estimation, and circadian-aware scheduling backed by our machine learning
          engine.
        </p>
      </section>

      <div className="mt-12 w-full">
        <CalendarIntegrationPanel />
      </div>

      <section className="mt-16 grid w-full max-w-4xl gap-6 rounded-3xl border border-slate-800 bg-slate-900/40 p-10 text-left shadow-2xl">
        <h2 className="text-2xl font-semibold text-slate-100">What happens after you connect?</h2>
        <ul className="grid gap-4 text-base text-slate-300 md:grid-cols-2">
          <li className="rounded-2xl bg-slate-950/60 p-4">
            <h3 className="text-lg font-semibold text-indigo-200">Adaptive focus plans</h3>
            <p className="mt-2 text-sm text-slate-300">
              We analyse circadian energy models to recommend focus blocks that match the unique
              productivity rhythms highlighted in Epic 4.
            </p>
          </li>
          <li className="rounded-2xl bg-slate-950/60 p-4">
            <h3 className="text-lg font-semibold text-indigo-200">Realistic timing</h3>
            <p className="mt-2 text-sm text-slate-300">
              The stochastic time estimation engine from Epic 2 learns how long tasks truly take so
              we can negotiate smarter buffers between events.
            </p>
          </li>
          <li className="rounded-2xl bg-slate-950/60 p-4">
            <h3 className="text-lg font-semibold text-indigo-200">Smart reminders</h3>
            <p className="mt-2 text-sm text-slate-300">
              Epic 3's proactive forgetfulness mitigation triggers accountability nudges when
              transitions are likely to slip.
            </p>
          </li>
          <li className="rounded-2xl bg-slate-950/60 p-4">
            <h3 className="text-lg font-semibold text-indigo-200">Ethical insights</h3>
            <p className="mt-2 text-sm text-slate-300">
              Epic 5's transparency pipelines keep you in control with explainable AI for every
              recommendation we surface.
            </p>
          </li>
        </ul>
      </section>
    </main>
  );
}
