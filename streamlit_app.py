import streamlit as st
import pandas as pd
import io

from fetcher import get_ranking_data
from visualization import create_interactive_team_chart

def main():
    st.title("チームポイント")
    
    with open("members.csv", "r") as f:
        csv_data = f.read()
    members_df = pd.read_csv(io.StringIO(csv_data))
    members_df["UserID"] = members_df["UserID"].astype(str)
    
    with st.spinner("ランキングデータを取得しています..."):
        ranking_data = get_ranking_data()
    
    ranking_df = pd.DataFrame(ranking_data[1:], columns=ranking_data[0])
    ranking_df["UserID"] = ranking_df["UserID"].astype(str)
    ranking_df["Points"] = pd.to_numeric(ranking_df["Points"], errors='coerce').fillna(0)
    
    merged_df = pd.merge(
        members_df,
        ranking_df[['UserID', 'Points']],
        on='UserID',
        how='left'
    ).fillna(0)
    #merged_df.loc[merged_df['TeamName'] == 'inest', 'Points'] = merged_df.loc[merged_df['TeamName'] == 'inest', 'Points'] * 1.25
    team_points = merged_df.groupby('TeamName')['Points'].sum().reset_index()
    team_points = team_points.sort_values('Points', ascending=False)

    team_members = merged_df.groupby(['TeamName', 'MemberName'])['Points'].sum().reset_index()
    
    fig = create_interactive_team_chart(team_points, team_members)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()