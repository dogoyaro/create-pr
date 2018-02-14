# create-pr
Uses Python and bash scripts to help semi-automate PR creation using Andela Engineering conventions from terminal


## Features
- Create PR descriptions interactively, answering questions outlined in Andela Engineering conventions
- Automatically create PR on github using the `--create` option.
- Ended process during input? continue from where you stopped using the `--continue` opt

## Pre-requisites
- Have > python 2 installed
- bash or zsh shell
- Make sure `user.name` on your terminal is the same as your account username on Github
  
    check by making sure: 
    ``git config user.name == (Signed in as: when you click on your profile on the top right of Github.com)``

    change by running:
    ``git config --global user.name='Your username on Github'``
    
## Instructions
- Download files and add them to your project. (Note: project must be a git working directory)
- Add `mkpr.py`, `mkpr.bash`, `pull-request.txt`, `continue-pr.txt` to your .gitignore file
- Create PR Description only by running: `python mkpr.py`
- Continue from previously ended operation by running: `python mkpr.py --continue`
- Push directly to Github by running: `python mkpr.py --create`


### NOTE: The bash script is a modification of one found at: https://pastebin.com/raw/F9n3nPuu
