# ADHD Productivity Frontend (Next.js)

This package delivers the web experience for the ADHD Productivity platform using the Next.js App
Router. It replaces the legacy Expo experiment with a production-friendly web surface that can
connect directly to Microsoft 365 and Outlook calendars via the Microsoft Graph API.

## Getting started

```bash
cd frontend
npm install
npm run dev
```

Then visit http://localhost:3000.

## Environment variables

Create a `.env.local` file using the template below. These values come from an Azure App
Registration that supports the Microsoft identity platform.

```
NEXT_PUBLIC_AZURE_CLIENT_ID=your-client-id
NEXT_PUBLIC_AZURE_TENANT_ID=your-tenant-id-or-common
NEXT_PUBLIC_AZURE_REDIRECT_URI=http://localhost:3000
NEXT_PUBLIC_GRAPH_SCOPES=User.Read Calendars.Read Calendars.ReadWrite offline_access
```

## Features

- App Router architecture with server and client components
- Microsoft Graph integration for Outlook/Microsoft 365 calendars
- Tailwind-powered UI tuned for neurodivergent-friendly readability
- Clear separation between authentication plumbing and calendar insights UI

## Scripts

- `npm run dev` – start a local development server
- `npm run build` – generate an optimized production build
- `npm run start` – start the production server
- `npm run lint` – run Next.js lint rules (includes TypeScript and React best practices)

## Folder structure

```
frontend/
├── app/
│   ├── layout.tsx      # Root layout wiring Providers
│   ├── page.tsx        # Landing page experience
│   ├── globals.css     # Tailwind + base styling
│   └── providers.tsx   # MSAL provider bootstrap
├── components/
│   └── CalendarIntegrationPanel.tsx
├── lib/
│   ├── graphClient.ts  # Microsoft Graph helper
│   └── msalConfig.ts   # Auth configuration sourced from env vars
└── ...config files
```
