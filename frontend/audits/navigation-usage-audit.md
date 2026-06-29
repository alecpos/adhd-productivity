# Navigation, Tabs, Drawer, Context, API, and Props Audit

## Scope

This audit focuses on the current frontend navigation surface and the code paths it pulls in:

- Expo Router layouts and route screens under `frontend/app`
- Dashboard tab pages and tab content components
- Any side-drawer/menu implementation references
- Context hooks and providers used by those screens
- Direct API route usage from pages/components/contexts/services
- Props declared, props passed, and likely-unused props/imports
- Generated export/database/schema noise that should not drive app logic

For repeatable output as the app grows, run:

```bash
cd frontend
npm run audit:navigation
```

This generates:

- `frontend/audits/navigation-usage-report.md`
- `frontend/audits/navigation-usage-report.json`

Use the JSON report for consolidation work and the Markdown report for review comments.

## Current navigation map

### Root shell

`frontend/app/_layout.tsx` currently wraps the app with:

- `SafeAreaProvider`
- `ThemeProvider`
- `NotificationProvider`
- root `Stack`

It does **not** mount the same provider tree used in tests (`AuthProvider`, `TaskProvider`, `ADHDSettingsProvider`, `CalendarProvider`, `GamificationProvider`, `HyperfocusProvider`, `MentalHealthProvider`). Any screen using those contexts must be under another provider or it will fail at runtime.

### Authenticated stack

`frontend/app/(auth)/_layout.tsx` is the current authenticated route layout. It declares stack screens:

- `index`
- `mental-health`
- `calendar-management`
- `scheduling`
- `calendar-settings`
- `fidget/index`

`fidget/index` is declared as a route but no matching `frontend/app/(auth)/fidget/index.tsx` file was found during review. The app does have dashboard-level `FidgetTab` components, so this is likely a stale route entry or a missing page.

### Legacy/alternate tab shell

`frontend/app/(app)/_layout.tsx` declares bottom tabs for:

- `tasks`
- `wellness`
- `calendar`
- `insights`

However, matching route files for those tab names were not found in the review pass. This looks like a second navigation shell that should either become the canonical shell or be removed.

### Dashboard inner tabs

`frontend/app/(auth)/index.tsx` is the current dashboard and owns an RNEUI `Tab` plus `TabView` with five user-facing tabs:

- Tasks
- Wellness
- Calendar
- Insights
- Fidget

The dashboard imports both `InsightsTab` and `ADHDDashboard`, but the Insights `TabView.Item` renders `ADHDDashboard` rather than `InsightsTab`. Decide which component is canonical and remove the unused import/component path.

### Side drawer / menu

No live `Drawer.Screen` or side-drawer implementation was found in the current app route files during review. Existing navigation docs still reference drawer/menu update surfaces, so the next step is to either:

1. add a real drawer from a single route registry, or
2. remove drawer references from docs and stale code until the drawer exists.

## Context/provider consolidation findings

### Provider mismatch

Tests mount a richer provider tree than the app root. Align the actual app root with the contexts used by live routes, or move feature routes under layouts that mount the required providers.

Suggested canonical provider order:

```tsx
<SafeAreaProvider>
  <ThemeProvider theme={theme}>
    <AuthProvider>
      <NotificationProvider>
        <TaskProvider>
          <CalendarProvider>
            <MentalHealthProvider>
              <HyperfocusProvider>
                <GamificationProvider>
                  {children}
                </GamificationProvider>
              </HyperfocusProvider>
            </MentalHealthProvider>
          </CalendarProvider>
        </TaskProvider>
      </NotificationProvider>
    </AuthProvider>
  </ThemeProvider>
</SafeAreaProvider>
```

### Auth logic duplication

`AuthContext` performs routing after auth initialization, and `(auth)/_layout.tsx` also redirects unauthenticated users. Pick one guard location.

Recommendation: keep redirects in route layouts and make `AuthContext` state-only. This prevents context side effects from fighting route-level guards.

### API client import drift

Several files import `api` from `@/lib/api`, but the visible API client is `frontend/app/services/api.ts` and exports a default `api`. Consolidate into one client path, for example:

```ts
// frontend/lib/api.ts
export { default as api } from '@/app/services/api';
```

or move the existing client to `frontend/lib/api.ts` and update imports.

### Task logic split

Task logic currently appears in at least four places:

