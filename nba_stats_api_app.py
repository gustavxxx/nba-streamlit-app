
import streamlit as st
import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll

st.set_page_config(page_title="NBA Player vs Team Stats", layout="centered")
st.title("🏀 NBA Player Stats vs Each Team")

# Fetch and sort all NBA players
@st.cache_data
def get_all_players():
    player_list = players.get_players()
    return sorted(player_list, key=lambda x: x['full_name'])

all_players = get_all_players()
player_names = [p['full_name'] for p in all_players]
player_lookup = {p['full_name']: p['id'] for p in all_players}

# Streamlit sidebar
st.sidebar.header("Player Selection")
selected_player = st.sidebar.selectbox("Select a player", player_names)

if selected_player:
    player_id = player_lookup[selected_player]
    st.sidebar.success(f"Player ID: {player_id}")

    if st.sidebar.button("Get Stats"):
        st.info("Fetching game logs...")
        try:
            gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=SeasonAll.all)
            df = gamelog.get_data_frames()[0]

            if not df.empty:
                st.subheader("📊 Game Log")
                st.dataframe(df[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST']])

                st.subheader("📈 Average Performance vs Each Team")
                df['OPPONENT'] = df['MATCHUP'].apply(lambda x: x.split(' ')[-1])
                df['TOTAL'] = df['PTS'] + df['REB'] + df['AST']
                summary = df.groupby('OPPONENT')[['PTS', 'REB', 'AST', 'TOTAL']].mean().round(2)
                summary = summary.rename(columns={
                    'PTS': 'Avg Points',
                    'REB': 'Avg Rebounds',
                    'AST': 'Avg Assists',
                    'TOTAL': 'Avg Total Contribution'
                })
                summary = summary.sort_values(by='Avg Total Contribution', ascending=False)
                st.dataframe(summary)

                csv = summary.to_csv().encode('utf-8')
                st.download_button(
                    label="Download Summary CSV",
                    data=csv,
                    file_name=f"{selected_player.replace(' ', '_')}_avg_vs_teams.csv",
                    mime='text/csv'
                )
            else:
                st.error("No game data found for this player.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
