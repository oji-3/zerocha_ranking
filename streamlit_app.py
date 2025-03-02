import time
import logging
import random
import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import japanize_matplotlib

# Selenium imports retained for local development
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False
    st.warning("Selenium模块导入失败。只能使用模拟数据模式。")

# ログ設定: INFO レベルのログをコンソールに出す
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# モックデータ用の乱数シードを設定（常に同じランダムデータを生成するため）
random.seed(42)

def generate_mock_data():
    """
    実際のWebスクレイピングを行う代わりに、モックデータを生成する関数
    """
    # csv_dataから読み込まれたメンバー情報を使用
    user_ids = members_df['UserID'].unique().tolist()
    
    # 一定の範囲内でランダムなポイントを生成
    data = [("UserID", "Points")]
    for user_id in user_ids:
        # TeamとZ情報をもとにポイントの範囲を決定
        member_info = members_df[members_df['UserID'] == user_id].iloc[0]
        team = member_info['TeamName']
        z_group = member_info['Z']
        
        # チームや区分ごとに違った範囲の値を生成（より現実的な分布に）
        base_points = 1000 if z_group == 'Z1' else 800
        team_factor = {
            'GeMuse': 1.2,
            'policy': 1.1,
            'まぶだちゅ！': 1.0,
            'Eleminus': 0.9,
            'inest': 1.3,
            'Lilly Palette': 1.05,
            'くろれぱふぇ': 0.95,
            'ぺぷるっ！': 1.15,
            'メロディーアロウ': 1.0
        }.get(team, 1.0)
        
        # ランダムなポイントを生成（チームによって傾向を変える）
        points = int(base_points * team_factor * (0.5 + random.random() * 1.5))
        data.append((user_id, str(points)))
    
    return data

def fetch_all_events_once(driver, urls):
    """
    1つのブラウザインスタンス (driver) を使い回し、
    与えられた各URLに順番にアクセスしてデータを取得する。
    """
    data = []
    for url in urls:
        logging.info(f"[SingleBrowser] Moving to: {url}")
        start_time = time.time()
        driver.get(url)

        # 要素がロードされるのを待つ（最大3秒）
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.nav-link.active[data-rr-ui-event-key='#ranking']")
                )
            )
        except Exception as e:
            logging.warning(f"[SingleBrowser] Timeout or error: {url} => {e}")
            continue

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        li_items = soup.select("ul.list li")

        for li in li_items:
            user_link = li.select_one("a.user-name")
            user_id = user_link["href"].split("/")[-1] if user_link else "N/A"
            point_tag = li.select_one("span.css-kidsya span.num")
            points = point_tag.get_text(strip=True).replace(",", "") if point_tag else "0"
            data.append((user_id, points))

        elapsed = time.time() - start_time
        logging.info(f"[SingleBrowser] Fetched {len(li_items)} items from {url} in {elapsed:.2f} sec")

    return data

def get_ranking_single_browser():
    """
    1つのブラウザインスタンスを使い回して各イベントURLを順番に取得する。
    ただし、Streamlit Cloudでの実行環境ではSeleniumが動作しないため、
    代わりにモックデータを生成する。
    """
    # Seleniumが利用可能かつ、モックデータモードが無効の場合のみ実際のスクレイピングを実行
    if SELENIUM_AVAILABLE and not st.session_state.get('use_mock_data', True):
        urls = [
            "https://mixch.tv/live/event/19704#ranking",
            "https://mixch.tv/live/event/19705#ranking",
            "https://mixch.tv/live/event/19707#ranking",
        ]

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--disable-gpu')
        
        try:
            # Try to create a ChromeDriver using webdriver_manager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # ヘッダー行を含むリストを用意
            data = [("UserID", "Points")]

            try:
                # 同じ driver を使って全URLを順番に取得
                event_data = fetch_all_events_once(driver, urls)
                data.extend(event_data)
            finally:
                # 全URL分取得し終わったらブラウザを閉じる
                driver.quit()
                
            return data
        except Exception as e:
            logging.error(f"Error in web scraping: {e}")
            st.error(f"ウェブスクレイピングエラー: {e}. モックデータを使用します。")
            # エラーが発生した場合はモックデータにフォールバック
            return generate_mock_data()
    else:
        # Seleniumが利用できないかモックデータモードが有効の場合は、モックデータを返す
        logging.info("Using mock data instead of web scraping")
        return generate_mock_data()

