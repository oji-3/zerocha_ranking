import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import plotly.graph_objects as go

def lighten_color(base_color, blend_factor=0.2):
    r, g, b, a = base_color
    r_new = r + (1.0 - r) * blend_factor
    g_new = g + (1.0 - g) * blend_factor
    b_new = b + (1.0 - b) * blend_factor
    return (r_new, g_new, b_new, a)

def create_interactive_team_chart(team_points, team_members):
    teams = team_points['TeamName'].tolist()
    
    fig = go.Figure()
    
    team_member_data = {
        team: team_members[team_members['TeamName'] == team].sort_values('Points', ascending=False)
        for team in teams
    }

    num_teams = len(teams)
    # Generate colors similar to viridis
    viridis_positions = np.linspace(0, 0.9, num_teams)
    team_colors = [
        (int(68 + 54 * pos), int(1 + 139 * pos), int(84 + 147 * pos))
        for pos in viridis_positions
    ]
    
    for i, team in enumerate(teams):
        team_data = team_member_data[team]
        base_color = team_colors[i]
        n_members = len(team_data)
        
        # Sort members by points for stacking (smallest at bottom)
        team_data = team_data.sort_values('Points', ascending=True)
        
        for j, (_, member_row) in enumerate(team_data.iterrows()):
            points = member_row['Points']
            if points == 0:
                continue
                
            # Calculate a shade of the base color
            blend_factor = 0.5 * (j / max(1, n_members - 1))
            r, g, b = base_color
            r_new = r + int((255 - r) * blend_factor)
            g_new = g + int((255 - g) * blend_factor)
            b_new = b + int((255 - b) * blend_factor)
            member_color = f'rgb({r_new}, {g_new}, {b_new})'
            
            fig.add_trace(go.Bar(
                x=[team],
                y=[points],
                name=member_row['MemberName'],
                marker_color=member_color,
                hoverinfo='text',
                hovertext=f"{member_row['MemberName']}: {int(points):,} ポイント",
                showlegend=True
            ))
    
    # Add total points labels
    for team in teams:
        total_points = team_points.loc[team_points['TeamName'] == team, 'Points'].values[0]
        fig.add_annotation(
            x=team,
            y=total_points,
            text=f'{int(total_points):,}',
            showarrow=False,
            yshift=10,
            font=dict(size=14, color='black', family='Arial, sans-serif')
        )
    
    fig.update_layout(
        title='チームポイント',
        yaxis_title='ポイント',
        barmode='stack',
        xaxis={'categoryorder': 'total descending'},
        hovermode='closest',
        xaxis_tickangle=-45,
        legend_title_text='メンバー (ポイント)',
        legend=dict(x=1.05, y=0.5),
        margin=dict(l=50, r=50, t=80, b=80),
    )
    
    return fig