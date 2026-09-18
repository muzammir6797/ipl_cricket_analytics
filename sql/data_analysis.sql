1. Top 10 grounds by number of matches

SELECT
    venue AS ground,
    COUNT(DISTINCT match_id) AS match_count
FROM matches
GROUP BY venue
ORDER BY match_count DESC
LIMIT 10;

Explanation:

GROUP BY venue groups matches by ground.
COUNT(DISTINCT match_id) counts each match only once.
ORDER BY ... DESC puts grounds with the most matches first.
LIMIT 10 returns the top 10.

2. Grounds with average innings score above 165, minimum 25 matches

SELECT
    m.venue AS ground,
    COUNT(DISTINCT m.match_id) AS match_count,
    AVG(i.innings_score) AS average_innings_score
FROM matches m
JOIN innings i
    ON m.match_id = i.match_id
GROUP BY m.venue
HAVING COUNT(DISTINCT m.match_id) >= 25
   AND AVG(i.innings_score) > 165
ORDER BY average_innings_score DESC;

Explanation:

Joins match information with innings scores.
AVG(i.innings_score) calculates the average innings score.
HAVING filters after grouping.
Only grounds with at least 25 matches are considered.
Then only grounds having an average score above 165 are displayed.


3. Chase win percentage for grounds with at least 50 matches

Assuming chase_win identifies matches won by the team batting second:

SELECT
    venue AS ground,
    COUNT(DISTINCT match_id) AS match_count,
    ROUND(
        100.0 * SUM(CASE WHEN chase_win = 1 THEN 1 ELSE 0 END)
        / COUNT(DISTINCT match_id),
        2
    ) AS chase_win_percentage
FROM matches
GROUP BY venue
HAVING COUNT(DISTINCT match_id) >= 50
ORDER BY chase_win_percentage DESC;

Explanation:

Counts matches at each ground.
chase_win = 1 represents a win while chasing.
SUM(CASE...) counts chase victories.
Dividing chase wins by total matches gives the percentage.
HAVING keeps only grounds with 50 or more matches.

4. Count the number of unique cleaned venues

If your database has a cleaned venue column called cleaned_venue:

SELECT COUNT(DISTINCT cleaned_venue) AS unique_cleaned_venues
FROM matches
WHERE cleaned_venue IS NOT NULL
  AND TRIM(cleaned_venue) <> '';

Explanation:

TRIM() removes unnecessary spaces.
DISTINCT removes duplicate venue names.
COUNT() gives the number of unique venues.
IS NOT NULL ignores missing venues.

5. Five grounds with the lowest powerplay run rate

Assuming the deliveries table has over, total_runs, and venue:

SELECT
    m.venue AS ground,
    ROUND(
        6.0 * SUM(d.total_runs) / COUNT(d.ball),
        2
    ) AS powerplay_run_rate
FROM matches m
JOIN deliveries d
    ON m.match_id = d.match_id
WHERE d.over < 6
GROUP BY m.venue
ORDER BY powerplay_run_rate ASC
LIMIT 5;

Explanation:

d.over < 6 selects overs 0–5, i.e. the first six overs.
SUM(d.total_runs) calculates total powerplay runs.
COUNT(d.ball) counts deliveries.
Multiplying by 6 converts runs per ball into runs per over.
ASC sorts from lowest to highest.
LIMIT 5 gives the five lowest grounds.

If your dataset has over numbered 1–20 instead of 0–19, use WHERE d.over <= 6.

6. Why COUNT(DISTINCT match_id) is safer than COUNT(*) after a JOIN

Example:

SELECT
    m.venue,
    COUNT(DISTINCT m.match_id) AS matches
FROM matches m
JOIN deliveries d
    ON m.match_id = d.match_id
GROUP BY m.venue;

Explanation:

Suppose one match has 120 deliveries.

After joining matches with deliveries, that one match can appear 120 times.

So:

COUNT(*)

could count the same match 120 times.

But:

COUNT(DISTINCT match_id)

counts that match only once.

Therefore, when a JOIN creates multiple rows for the same match, COUNT(DISTINCT match_id) is safer for calculating the number of matches.

7. Why day/night cannot be answered from match_date alone

match_date only tells us which date the match happened.

For example:

2026-04-10

doesn't tell us whether the match started in the morning, afternoon, or evening.

To determine day/night, you need additional information such as:

match_start_time

or a field such as:

day_night

For example:

SELECT
    match_date,
    match_start_time,
    day_night
FROM matches;

Explanation:
Two matches can happen on the same date but have different start times:

match_date	start_time	Type
2026-04-10	15:30	Day
2026-04-10	19:30	Night