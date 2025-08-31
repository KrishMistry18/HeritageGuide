# HistoryGate 🏛️🗺️

Discover cities like a local. HistoryGate is a Django-powered travel companion that blends an elegant map UI, curated attractions, itinerary planning, and simple slot booking — all with a privacy‑friendly, keyless default map.

## ✨ Highlights
- 🗺️ **Interactive Map**: Works out of the box using Leaflet + OpenStreetMap (no API key needed). If you add a Google API key, the page upgrades to Place Search + Drawing.
- 🧭 **Smart Directions**: Get driving/walking/cycling/transit routes with a single click (Leaflet Routing Machine via OSRM).
- 🏷️ **Points of Interest**: Curated markers for historic sites, museums, and monuments with quick actions.
- 🗓️ **Itineraries**: Create multi-day plans with activities and attractions (clean `City → Attraction → Day → Activity` model).
- 🎟️ **Slot Booking**: Reserve slots for attractions with availability checks.
- 💬 **Chat Assistant**: Optional AI-powered helper for travel queries.

## 🚀 Quick Start

1) Clone the repo
```bash
git clone https://github.com/<your-username>/-HistoryGate-App.git
cd -HistoryGate-App
```

2) Create a virtual environment and install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3) Run database migrations
```bash
python manage.py migrate
```

4) Start the server
```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and explore!

Tip: Create a superuser to access the admin dashboard.
```bash
python manage.py createsuperuser
```

## 🔑 Optional: Google Maps API
The map page is fully functional without any keys (Leaflet + OSM). If you prefer Google Maps for Place Search and Drawing tools, set an API key:

1) Get a key from the Google Cloud Console and enable the Maps JavaScript API
2) Create a `.env` file in the project root using the template below

```env
GOOGLE_MAPS_API_KEY=your_api_key_here
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
OPENAI_API_KEY=your_openai_key_if_used
DEBUG=True
SECRET_KEY=your_django_secret
```

We’ve included `env_example.txt` as a reference. The app will fall back to Leaflet if Google Maps fails to load.

## 🧱 Tech Stack
- Django 5
- django-allauth (Google OAuth)
- Leaflet + Leaflet Routing Machine (OSRM)
- Optional Google Maps JS API (Places, Drawing)
- SQLite (dev), easily swappable

## 🧹 Project Structure
- `users/` app with templates, views, URLs, and management commands for sample data
- `users/templates/map.html` includes a graceful Leaflet fallback (no key required)
- `users/management/commands/` includes helpers to populate cities and attractions

## 🛡️ Security & GitHub Hygiene
- `.gitignore` excludes secrets (`.env`), local DB (`db.sqlite3`), and media uploads
- Sensitive OAuth client files have been removed; use your own credentials locally

## 🖼️ Screenshots
Add screenshots or a short GIF demo here!
```
docs/
 ├─ screenshot-home.png
 ├─ screenshot-map.png
 └─ itinerary-flow.gif
```

## 🧩 Notable Features
- **Leaflet Fallback**: If Google Maps is unavailable or the key is missing, the app auto-loads a Leaflet map with search and routing
- **Itinerary Data Model**: Clean `City`, `Attraction`, `Itinerary`, and `ItineraryDay` models designed for extensibility
- **Booking Engine**: Enforces one booking per user per slot and tracks availability

## 📝 Scripts & Data
Populate sample data using the management commands:
```bash
python manage.py populate_cities
python manage.py populate_attractions
```

## ❓ FAQ
- **Q: Do I need a Google API key to see the map?**
  - No. The app uses Leaflet + OpenStreetMap by default. A Google key only unlocks Place Search + Drawing on top.
- **Q: Can I use Postgres or MySQL?**
  - Yes, update `DATABASES` in `historify/settings.py`.
- **Q: How do I add my own cities/attractions?**
  - Use the admin panel or copy the management commands as a template.

## 🤝 Contributing
PRs and suggestions are welcome! If you find a bug or have an idea, open an issue.

---

## 📞 **Contact**

- Project: <https://github.com/KrishMistry18/EduCycle>
- Email: <mistrykrish2005@gmail.com>
- LinkedIn: <https://www.linkedin.com/in/krishmistry18>

---

**Built with ❤️ by Krish Mistry** 




