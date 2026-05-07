# Supabase Migration Runbook

This project is now Supabase-ready using:

- `DATABASE_URL` for Supabase Postgres
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`

## 1) Create Supabase schema

Use Supabase SQL editor and create tables/policies for:

- `profiles` (linked to `auth.users`)
- `cities`
- `attractions`
- `itineraries`
- `itinerary_days`
- `itinerary_activities`
- `bookings`

Keep names close to existing Django models to simplify migration.

## 2) Export existing local data

From project root:

```bash
python manage.py dumpdata users.City users.Attraction users.Itinerary users.ItineraryDay users.ItineraryActivity users.Booking users.Profile --indent 2 > data_export.json
```

## 3) Import data into Supabase Postgres

Option A:
- load `data_export.json`
- transform to CSV
- import into Supabase table editor

Option B:
- write one-time Python ETL script using `SUPABASE_SERVICE_ROLE_KEY`
- insert in dependency order (cities -> attractions -> itineraries -> days -> activities -> bookings).

## 4) Auth migration strategy

1. Enable Email + Google providers in Supabase Auth.
2. Migrate users:
   - create Supabase auth users
   - map Django user ids to Supabase auth ids in `profiles`.
3. Keep Django session auth during transition, then cut over to Supabase auth endpoints.

## 5) Cutover checklist

- [ ] `DATABASE_URL` points to Supabase Postgres.
- [ ] `python manage.py migrate` runs against Supabase DB.
- [ ] Signup/login/google flow verified.
- [ ] Itinerary + booking flows verified.
- [ ] Row-level security policies active for user-owned data.
