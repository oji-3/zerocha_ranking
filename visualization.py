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
    
    # Use consistent width but restore original height
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.set_tight_layout(True)
    
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

    # Use a consistent layout
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

def create_comparison_table(melody_arrow_members, top_z2_team_members, melody_arrow_name, top_z2_team_name):
    """
    Creates comparison table data between Melody Arrow members and top Z2 team members.
    
    Parameters:
    melody_arrow_members (DataFrame): DataFrame with MemberName and Points for Melody Arrow
    top_z2_team_members (DataFrame): DataFrame with MemberName and Points for top Z2 team
    melody_arrow_name (str): Name of the Melody Arrow team
    top_z2_team_name (str): Name of the top Z2 team
    
    Returns:
    dict: Dictionary containing table data and win-loss record
    """
    # Sort members by points in descending order
    melody_arrow_members = melody_arrow_members.sort_values('Points', ascending=False).reset_index(drop=True)
    top_z2_team_members = top_z2_team_members.sort_values('Points', ascending=False).reset_index(drop=True)
    
    # Ensure we have at least 5 rows (or as many as available)
    max_rows = min(5, max(len(melody_arrow_members), len(top_z2_team_members)))
    
    # Prepare data for the table
    table_data = []
    melody_wins = 0
    z2_wins = 0
    
    for i in range(max_rows):
        row = {}
        
        # Melody Arrow member
        if i < len(melody_arrow_members):
            melody_member = melody_arrow_members.iloc[i]
            row["melody_name"] = f"{i+1}. {melody_member['MemberName']}"
            row["melody_points"] = int(melody_member['Points'])
        else:
            row["melody_name"] = ""
            row["melody_points"] = 0
        
        # Top Z2 team member
        if i < len(top_z2_team_members):
            z2_member = top_z2_team_members.iloc[i]
            row["z2_name"] = f"{i+1}. {z2_member['MemberName']}"
            row["z2_points"] = int(z2_member['Points'])
        else:
            row["z2_name"] = ""
            row["z2_points"] = 0
        
        # Result column
        if i < len(melody_arrow_members) and i < len(top_z2_team_members):
            melody_points = row["melody_points"]
            z2_points = row["z2_points"]
            
            if melody_points > z2_points:
                row["result"] = "WIN"
                melody_wins += 1
            elif melody_points < z2_points:
                row["result"] = "LOSE"
                z2_wins += 1
            else:
                row["result"] = "TIE"
        else:
            row["result"] = ""
        
        table_data.append(row)
    
    return {
        "table_data": table_data,
        "melody_name": melody_arrow_name,
        "z2_name": top_z2_team_name,
        "melody_wins": melody_wins,
        "z2_wins": z2_wins
    }

def create_comparison_svg(comparison_data):
    """
    Creates an SVG visualization for the comparison table.
    
    Parameters:
    comparison_data (dict): Dictionary with comparison data from create_comparison_table
    
    Returns:
    str: SVG markup as a string
    """
    melody_name = comparison_data["melody_name"]
    z2_name = comparison_data["z2_name"]
    table_data = comparison_data["table_data"]
    
    svg = f'''<div style="padding: 0; margin: 0 auto; width: 100%; max-width: 800px;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="100%">
  <!-- Background -->
  <rect width="800" height="320" fill="#f8f9fa" rx="10" ry="10" />
  
  <!-- Team headers -->
  <rect x="100" y="10" width="250" height="50" rx="8" ry="8" fill="#3D5A80" />
  <text x="225" y="42" font-family="'Helvetica Neue', Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#ffffff">
    {melody_name}
  </text>
  
  <rect x="450" y="10" width="250" height="50" rx="8" ry="8" fill="#E07A5F" />
  <text x="575" y="42" font-family="'Helvetica Neue', Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#ffffff">
    {z2_name}
  </text>
  
  <!-- Center column -->
  <rect x="350" y="10" width="100" height="50" rx="8" ry="8" fill="#3D5A80" opacity="0.2" />
  <text x="400" y="42" font-family="'Helvetica Neue', Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">
    結果
  </text>
'''
    
    # Add rows for each member comparison
    y_pos = 70
    for row in table_data:
        melody_name = row.get("melody_name", "")
        melody_points = row.get("melody_points", 0)
        z2_name = row.get("z2_name", "")
        z2_points = row.get("z2_points", 0)
        result = row.get("result", "")
        
        # Format points with commas
        melody_points_formatted = f"{melody_points:,}" if melody_points else ""
        z2_points_formatted = f"{z2_points:,}" if z2_points else ""
        
        result_color = "#81B29A" if result == "WIN" else "#E07A5F" if result == "LOSE" else "#95a5a6"
        
        svg += f'''
  <!-- Row -->
  <rect x="100" y="{y_pos}" width="250" height="50" rx="5" ry="5" fill="#ffffff" stroke="#ddd" stroke-width="1" />
  <text x="110" y="{y_pos + 30}" font-family="'Helvetica Neue', Arial, sans-serif" font-size="14" fill="#333">
    {melody_name}
  </text>
  <text x="320" y="{y_pos + 30}" font-family="'Helvetica Neue', Arial, sans-serif" font-size="14" text-anchor="end" fill="#333">
    {melody_points_formatted}
  </text>
  
  <rect x="350" y="{y_pos}" width="100" height="50" rx="5" ry="5" fill="{result_color}" stroke="#ddd" stroke-width="1" />
  <text x="400" y="{y_pos + 30}" font-family="'Helvetica Neue', Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#ffffff">
    {result}
  </text>
  
  <rect x="450" y="{y_pos}" width="250" height="50" rx="5" ry="5" fill="#ffffff" stroke="#ddd" stroke-width="1" />
  <text x="690" y="{y_pos + 30}" font-family="'Helvetica Neue', Arial, sans-serif" font-size="14" text-anchor="end" fill="#333">
    {z2_points_formatted}
  </text>
  <text x="460" y="{y_pos + 30}" font-family="'Helvetica Neue', Arial, sans-serif" font-size="14" fill="#333">
    {z2_name}
  </text>
'''
        y_pos += 50
    
    svg += '''
</svg>
</div>'''
    
    return svg