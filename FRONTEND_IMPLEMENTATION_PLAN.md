# CIM Frontend Implementation Plan

## SECTION 1 — Executive Summary

**What CIM is:**
The Competitor Intelligence Monitor (CIM) is a platform that automatically extracts, tracks, and analyzes strategic intelligence from competitor websites. It detects messaging shifts, ICP changes, and market momentum, issuing alerts to integrated channels.

**Frontend Goals:**
Deliver a high-performance, robust, and highly polished dashboard application to manage watchlists, monitor competitor intelligence, and configure alerts.

**Current Backend Status:**
The RESTful backend is 100% complete and production-ready. All endpoints, schemas, authentication (JWT), and background pipelines (Celery) are deployed and verified.

**Frontend Scope:**
Implementing the full Next.js 15 client according to this architecture plan without modifying backend API contracts or schemas.

**Out-of-scope features:**
- WebSockets/Real-time streaming (we use polling).
- Complex user roles/teams (V1 is single-user focused).
- Complex alert suppression configuration (currently basic toggle).

**V1 Features:**
- Auth, Dashboard, Watchlists, Competitors, Monitoring Run triggers, and Notification Channels.

**V1.1 Features:**
- Historical trend visualization, Advanced drift settings.

**Future Vision:**
- Fully autonomous agentic competitive response systems integrated with the dashboard.

---

## SECTION 2 — Route Map

```text
/
├── (auth)/
│   ├── login/
│   └── signup/
├── (dashboard)/
│   ├── dashboard/
│   ├── watchlists/
│   │   ├── page.tsx
│   │   └── [id]/
│   │       └── page.tsx
│   ├── notifications/
│   └── settings/
```

- `/(auth)/login`: User login form. Uses `POST /api/auth/login`. Public. Uses Public Layout.
- `/(auth)/signup`: User registration. Uses `POST /api/auth/signup`. Public. Uses Public Layout.
- `/(dashboard)/dashboard`: Home metrics. Uses `GET /api/dashboard/*`. Protected. Uses Protected Layout.
- `/(dashboard)/watchlists`: Master list of watchlists. Uses `GET /api/watchlists` & `POST /api/watchlists`. Protected. Uses Protected Layout.
- `/(dashboard)/watchlists/[id]`: Detailed view for a specific watchlist (Competitors Tab, Runs Tab, Trigger Run). Uses `GET /api/watchlists/[id]/*`. Protected. Uses Protected Layout.
- `/(dashboard)/notifications`: Notification channel settings. Uses `GET|POST|PUT|DELETE /api/notifications/channels`. Protected. Uses Protected Layout.
- `/(dashboard)/settings`: Future user profile settings. Uses `GET /api/auth/me`. Protected. Uses Protected Layout.

---

## SECTION 3 — Application Architecture

```text
src/
├── app/          # Next.js App Router (pages, layouts, error.tsx, not-found.tsx, loading.tsx)
├── components/   # Pure presentational UI components
│   ├── ui/       # shadcn/ui generic primitives (Button, Input, Table)
│   └── layout/   # Shared layout wrappers (Sidebar, Topbar)
├── features/     # Domain-driven feature modules
│   ├── auth/
│   │   ├── api/
│   │   ├── hooks/
│   │   ├── schemas/
│   │   └── components/
│   ├── dashboard/
│   ├── watchlists/
│   └── notifications/
├── providers/    # Global React Context providers (Auth, QueryClient, Theme)
├── lib/          # Utilities, Zod schemas, date formatting, Axios interceptors
├── constants/    # Hardcoded values, query keys, route paths
├── types/        # TypeScript interfaces matching backend models
└── styles/       # Global CSS, Tailwind config
```

---

## SECTION 4 — Layout Architecture

### Public Layout
Used for `/login` and `/signup`.
Contains: A centered, minimal aesthetic box for authentication forms, using the locked CIM background colors.

### Protected Layout
Used for all `/dashboard/*` routes.
- **Sidebar**: Primary navigation (`Dashboard`, `Watchlists`, `Notifications`). Includes a "User" profile section at the bottom for logout.
- **Topbar**: Contextual actions, Breadcrumbs, and Mobile Menu toggle.
- **Content Container**: Scrollable main area where `children` are injected. Wraps `children` with consistent max-width padding.

**Next.js App Router Nested Layouts**:
The `(dashboard)` route group has a `layout.tsx` that wraps all protected pages. It verifies the auth token before rendering and mounts the Sidebar/Topbar shell.

### Error Boundary Strategy
- `app/error.tsx`: Catch-all for uncaught render errors. Shows a friendly CIM-branded "Something went wrong" screen with a reset button.
- `app/not-found.tsx`: Global 404 page for unmatched routes.

