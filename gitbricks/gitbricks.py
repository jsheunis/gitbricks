from github import Github
import os
import plotly.graph_objects as go
import sys
import numpy as np
import calendar
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
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
    start_date, end_date, df_dates, week_count, months, weekdays, months_long, weekdays_long = calculate_dates(start_year, start_month, start_day)
    # Connect to repo via GitHub API
    repo = connect_brick_factory(repo_name)
    # Get all commits from start_date to end_date
    commits = fetch_bricks(repo, start_date, end_date)
    # Sum commits per date
    df_dates, total = sum_bricks(df_dates, commits)
    # Prepare data for plotting 
    comments, commit_counts, month_of_week = process_bricks(df_dates, week_count, months, weekdays_long) 
    # Figure parameters
    if colormap is None:
        colormap = defaults.COLORMAP["githubgreen"]
    if title is None:
        title = f'Commit overview for "{repo.full_name}" from {start_day} {months[start_month]} {start_year} to {start_day} {months[start_month]} {start_year+1} (total={total})'
    gapwidth = defaults.GAPWIDTH
    x_vals = list(range(week_count))
    y_vals = weekdays
    z_vals = commit_counts
    hovertext = comments
    x_tick_text = month_of_week[1::4]
    x_tick_vals = list(range(1, week_count, 4))
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


def sum_bricks(dates_frame, commits):
    """
    """
    # Add/rewrite commits column in data frame
    dates_frame['n_commits'] = [0]*len(dates_frame.index)
    # Sum commits per date in date range
    i=0
    for cmt in commits:
        i+=1
        dt = cmt.commit.author.date
        dt = datetime.combine(dt.date(), datetime.min.time())
        dates_frame.loc[dates_frame['date']==dt, 'n_commits'] += 1
    return dates_frame, i


def process_bricks(df, week_count, months, weekdays_long):
    """
    """
    first_day = df.iloc[0]['dayofweek']
    # Generate lists for:
    # commits = 7*week_count
    # hover_comments = 7*week_count
    commits = []
    comments = []
    for d, day in enumerate(weekdays_long):
        df_commits = df[df['dayname']==day]['n_commits']
        commits_list = df_commits.to_numpy().T.tolist()
        dates_list = list(df_commits.index)
        idx_count = len(commits_list)
        if idx_count < week_count:
            if d < first_day:
                commits_list = [0] + commits_list
                dates_list = [''] + dates_list
            if d > first_day:
                commits_list = commits_list + [0]
                dates_list = dates_list + ['']
        commits.append(commits_list)
        comments_list = [get_hover_string(cmt, dt) for cmt, dt in zip(commits_list, dates_list)]
        comments.append(comments_list)
    # month_of_week = 1*week_count
    df_months = df[df['dayname']=='Monday']['monthname']
    months_list = df_months.to_numpy().T.tolist()
    month_of_week = [m[:3] for m in months_list]
    return comments, commits, month_of_week

def get_hover_string(n_commits, dt):
    """
    """
    if n_commits == 0:
        n_txt = 'No commits on '
    elif n_commits == 1:
        n_txt = '1 commit on '
    else:
        n_txt = f'{n_commits} commits on '

    if dt == '':
        return ''
    else:
        return n_txt + dt.strftime('%b %d, %Y')

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
    # Get start and end date
    start_date = datetime(start_year, start_month, start_day)
    end_date = start_date + relativedelta(years=1) - relativedelta(days=1)
    # Get date range
    dtrange = pd.date_range(start=start_date, end=end_date)
    dtrange_s = dtrange.to_series()
    # Get days of week, day names, days of month, month names, add all to dataframe
    days_of_week = dtrange_s.dt.dayofweek
    days_of_month = dtrange_s.dt.day
    day_names = dtrange_s.dt.day_name()
    month_names = dtrange_s.dt.month_name()
    df_dates = pd.DataFrame({'date': dtrange_s, 'dayofweek': days_of_week, 'dayname': day_names, 'dayofmonth': days_of_month, 'monthname': month_names})
    # Get months and weekdays
    months = list(calendar.month_abbr)
    weekdays = list(calendar.day_abbr)
    months_long = list(calendar.month_name)
    weekdays_long = list(calendar.day_name)
    # Get week count
    week_count = 0
    for day in weekdays_long:
        fr = df_dates[df_dates['dayname']==day]
        temp_count = len(fr.index)
        if temp_count > week_count:
            week_count = temp_count

    return start_date, end_date, df_dates, week_count, months, weekdays, months_long, weekdays_long

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