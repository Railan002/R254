import streamlit as st
import requests
from datetime import datetime, timezone

API_KEY = 'f104f27bfbcccdd991a83aa22a1941f4'
REGIONS = 'uk,eu,us'
MARKETS = 'h2h'
ODDS_FORMAT = 'decimal'
DATE_FORMAT = 'iso'
BASE_URL = 'https://api.the-odds-api.com/v4/sports/soccer/odds'

st.set_page_config(page_title="Low Risk Football Bets", layout="centered")
st.title("Today's Low-Risk Football Predictions")

def fetch_odds():
    url = f"{BASE_URL}?regions={REGIONS}&markets={MARKETS}&oddsFormat={ODDS_FORMAT}&dateFormat={DATE_FORMAT}&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Error fetching odds: {response.status_code}")
        return []
    return response.json()

def is_today(match_time_str):
    match_time = datetime.fromisoformat(match_time_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    return match_time.date() == now.date()

def calculate_win_percentage(odds):
    return round((1 / odds) * 100, 2)

def get_low_risk_matches(matches):
    low_risk = []
    for match in matches:
        if not is_today(match['commence_time']):
            continue
        for bookmaker in match.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                if market['key'] == 'h2h':
                    outcomes = market['outcomes']
                    best_odds = sorted(outcomes, key=lambda x: x['price'])[0]
                    if best_odds['price'] <= 1.60:
                        win_pct = calculate_win_percentage(best_odds['price'])
                        low_risk.append({
                            'match': f"{match['home_team']} vs {match['away_team']}",
                            'time': match['commence_time'],
                            'tip': best_odds['name'],
                            'odds': best_odds['price'],
                            'win_pct': win_pct,
                            'bookmaker': bookmaker['title']
                        })
    return low_risk

# Main App Logic
matches = fetch_odds()
low_risk_matches = get_low_risk_matches(matches)

if not low_risk_matches:
    st.warning("No low-risk matches found for today.")
else:
    for match in low_risk_matches:
        st.subheader(match['match'])
        st.write(f"**Tip:** {match['tip']}  \n**Odds:** {match['odds']}  \n**Win %:** {match['win_pct']}%  \n**Bookmaker:** {match['bookmaker']}  \n**Time:** {datetime.fromisoformat(match['time'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}")
        st.markdown("---")