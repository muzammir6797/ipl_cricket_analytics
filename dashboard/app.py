from pathlib import Path
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="IPL Neon Analytics", page_icon="🏏", layout="wide")
ROOT = Path(__file__).resolve().parent.parent
DB_CANDIDATES = [ROOT / "data" / "raw" / "ipl.db", ROOT / "ipl.db", Path("data/raw/ipl.db"), Path("ipl.db")]
DB_PATH = next((p for p in DB_CANDIDATES if p.exists() and p.stat().st_size > 0), DB_CANDIDATES[0])

st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #123b28 0%, #07130f 42%, #050a08 100%); color:#eafff1; overflow-x:hidden; }
.stApp:before { content:""; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.26; background:
  radial-gradient(circle at 12% 24%, rgba(62,255,137,.22) 0 2px, transparent 3px),
  radial-gradient(circle at 78% 62%, rgba(62,255,137,.17) 0 2px, transparent 3px),
  linear-gradient(115deg, transparent 0 44%, rgba(74,255,145,.07) 45%, transparent 46% 100%);
  background-size:170px 170px, 230px 230px, 100% 100%; animation: stadiumDrift 24s linear infinite; }
.stApp:after { content:""; position:fixed; width:230px; height:230px; right:4%; top:18%; pointer-events:none; z-index:0; opacity:.13; border:1px solid #55ff9a; border-radius:50%; box-shadow:0 0 0 22px #55ff9a0b,0 0 0 48px #55ff9a0a,0 0 50px #55ff9a; animation: fieldPulse 9s ease-in-out infinite; }
/* Full-page cricket stadium motion layer: purely decorative, behind all content. */
.stApp .main:before { content:""; position:fixed; inset:0; z-index:-1; pointer-events:none; opacity:.34;
  background:
    radial-gradient(ellipse at 50% 120%, rgba(32,190,92,.22), transparent 54%),
    linear-gradient(180deg, transparent 0 68%, rgba(22,120,59,.13) 69%, transparent 70%),
    repeating-linear-gradient(90deg, transparent 0 7.9%, rgba(91,255,151,.045) 8% 8.12%, transparent 8.2% 16.5%);
  animation: stadiumWash 18s ease-in-out infinite alternate;
}
.cricket-bg-layer { position:fixed; inset:0; z-index:0; pointer-events:none; overflow:hidden; opacity:.52; }
.cricket-bg-layer .stadium-beam { position:absolute; top:-18%; width:22vw; height:78vh; opacity:.12; filter:blur(16px);
  background:linear-gradient(180deg,rgba(171,255,199,.0),rgba(105,255,157,.2),rgba(105,255,157,0));
  transform-origin:top center; animation: beamSweep 16s ease-in-out infinite alternate; }
.cricket-bg-layer .beam-a { left:4%; transform:rotate(18deg); }
.cricket-bg-layer .beam-b { right:8%; transform:rotate(-22deg); animation-delay:-7s; }
.cricket-bg-layer .field-ring { position:absolute; width:min(78vw,1000px); height:min(42vw,500px); left:50%; bottom:-22%; transform:translateX(-50%);
  border:1px solid rgba(104,255,156,.16); border-radius:50%; box-shadow:0 0 0 22px rgba(104,255,156,.025),0 0 0 52px rgba(104,255,156,.02),inset 0 0 70px rgba(104,255,156,.035); animation:ringBreathe 11s ease-in-out infinite; }
.cricket-bg-layer .pitch-line { position:absolute; top:40%; left:50%; width:2px; height:32vh; opacity:.14;
  background:linear-gradient(180deg,transparent,#aaffc3,transparent); transform:rotate(22deg); animation:pitchDrift 12s ease-in-out infinite alternate; }
.cricket-bg-layer .bg-ball { position:absolute; width:11px; height:11px; border-radius:50%;
  background:radial-gradient(circle at 30% 25%,#fff 0 5%,#ffb4b4 13%,#f03a4d 45%,#7d1020 78%,#330812 100%);
  box-shadow:0 0 10px #ff344f,0 0 25px rgba(255,52,79,.45); opacity:.7; animation: backgroundBall 13s linear infinite; }
.cricket-bg-layer .bg-ball:after { content:""; position:absolute; left:-22px; top:4px; width:24px; height:2px; transform:rotate(-18deg); background:linear-gradient(90deg,transparent,#ff5969aa); }
.cricket-bg-layer .ball-a { top:18%; left:-4%; animation-duration:17s; }
.cricket-bg-layer .ball-b { top:66%; left:-5%; width:7px;height:7px; animation-duration:23s; animation-delay:-11s; opacity:.45; }
.cricket-bg-layer .ball-c { top:39%; left:-3%; width:5px;height:5px; animation-duration:20s; animation-delay:-6s; opacity:.38; }
.cricket-bg-layer .bg-stumps { position:absolute; right:11%; bottom:17%; width:24px; height:42px; opacity:.12; transform:skewY(-9deg); }
.cricket-bg-layer .bg-stumps:before { content:""; position:absolute; left:3px; top:0; width:3px;height:42px;background:#baffcc;box-shadow:8px 0 #baffcc,16px 0 #baffcc; }
.cricket-bg-layer .bg-stumps:after { content:""; position:absolute; top:-2px;left:1px;width:20px;height:3px;background:#baffcc;box-shadow:0 0 10px #76ff9e; }
@keyframes stadiumWash { from { background-position:0 0,0 0,0 0; } to { background-position:0 -40px,0 0,4% 0; } }
@keyframes beamSweep { 0% { opacity:.06; translate:-8px 0; } 50% { opacity:.18; } 100% { opacity:.08; translate:18px 0; } }
@keyframes ringBreathe { 0%,100% { transform:translateX(-50%) scale(.96); opacity:.6; } 50% { transform:translateX(-50%) scale(1.04); opacity:1; } }
@keyframes pitchDrift { from { transform:translateX(-35px) rotate(22deg); opacity:.05; } to { transform:translateX(35px) rotate(22deg); opacity:.2; } }
@keyframes backgroundBall { 0% { transform:translate3d(0,0,0) rotate(0deg); } 45% { transform:translate3d(48vw,16vh,0) rotate(400deg); } 100% { transform:translate3d(112vw,-8vh,0) rotate(900deg); } }
@media (prefers-reduced-motion: reduce) {
  .stApp:before,.stApp:after,.cricket-bg-layer *, .stApp .main:before { animation:none !important; }
}
@keyframes stadiumDrift { from { background-position:0 0,0 0,0 0; } to { background-position:170px 170px,-230px 230px,0 0; } }
@keyframes fieldPulse { 0%,100% { transform:scale(.94); opacity:.08; } 50% { transform:scale(1.06); opacity:.2; } }
[data-testid="stAppViewContainer"] > .main { position:relative; z-index:1; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0b2117,#07110d); border-right:1px solid #1c6c43; }
.block-container { padding-top:1.4rem; max-width:1500px; }
.hero { padding:26px 28px; border:1px solid #2ee879; border-radius:20px; background:linear-gradient(110deg,rgba(10,55,31,.96),rgba(6,20,15,.88)); box-shadow:0 0 30px #1bdc5b20; position:relative; overflow:hidden; }
.hero:after { content:'🏏'; position:absolute; right:35px; top:12px; font-size:58px; opacity:.8; animation: floatbat 3s ease-in-out infinite; }
@keyframes floatbat { 0%,100%{transform:translateY(0) rotate(-8deg)} 50%{transform:translateY(-8px) rotate(5deg)} }
.hero h1 {color:#8cffb0; margin:0; font-size:2.2rem; letter-spacing:.04em}
.hero p {color:#c1e9cf; margin:.45rem 0 0 0}
.kpi {border:1px solid #236d45; border-radius:15px; padding:16px; background:linear-gradient(145deg,#102a1d,#09150f); box-shadow:inset 0 1px #ffffff08; min-height:100px}
.kpi-label {font-size:.82rem;color:#9bc9aa}.kpi-value {font-size:1.65rem;font-weight:750;color:#8cffb0;margin-top:5px}
.chart-shell {border:1px solid #1f6941; border-radius:16px; padding:12px 14px 4px; background:rgba(7,22,15,.76); }
.chart-head {color:#a2ffbd;font-size:1.05rem;font-weight:700;padding:4px 2px 10px}
.cricket-scene {height:68px; position:relative; overflow:hidden; border-radius:12px; margin:2px 0 12px; border:1px solid rgba(117,255,173,.22); }
.cricket-scene:before {content:""; position:absolute; inset:0; opacity:.7;}
.cricket-scene:after {content:""; position:absolute; width:15px;height:15px;border-radius:50%;background:radial-gradient(circle at 30% 25%,#fff0e8 0 8%,#ff8a8a 20%,#e52336 60%,#650c1a 100%);box-shadow:0 0 12px #ff344f,0 0 28px #ff344f80;top:25px;left:8%;animation: ballFlight 4.5s ease-in-out infinite;}
.scene-stadium {background:linear-gradient(180deg,#102d21,#07140f); }
.scene-stadium:before {background:repeating-linear-gradient(90deg,transparent 0 35px,#9affbd10 36px 37px),linear-gradient(180deg,transparent 45%,#54ff9b14 46%,transparent 48%);}
.scene-pitch {background:linear-gradient(90deg,#0b281a,#1c5834,#0b281a);}
.scene-pitch:before {inset:10px 8%;border:1px dashed #baffcc77;border-radius:50%;background:linear-gradient(90deg,transparent 49.7%,#c9ffd455 50%,transparent 50.3%);}
.scene-boundary {background:radial-gradient(ellipse at center,#1c5936,#07140f 70%);}
.scene-boundary:before {inset:7px 18%;border:2px solid #79ffac88;border-radius:50%;box-shadow:0 0 20px #42ff8a44;}
.scene-scoreboard {background:repeating-linear-gradient(90deg,#0b2418 0 22px,#103823 23px 24px);}
.scene-scoreboard:before {background:linear-gradient(90deg,transparent,#75ffad19,transparent);animation: scanSweep 3.5s linear infinite;}
.scene-wicket {background:linear-gradient(135deg,#0a2117,#17492d,#07130f);}
.scene-wicket:before {background:linear-gradient(90deg,transparent 48%,#b5ffcc 48% 49%,transparent 49% 51%,#b5ffcc 51% 52%,transparent 52%),linear-gradient(0deg,transparent 72%,#b5ffcc 73% 76%,transparent 77%);opacity:.28;}
.scene-orbit {background:radial-gradient(circle at 50% 50%,#164b2c,#07140f 68%);}
.scene-orbit:before {inset:7px 35%;border:1px solid #78ffa7aa;border-radius:50%;transform:rotate(-18deg);box-shadow:0 0 0 10px #78ffa718,0 0 0 20px #78ffa710;}
@keyframes ballFlight {0%{left:7%;top:28px;transform:rotate(0)}45%{left:55%;top:8px;transform:rotate(250deg)}70%{left:78%;top:36px;transform:rotate(420deg)}100%{left:7%;top:28px;transform:rotate(720deg)}}
@keyframes scanSweep {0%{transform:translateX(-70%)}100%{transform:translateX(70%)}}
.bat-mark {position:absolute;right:8%;top:9px;font-size:36px;filter:drop-shadow(0 0 8px #8cffb0);animation: batSwing 3.2s ease-in-out infinite;transform-origin:70% 80%;}
@keyframes batSwing {0%,100%{transform:rotate(-18deg) translateY(0)}50%{transform:rotate(17deg) translateY(-3px)}}
[data-testid="stMetric"] {background:#0b2117;border:1px solid #236d45;padding:14px;border-radius:13px}
.stSelectbox label,.stMultiSelect label,.stSlider label {color:#c9f7d6!important}
@media (prefers-reduced-motion: reduce) { *,*::before,*::after { animation:none!important; transition:none!important; } }
</style>
<div class="hero"><h1>IPL // CRICKET ANALYTICS</h1><p>NEON GREEN PERFORMANCE COMMAND CENTER · DATA-DRIVEN CRICKET INSIGHTS</p></div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="cricket-bg-layer" aria-hidden="true">
  <div class="stadium-beam beam-a"></div>
  <div class="stadium-beam beam-b"></div>
  <div class="field-ring"></div>
  <div class="pitch-line"></div>
  <div class="bg-ball ball-a"></div>
  <div class="bg-ball ball-b"></div>
  <div class="bg-ball ball-c"></div>
  <div class="bg-stumps"></div>
</div>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_tables(db_path, modified):
    with sqlite3.connect(db_path) as con:
        names = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", con)["name"].tolist()
        data = {}
        for name in ["deliveries", "matches", "players"]:
            if name in names:
                data[name] = pd.read_sql_query(f'SELECT * FROM "{name}"', con)
        return names, data

try:
    if not DB_PATH.exists() or DB_PATH.stat().st_size == 0:
        st.error(f"Database not found or empty: {DB_PATH}")
        st.info("Put your IPL database at data/raw/ipl.db, then refresh this page.")
        st.stop()
    tables, db = load_tables(str(DB_PATH), DB_PATH.stat().st_mtime)
except Exception as e:
    st.error(f"Could not open database: {e}")
    st.stop()

if "deliveries" not in db:
    st.error("The database must contain a table named 'deliveries'. Tables found: " + (", ".join(tables) if tables else "none"))
    st.stop()
df = db["deliveries"].copy()
# Normalize common column-name variations.
aliases = {"batter_runs":"batter_runs", "batsman_runs":"batter_runs", "runs_batter":"batter_runs", "total_runs":"total_runs", "batter":"batter", "batsman":"batter", "batting_team":"batting_team", "bowler":"bowler", "season_id":"season_id", "match_id":"match_id", "over_number":"over_number", "over":"over_number", "player_out":"player_out", "is_wide_ball":"is_wide_ball", "is_no_ball":"is_no_ball"}
rename = {}
for col in df.columns:
    key = str(col).lower().strip()
    if key in aliases and aliases[key] not in df.columns: rename[col] = aliases[key]
df = df.rename(columns=rename)
for c in ["batter_runs", "total_runs", "season_id", "match_id", "over_number", "innings"]:
    if c not in df: df[c] = 0
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
for c in ["batter", "bowler", "batting_team", "bowling_team", "player_out"]:
    if c not in df: df[c] = "Unknown"
    df[c] = df[c].fillna("Unknown").astype(str)

with st.sidebar:
    st.markdown("## 🟢 CONTROL DECK")
    page = st.radio("Navigate", ["Overview", "Batter Lab", "Team Matchups"], index=0)
    st.markdown("---")
    st.caption("DATABASE STATUS")
    st.success("Connected")
    st.caption(f"File: {DB_PATH.name}")
    st.caption(f"Delivery rows: {len(df):,}")
    st.caption(f"Tables: {', '.join(tables)}")
    st.markdown("---")
    st.caption("Use each chart's selector to change its graph type. Animation filters are not included.")

seasons = sorted(df["season_id"].dropna().unique().tolist())
with st.sidebar:
    chosen_seasons = st.multiselect("Season IDs", seasons, default=seasons)
filtered = df[df["season_id"].isin(chosen_seasons)] if chosen_seasons else df.iloc[0:0]

def chart_card(title, data, x, y, key, default="Bar", color=None, labels=None):
    # Give each chart family its own cricket-ground visual.
    scene_by_key = {
        "team_runs": "scene-stadium", "season_runs": "scene-pitch",
        "top_batters": "scene-scoreboard", "innings_runs": "scene-orbit",
        "batter_season": "scene-boundary", "batter_innings": "scene-wicket",
        "opponents": "scene-stadium", "over_phase": "scene-pitch"
    }
    scene = scene_by_key.get(key, "scene-orbit")
    with st.container(border=True):
        st.markdown(f'<div class="chart-head">✦ {title}</div><div class="cricket-scene {scene}"><span class="bat-mark">🏏</span></div>', unsafe_allow_html=True)
        types = ["Bar", "Line", "Area", "Scatter", "Pie / Donut"]
        kind = st.selectbox("Chart type", types, index=types.index(default), key=f"type_{key}", label_visibility="collapsed")
        if data.empty:
            st.info("No data available for this chart with the current filters.")
            return
        # Each chart has its own accent palette, so charts no longer all look the same.
        chart_palettes = {
            "team_runs": ["#35F2A0", "#00BFA6", "#B6FF4D", "#1E9B72"],
            "season_runs": ["#42D9FF", "#458BFF", "#8C7CFF", "#5EF0D0"],
            "top_batters": ["#FFD166", "#FF9F43", "#FF6B6B", "#F7B7A3"],
            "innings_runs": ["#C084FC", "#8B5CF6", "#EC4899", "#F0ABFC"],
            "batter_season": ["#2DD4BF", "#22D3EE", "#60A5FA", "#A7F3D0"],
            "batter_innings": ["#FB7185", "#F97316", "#FBBF24", "#FDBA74"],
            "opponents": ["#A3E635", "#4ADE80", "#D9F99D", "#14B8A6"],
            "over_phase": ["#F472B6", "#A78BFA", "#60A5FA", "#F0ABFC"],
        }
        palette = chart_palettes.get(key, ["#35F2A0", "#42D9FF", "#C084FC", "#FFD166"])
        if kind == "Pie / Donut":
            pie_data = data.groupby(x, dropna=False)[y].sum().reset_index().nlargest(12, y)
            fig = px.pie(pie_data, names=x, values=y, hole=.58, color_discrete_sequence=palette)
        else:
            kwargs = dict(data_frame=data, x=x, y=y, color=color if color in data.columns else None, labels=labels)
            if kind == "Bar": fig = px.bar(**kwargs, color_discrete_sequence=palette)
            elif kind == "Line": fig = px.line(**kwargs, markers=True, color_discrete_sequence=palette)
            elif kind == "Area": fig = px.area(**kwargs, color_discrete_sequence=palette)
            else: fig = px.scatter(**kwargs, color_discrete_sequence=palette, size=y if (data[y].gt(0).any()) else None)
        # Different plot surface tint per chart, while keeping text readable.
        plot_tints = {
            "team_runs": "rgba(8,48,27,.72)", "season_runs": "rgba(8,32,42,.72)",
            "top_batters": "rgba(34,42,12,.72)", "innings_runs": "rgba(25,18,44,.72)",
            "batter_season": "rgba(9,45,42,.72)", "batter_innings": "rgba(44,22,18,.72)",
            "opponents": "rgba(8,39,33,.72)", "over_phase": "rgba(23,40,14,.72)"
        }
        tint = plot_tints.get(key, "rgba(7,22,15,.76)")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=tint, font_color="#dfffea", margin=dict(l=12,r=12,t=18,b=12), height=340, legend_title_text="", xaxis=dict(showgrid=False, zerolinecolor="rgba(130,255,170,.16)"), yaxis=dict(gridcolor="rgba(130,255,170,.12)", zerolinecolor="rgba(130,255,170,.16)"))
        # Keep outlines subtle and let each chart's individual palette stand out.
        fig.update_traces(marker_line_color="rgba(240,255,245,.72)", marker_line_width=.5)
        if kind == "Line":
            fig.update_traces(line_width=3)
        st.plotly_chart(fig, use_container_width=True, key=f"plot_{key}")

if page == "Overview":
    total_runs = int(filtered["total_runs"].sum())
    matches_count = int(filtered["match_id"].nunique())
    batter_count = int(filtered["batter"].nunique())
    sixes = int((filtered["batter_runs"] == 6).sum())
    cols = st.columns(4)
    for col, label, value in zip(cols, ["TOTAL RUNS", "MATCHES", "BATTERS", "SIXES"], [f"{total_runs:,}", f"{matches_count:,}", f"{batter_count:,}", f"{sixes:,}"]):
        col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)
    st.write("")
    a,b = st.columns(2)
    with a:
        team = filtered.groupby("batting_team", as_index=False)["total_runs"].sum().sort_values("total_runs", ascending=False).head(12)
        chart_card("TEAM RUNS LEADERBOARD", team, "batting_team", "total_runs", "team_runs", "Bar")
    with b:
        season = filtered.groupby("season_id", as_index=False)["total_runs"].sum().sort_values("season_id")
        chart_card("SCORING BY SEASON", season, "season_id", "total_runs", "season_runs", "Line")
    c,d = st.columns(2)
    with c:
        bat = filtered.groupby("batter", as_index=False)["batter_runs"].sum().sort_values("batter_runs", ascending=False).head(12)
        chart_card("TOP BATTERS", bat, "batter", "batter_runs", "top_batters", "Bar")
    with d:
        runs = filtered.groupby("innings", as_index=False)["total_runs"].sum().sort_values("innings")
        chart_card("RUNS BY INNINGS", runs, "innings", "total_runs", "innings_runs", "Pie / Donut")
elif page == "Batter Lab":
    st.subheader("🧪 Batter Lab")
    options = sorted(filtered["batter"].dropna().unique().tolist())
    selected = st.selectbox("Choose batter", options) if options else None
    batter_df = filtered[filtered["batter"] == selected] if selected else filtered.iloc[0:0]
    c1,c2,c3 = st.columns(3)
    c1.metric("Runs", f"{int(batter_df['batter_runs'].sum()):,}")
    c2.metric("Balls recorded", f"{len(batter_df):,}")
    c3.metric("Fours + Sixes", f"{int(batter_df['batter_runs'].isin([4,6]).sum()):,}")
    a,b = st.columns(2)
    with a:
        byseason = batter_df.groupby("season_id", as_index=False)["batter_runs"].sum().sort_values("season_id")
        chart_card("BATTER SEASON TREND", byseason, "season_id", "batter_runs", "batter_season", "Area")
    with b:
        byinnings = batter_df.groupby("innings", as_index=False)["batter_runs"].sum()
        chart_card("RUNS BY INNINGS", byinnings, "innings", "batter_runs", "batter_innings", "Bar")
    with st.expander("View batter data"):
        st.dataframe(batter_df, use_container_width=True, hide_index=True)
else:
    st.subheader("⚔️ Team Matchups")
    teams = sorted(filtered["batting_team"].dropna().unique().tolist())
    chosen_team = st.selectbox("Choose batting team", teams) if teams else None
    team_df = filtered[filtered["batting_team"] == chosen_team] if chosen_team else filtered.iloc[0:0]
    a,b = st.columns(2)
    with a:
        vs = team_df.groupby("bowling_team", as_index=False)["total_runs"].sum().sort_values("total_runs", ascending=False).head(12)
        chart_card("RUNS AGAINST OPPONENTS", vs, "bowling_team", "total_runs", "opponents", "Bar")
    with b:
        phase = team_df.copy()
        phase["over_phase"] = pd.cut(phase["over_number"], bins=[-1,5,14,100], labels=["Powerplay", "Middle", "Death"])
        phase_data = phase.groupby("over_phase", observed=False, as_index=False)["total_runs"].sum()
        chart_card("SCORING BY OVER PHASE", phase_data, "over_phase", "total_runs", "over_phase", "Pie / Donut")
    with st.expander("View team delivery data"):
        st.dataframe(team_df, use_container_width=True, hide_index=True)

st.markdown("<div style='text-align:center;color:#6f9b7e;padding:24px 0 6px;font-size:.8rem'>IPL ANALYTICS • NEON GREEN EDITION • INSIGHTS FROM YOUR LOCAL DATABASE</div>", unsafe_allow_html=True)
