import streamlit as st
import pandas as pd
import io
import os
import time
from fetcher import get_ranking_data
from visualization import create_team_chart, create_comparison_table, create_comparison_svg

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
    
    # First, create the comparison table
    # Get Melody Arrow data regardless of Z group
    melody_arrow_df = all_merged_df[all_merged_df["TeamName"] == "メロディーアロウ"]
    
    if len(melody_arrow_df) > 0:
        # Get Melody Arrow team information
        melody_arrow_members = melody_arrow_df.groupby('MemberName')['Points'].sum().reset_index()
        
        # Check if Melody Arrow is in Z2
        melody_arrow_in_z2 = "Z2" in melody_arrow_df["Z"].values
        
        # Determine which Z2 team to compare with
        position = "1位"
        if melody_arrow_in_z2 and len(team_points) > 0 and team_points.iloc[0]['TeamName'] == "メロディーアロウ":
            # If Melody Arrow is top Z2 team, compare with 2nd place
            if len(team_points) > 1:
                top_z2_team_name = team_points.iloc[1]['TeamName']
                position = "2位"
            else:
                st.warning("メロディーアロウは1位ですが、比較するZ2チームがありません。")
                
                # Display the team chart
                fig = create_team_chart(team_points, team_members)
                st.pyplot(fig)
                return
        else:
            # Compare with top Z2 team
            if len(team_points) > 0:
                top_z2_team_name = team_points.iloc[0]['TeamName']
            else:
                st.warning("Z2チームが見つかりません。")
                return
        
        # Get top Z2 team member data
        top_z2_team_members = z2_df[z2_df["TeamName"] == top_z2_team_name]
        top_z2_team_members = top_z2_team_members.groupby('MemberName')['Points'].sum().reset_index()
        
        # Create and get the comparison table data
        comparison_data = create_comparison_table(
            melody_arrow_members,
            top_z2_team_members,
            "メロディーアロウ",
            top_z2_team_name
        )
        
        # Create SVG comparison chart
        svg_chart = create_comparison_svg(comparison_data)
        
        # Display the SVG chart
        st.markdown(svg_chart, unsafe_allow_html=True)
        
        # Add some vertical space
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        
        # Add some vertical space
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        
        # Now display the team chart
        fig = create_team_chart(team_points, team_members)
        st.pyplot(fig)
    else:
        st.warning("メロディーアロウチームが見つかりません。")
        
        # Display the team chart if no comparison is possible
        fig = create_team_chart(team_points, team_members)
        st.pyplot(fig)

if __name__ == "__main__":
    main()