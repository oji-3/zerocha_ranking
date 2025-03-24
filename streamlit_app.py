import streamlit as st
import pandas as pd
import io
import os
import time
from fetcher import get_ranking_data
from visualization import create_team_chart, create_comparison_table

def main():
    st.title("チームポイント")
    
    with st.spinner("Playwrightを準備しています。少々お待ちください..."):
        os.system("playwright install")
    
    
    if not os.path.exists("members.csv"):
        st.error("members.csv ファイルが見つかりません。")
        return
    
    with open("members.csv", "r") as f:
        csv_data = f.read()
    members_df = pd.read_csv(io.StringIO(csv_data))
    members_df["UserID"] = members_df["UserID"].astype(str)
    
    with st.spinner("ランキングデータを取得しています..."):
        try:
            ranking_data = get_ranking_data()
        except Exception as e:
            st.error(f"ランキングデータの取得中にエラーが発生しました: {e}")
            ranking_data = [("UserID", "Points")]
    
    if len(ranking_data) <= 1:
        st.warning("ランキングデータが取得できませんでした。サイト構造が変更された可能性があります。")
        st.warning("何回もリロードすればいつか出ます。")
    
    ranking_df = pd.DataFrame(ranking_data[1:], columns=ranking_data[0])
    
    ranking_df["UserID"] = ranking_df["UserID"].astype(str)
    ranking_df["Points"] = pd.to_numeric(ranking_df["Points"], errors='coerce').fillna(0)
    
    merged_df = pd.merge(
        members_df,
        ranking_df[['UserID', 'Points']],
        on='UserID',
        how='left'
    ).fillna(0)
    
    # Keep all data for reference
    all_merged_df = merged_df.copy()
    
    # Filter for Z2 data for the team chart
    z2_df = merged_df[merged_df["Z"] == "Z2"]
    
    team_points = z2_df.groupby('TeamName')['Points'].sum().reset_index()
    team_points = team_points.sort_values('Points', ascending=False)

    team_members = z2_df.groupby(['TeamName', 'MemberName'])['Points'].sum().reset_index()
    
    # Create and display the original team chart
    fig = create_team_chart(team_points, team_members)
    st.pyplot(fig)
    
    # Now create the comparison table
    # Get Melody Arrow data regardless of Z group
    melody_arrow_df = all_merged_df[all_merged_df["TeamName"] == "メロディーアロウ"]
    
    if len(melody_arrow_df) > 0:
        # Get Melody Arrow team information
        melody_arrow_members = melody_arrow_df.groupby('MemberName')['Points'].sum().reset_index()
        
        # Check if Melody Arrow is in Z2
        melody_arrow_in_z2 = "Z2" in melody_arrow_df["Z"].values
        
        # Determine which Z2 team to compare with
        if melody_arrow_in_z2 and len(team_points) > 0 and team_points.iloc[0]['TeamName'] == "メロディーアロウ":
            # If Melody Arrow is top Z2 team, compare with 2nd place
            if len(team_points) > 1:
                top_z2_team_name = team_points.iloc[1]['TeamName']
                st.subheader(f"メロディーアロウ (1位) vs {top_z2_team_name} (2位) 比較")
            else:
                st.warning("メロディーアロウは1位ですが、比較するZ2チームがありません。")
                return
        else:
            # Compare with top Z2 team
            if len(team_points) > 0:
                top_z2_team_name = team_points.iloc[0]['TeamName']
                st.subheader(f"メロディーアロウ vs {top_z2_team_name} (Z2 1位) 比較")
            else:
                st.warning("Z2チームが見つかりません。")
                return
        
        # Get top Z2 team member data
        top_z2_team_members = z2_df[z2_df["TeamName"] == top_z2_team_name]
        top_z2_team_members = top_z2_team_members.groupby('MemberName')['Points'].sum().reset_index()
        
        # Create and display the comparison table
        comparison_fig = create_comparison_table(
            melody_arrow_members,
            top_z2_team_members,
            "メロディーアロウ",
            top_z2_team_name
        )
        st.pyplot(comparison_fig)
    else:
        st.warning("メロディーアロウチームが見つかりません。")

if __name__ == "__main__":
    main()