def lighten_color(base_color, blend_factor=0.2):
    r, g, b, a = base_color
    r_new = r + (1.0 - r) * blend_factor
    g_new = g + (1.0 - g) * blend_factor
    b_new = b + (1.0 - b) * blend_factor
    return (r_new, g_new, b_new, a)

# --- 内部変数として持つCSVデータ（メンバー情報） ---
csv_data = """UserID,MemberName,TeamName,Z
17816674,セル,GeMuse,Z1
18322396,栗山さとみ,GeMuse,Z1
17277753,日向まりの,GeMuse,Z1
18325377,白咲ひかり,GeMuse,Z1
17843359,藤宮かれん,GeMuse,Z1
18236437,雪野まひろ,policy,Z1
18323091,花井瑠莉奈,policy,Z1
18324664,空音ここみ,policy,Z1
18325059,朝比奈凛,policy,Z1
18325046,白花まりや,policy,Z1
15497902,りりあ,まぶだちゅ！,Z1
17012428,希咲りほ,まぶだちゅ！,Z1
18324686,三崎桃果,まぶだちゅ！,Z1
16268782,POLLIE,まぶだちゅ！,Z1
15149101,白咲ひとみ,まぶだちゅ！,Z1
18323474,水無月黎音,Eleminus,Z2
17450977,姫菫めぐ,Eleminus,Z2
18359702,鈴蘭なび,Eleminus,Z2
18323582,雪名ゆき,Eleminus,Z2
18330867,愛乃もも,Eleminus,Z2
17788691,神乃さや,inest,Z2
10049453,白雪らら,inest,Z2
18324871,桜井みなみ,inest,Z2
18323389,夏月涼花,inest,Z2
18320795,なのは,Lilly Palette,Z2
18323162,平手美羽,Lilly Palette,Z2
18321708,藤堂いちご,Lilly Palette,Z2
18320812,駒音にこ,Lilly Palette,Z2
17960902,倉田いとは,Lilly Palette,Z2
18324271,あまの,くろれぱふぇ,Z2
18323171,春風りな,くろれぱふぇ,Z2
18322580,星野らら,くろれぱふぇ,Z2
18325056,理生,くろれぱふぇ,Z2
18321693,松井ほのか,くろれぱふぇ,Z2
18321472,安室ことり,ぺぷるっ！,Z2
8323532,ゆり,ぺぷるっ！,Z2
18323398,夢咲ここあ ,ぺぷるっ！,Z2
18348648,七瀬ゆめ,ぺぷるっ！,Z2
18314414,星凪ゆあ,ぺぷるっ！,Z2
17100255,枢木ゆん,メロディーアロウ,Z2
18325540,池田 遥希,メロディーアロウ,Z2
18324803,真白もるつ,メロディーアロウ,Z2
18324140,望月まりあ,メロディーアロウ,Z2
18326499,黒川奈音,メロディーアロウ,Z2
"""
members_df = pd.read_csv(io.StringIO(csv_data))
members_df["UserID"] = members_df["UserID"].astype(str)

# セッション状態の初期化
if 'use_mock_data' not in st.session_state:
    st.session_state.use_mock_data = True

# ----------------------------------------
# Streamlit アプリ本体
# ----------------------------------------
st.title("チームポイント")

# サイドバー設定
st.sidebar.title("設定")

# モックデータモードの切り替えスイッチ
use_mock = st.sidebar.checkbox(
    "モックデータを使用", 
    value=st.session_state.use_mock_data,
    help="オンの場合、実際のスクレイピングを行わず、モックデータを使用します"
)
st.session_state.use_mock_data = use_mock

# モード表示
if st.session_state.use_mock_data:
    st.sidebar.info("現在モックデータモードで実行中です。実際のデータは取得されません。")
else:
    st.sidebar.warning("実際のデータ取得モードです。Streamlit Cloudでは失敗する可能性があります。")

# データ取得部分
with st.spinner("ランキングデータを取得しています..."):
    ranking_data = get_ranking_single_browser()

