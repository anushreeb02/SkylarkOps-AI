import streamlit as st

from google_sheets import (
    get_client,
    read_sheet,
    update_pilot_status,
    update_drone_status,
    assign_mission
)
from logic import suggest_assignments, is_urgent

st.set_page_config(page_title="DroneOpsAgent", layout="wide")
st.title("🚁 SkylarkOps AI - Drone Operations Coordinator")


client = get_client()


# load sheets
pilots_df = read_sheet(client, "pilot_roster", "pilot_roster")
drones_df = read_sheet(client, "drone_fleet", "drone_fleet")
missions_df = read_sheet(client, "missions", "missions")

menu = st.sidebar.radio("Menu", [
    "View Data",
    "Pilot Search",
    "Drone Inventory",
    "Update Pilot Status",
    "Update Drone Status",
    "Mission Assignment",
    "AI Chat Agent"
])


# ---------------- VIEW DATA ----------------
if menu == "View Data":
    st.subheader("📌 Pilot Roster")
    st.dataframe(pilots_df)

    st.subheader("📌 Drone Fleet")
    st.dataframe(drones_df)

    st.subheader("📌 Missions")
    st.dataframe(missions_df)


# ---------------- PILOT SEARCH ----------------
elif menu == "Pilot Search":
    st.subheader("🔍 Search Available Pilots")

    location = st.text_input("Location (optional)")
    skill = st.text_input("Skill (optional)")
    cert = st.text_input("Certification (optional)")

    filtered = pilots_df.copy()

    filtered["status"] = filtered["status"].astype(str)
    filtered["location"] = filtered["location"].astype(str)
    filtered["skills"] = filtered["skills"].astype(str)
    filtered["certifications"] = filtered["certifications"].astype(str)

    filtered = filtered[filtered["status"].str.lower().str.strip() == "available"]

    if location:
        filtered = filtered[
            filtered["location"].str.lower().str.strip() == location.lower().strip()
        ]

    if skill:
        filtered = filtered[
            filtered["skills"].str.lower().str.contains(skill.lower().strip(), na=False)
        ]

    if cert:
        filtered = filtered[
            filtered["certifications"].str.lower().str.contains(cert.lower().strip(), na=False)
        ]

    st.write(f"✅ Found {len(filtered)} pilots")
    st.dataframe(filtered)


# ---------------- DRONE INVENTORY ----------------
elif menu == "Drone Inventory":
    st.subheader("🚁 Drone Inventory Search")

    location = st.text_input("Location (optional)")
    capability = st.text_input("Capability (optional)")
    weather = st.selectbox("Weather Filter", ["None", "Rainy", "Sunny", "Cloudy"])

    filtered = drones_df.copy()

    filtered["location"] = filtered["location"].astype(str)
    filtered["capabilities"] = filtered["capabilities"].astype(str)
    filtered["weather_resistance"] = filtered["weather_resistance"].astype(str)

    if location:
        filtered = filtered[
            filtered["location"].str.lower().str.strip() == location.lower().strip()
        ]

    if capability:
        filtered = filtered[
            filtered["capabilities"].str.lower().str.contains(capability.lower().strip(), na=False)
        ]

    if weather == "Rainy":
        filtered = filtered[
            filtered["weather_resistance"].str.lower().str.contains("ip43|rain", na=False)
        ]

    st.write(f"✅ Found {len(filtered)} drones")
    st.dataframe(filtered)


# ---------------- UPDATE PILOT STATUS ----------------
elif menu == "Update Pilot Status":
    st.subheader("✍️ Update Pilot Status (Sync to Google Sheet)")

    pilot_selected = st.selectbox("Select Pilot", pilots_df["name"].tolist())
    new_status = st.selectbox("New Status", ["Available", "On Leave", "Unavailable", "Assigned"])

    if st.button("Update Pilot Status"):
        ok, msg = update_pilot_status(client, pilot_selected, new_status)
        if ok:
            st.success(msg)
        else:
            st.error(msg)


# ---------------- UPDATE DRONE STATUS ----------------
elif menu == "Update Drone Status":
    st.subheader("✍️ Update Drone Status")

    drone_selected = st.selectbox("Select Drone", drones_df["drone_id"].tolist())
    new_status = st.selectbox("New Drone Status", ["Available", "Maintenance", "Deployed", "Unavailable"])

    if st.button("Update Drone Status"):
        ok, msg = update_drone_status(client, drone_selected, new_status)
        if ok:
            st.success(msg)
        else:
            st.error(msg)


