# 🚁 SkylarkOps AI - Drone Operations Coordinator Agent

SkylarkOps AI is a Streamlit-based AI agent designed to automate the core responsibilities of a Drone Operations Coordinator.  
It manages pilot rosters, drone inventory, mission assignments, and detects scheduling/equipment conflicts using real-time Google Sheets data.

---
Author - Anushree B
## 📌 Features

### ✅ 1. Pilot Roster Management
- View all pilots and their details
- Search pilots by skill, certification, and location
- Check pilot availability
- Update pilot status (Available / On Leave / Unavailable / Assigned)
- Status updates sync back to Google Sheets

### ✅ 2. Drone Inventory Management
- View all drones in the fleet
- Filter drones by capability, location, and weather resistance
- Detect maintenance issues
- Update drone status (Available / Maintenance / Deployed)
- Updates sync back to Google Sheets

### ✅ 3. Mission Assignment Tracking
- Select a mission and get recommended pilot + drone
- Assign pilot and drone to a mission
- Stores assigned pilot and drone in missions sheet
- Supports reassignment

### ✅ 4. Conflict Detection
The agent automatically flags:
- Double booking (pilot assigned to overlapping missions)
- Double booking (drone assigned to overlapping missions)
- Skill mismatch warnings
- Certification mismatch warnings
- Location mismatch alerts
- Budget overrun warnings (Pilot Cost > Mission Budget)
- Weather risk alerts (Non-waterproof drone assigned to Rainy mission)
- Maintenance issues

### ✅ 5. Conversational Interface
A chat-based interface is provided where the user can ask:
- "available pilots"
- "available drones"
- "suggest assignment for PRJ001"

---

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** Google Sheets (2-way sync)
- **Libraries:** pandas, gspread, oauth2client

---

## 📂 Project Structure
SkylarkOps-AI/
│── app.py
│── logic.py
│── google_sheets.py
│── requirements.txt
│── README.md

## 🔗 Google Sheets Integration
This project reads data from:
- `pilot_roster` sheet
- `drone_fleet` sheet
- `missions` sheet

And writes updates back to:
- Pilot status updates
- Drone status updates
- Mission assignments