# 取得結果を DataFrame 化
ranking_df = pd.DataFrame(ranking_data[1:], columns=ranking_data[0])
ranking_df["UserID"] = ranking_df["UserID"].astype(str)
ranking_df["Points"] = pd.to_numeric(ranking_df["Points"], errors='coerce').fillna(0)

# マージ
merged_df = pd.merge(
    members_df,
    ranking_df[['UserID', 'Points']],
    on='UserID',
    how='left'
).fillna(0)

# チームごとに集計
team_points = merged_df.groupby('TeamName')['Points'].sum().reset_index()
team_points = team_points.sort_values('Points', ascending=False)
team_members = merged_df.groupby(['TeamName', 'MemberName'])['Points'].sum().reset_index()
teams = team_points['TeamName'].tolist()

# Z区分ごとのサブグループを作成
z1_teams = merged_df[merged_df['Z'] == 'Z1']['TeamName'].unique().tolist()
z2_teams = merged_df[merged_df['Z'] == 'Z2']['TeamName'].unique().tolist()

# グラフ描画
st.header("チーム別ポイント総計")

# Z区分によって別々に表示するオプション
show_by_z = st.checkbox("Z区分ごとに表示", value=True)

if show_by_z:
    # Z1チームのグラフ
    if z1_teams:
        st.subheader("Z1チーム")
        plot_teams(z1_teams, team_points, team_members, merged_df)
    
    # Z2チームのグラフ 
    if z2_teams:
        st.subheader("Z2チーム")
        plot_teams(z2_teams, team_points, team_members, merged_df)
else:
    # すべてのチームを一つのグラフに表示
    plot_teams(teams, team_points, team_members, merged_df)

# データテーブル表示
if st.checkbox("詳細データを表示"):
    st.subheader("メンバー別ポイント詳細")
    
    # Z区分によるフィルタリングオプション
    z_filter = st.radio("Z区分フィルター", ["すべて", "Z1", "Z2"])
    
    filtered_df = merged_df
    if z_filter != "すべて":
        filtered_df = merged_df[merged_df['Z'] == z_filter]
    
    # データを表示
    st.dataframe(
        filtered_df[['TeamName', 'MemberName', 'Points', 'Z']]
        .sort_values(['Z', 'TeamName', 'Points'], ascending=[True, True, False])
    )

# グラフ描画関数
def plot_teams(teams_to_plot, team_points, team_members, merged_df):
    if not teams_to_plot:
        st.write("表示するチームがありません")
        return
        
    fig, ax = plt.subplots(figsize=(12, 8))
    team_member_data = {
        team: team_members[team_members['TeamName'] == team].sort_values('Points', ascending=False)
        for team in teams_to_plot
    }

    num_teams = len(teams_to_plot)
    team_colors = plt.cm.viridis(np.linspace(0, 0.9, num_teams))
    bottom = np.zeros(len(teams_to_plot))
    legend_handles = []
    legend_labels = []

    for i, team in enumerate(teams_to_plot):
        team_data = team_member_data[team]
        base_color = team_colors[i]
        n_members = len(team_data)

        for j, (_, member_row) in enumerate(team_data.iterrows()):
            height = member_row['Points']
            if height == 0:
                continue
            blend_factor = 0.5 * (j / max(1, n_members - 1))
            member_color = lighten_color(base_color, blend_factor)

            ax.bar(
                i,
                height,
                bottom=bottom[i],
                color=member_color,
                alpha=0.9
            )
            bottom[i] += height

            legend_handles.append(plt.Rectangle((0, 0), 1, 1, color=member_color))
            legend_labels.append(f"{member_row['MemberName']} ({int(height)})")

        # チームの合計点数をグラフ上部に表示
        total_height = team_points.loc[team_points['TeamName'] == team, 'Points'].values[0]
        ax.text(
            i,
            total_height + (total_height * 0.02),
            f'{int(total_height):,}',
            ha='center',
            fontsize=10,
            fontweight='bold'
        )

    ax.set_xticks(range(len(teams_to_plot)))
    ax.set_xticklabels(teams_to_plot, rotation=45, ha='right')
    ax.set_ylabel('ポイント')
    ax.set_title('チームポイント')
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # 凡例の配置調整
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
    ax.legend(
        legend_handles,
        legend_labels,
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        fontsize=8,
        title='メンバー (ポイント)'
    )
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{int(x):,}"))

    st.pyplot(fig)