---

## SECTION 5 — Authentication Architecture

### Auth Flow
1. **Signup/Login**: User submits form. TanStack mutation calls API. JWT is returned.
2. **Session Restore**: JWT is read from `LocalStorage` and user data is loaded using `GET /api/auth/me`.
3. **Logout**: JWT is purged from storage and user redirected to `/login`.

### JWT Strategy
- **Storage**: `LocalStorage`. The backend returns a standard JSON payload with the bearer token; no cookies are automatically set.
- **Axios Interceptor**: A global Axios interceptor (`lib/api-client.ts`) retrieves the token from `LocalStorage` and appends it to the `Authorization: Bearer <token>` header on every request. On `401 Unauthorized`, it triggers a logout redirect.

### Auth Provider
- **Responsibilities**: Provide `user`, `isAuthenticated`, `login`, `logout` functions via React Context.
- **State**: `user | null`, `isLoading`.
- **Loading Handling**: Blocks rendering of Protected Layout until `GET /api/auth/me` resolves or fails.
- **Error Handling**: Clears `LocalStorage` on 401 and sets `isAuthenticated` to false.

---

## SECTION 6 — API Layer Architecture

### Environment Strategy
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```
```ts
// lib/api-client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});
```

### Services
Inside `features/*/api/`:
- `auth.service.ts`
- `dashboard.service.ts`
- `watchlist.service.ts`
- `notification.service.ts`

All functions use `apiClient` and return heavily typed Promises mapped to `types/api.ts`.

---

## SECTION 7 — TanStack Query Architecture

### Query Keys
```ts
export const QUERY_KEYS = {
  me: ["me"],
  dashboardSummary: ["dashboard-summary"],
  recentAlerts: ["recent-alerts"],
  recentRuns: ["recent-runs"],
  activity: ["activity"],
  watchlists: ["watchlists"],
  competitors: (watchlistId: string) => ["competitors", watchlistId],
  runs: (watchlistId: string) => ["runs", watchlistId],
  notificationChannels: ["notification-channels"],
};
```

### Query Hooks
- `useCurrentUser()`
- `useDashboardSummary()` (Includes polling: `refetchInterval: 10000`)
- `useRecentAlerts()`
- `useRecentRuns()` (Includes polling: `refetchInterval: 10000`)
- `useDashboardActivity()`
- `useWatchlists(limit, offset)`
- `useCompetitors(watchlistId)`
- `useMonitoringRuns(watchlistId)` (Includes polling: `refetchInterval: 10000`)
- `useNotificationChannels()`

### Mutation Hooks
- `useLogin()` -> sets token
- `useSignup()` -> sets token
- `useCreateWatchlist()` -> invalidates `watchlists`
- `useAddCompetitor()` -> invalidates `competitors(id)`
- `useCreateMonitoringRun()` -> invalidates `runs(id)`, `dashboardSummary`
- `useCreateNotificationChannel()` -> invalidates `notificationChannels`
- `useToggleNotificationChannel()` -> invalidates `notificationChannels`
- `useDeleteNotificationChannel()` -> invalidates `notificationChannels`

---

## SECTION 8 — TypeScript Types

All types live in `types/api.ts` or inside their respective `features/*/schemas/`.

*(See Section 19 for Exact Payloads)*

---

## SECTION 9 — Component Architecture

```text
features/
├── dashboard/components/
│   ├── MetricCard.tsx
│   ├── AlertFeed.tsx
│   ├── RecentRunsTable.tsx
│   └── ActivityTimeline.tsx
├── watchlists/components/
│   ├── WatchlistCard.tsx
│   ├── CompetitorTable.tsx
│   ├── RunHistoryTable.tsx
│   ├── CreateWatchlistModal.tsx
│   └── AddCompetitorModal.tsx
├── notifications/components/
│   ├── ChannelList.tsx
│   └── CreateChannelModal.tsx
```

**Props & Reusability**:
- `MetricCard`: Takes `title`, `value`, `icon`, `trend`. Highly reusable.
- `CompetitorTable`: Takes `competitors` data array, isolated to Watchlist Detail.
- Forms use Modal wrappers that control open/close state locally, executing `onSuccess` callbacks to invalidate queries.

---

## SECTION 10 — Page Architecture

### Dashboard
- **Purpose**: At-a-glance system metrics.
- **Components**: `MetricCard`, `AlertFeed`, `RecentRunsTable`, `ActivityTimeline`.
- **Queries**: `useDashboardSummary`, `useRecentAlerts`, `useRecentRuns`, `useDashboardActivity`.
- **States**: Skeleton grids while loading. Empty states if no data.

### Watchlists
- **Purpose**: Paginated directory of monitoring configurations.
- **Components**: `WatchlistCard`, `CreateWatchlistModal`.
- **Queries**: `useWatchlists`.
- **Mutations**: `useCreateWatchlist`.

### Watchlist Detail (`watchlists/[id]`)
- **Purpose**: Drill down into competitors and run history for one watchlist. Highly critical V1 screen.
- **Architecture**:
  - **Tabs Layout**: Switch between `Competitors` and `Monitoring Runs`.
  - **Action Bar**: "Trigger Run" action button.
- **Components**: `CompetitorTable`, `RunHistoryTable`, `AddCompetitorModal`.
- **Queries**: `useCompetitors(id)`, `useMonitoringRuns(id)`.
- **Mutations**: `useAddCompetitor`, `useCreateMonitoringRun`.

### Notifications
- **Purpose**: Manage delivery integrations.
- **Components**: `ChannelList`, `CreateChannelModal`.
- **Queries**: `useNotificationChannels`.
- **Mutations**: `useCreateNotificationChannel`, `useDeleteNotificationChannel`.

---

## SECTION 11 — Forms Architecture

### Login Form
- **Fields**: `email`, `password`.
- **Submit**: Triggers `useLogin`.

### Create Watchlist Form
- **Fields**: `name`, `description`. (Backend defaults `monitoring_frequency` to `"DAILY"`).
- **Success**: Closes modal, toasts "Watchlist Created", invalidates `watchlists` query.

### Add Competitor Form
- **Fields**: `company_name`, `domain` (optional).
- **Success**: Closes modal, invalidates `competitors` query.

### Create Notification Channel Form
- **Fields**: `channel_type` (Select: SLACK | EMAIL | WEBHOOK), `destination`, `label` (optional).
- **Validation**: Ensure type matches exactly what backend accepts (`SLACK`, `EMAIL`, `WEBHOOK`).

---

## SECTION 12 — Design System Mapping

**Locked CIM Design System:**

- **Backgrounds**:
  - Page/Body: `#0B1020`
  - Cards/Containers: `#121826`
  - Borders/Hover States: `#1A2332`
