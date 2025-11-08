"use client";

import { useCallback, useMemo, useState } from "react";
import type { AccountInfo } from "@azure/msal-browser";
import { useMsal } from "@azure/msal-react";
import classNames from "classnames";
import { createGraphClient } from "../lib/graphClient";
import { loginRequest } from "../lib/msalConfig";

interface GraphEvent {
  id: string;
  subject: string;
  start?: { dateTime?: string; timeZone?: string };
  end?: { dateTime?: string; timeZone?: string };
  location?: { displayName?: string };
  webLink?: string;
  organizer?: { emailAddress?: { name?: string } };
}

const formatDate = (iso?: string, tz?: string) => {
  if (!iso) {
    return "No start time";
  }

  try {
    const date = new Date(iso);
    return `${date.toLocaleDateString(undefined, {
      weekday: "short",
      month: "short",
      day: "numeric"
    })} · ${date.toLocaleTimeString(undefined, {
      hour: "2-digit",
      minute: "2-digit"
    })} ${tz ?? ""}`.trim();
  } catch (error) {
    return iso;
  }
};

export function CalendarIntegrationPanel() {
  const { instance, accounts } = useMsal();
  const [activeAccount, setActiveAccount] = useState<AccountInfo | null>(
    instance.getActiveAccount() ?? accounts[0] ?? null
  );
  const [status, setStatus] = useState<string>("Connect to Microsoft 365 to sync events");
  const [events, setEvents] = useState<GraphEvent[]>([]);
  const [loading, setLoading] = useState(false);

  const signedIn = Boolean(activeAccount);

  const handleLogin = useCallback(async () => {
    setStatus("Authenticating with Microsoft…");
    try {
      const response = await instance.loginPopup(loginRequest);
      if (response.account) {
        instance.setActiveAccount(response.account);
        setActiveAccount(response.account);
        setStatus(`Signed in as ${response.account.username ?? "your account"}`);
      } else {
        setStatus("Authentication completed, but we could not determine the signed-in account.");
      }
    } catch (error) {
      console.error(error);
      setStatus(`Authentication failed: ${(error as Error).message}`);
    }
  }, [instance]);

  const handleLogout = useCallback(async () => {
    if (!activeAccount) {
      setStatus("You're already signed out.");
      return;
    }

    try {
      await instance.logoutPopup({ account: activeAccount });
      instance.setActiveAccount(null);
      setActiveAccount(null);
      setEvents([]);
      setStatus("Signed out. Connect again when you're ready to sync.");
    } catch (error) {
      console.error(error);
      setStatus(`Sign-out failed: ${(error as Error).message}`);
    }
  }, [activeAccount, instance]);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    setStatus("Loading your next ten events…");
    try {
      const client = await createGraphClient(instance, activeAccount);
      const response = await client
        .api("/me/events")
        .top(10)
        .orderby("start/dateTime")
        .select("id,subject,start,end,location,organizer,webLink")
        .get();

      const pulledEvents: GraphEvent[] = response.value ?? [];

      if (pulledEvents.length === 0) {
        setStatus("No upcoming events found. Create one to see it appear instantly.");
      } else {
        setStatus(`Loaded ${pulledEvents.length} event${pulledEvents.length === 1 ? "" : "s"}.`);
      }

      setEvents(pulledEvents);
    } catch (error) {
      console.error(error);
      setStatus(`Unable to load events: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  }, [activeAccount, instance]);

  const actions = useMemo(() => [
    {
      label: signedIn ? "Refresh events" : "Connect calendar",
      onClick: signedIn ? fetchEvents : handleLogin,
      primary: true
    },
    {
      label: signedIn ? "Sign out" : "Learn about integration",
      onClick: signedIn
        ? handleLogout
        : () =>
            setStatus(
              "We use the official Microsoft identity platform so you retain full control over your calendar."
            ),
      primary: false
    }
  ], [fetchEvents, handleLogin, handleLogout, signedIn]);

  return (
    <section className="mx-auto w-full max-w-5xl rounded-3xl bg-slate-900/60 p-10 shadow-2xl ring-1 ring-slate-700/60 backdrop-blur-xl">
      <header className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-indigo-400">Calendar integration</p>
          <h2 className="mt-2 text-3xl font-semibold text-slate-100">
            {signedIn ? "Your Microsoft 365 events" : "Connect Microsoft 365 or Outlook"}
          </h2>
          <p className="mt-2 max-w-2xl text-base text-slate-300">
            Securely sync Outlook and Microsoft 365 calendars, then enrich events with ADHD-aware
            productivity coaching. We request the smallest set of permissions needed to read and
            write events on your behalf.
          </p>
        </div>
        <div className="flex shrink-0 gap-3">
          {actions.map((action) => (
            <button
              key={action.label}
              type="button"
              onClick={action.onClick}
              disabled={loading && action.primary}
              className={classNames(
                "rounded-full px-6 py-2 text-sm font-semibold transition",
                action.primary
                  ? "bg-indigo-500 text-white shadow-lg shadow-indigo-500/30 hover:bg-indigo-400"
                  : "border border-slate-600 text-slate-200 hover:border-slate-400 hover:text-white"
              )}
            >
              {loading && action.primary ? "Loading…" : action.label}
            </button>
          ))}
        </div>
      </header>

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/60 p-6">
        <p className="text-sm font-medium text-indigo-300">Status</p>
        <p className="mt-1 text-base text-slate-200">{status}</p>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2">
        {events.map((event) => (
          <article
            key={event.id}
            className="flex flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-950/60 p-5 shadow-lg shadow-indigo-950/20"
          >
            <header>
              <h3 className="text-xl font-semibold text-slate-100">
                {event.subject || "Untitled event"}
              </h3>
              <p className="mt-1 text-sm text-indigo-200">
                {formatDate(event.start?.dateTime, event.start?.timeZone)}
              </p>
            </header>
            {event.location?.displayName ? (
              <p className="text-sm text-slate-300">📍 {event.location.displayName}</p>
            ) : null}
            {event.organizer?.emailAddress?.name ? (
              <p className="text-sm text-slate-400">
                Hosted by {event.organizer.emailAddress.name}
              </p>
            ) : null}
            <footer className="mt-auto text-sm">
              {event.webLink ? (
                <a
                  href={event.webLink}
                  target="_blank"
                  rel="noreferrer"
                  className="text-indigo-300 underline decoration-indigo-500/50 underline-offset-4 hover:text-indigo-200"
                >
                  View in Outlook →
                </a>
              ) : (
                <span className="text-slate-500">Synced from your Microsoft 365 calendar</span>
              )}
            </footer>
          </article>
        ))}
      </div>

      {!signedIn ? (
        <div className="mt-8 rounded-2xl border border-dashed border-indigo-500/60 bg-indigo-500/5 p-6 text-sm text-indigo-100">
          <h3 className="text-lg font-semibold text-indigo-200">Why connect your calendar?</h3>
          <ul className="mt-3 list-disc space-y-1 pl-5">
            <li>Surface ADHD-friendly focus windows from your synced events.</li>
            <li>Generate realistic duration estimates powered by our ML services.</li>
            <li>Trigger smart reminders and accountability prompts when transitions are tight.</li>
          </ul>
        </div>
      ) : null}
    </section>
  );
}
