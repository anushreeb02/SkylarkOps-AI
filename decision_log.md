Decision Log – SkylarkOps AI (Drone Operations Coordinator Agent)

1. Key Assumptions-
    -Pilot availability is determined using the status field (Available, On Leave, Unavailable, Assigned).
    -A pilot is considered eligible for a mission only if they match the required skills and certifications
    listed in the mission sheet.
    -Drone eligibility is determined using capability matching, weather resistance, and maintenance due date.
    -Mission duration is calculated using start_date and end_date (inclusive of both dates).

Pilot cost is calculated as:
Pilot Cost = daily_rate_inr × mission duration (days).
A mission is considered “urgent” if its priority is marked as High or Urgent.
All dates are assumed to be stored in Google Sheets in the format YYYY-MM-DD for consistent parsing.

2. Trade-offs and Design Choices-
Google Sheets as Database: Google Sheets was chosen as the database because it satisfies the integration requirement and allows non-technical users to easily edit and view data.
Trade-off: Google Sheets is not as fast or reliable as a real database, but it is sufficient for this prototype.

Streamlit for UI-
Streamlit was selected to quickly build a hosted prototype with a clean interface and minimal setup.
Trade-off: Streamlit UI is simpler compared to a full React/Next.js app, but it is ideal for rapid prototyping and demonstration.

Rule-based Conversational Agent-
The conversational interface is implemented using a rule-based intent detection (keyword matching) rather than a full LLM-based chatbot.
Trade-off: This reduces cost and complexity while still demonstrating conversational workflow. With more time, a proper NLP/LLM intent classifier would improve accuracy.

Conflict Detection Strategy
Conflicts such as double booking are detected by comparing mission date ranges and checking assigned pilot/drone fields in the missions sheet.
Trade-off: This works well for structured sheet data but may require optimization if the dataset becomes very large.

3. Handling Edge Cases-

The system detects and flags:
    Pilot double booking when assigned to overlapping mission dates.
    Drone double booking when assigned to overlapping mission dates.
    Skill mismatch when pilot skills do not match mission requirements.
    Certification mismatch when required certifications are missing.
    Budget overrun when calculated pilot cost exceeds mission budget.
    Weather risk when a drone without proper weather resistance is assigned to a rainy mission.
    Maintenance issues when maintenance_due is earlier than the mission start date.
    Location mismatch when pilot/drone location differs from mission location.
    Warnings are shown instead of blocking assignments to allow human decision-making.

4. Interpretation of “Urgent Reassignments”-
Urgent reassignment is interpreted as the ability to quickly suggest alternative pilot/drone options when a mission is marked as high priority.
For missions with priority “High” or “Urgent”, the system highlights urgency and provides top assignment recommendations with conflict warnings, enabling fast decision-making.

5. What Would Be Improved With More Time-
    Add an LLM-based conversational agent to support natural language queries beyond keyword matching.
    Implement scoring-based optimization (weighted ranking based on distance, cost, skill match, priority).
    Add real-time weather API integration to automatically update mission weather forecasts.
    Add automated notifications (email/WhatsApp) for urgent conflicts or reassignment needs.
    Improve logging and auditing to track who made changes and when.

6. Final Outcome-
The final prototype successfully demonstrates an AI agent that can coordinate pilots, drones, and missions using Google Sheets as a live database. It supports real-time updates, assignment tracking, conflict detection, and a conversational interface, meeting the core requirements of the technical assignment.