- **Primary Color**: `#14B8A6` (Teal)
- **Status Colors**:
  - Success: `#22C55E`
  - Warning: `#F59E0B`
  - Danger: `#EF4444`
  - Info: `#8B5CF6`
- **Typography**: Inter (sans-serif). High contrast text.

Use `shadcn/ui` components but override the CSS variables (`--background`, `--primary`, etc.) to match these EXACT hex codes. Do NOT use default Slate/Zinc.

---

## SECTION 13 — State Management Strategy

- **Server State**: Managed strictly by **TanStack Query**. Caching, refetching, and polling.
- **Form State**: Managed entirely by **React Hook Form** + Zod.
- **UI State**: Managed by local `useState` or URL search params.
- **Global State**: **React Context** used only for Authentication. Avoid Redux/Zustand.

---

## SECTION 14 — Error Handling Strategy

- **401 Unauthorized**: Handled by Axios Interceptor -> Redirect to `/login` and purge `LocalStorage`.
- **403 Forbidden**: Toast "Permission Denied".
- **404 Not Found**: Display `app/not-found.tsx` illustration.
- **500 Server Error**: Toast "Internal Server Error" and log to console.
- **Network Failure**: Toast "Network Error. Please check your connection."
- **Validation Errors (400/422)**: Extract detail message and display inline under relevant form fields.

---

## SECTION 15 — Loading Strategy

- **Skeletons**: Use `shadcn/ui` Skeleton for dashboard cards and tables.
- **Spinners**: Used inside buttons (`LucideLoader2` spinning) during mutations.
- **Button States**: `disabled={isPending}` alongside a spinner.
- **Page Transitions**: Next.js `loading.tsx` for route transitions.

---

## SECTION 16 — Responsive Strategy

- **Desktop**: Persistent Sidebar, wide tables.
- **Tablet**: Collapsible Sidebar, fluid grids.
- **Mobile**: Sidebar becomes a Hamburger Drawer. Tables scroll horizontally with `overflow-x-auto`.

---

## SECTION 17 — Implementation Order

