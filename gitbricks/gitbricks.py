from github import Github
import os
import plotly.graph_objects as go
import numpy as np
import calendar
from datetime import datetime, date, timedelta
import pandas as pd
from kaleido.scopes.plotly import PlotlyScope

def gitbricks(repo_name, start_year, start_month):
    """
    """
    start_day = 1
    g = Github(os.environ["GITHUB_TOKEN"])

    start_date = datetime(start_year, start_month, start_day)
    end_date = add_years(start_date, 1)

    dates_list = daterange(start_date, end_date)

    df = pd.DataFrame(dates_list, columns = ['date'] )
    df['n_commits'] = [0]*len(df.index)

    repo = g.get_repo(repo_name)
    commits = repo.get_commits(since=start_date, until=end_date)
    commits.totalCount

    for cmt in commits:
        dt = cmt.commit.author.date
        dt = datetime.combine(dt.date(), datetime.min.time())
        df.loc[df['date']==dt, 'n_commits'] += 1

    total = commits.totalCount

    all_weeks_start_month = calendar.monthcalendar(start_year, start_month)
    first_week = all_weeks_start_month[0]
    months = list(calendar.month_abbr)
    week_list = []
    row = []
    month_of_week = []
    date_text_row = []
    date_text = []
    extra_days = 0
    for i in range(365):
        
        if i < 7 and first_week[i] == 0:
            date_text_row.append('')
            row.append(0)
            extra_days+=1
            continue
        
        j = i-extra_days
        if i % 7 == 0:
            week_list.append(row)
            txt = str(months[df.iloc[j]['date'].month])
            month_of_week.append(txt)
            date_text.append(date_text_row)
            date_text_row = []
            row = []
        
        n_commits = df.iloc[j]['n_commits']
        row.append(n_commits)
        
        if n_commits == 0:
            n_txt = 'No commits on '
        elif n_commits == 1:
            n_txt = '1 commit on '
        else:
            n_txt = f'{n_commits} commits on '
        
        dt = df.iloc[j]['date']
        date_text_row.append(n_txt + dt.strftime('%b %d, %Y'))

    date_text_T = list(map(list, zip(*date_text)))

    gapwidth = 5
    arr = np.array(week_list)
    arrT = arr.T
    arrT_list = arrT.tolist()

    weekdays = list(calendar.day_abbr)

    title = f'Commit overview for "{repo.full_name}" from {start_day} {months[start_month]} {start_year} to {start_day} {months[start_month]} {start_year+1} (total={total})'

    layout = go.Layout(
        title=title,
        title_font_family='IBM Plex Mono,monospace',
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        autosize=False,
        height=175,
        width=1000,
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=50,
            pad=0
        ),
        showlegend=False,
        xaxis={'side': 'top'}
    )

    heatmap2 = go.Heatmap(
        z=arrT_list,
        x=list(range(weeks_for_year(start_year))),
        y=weekdays,
        hoverongaps = False,
        xgap = gapwidth,
        ygap = gapwidth,
        colorscale=[
            [0, "#ebedf0"],
            [0.01, "#ebedf0"],
            [0.01, "#9be9a8"],
            [0.4, "#9be9a8"],
            [0.4, "#40c463"],
            [0.6, "#40c463"],
            [0.6, "#30a14e"],
            [0.8, "#30a14e"],
            [0.8, "#216e39"],
            [1, "#216e39"],
        ],
        hoverinfo='text',
        text=date_text_T
    )
    fig2 = go.Figure(
        data=heatmap2,
        layout=layout
    )
    fig2.update_yaxes(autorange="reversed", tick0=1, dtick=2)
    fig2.update_xaxes(tick0=1, dtick=4, ticklabelposition="outside right",
                    ticktext=month_of_week[1::4],
                    tickvals=list(range(1, weeks_for_year(start_year), 4)))
    fig2.update_traces(showscale=False)
    fig2.show()
    
    scope = PlotlyScope(
        plotlyjs="https://cdn.plot.ly/plotly-latest.min.js",
    )
    with open("commit_overview.svg", "wb") as f:
        f.write(scope.transform(fig2, format="svg"))

    fig2.write_html("commit_overview.html")


def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 3, 1) - date(d.year, 3, 1))

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def weeks_for_year(year):
    last_week = date(year, 12, 28)
    return last_week.isocalendar()[1]