# CIM_FRONTEND_V2_MASTER_PROMPT

## Mission

Build the production-ready frontend for Competitor Intelligence Monitor (CIM).

IMPORTANT:

This frontend MUST integrate with the existing backend.

Do NOT invent APIs.

Do NOT modify backend contracts.

The backend is already production-stable and tagged.

Frontend adapts to backend.

Backend does NOT adapt to frontend.

---

# Product Goal

CIM is not a generic SaaS dashboard.

CIM is an intelligence platform.

Users should feel like they are operating a competitive intelligence command center.

The UI should communicate:

* Intelligence
* Monitoring
* Strategic Awareness
* Threat Detection
* Market Visibility

NOT:

* CRM
* Project Management
* Analytics Dashboard

---

# Design System (LOCKED)

These visual decisions are mandatory.

## Color Palette

Background:

```css
#0B1020
#121826
#1A2332
```

Primary:

```css
#14B8A6
```

Success:

```css
#22C55E
```

Warning:

```css
#F59E0B
```

Danger:

```css
#EF4444
```

Info:

```css
#8B5CF6
```

Text:

```css
#F8FAFC
#CBD5E1
#94A3B8
```

---

## Typography

Use:

```text
Inter
```

Hierarchy:

```text
H1 → 32
H2 → 24
H3 → 20
Body → 14–16
Caption → 12
```

---

## UI Style

Dark-first.

Modern.

Clean.

Premium SaaS.

Glassmorphism only where valuable.

Avoid visual clutter.

No excessive gradients.

No neon cyberpunk aesthetics.

---

# Tech Stack

Mandatory:

```text
Next.js 15
TypeScript
TailwindCSS
shadcn/ui
TanStack Query
Axios
React Hook Form
Zod
Lucide Icons
Recharts
```

Do NOT use:

```text
Redux
MobX
Context-heavy state management
Manual fetch() everywhere
```

---

# Folder Architecture

```text
src/
├── app/
│
├── components/
│   ├── ui/
│   ├── layout/
│   ├── dashboard/
│   ├── watchlists/
│   ├── competitors/
│   ├── notifications/
│
├── features/
│   ├── auth/
│   ├── dashboard/
│   ├── watchlists/
│   ├── notifications/
│
├── hooks/
│
├── lib/
│
├── services/
│
├── types/
│
├── providers/
│
└── constants/
```

---

# Backend Contract (LOCKED)

Use ONLY these APIs.

## Authentication

```text
POST /api/auth/signup
POST /api/auth/login
GET  /api/auth/me
```

---

## Dashboard

```text
GET /api/dashboard/summary
GET /api/dashboard/recent-runs
GET /api/dashboard/recent-alerts
GET /api/dashboard/activity
```

---

## Watchlists

```text
GET  /api/watchlists
POST /api/watchlists
```

---

## Competitors

```text
GET  /api/watchlists/{id}/competitors
POST /api/watchlists/{id}/competitors
```

---

## Monitoring Runs

```text
GET  /api/watchlists/{id}/runs
POST /api/watchlists/{id}/runs
```

---

## Notifications

```text
GET    /api/notifications/channels
POST   /api/notifications/channels
PUT    /api/notifications/channels/{id}
DELETE /api/notifications/channels/{id}
```

Never invent additional endpoints.

---

# Authentication Architecture

Implement:

## Auth Provider

Responsibilities:

* Login
* Logout
* User loading
* Session restoration

Store:

```text
JWT Access Token
```

Use Axios interceptor:

```text
Authorization: Bearer <token>
```

---

# Layout Architecture

Authenticated Area:

```text
Sidebar
Topbar
Content Area
```

Sidebar:

```text
Dashboard
Watchlists
Notifications
Settings
```

Topbar:

```text
Search Placeholder
User Profile
Logout
```

---

# Page 1: Login

Features:

* Email
* Password
* Validation
* Error handling
* Loading state

Success:

```text
Redirect → Dashboard
```

---

# Page 2: Signup

Features:

* Display Name
* Email
* Password

Success:

```text
Auto Login
Redirect Dashboard
```

---

# Page 3: Dashboard

Consume:

```text
/dashboard/summary
/dashboard/recent-runs
/dashboard/recent-alerts
/dashboard/activity
```

Widgets:

## Summary Cards

* Watchlists
* Competitors
* Monitoring Runs Today
* Notification Channels

---

## Recent Alerts

Severity badges:

```text
LOW
MEDIUM
HIGH
```

---

## Recent Runs

Status badges:

```text
QUEUED
RUNNING
COMPLETED
FAILED
```

---

## Activity Feed

Timeline UI.

---

# Page 4: Watchlists

Features:

```text
List Watchlists
Create Watchlist
Pagination
```

Card displays:

```text
Name
Description
Frequency
Created Date
```

Click:

```text
Open Watchlist Detail
```

---

# Page 5: Watchlist Detail

Tabs:

## Competitors

Uses:

```text
GET competitors
POST competitor
```

Table:

```text
Company
Domain
Status
Added Date
```

---

## Monitoring Runs

Uses:

```text
GET runs
POST run
```

Table:

```text
Status
Trigger Type
Competitors Checked
Alerts Generated
Created Date
```

Button:

```text
Run Monitoring
```

---

# Page 6: Notifications

Features:

```text
List channels
Add channel
Enable/Disable
Delete
```

Channel Types:

```text
Webhook
Slack
Email
```

---

# Data Fetching Strategy

Use TanStack Query everywhere.

Example:

```text
useWatchlists()
useDashboardSummary()
useRecentAlerts()
useMonitoringRuns()
```

Mutations:

```text
createWatchlist()
addCompetitor()
createRun()
createNotificationChannel()
```

Invalidate queries after mutations.

---

# Loading States

Every page must include:

```text
Skeletons
Loading Spinners
Disabled Buttons
```

---

# Empty States

Examples:

```text
No Watchlists Yet
No Competitors Added
No Alerts Generated
No Monitoring Runs
```

Must be visually appealing.

---

# Error Handling

Handle:

```text
401
403
404
500
Network Failure
```

Use toast notifications.

---

# Responsive Behaviour

Support:

```text
Desktop
Tablet
Mobile
```

Priority:

```text
Desktop First
Tablet Second
Mobile Third
```

---

# Things NOT To Build

Do NOT build:

```text
Battlecards
Knowledge Graph
Competitor Detail Intelligence Pages
Executive Briefings
Market Maps
Trend Explorer
AI Chat
RBAC
Organizations
Teams
Billing
Pricing
Landing Pages
```

These belong to V1.1+.

---

# Success Criteria

A user can:

1. Sign up
2. Login
3. Create watchlists
4. Add competitors
5. Trigger monitoring runs
6. View monitoring history
7. View alerts
8. Configure notifications

At that point CIM Frontend V1 is complete.
