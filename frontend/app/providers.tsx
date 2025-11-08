"use client";

import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import { msalConfig } from "../lib/msalConfig";

export function Providers({ children }: { children: ReactNode }) {
  const [client, setClient] = useState<PublicClientApplication | null>(null);

  useEffect(() => {
    const instance = new PublicClientApplication(msalConfig);
    instance
      .initialize()
      .then(() => {
        const activeAccount = instance.getActiveAccount() ?? instance.getAllAccounts()[0];
        if (activeAccount) {
          instance.setActiveAccount(activeAccount);
        }
        setClient(instance);
      })
      .catch((error) => {
        console.error("Failed to initialise MSAL", error);
      });
  }, []);

  if (!client) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-200">
        <div className="rounded-xl bg-slate-900/60 p-8 shadow-2xl backdrop-blur-lg">
          <h2 className="text-lg font-semibold">Preparing secure authentication…</h2>
          <p className="mt-2 text-sm text-slate-400">
            Hold tight while we load your calendar integration tools.
          </p>
        </div>
      </div>
    );
  }

  return <MsalProvider instance={client}>{children}</MsalProvider>;
}
