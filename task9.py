
# Multi-Event Sports Scheduling and Scoring System

# List of events stored as tuples:
# (Event Name, Date, Time, Team 1, Team 2)

events = [
    ("Football", "2026-11-01", "10:00", "Team A", "Team B"),
    ("Basketball", "2026-11-01", "10:00", "Team A", "Team C"),
    ("Cricket", "2026-11-01", "12:00", "Team B", "Team C"),
    ("Volleyball", "2026-11-02", "09:00", "Team A", "Team B"),
    ("Badminton", "2026-11-02", "11:00", "Team C", "Team A")
]

# Scores stored as tuples:
# (Event Name, Team 1, Team 1 Score, Team 2, Team 2 Score)

scores = [
    ("Football", "Team A", 3, "Team B", 1),
    ("Basketball", "Team A", 60, "Team C", 55),
    ("Cricket", "Team B", 150, "Team C", 140),
    ("Volleyball", "Team A", 2, "Team B", 3),
    ("Badminton", "Team C", 21, "Team A", 15)
]

# 1. Display the event schedule
print("===== SPORTS EVENT SCHEDULE =====")

for event in events:
    print(
        f"Event: {event[0]}, Date: {event[1]}, "
        f"Time: {event[2]}, Teams: {event[3]} vs {event[4]}"
    )


# 2. Identify scheduling conflicts
print("\n===== SCHEDULING CONFLICTS =====")

conflicts_found = False

for i in range(len(events)):
    for j in range(i + 1, len(events)):
        event1 = events[i]
        event2 = events[j]

        # Events conflict if they have the same date and time
        if event1[1] == event2[1] and event1[2] == event2[2]:
            teams1 = {event1[3], event1[4]}
            teams2 = {event2[3], event2[4]}

            # Check whether a team is scheduled for both events
            common_teams = teams1.intersection(teams2)

            if common_teams:
                conflicts_found = True
                print(
                    f"Conflict: {event1[0]} and {event2[0]} "
                    f"at {event1[1]} {event1[2]}"
                )
                print("Common team(s):", ", ".join(sorted(common_teams)))

if not conflicts_found:
    print("No scheduling conflicts found.")


# 3. Aggregate points for each team
team_points = {}

for match in scores:
    event_name, team1, score1, team2, score2 = match

    # Initialize teams if they are not already present
    team_points.setdefault(team1, 0)
    team_points.setdefault(team2, 0)

    # Award 3 points for a win and 1 point for a draw
    if score1 > score2:
        team_points[team1] += 3
    elif score2 > score1:
        team_points[team2] += 3
    else:
        team_points[team1] += 1
        team_points[team2] += 1


# 4. Generate final rankings
rankings = sorted(
    team_points.items(),
    key=lambda item: item[1],
    reverse=True
)

print("\n===== FINAL TEAM RANKINGS =====")
print(f"{'Rank':<8}{'Team':<15}{'Points':<10}")

for rank, (team, points) in enumerate(rankings, start=1):
    print(f"{rank:<8}{team:<15}{points:<10}")

print("\nTournament completed successfully!")
