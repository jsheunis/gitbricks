import sys
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
import os
from .gitbricks import gitbricks
from . import app as dash_app

def main():
    """
    Entry point for the application script
    """

    asciiart="""
          _ _   _          _      _        
         (_) | | |        (_)    | |       
     __ _ _| |_| |__  _ __ _  ___| | _____ 
    / _` | | __| '_ \| '__| |/ __| |/ / __|
   | (_| | | |_| |_) | |  | | (__|   <\__ \\
    \__, |_|\__|_.__/|_|  |_|\___|_|\_\___/
    __/ |                                 
   |___/                                  
    
    GitHub-inspired calendar heatmap of the 1-year commit history of a git repository.
    Let's plot some colorful bricks!
    """

    try:  
        os.environ["GITHUB_TOKEN"]
    except KeyError: 
        print(
        """
        Your GitHub personal access token has not been saved as the environment variable 'GITHUB_TOKEN'.
        In order to gain access to GitHub's API, please first create a personal access token (see:
        https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
        and then save it as an environment variable via the command line as follows:

        >> export GITHUB_TOKEN="your-personal-access-token"
        """)
        sys.exit(1)

    argument_parser = ArgumentParser(
        description=asciiart,
        formatter_class=RawDescriptionHelpFormatter)

    subparsers = argument_parser.add_subparsers(
        dest='command',
        title='subcommands',
        description='',
        help='Open gitbricks as an interactive dashboard application'
    )
    dashboard = subparsers.add_parser('dashboard')
    plot = subparsers.add_parser('plot')
    # dashboard.set_defaults(func=app)
    plot.add_argument(
        "repo_name",
        type=str,
        help="""GitHub repository in the format <org-or-user-name/repository-name>, e.g. datalad/datalad""")
    plot.add_argument(
        "-y", "--start_year",
        type=int,
        help="""Start year of bricks, e.g. 2019""")
    plot.add_argument(
        "-m", "--start_month",
        type=int,
        default=1,
        help="""Start month of bricks (integer), where January=1 and December=12""")
    plot.add_argument(
        "-c", "--colormap",
        type=str,
        help="""Colormap used """)
    plot.add_argument(
        "-o", "--outputdir",
        type=str,
        help="""Directory to which outputs are written.
        Default is the current working directory.""")
    # plot.usage = ''

    


    arguments: Namespace = argument_parser.parse_args()
    print(arguments, file=sys.stderr)

    if arguments.command != 'dashboard':
        print('running plotter')
        # Set parameters
        script_path = os.path.realpath(__file__)
        sep = os.path.sep
        repo_path = sep.join(script_path.split(sep)[0:-2])
        package_path = sep.join(script_path.split(sep)[0:-1])
        # Call main function to generate bricks
        gitbricks(
            arguments.repo_name,
            arguments.start_year,
            arguments.start_month)
    else:
        print('running dashboard app')
        dash_app.app.run_server(debug=True)