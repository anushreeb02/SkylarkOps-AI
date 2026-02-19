from datetime import datetime

def split_list(value):
    if value is None:
        return []
    return [x.strip().lower() for x in str(value).split(",") if x.strip()]

def parse_date(date_str):
    return datetime.strptime(str(date_str), "%Y-%m-%d")

def overlap(start1, end1, start2, end2):
    return start1 <= end2 and start2 <= end1

def calculate_days(start_date, end_date):
    s = parse_date(start_date)
    e = parse_date(end_date)
    return (e - s).days + 1

def calculate_pilot_cost(rate_per_day, start_date, end_date):
    return float(rate_per_day) * calculate_days(start_date, end_date)


# ---------------- DOUBLE BOOKING CHECK ----------------

def check_double_booking(missions_df, entity_value, column_name, start_date, end_date):
    warnings = []
    start = parse_date(start_date)
    end = parse_date(end_date)

    if column_name not in missions_df.columns:
        return warnings

    for _, row in missions_df.iterrows():
        if str(row.get(column_name, "")).strip().lower() == str(entity_value).strip().lower():
            try:
                s2 = parse_date(row["start_date"])
                e2 = parse_date(row["end_date"])

                if overlap(start, end, s2, e2):
                    warnings.append(
                        f"Double Booking: overlaps with project {row['project_id']} ({row['start_date']} to {row['end_date']})"
                    )
            except:
                pass

    return warnings


# ---------------- PILOT CONFLICTS ----------------

def pilot_conflicts(pilot_row, mission_row, missions_df):
    warnings = []

    required_skills = split_list(mission_row.get("required_skills"))
    required_certs = split_list(mission_row.get("required_certs"))

    pilot_skills = split_list(pilot_row.get("skills"))
    pilot_certs = split_list(pilot_row.get("certifications"))

    for skill in required_skills:
        if skill not in pilot_skills:
            warnings.append(f"Skill mismatch: pilot missing '{skill}'")

    for cert in required_certs:
        if cert not in pilot_certs:
            warnings.append(f"Certification mismatch: pilot missing '{cert}'")

    if str(pilot_row.get("location", "")).lower() != str(mission_row.get("location", "")).lower():
        warnings.append("Location mismatch: pilot is in different city")

    # budget check
    try:
        cost = calculate_pilot_cost(
            pilot_row["daily_rate_inr"],
            mission_row["start_date"],
            mission_row["end_date"]
        )
        budget = float(mission_row["mission_budget"])
        if cost > budget:
            warnings.append(f"Budget Overrun: pilot cost {cost} > budget {budget}")
    except:
        pass

    # double booking check
    pilot_name = pilot_row.get("name")
    if pilot_name:
        warnings.extend(
            check_double_booking(
                missions_df,
                pilot_name,
                "assigned_pilot",
                mission_row["start_date"],
                mission_row["end_date"]
            )
        )

    return warnings


# ---------------- DRONE CONFLICTS ----------------

def drone_conflicts(drone_row, mission_row, missions_df):
    warnings = []

    if str(drone_row.get("location", "")).lower() != str(mission_row.get("location", "")).lower():
        warnings.append("Location mismatch: drone is in different city")

    # maintenance check
    try:
        due = parse_date(drone_row["maintenance_due"])
        start = parse_date(mission_row["start_date"])
        if due < start:
            warnings.append("Maintenance issue: drone maintenance due before mission start")
    except:
        pass

    # weather check
    weather = str(mission_row.get("weather_forecast", "")).lower()
    resistance = str(drone_row.get("weather_resistance", "")).lower()

    if weather == "rainy":
        if "ip43" not in resistance and "rain" not in resistance:
            warnings.append("Weather Risk: drone not rain resistant (Rainy mission)")

    # capability check
    required_skills = split_list(mission_row.get("required_skills"))
    drone_caps = split_list(drone_row.get("capabilities"))

    for skill in required_skills:
        if skill not in drone_caps:
            warnings.append(f"Drone capability mismatch: missing '{skill}'")

    # double booking check
    drone_id = drone_row.get("drone_id")
    if drone_id:
        warnings.extend(
            check_double_booking(
                missions_df,
                drone_id,
                "assigned_drone",
                mission_row["start_date"],
                mission_row["end_date"]
            )
        )

    return warnings


# ---------------- FILTER FUNCTIONS ----------------

def available_pilots(pilots_df):
    return pilots_df[pilots_df["status"].str.lower() == "available"]

def available_drones(drones_df):
    return drones_df[drones_df["status"].str.lower() == "available"]


# ---------------- SUGGESTION ENGINE ----------------

def suggest_assignments(pilots_df, drones_df, missions_df, mission_row, top_k=3):
    pilots = available_pilots(pilots_df)
    drones = available_drones(drones_df)

    pilot_results = []
    for _, p in pilots.iterrows():
        warns = pilot_conflicts(p, mission_row, missions_df)
        pilot_results.append((p, warns))

    drone_results = []
    for _, d in drones.iterrows():
        warns = drone_conflicts(d, mission_row, missions_df)
        drone_results.append((d, warns))

    pilot_results.sort(key=lambda x: len(x[1]))
    drone_results.sort(key=lambda x: len(x[1]))

    return pilot_results[:top_k], drone_results[:top_k]


# ---------------- URGENT CHECK ----------------

def is_urgent(mission_row):
    priority = str(mission_row.get("priority", "")).lower()
    return priority in ["urgent", "high"]