# ---------------- MISSION ASSIGNMENT ----------------
elif menu == "Mission Assignment":
    st.subheader("📌 Mission Assignment + Conflict Detection")

    project_ids = missions_df["project_id"].tolist()
    selected_project = st.selectbox("Select Project", project_ids)

    mission_row = missions_df[missions_df["project_id"] == selected_project].iloc[0]

    st.write("### Mission Details")
    st.json(mission_row.to_dict())

    if is_urgent(mission_row):
        st.warning("🚨 URGENT MISSION DETECTED! Recommend quick reassignment if conflicts appear.")

    pilot_suggestions, drone_suggestions = suggest_assignments(
        pilots_df, drones_df, missions_df, mission_row, top_k=3
    )

    st.write("## 👨‍✈️ Pilot Suggestions")
    for p, warns in pilot_suggestions:
        st.write(f"✅ **{p['name']}** | {p['location']} | Rate: {p.get('daily_rate_inr','-')}")
        if warns:
            for w in warns:
                st.write("⚠️", w)
        else:
            st.write("No issues found.")
        st.divider()

    st.write("## 🚁 Drone Suggestions")
    for d, warns in drone_suggestions:
        st.write(f"✅ **{d['drone_id']}** ({d['model']}) | {d['location']}")
        if warns:
            for w in warns:
                st.write("⚠️", w)
        else:
            st.write("No issues found.")
        st.divider()

    st.write("## Confirm Assignment")
    pilot_pick = st.selectbox("Select Pilot", [p[0]["name"] for p in pilot_suggestions])
    drone_pick = st.selectbox("Select Drone", [d[0]["drone_id"] for d in drone_suggestions])

    if st.button("Confirm Assignment (Write to Missions Sheet)"):
        ok, msg = assign_mission(client, selected_project, pilot_pick, drone_pick)
        if ok:
            st.success("✅ Assignment Saved to Google Sheet!")
            st.info(msg)
        else:
            st.error(msg)


# ---------------- AI CHAT AGENT ----------------
elif menu == "AI Chat Agent": 
    st.subheader("🤖 Conversational DroneOps Agent")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        st.chat_message(m["role"]).write(m["content"])

    user_input = st.chat_input("Ask: suggest assignment for PRJ001")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        text = user_input.lower()
        reply = "Sorry, I didn't understand."

        if "available pilots" in text:
            count = len(pilots_df[pilots_df["status"].str.lower() == "available"])
            reply = f"✅ Available pilots: {count}"

        elif "available drones" in text:
            count = len(drones_df[drones_df["status"].str.lower() == "available"])
            reply = f"✅ Available drones: {count}"

        elif "suggest" in text or "assign" in text:
            project_id = None
            for pid in missions_df["project_id"].tolist():
                if pid.lower() in text:
                    project_id = pid

            if project_id:
                mission_row = missions_df[missions_df["project_id"] == project_id].iloc[0]
                pilot_suggestions, drone_suggestions = suggest_assignments(
                    pilots_df, drones_df, missions_df, mission_row, top_k=3
                )

                reply = f"Suggestions for {project_id}:\n\n"

                reply += "Pilots:\n"
                for p, warns in pilot_suggestions:
                    reply += f"- {p['name']} ({len(warns)} warnings)\n"

                reply += "\nDrones:\n"
                for d, warns in drone_suggestions:
                    reply += f"- {d['drone_id']} ({len(warns)} warnings)\n"

            else:
                reply = "Please mention a valid project ID like PRJ001."

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)
def handle_chat_query(user_input, pilots_df, drones_df, missions_df):
    q = user_input.lower().strip()

    if "available pilots" in q or "pilots" in q:
        available = pilots_df[pilots_df["status"].str.lower() == "available"]
        if available.empty:
            return "No available pilots found."
        return f"Available pilots:\n\n{available[['pilot_id','name','skills','certifications','location']].to_string(index=False)}"

    if "available drones" in q or "drones" in q:
        available = drones_df[drones_df["status"].str.lower() == "available"]
        if available.empty:
            return "No available drones found."
        return f"Available drones:\n\n{available[['drone_id','model','capabilities','location','weather_resistance']].to_string(index=False)}"

    if "suggest assignment for" in q:
        project_id = user_input.split()[-1].strip()
        mission = missions_df[missions_df["project_id"] == project_id]

        if mission.empty:
            return f"Mission {project_id} not found."

        mission_row = mission.iloc[0]
        loc = str(mission_row["location"]).lower()
        skill_req = str(mission_row["required_skills"]).lower()
        cert_req = str(mission_row["required_certs"]).lower()

        # filter pilots
        pilots_ok = pilots_df[
            (pilots_df["status"].str.lower() == "available") &
            (pilots_df["location"].str.lower() == loc) &
            (pilots_df["skills"].str.lower().str.contains(skill_req)) &
            (pilots_df["certifications"].str.lower().str.contains(cert_req))
        ]

        if pilots_ok.empty:
            return f"No suitable pilot found for {project_id}."

        best_pilot = pilots_ok.iloc[0]["name"]

        # filter drones
        drones_ok = drones_df[
            (drones_df["status"].str.lower() == "available") &
            (drones_df["location"].str.lower() == loc)
        ]

        if drones_ok.empty:
            return f"Pilot found ({best_pilot}) but no suitable drone available."

        best_drone = drones_ok.iloc[0]["drone_id"]

        return f"Suggested Assignment for {project_id}:\nPilot: {best_pilot}\nDrone: {best_drone}"

    return "Try asking: 'available pilots', 'available drones', or 'suggest assignment for PRJ001'."





