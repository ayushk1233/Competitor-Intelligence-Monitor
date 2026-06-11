# Watchlist Detail Implementation Report

## APIs Used

| Endpoint | Method | Purpose |
|---|---|---|
| `GET /api/watchlists` | Fetch | Get watchlist name/description for header |
| `GET /api/watchlists/{id}/competitors` | Fetch | List competitors in the watchlist |
| `POST /api/watchlists/{id}/competitors` | Create | Add a competitor to the watchlist |
| `GET /api/watchlists/{id}/runs` | Fetch | List monitoring runs for the watchlist |
| `POST /api/watchlists/{id}/runs` | Create | Trigger a new monitoring run |

## Files Created (8)

| File | Lines | Purpose |
|---|---|---|
| `src/services/competitor.service.ts` | 19 | `fetchCompetitors()`, `addCompetitor()` |
| `src/services/monitoring-run.service.ts` | 19 | `fetchMonitoringRuns()`, `createMonitoringRun()` |
| `src/hooks/use-competitors.ts` | 27 | `useCompetitors()`, `useAddCompetitor()` with invalidation |
| `src/hooks/use-monitoring-runs.ts` | 28 | `useMonitoringRuns()`, `useCreateMonitoringRun()` with invalidation |
| `src/components/watchlists/CompetitorTable.tsx` | 113 | Table: Company Name, Domain, Added Date, Status; 5 skeleton rows; empty state |
| `src/components/watchlists/AddCompetitorDialog.tsx` | 118 | Dialog: Company Name (required) + Domain (optional), Zod + RHF, sonner toasts |
| `src/components/watchlists/RunHistoryTable.tsx` | 156 | Table: Status, Trigger, Checked, Alerts, Sent, Created; 5 skeleton rows; empty state |
| `src/app/(dashboard)/watchlists/[id]/page.tsx` | 121 | Detail page: back button, title, desc, Run Monitoring button, tabs (Competitors/Runs) |

## Query Hooks Created

| Hook | Type | Invalidation |
|---|---|---|
| `useCompetitors(watchlistId)` | `useQuery` | — |
| `useAddCompetitor(watchlistId)` | `useMutation` | `["competitors", watchlistId]` |
| `useMonitoringRuns(watchlistId)` | `useQuery` | — |
| `useCreateMonitoringRun(watchlistId)` | `useMutation` | `["runs", watchlistId]` |

## Screens Implemented

| Screen | Route | Type |
|---|---|---|
| Watchlist Detail | `/watchlists/[id]` | Dynamic (ƒ) |

## Page Structure

```
Header
├── Back button → /watchlists
├── Watchlist name + description (from GET /api/watchlists)
└── "Run Monitoring" button → POST /api/watchlists/{id}/runs { trigger_type: "MANUAL" }

Tabs
├── Competitors (default)
│   ├── "Add Competitor" button → opens dialog
│   └── CompetitorTable
├── Monitoring Runs
│   └── RunHistoryTable
```

## States Covered

| State | CompetitorTable | RunHistoryTable | Page Header |
|---|---|---|---|
| **Loading** | 5 skeleton rows | 5 skeleton rows | Skeleton title/desc |
| **Empty** | "No competitors yet" + CTA | "No monitoring runs yet" | Watchlist name (found) |
| **Data** | Full table with status badges | Full table with status badges | Name + description |
| **Error** | Silent (TanStack retry) | Silent (TanStack retry) | Fallback title |

## Build Result

```
✓ Compiled successfully
✓ TypeScript finished — zero errors
✓ Routes: /watchlists (static), /watchlists/[id] (dynamic)
```

## Remaining Work

**Not started (waiting for approval):**
- Notifications
- Monitoring Runs UI (beyond table)
- Competitor detail/edit/remove
- Settings
- Charts
