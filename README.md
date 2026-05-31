<div align="center">

# 🏛️ HeritageGuide

### Django-Powered City Discovery & Travel Companion

[![Live Demo](https://img.shields.io/badge/🔗%20Live%20Demo-heritage--guide.vercel.app-blue?style=for-the-badge)](https://heritage-guide.vercel.app/)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![Firebase](https://img.shields.io/badge/Firebase-039BE5?style=for-the-badge&logo=firebase)](https://firebase.google.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

*Discover cities like a local — interactive maps, curated attractions, itinerary planning, and slot booking. No API key required to get started.*

</div>

---

## Features

- **Interactive Map** — Works out of the box with Leaflet + OpenStreetMap (zero API key needed). Upgrade to Google Maps for Place Search and Drawing by adding a single key.
- **Smart Directions** — Driving, walking, cycling, and transit routes via Leaflet Routing Machine (OSRM).
- **Points of Interest** — Curated markers for historic sites, museums, and monuments with quick-action cards.
- **Itinerary Builder** — Create multi-day travel plans with activities and attractions stored in Firebase Firestore.
- **Slot Booking** — Reserve attraction slots with live availability checks directly from the database.
- **Roamly Chat Assistant** — A keyword-driven AI helper that queries your live Firestore data for highly accurate, real-time travel recommendations.
- **Earthy Design** — An immersive Sage/Olive colour palette built to inspire exploration.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5 |
| Database | Firebase Firestore (NoSQL) |
| Authentication | Firebase Auth |
| Maps | Leaflet + Leaflet Routing Machine (OSRM) |
| Optional Upgrade | Google Maps JS API (Places, Drawing) |
| Deployment | Vercel |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/KrishMistry18/HeritageGuide.git
cd HeritageGuide
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### 3. Set up Firebase credentials

Place your `firebase_credentials.json` Service Account file in the project root.

### 4. Configure environment variables

```bash
cp .env.example .env
# Fill in your values
```

### 5. Start the server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and start exploring.

---

## Project Structure

```text
HeritageGuide/
├── historify/               # Core Django app
├── users/                   # Auth, profiles, templates, views, URLs
│   └── templates/           # All HTML templates (travel theme)
├── static/                  # Static assets (CSS, JS, images)
├── docs/                    # Documentation assets
├── firebase_credentials.json  # Firebase Service Account (not committed)
├── manage.py
├── requirements.txt
└── vercel.json
```

---

## FAQ

**Do I need a Google API key to see the map?**
No. The default setup uses Leaflet + OpenStreetMap. A Google key only unlocks Place Search and Drawing on top.

**What database does this use?**
HeritageGuide uses Firebase Firestore for all data. Just set up your Service Account JSON and you're ready.

**How does Roamly work?**
Roamly queries the live Firebase database to find attractions based on the city or category you mention in the chat.

---

## Contributing

PRs and suggestions are welcome. If you find a bug or have an idea, open an issue.

---

## License

MIT

---

<div align="center">

*Built with ❤️ by [Krish Mistry](https://github.com/KrishMistry18)*

</div>