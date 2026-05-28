# HeritageGuide 🏛️🗺️

Discover cities like a local. HeritageGuide (formerly HistoryGate) is a Django-powered travel companion that blends an elegant map UI, curated attractions, itinerary planning, and simple slot booking — all backed by a real-time **Firebase** backend.

<br>🔗 Live Demo: https://heritage-guide.vercel.app/

<br>## ✨ Highlights
- 🗺️ **Interactive Map**: Works out of the box using Leaflet + OpenStreetMap (no API key needed). If you add a Google API key, the page upgrades to Place Search + Drawing.
- 🧭 **Smart Directions**: Get driving/walking/cycling/transit routes with a single click (Leaflet Routing Machine via OSRM).
- 🏷️ **Points of Interest**: Curated markers for historic sites, museums, and monuments with quick actions.
- 🗓️ **Itineraries**: Create multi-day plans with activities and attractions using Firebase Firestore.
- 🎟️ **Slot Booking**: Reserve slots for attractions with availability checks right from the database.
- 💬 **Chat Assistant**: Roamly, the local keyword-driven AI helper that queries the Firestore database to provide highly accurate travel recommendations.
- 🎨 **Earthy Theme**: A beautiful, immersive Sage/Olive color palette designed to inspire travel.

## 🚀 Quick Start

1) Clone the repo
```bash
git clone https://github.com/KrishMistry18/HeritageGuide.git
cd HeritageGuide
```

2) Create a virtual environment and install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate # Mac/Linux
pip install -r requirements.txt
```

3) Set up Firebase Credentials
You must place your `firebase_credentials.json` file in the project root to connect to the Firestore database.

4) Start the server
```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and explore!

## 🧱 Tech Stack
- Django 5 (Backend Framework)
- Firebase / Firestore (NoSQL Database)
- Firebase Auth (Authentication)
- Leaflet + Leaflet Routing Machine (OSRM)
- Optional Google Maps JS API (Places, Drawing)

## 🧹 Project Structure
- `users/` app with templates, views, and URLs.
- `users/templates/` contains all the HTML templates styled with the new travel theme.
- `firebase_credentials.json` authenticates the backend with the Firebase project.

## 🛡️ Security & GitHub Hygiene
- `.gitignore` excludes secrets (`.env`), Firebase credentials (`firebase_credentials.json`), and virtual environments.

## ❓ FAQ
- **Q: Do I need a Google API key to see the map?**
  - No. The app uses Leaflet + OpenStreetMap by default. A Google key only unlocks Place Search + Drawing on top.
- **Q: Does this use SQLite or Postgres?**
  - No, HeritageGuide uses Firebase Firestore for all data storage. Ensure you have your Firebase Service Account JSON file set up!
- **Q: How does the Chatbot work?**
  - Roamly queries the live Firebase database to find attractions based on the cities or categories you mention.

## 🤝 Contributing
PRs and suggestions are welcome! If you find a bug or have an idea, open an issue.

---

## 📞 **Contact**

- Project: <https://github.com/KrishMistry18/HeritageGuide>
- Email: <mistrykrish2005@gmail.com>
- LinkedIn: <https://www.linkedin.com/in/krishmistry18>

---

**Built with ❤️ by Krish Mistry**
