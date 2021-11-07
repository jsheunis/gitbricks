# gitbricks

[UNDER CURRENT DEVELOPMENT]

Plot a bunch of colorful bricks! 

![alt text](assets/commit_overview.svg)

A command line tool and dashboard applicaton to create a calendar heatmap of the commit history of a GitHub repository.

Uses PyGitHub, Plotly and Dash.

## Installation

In a virtual environment:
```
git clone https://github.com/jsheunis/gitbricks.git
cd gitbricks
pip install .
# or for developers:
pip install . -e
```

## Usage

### 1. Create a GitHub personal access token and set as environment variable

This is necessary so as not to be rate-limited when using the GitHub API.

Create or find your personal access token [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

Set it as an environment variable `GITHUB_TOKEN`:

```
export GITHUB_TOKEN="your-personal-access-token"
```

### 2. Call `gitbricks plot` from the command line

Example:
```
gitbricks plot datalad/datalad -y 2019 -m 1
```
Arguments:
- `repo_name` (string, positional): GitHub repository in the format `org-or-user-name/repository-name`, e.g. `datalad/datalad` or `jsheunis/fMRwhy`
- `-y --start_year` (integer, optional): Start year of bricks, e.g. `2019`
- `-m --start_month` (integer, optional): Start month of bricks (integer), where January=1 and December=12

The call above saves two files in the working directory:

- `commit_overview.svg` (example above)
- `commit_overview.html` (interactive figure)

The latter is automatically opened in the browser after you run the command.

### 3. Dash application: `gitbricks dashboard`

Run the following from the command line:
```
gitbricks dashboard
```

This starts a Dash application, which is accessible at http://127.0.0.1:8050/
in your browser. Here you can enter the repo and year information and generate the
interactive heatmap *(more functionality = WIP)*.

To exit the application (and stop the webserver) press `CTRL+C` in 

## TODOS

- Add arguments (outputdir, colormap, styling options, custom dates, user commits, more hover functionality)
- Extend Dash app
- Deploy on Heroku
- (Implement OAuth / GitHub app authentication?)

## Contributing

Please feel free to create an issue or send a pull request!
