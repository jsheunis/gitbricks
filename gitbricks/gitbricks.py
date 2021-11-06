from github import Github
import os
import plotly.graph_objects as go
import sys
import numpy as np
import calendar
from datetime import datetime, date, timedelta
import pandas as pd
from kaleido.scopes.plotly import PlotlyScope
from . import defaults

def gitbricks(repo_name, start_year,
              start_month=1, start_day=1, colormap=None,
              title=None, showfig=True, savefig=False):
    """
    GitHub-inspired calendar heatmap of the 1-year commit history of a git repository.
    """

    # Important dates
    start_date, end_date, dates_list, first_week, months, weekdays = calculate_dates(start_year, start_month, start_day)
    # Connect to repo via GitHub API
    repo = connect_brick_factory(repo_name)
    # Get all commits from start_date to end_date
    commits = fetch_bricks(repo, start_date, end_date)
    # Sum commits per date
    df, total = sum_bricks(dates_list, commits)
    # Prepare data for plotting 
    date_text_T, arrT_list, month_of_week = process_bricks(first_week, months, df) 
    # Figure parameters
    if colormap is None:
        colormap = defaults.COLORMAP["githubgreen"]
    if title is None:
        title = f'Commit overview for "{repo.full_name}" from {start_day} {months[start_month]} {start_year} to {start_day} {months[start_month]} {start_year+1} (total={total})'
    gapwidth = defaults.GAPWIDTH
    x_vals = list(range(weeks_for_year(start_year)))
    y_vals = weekdays
    z_vals = arrT_list
    hovertext = date_text_T
    x_tick_text = month_of_week[1::4]
    x_tick_vals = list(range(1, weeks_for_year(start_year), 4))
    fig = create_bricks_figure(
        x_vals, y_vals, z_vals, gapwidth, colormap,
        hovertext, x_tick_text, x_tick_vals, title)
    
    if showfig:
        fig.show()
    
    if savefig:
        # save svg and html to disk
        save_figure(fig, file_type="html")
        save_figure(fig, file_type="svg")
    
    return fig


def connect_brick_factory(repo_name):
    """
    """
    # Initialise and authenticate to GitHub API, access repository
    g = Github(os.environ["GITHUB_TOKEN"])
    return g.get_repo(repo_name)
    

def fetch_bricks(repo, start_date, end_date):
    """
    """
    return repo.get_commits(since=start_date, until=end_date)

def sum_bricks(dates_list, commits):
    """
    """
    # Dataframe to sum commits
    df = pd.DataFrame(dates_list, columns = ['date'] )
    df['n_commits'] = [0]*len(df.index)
    # Sum commits per date in date range
    i=0
    for cmt in commits:
        i+=1
        dt = cmt.commit.author.date
        dt = datetime.combine(dt.date(), datetime.min.time())
        df.loc[df['date']==dt, 'n_commits'] += 1
    return df, i


def process_bricks(first_week, months, df):
    """
    """
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
    # TODO: this is a temporary "fix" for 2018 issue where first element in week_list is
    # an empty list:
    # /Users/jsheunis/Documents/gitbricks/gitbricks/gitbricks.py:123: VisibleDeprecationWarning: Creating an ndarray from ragged nested sequences (which is a list-or-tuple of lists-or-tuples-or ndarrays with different lengths or shapes) is deprecated. If you meant to do this, you must specify 'dtype=object' when creating the ndarray.
    # Fix this correctly!!!!!
    if not week_list[0]:
        week_list[0] = [0, 0, 0, 0, 0, 0, 0]
    print(week_list)
    print(date_text_T)
    arr = np.array(week_list)
    arrT = arr.T
    arrT_list = arrT.tolist()

    return date_text_T, arrT_list, month_of_week

def create_bricks_figure(x_vals, y_vals, z_vals, gapwidth, colormap,
hovertext, x_tick_text, x_tick_vals, title, height=175, width=1000):
    """
    """
    layout = go.Layout(
        title=title,
        title_font_family='IBM Plex Mono,monospace',
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        autosize=False,
        height=height,
        width=width,
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
    heatmap = go.Heatmap(
        z=z_vals,
        x=x_vals,
        y=y_vals,
        hoverongaps = False,
        xgap = gapwidth,
        ygap = gapwidth,
        colorscale=colormap,
        hoverinfo='text',
        text=hovertext
    )
    fig = go.Figure(
        data=heatmap,
        layout=layout
    )
    fig.update_yaxes(autorange="reversed", tick0=1, dtick=2)
    fig.update_xaxes(tick0=1, dtick=4, ticklabelposition="outside right",
                    ticktext=x_tick_text,
                    tickvals=x_tick_vals)
    fig.update_traces(showscale=False)
    return fig

def calculate_dates(start_year, start_month, start_day):
    """
    """
    # Important dates
    start_date = datetime(start_year, start_month, start_day)
    end_date = add_years(start_date, 1)
    dates_list = daterange(start_date, end_date)
    all_weeks_start_month = calendar.monthcalendar(start_year, start_month)
    first_week = all_weeks_start_month[0]
    months = list(calendar.month_abbr)
    weekdays = list(calendar.day_abbr)
    return start_date, end_date, dates_list, first_week, months, weekdays

def save_figure(fig, file_name="commit_overview", file_type="svg"):
    """
    """

    if file_type=="svg":
        scope = PlotlyScope(
            plotlyjs="https://cdn.plot.ly/plotly-latest.min.js",
        )
        with open(file_name + '.svg', "wb") as f:
            f.write(scope.transform(fig, format="svg"))
    elif file_type=="html":
        fig.write_html(file_name + '.html')


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