# Next.js frontend guidelines

This directory contains the web app built with Next.js (App Router). Follow these practices when
working inside `frontend/`:

- Stick to TypeScript (`.ts`/`.tsx`) for React components and utility modules.
- Keep React server components in `app/` minimal and push interactive behaviour into `"use client"`
  components under `app/` or `components/`.
- Use Tailwind classes for styling; prefer semantic, accessibility-friendly HTML.
- Authentication helpers should reuse `app/providers.tsx`, `lib/msalConfig.ts`, and
  `lib/graphClient.ts`. Do not create alternative MSAL instances.
- Surface calendar data through composable components—if you need new UI states, add them to the
  existing `CalendarIntegrationPanel` or adjacent components rather than duplicating fetch logic.
- Document any new environment variables in `.env.example` and the local README.