1. **Phase 1: Project Setup** (Next.js, UI config, exact hex codes, API client).
2. **Phase 2: Authentication** (AuthProvider, LocalStorage, Login/Signup).
3. **Phase 3: Layout** (Sidebar, Topbar, Protected wrapper, error boundaries).
4. **Phase 4: Dashboard** (Metric cards, alert feeds, run tables, polling hooks).
5. **Phase 5: Watchlists** (Directory, create modal).
6. **Phase 6: Watchlist Detail & Runs** (Tabs, Competitor Table, Trigger Run polling).
7. **Phase 7: Notifications** (Channel mapping, modals).
8. **Phase 8: Polish** (Skeletons, empty states, responsive checks).

---

## SECTION 18 — Integration Checklist

- [ ] Next.js + Tailwind + shadcn/ui configured with EXACT colors.
- [ ] Environment variables (`NEXT_PUBLIC_API_URL`) working.
- [ ] API Client intercepting and attaching JWT from `LocalStorage`.
- [ ] Dashboard aggregates polling properly (`refetchInterval: 10000`).
- [ ] Watchlists fetching, paginating, and creating.
- [ ] Watchlist Detail tabs and action buttons fully wired.
- [ ] Competitors successfully adding to watchlists.
- [ ] Monitoring runs triggering without 500 errors.
- [ ] Notifications fetching and creating.
- [ ] 401s triggering automatic logouts.

---

## SECTION 19 — Backend Contract Validation

These are the EXACT payloads required and returned by the FastAPI backend. Do not deviate.

### POST /api/auth/signup
**Request:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword",
  "display_name": "Optional Name"
}
```
**Response:**
```json
{
  "access_token": "eyJhb...",
  "token_type": "bearer",
  "user_id": "uuid",
  "email": "user@example.com",
  "display_name": "Optional Name"
}
```

### POST /api/auth/login
**Request:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword"
}
```
**Response:** Same as signup.

### GET /api/dashboard/summary
**Response:**
```json
{
  "watchlists": 5,
  "competitors": 12,
  "monitoring_runs_today": 3,
  "notification_channels": 2
}
```

### GET /api/watchlists
**Query:** `?limit=20&offset=0`
**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "name": "SaaS Competitors",
      "description": "Tracking main rivals",
      "is_active": true,
      "monitoring_frequency": "DAILY",
      "last_monitored_at": "2026-06-10T12:00:00Z",
      "next_run_at": "2026-06-11T12:00:00Z",
      "created_at": "2026-06-01T12:00:00Z"
    }
  ]
}
```

### POST /api/watchlists
**Request:**
```json
{
  "name": "SaaS Competitors",
  "description": "Tracking main rivals",
  "monitoring_frequency": "DAILY" 
}
```
*(Note: `monitoring_frequency` is optional and defaults to `"DAILY"` in the backend).*
**Response:** Returns created Watchlist object.

### GET /api/watchlists/{id}/competitors
**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "watchlist_id": "uuid",
      "company_name": "RivalCorp",
      "domain": "rivalcorp.com",
      "is_active": true,
      "added_at": "2026-06-10T12:00:00Z"
    }
  ]
}
```

### POST /api/watchlists/{id}/competitors
**Request:**
```json
{
  "company_name": "RivalCorp",
  "domain": "rivalcorp.com"
}
```
**Response:** Returns created Competitor object.

### GET /api/watchlists/{id}/runs
**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "watchlist_id": "uuid",
      "trigger_type": "MANUAL",
      "status": "COMPLETED",
      "competitors_checked": 4,
      "alerts_generated": 1,
      "notifications_sent": 1,
      "celery_task_id": "task-uuid",
      "started_at": "2026-06-10T12:00:00Z",
      "completed_at": "2026-06-10T12:05:00Z",
      "created_at": "2026-06-10T12:00:00Z"
    }
  ]
}
```

### POST /api/watchlists/{id}/runs
**Request:**
```json
{
  "trigger_type": "MANUAL"
}
```
**Response:** Returns created MonitoringRun object.

### GET /api/notifications/channels
**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "channel_type": "SLACK",
      "destination": "https://hooks.slack.com/...",
      "label": "Engineering Team",
      "enabled": true,
      "verified": true,
      "created_at": "2026-06-10T12:00:00Z"
    }
  ]
}
```

### POST /api/notifications/channels
**Request:**
```json
{
  "channel_type": "SLACK", 
  "destination": "https://hooks.slack.com/...",
  "label": "Engineering Team"
}
```
*(Note: `channel_type` must be exactly `"SLACK"`, `"EMAIL"`, or `"WEBHOOK"`).*
**Response:** Returns created NotificationChannel object.

### PUT /api/notifications/channels/{id}
**Request:**
```json
{
  "enabled": false
}
```
**Response:** Returns updated NotificationChannel object.

### DELETE /api/notifications/channels/{id}
**Response:** Returns 200 OK.
