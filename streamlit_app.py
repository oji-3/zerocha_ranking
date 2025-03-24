import streamlit as st
import pandas as pd
import io
import os
import time
from fetcher import get_ranking_data
from visualization import create_team_chart

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
    
    # リーグ選択のプルダウンを追加（デフォルトをZ2に変更）
    league_filter = st.selectbox(
        "リーグを選択",
        ["Z2", "ALL"],
        index=0  # Z2をデフォルト選択に設定
    )
    
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
    
    # 選択されたリーグでデータをフィルタリング
    if league_filter == "Z2":
        merged_df = merged_df[merged_df["Z"] == "Z2"]
    
    team_points = merged_df.groupby('TeamName')['Points'].sum().reset_index()
    team_points = team_points.sort_values('Points', ascending=False)

    team_members = merged_df.groupby(['TeamName', 'MemberName'])['Points'].sum().reset_index()
    
    fig = create_team_chart(team_points, team_members)
    st.pyplot(fig)

if __name__ == "__main__":
    main()