import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib

def lighten_color(base_color, blend_factor=0.2):
    r, g, b, a = base_color
    r_new = r + (1.0 - r) * blend_factor
    g_new = g + (1.0 - g) * blend_factor
    b_new = b + (1.0 - b) * blend_factor
    return (r_new, g_new, b_new, a)

def create_team_chart(team_points, team_members):
    teams = team_points['TeamName'].tolist()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    team_member_data = {
        team: team_members[team_members['TeamName'] == team].sort_values('Points', ascending=False)
        for team in teams
    }

    num_teams = len(teams)
    team_colors = plt.cm.viridis(np.linspace(0, 0.9, num_teams))
    bottom = np.zeros(len(teams))
    legend_handles = []
    legend_labels = []

    for i, team in enumerate(teams):
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

        total_height = team_points.loc[team_points['TeamName'] == team, 'Points'].values[0]
        ax.text(
            i,
            total_height + (total_height * 0.02),
            f'{int(total_height):,}',
            ha='center',
            fontsize=10,
            fontweight='bold'
        )

    ax.set_xticks(range(len(teams)))
    ax.set_xticklabels(teams, rotation=45, ha='right')
    ax.set_ylabel('ポイント')
    ax.set_title('チームポイント')
    ax.grid(axis='y', linestyle='--', alpha=0.3)

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
    
    return fig