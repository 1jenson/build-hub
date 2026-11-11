# Life OS (Phase 1)

Today, Habits and Mood inside the Command Centre. All data lives in `public.hub_docs`
(Supabase project `build-hub`), using the same `owner / col / id / data` pattern and the same
per-owner row-level security as the rest of the hub. No schema changes. Records are small and flat
so a later widget can read them with one query per collection.

No secrets belong in this file or in any collection.

## Collections

| `col` | doc `id` | Purpose |
|---|---|---|
| `tasks` | auto | Life to-dos |
| `habits` | auto (defaults: `gym`, `water`, `steps`, `read`) | The habit list |
| `habitlog` | the date, `YYYY-MM-DD` | Which habits were ticked on that day |
| `mood` | the date, `YYYY-MM-DD` | One mood entry per day |

Dates are the device's local date (Europe/London for Jenson). Times are ISO 8601 UTC strings.

### `tasks/<id>`

| field | type | notes |
|---|---|---|
| `text` | string | to-do text |
| `area` | `"life"` | reserved so more areas can be added later |
| `due` | `YYYY-MM-DD` or `""` | the day it is planned for. `""` means Later |
| `done` | bool | |
| `doneAt` | ISO string or `""` | |
| `created` | ISO string | |
| `order` | number | creation time in ms, used for sorting |

### Business to-dos (existing `items`)

Business to-dos are not copied. Today reads `items` where `kind = "todo"` and tags them Business.
`items.due` is used as "planned for": a to-do with `due <= today` that is not done shows on Today
(earlier dates show as Carried over). The "More to do" list pulls in any other open to-do
with a "+ Today" button, which just sets `due` to today. "Not today" clears `due`. Ticking
uses the existing item logic, so the activity log still records it.

### `habits/<id>`

| field | type | notes |
|---|---|---|
| `name` | string | |
| `icon` | string | one of `gym water steps read sleep leaf food sun heart pen phone bolt star` |
| `target` | 1 to 7 | days per week |
| `order` | number | list order |
| `archived` | bool | archived habits keep their history |
| `created` | ISO string | |

The four defaults are created once, on first load of an empty `habits` collection, with fixed ids so two devices cannot duplicate them.

### `habitlog/<YYYY-MM-DD>`

| field | type | notes |
|---|---|---|
| `d` | string | the date again, for convenience |
| `done` | array of habit ids | habits ticked that day |

### `mood/<YYYY-MM-DD>`

| field | type | notes |
|---|---|---|
| `d` | string | the date |
| `mood` | 0 to 5 | 1 awful, 2 low, 3 okay, 4 good, 5 great. 0 means only energy or a note was logged |
| `energy` | 0 to 5 | optional, 0 means not logged |
| `note` | string | optional, up to 140 characters |
| `at` | ISO string | last update |

## Rules the app uses

* Weeks run Monday to Sunday.
* A habit with `target = 7` has a daily streak: consecutive days ending today, or ending yesterday if today is not ticked yet.
* A habit with `target < 7` has a weekly streak: consecutive weeks that met the target. The current week counts once it is met and does not break the streak while still in progress.
* "This week" is the number of ticked days Monday to today.
* Steps is a manual tick.

## Reading it from a widget (Phase 2 idea)

A Scriptable widget could read `habits`, `habitlog` (last 7 days) and `tasks`/`items` for today with a limited
read-only credential. That credential does not exist yet and needs Jenson's go-ahead.