- `TaskContext`
- `app/(auth)/tasks/index.tsx`
- `app/(auth)/tasks/create.tsx`
- `app/(auth)/tasks/[id].tsx`
- `app/(auth)/calendar-management.tsx`

The task index uses `TaskContext`, while create/edit/calendar management bypass it with direct `api`, `axios`, Redux, or `TaskService` usage. Pick one source of truth.

Recommendation: route screens should call `TaskContext` actions, and `TaskContext` should call the task service/API client. Delete direct localhost axios calls from screens.

## API route consistency findings

API routes are mixed across direct localhost URLs, `/tasks`, and `/api/...` routes. Normalize all frontend calls to one API client and one route convention.

Examples to consolidate:

- `http://localhost:8000/tasks/${id}` in the task edit route
- `http://localhost:8000/api/auth/register` in unauth register
- `/tasks` in task create
- `/api/calendar/events` in task create
- `/api/hyperfocus/session` and `/api/hyperfocus/statistics` in hyperfocus context

Recommended target:

```ts
api.get('/api/tasks')
api.post('/api/tasks')
api.put('/api/tasks/:id')
api.post('/api/tasks/:id/complete')
```

If the backend truly exposes both `/tasks` and `/api/tasks`, add a small route map file and migrate one screen at a time.

## Props/import cleanup findings

Run the generated report for the complete list. Manual hotspots found during this review:

- `app/(auth)/index.tsx`: `router`, `appTheme`, `showToast`, `recommendedActions`, and `InsightsTab` look unused or mismatched.
- `app/(auth)/tasks/index.tsx`: `user`, `filter`, `setFilter`, `Button`, and `Badge` look stale; tasks are rendered directly from `tasks` instead of a filtered list.
- `components/TaskCard.tsx`: `StartSessionRequest` and local `theme` look unused; `TaskCardProps` fields are used.
- `app/(auth)/scheduling.tsx`: uses `Tabs.Screen` with `component` props inside a page and includes static 2024 schedule data. Convert this to nested Expo Router route files or a normal in-page tab component.
- `app/(unauth)/login.tsx`: `Link href="/register"` should be checked against the current `(unauth)` group route convention.

## Generated/db/schema noise candidates

The audit script flags generated exports and dump-like files so they can be reviewed before deletion. Current obvious candidates include:

- `frontend/frontend_consolidated_export.txt`
- `frontend/app_export.txt`
- `frontend/app_(auth)_export.txt`
- `frontend/navigation_export.txt`
- `frontend/screens_export.txt`

These files are useful for snapshots, but they should not be imported, searched as source of truth, or used to decide live navigation behavior.

## Consolidation plan

1. Pick one shell: either `(auth)` stack plus dashboard inner tabs, or `(app)` bottom tabs. Remove the other after migration.
2. Create a route registry for tab/drawer/menu items and derive UI from it.
3. Move auth redirects into route layouts only.
4. Mount the real provider tree in `app/_layout.tsx` or in the authenticated layout.
5. Move all API calls through one API client and one route map.
6. Move task create/edit/complete/delete through `TaskContext`.
7. Delete generated export/db/schema noise after confirming the audit report and CI are clean.

## Suggested route registry shape

```ts
type AppRoute = {
  key: string;
  title: string;
  href: string;
  icon: string;
  surface: Array<'tab' | 'drawer' | 'dashboard'>;
  requiresAuth: boolean;
};

export const APP_ROUTES: AppRoute[] = [
  { key: 'tasks', title: 'Tasks', href: '/(auth)/tasks', icon: 'list-outline', surface: ['tab', 'drawer', 'dashboard'], requiresAuth: true },
  { key: 'wellness', title: 'Wellness', href: '/(auth)/mental-health', icon: 'heart-outline', surface: ['tab', 'drawer', 'dashboard'], requiresAuth: true },
  { key: 'calendar', title: 'Calendar', href: '/(auth)/calendar-management', icon: 'calendar-outline', surface: ['tab', 'drawer', 'dashboard'], requiresAuth: true },
  { key: 'insights', title: 'Insights', href: '/(auth)', icon: 'analytics-outline', surface: ['tab', 'drawer', 'dashboard'], requiresAuth: true },
  { key: 'settings', title: 'Settings', href: '/(auth)/calendar-settings', icon: 'settings-outline', surface: ['drawer'], requiresAuth: true },
];
```

The audit script is intentionally independent of this registry, so it can keep reporting drift as new routes/components are added.
