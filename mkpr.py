#!/user/bin/env python3

from os import getcwd
import subprocess
import requests
import sys
import json


questions = ['#### What does this PR do?',
             '#### Description of task to be completed?',
             '#### How should this be manually tested?',
             '#### Any background context you want to provide?',
             '#### Screenshots?',
             '#### Questions?',
             '#### What are the relevant pivotal tracker stories?']

answers = ['' for i in range(len(questions))]
options = [option for option in sys.argv]

cwd = getcwd()


def openGitFile(path):
    return open('{}{}'.format(cwd, path))


def getNameOfBranch():
    try:
        reference_file = openGitFile('/.git/HEAD')
    except FileNotFoundError:
        print("==========Please make sure you're in a Git working directory")
        raise FileNotFoundError
    else:
        branch_ref = reference_file.readline()
        reference_file.close()
        branch_name = branch_ref.split('/')[-1]
        return branch_name


def isRemoteUpdated():
    branch_name = getNameOfBranch()
    try:
        head = openGitFile('/.git/refs/heads/{}'.format(branch_name[:-1]))
    except FileNotFoundError:
        print("============Please make sure you're in a Git working directory")
        raise FileNotFoundError
    else:
        branch_commit = head.readline()
        try:
            remote_head = openGitFile(
                            '/.git/refs/remotes/origin/{}'
                            .format(branch_name[:-1]))
            remote_commit = remote_head.readline()
        except (IOError, FileNotFoundError):
            return False
        if branch_commit == remote_commit:
            return True
        remote_head.close()
        head.close()
        return False


def isNothingToCommit():
    proc = subprocess.Popen(
            ["git status"],
            stdout=subprocess.PIPE,
            shell=True)
    (out, err) = proc.communicate()
    lines = out.decode("utf-8").split('\n')
    status = lines[1].split(' ')[0]
    if status == 'nothing':
        return True
    return False


def getContributorName():
    try:
        ref_file = openGitFile('/.git/logs/HEAD')
    except FileNotFoundError:
        print("============Please make sure you're in a Git working directory")
        raise FileNotFoundError
    else:
        logs = ref_file.readlines()
        commit = logs[-1]
        token = commit.split(' ')
        name = token[2]
        ref_file.close()
        return name


def getProjectUrl():
    config_file = openGitFile('/.git/config')
    for line in config_file.readlines():
        if 'url' in line:
            return line.split('=')[1].strip()[:-4]


def getInput(index):
    answer = ''
    while True:
        line = custom_input()
        if len(line) < 1:
            break
        answer += line + '\n'
    ''.join(answer)
    answers[index] = answer


def outputPRDescription(question, answers, index, file):
    if len(answers[index]):
        file.write(question + '\n')
        file.write('\n')
        file.write(answers[index])
        file.write('\n')


def continueFromUserEnd():
    try:
        continue_file = open('continue-pr.txt', mode='r+')
        question_index = int(continue_file.readline())
        write_pr(question_index, 'a')
    except IOError:
        print('You were not on a previous operation, run `python mkpr.py` \
                to start one')


def call_api(title, base_branch, description):
    if isRemoteUpdated():
        print('hollup, hollup.. you have not pushed your changes')
        return
    if isNothingToCommit():
        print('hollup, hollup.. you have changes that are not committed')
        return
    branch = getNameOfBranch().strip()
    contributor = getContributorName()
    project = getProjectUrl()
    password = getPassword()
    project = '/'.join(project.split('/')[-2:])
    data = {
            "title": title,
            "base": base_branch,
            "head": branch,
            "body": description,
            }
    data = json.dumps(data, ensure_ascii=False)
    headers = {
            "user": contributor,
            "password": password
            }
    request_url = 'https://api.github.com/repos/{}/pulls'.format(project)
    print(request_url)
    result = requests.post(request_url,
                           auth=(headers['user'],
                                 headers['password']), data=data)
    if result.status_code == 201:
        print('Welldone o, your PR is waiting for you on github')
        return
    else:
        print('Chai, something terrible has happened, still find your \
                description in pull-request.txt')
    return result


def create_pr():
    print('==============================================')
    print('   ========================================   ')
    print('   ========================================   ')
    print('==============================================')
    if '--create' in options:
        print('create PR against what branch?')
        branch = custom_input()
        description_file = open('pull-request.txt')
        description = ''.join(description_file.readlines())
        description_file.close()
        print('Enter the title of the PR:')
        title = custom_input().encode('string-escape')
        show_pr(title, branch, description)
        confirm = custom_input('This good? (yes/no): ')
        if (confirm[0].lower() == 'y'):
            call_api(title, branch, description)
        else:
            print('Start over `python mkpr.py` or go on github.com to make \
                    your pr directly')


def write_pr(index, mode):
    print('\n')
    print('Create your PR description from the terminal')
    print('Ctl-D for unix to end operation')
    print('Ctl-Z+Return for windows to end operation')
    print('Running mkpr.py --create will create a PR directly on Github')
    print('make sure to read the README.md to get it setup')
    print('\n')
    try:
        pr_file = open('pull-request.txt', mode=mode)
        for question in questions[index:]:
            print(' '.join(question.split(' ')[1:]))
            getInput(index)
            outputPRDescription(question, answers, index, pr_file)
            index += 1
        pr_file.close()
        print('Thank you, find your PR description ready in\
                pull-request.txt \n')
        create_pr()
    except EOFError:
        continue_file = open('continue-pr.txt', mode='w')
        continue_file.write(str(index))
        continue_file.close()
        print('\n')
        print('You ended the operation, run `python mkpr.py` to start\
                all over')
        print('You can also run `python mkpr.py --continue` to continue from \
                where you stopped')
    except OSError:
        pass


def show_pr(title, branch, description):
    print('\n')
    print('\n')
    print('==============================================')
    print('You are about to make a PR on Github!')
    print('Title: {}'.format(title))
    print('\n')
    print('Base Branch: {}'.format(branch))
    print('\n')
    print('Description \n')
    print(description)


def custom_input(description=''):
    try:
        value = raw_input(description)
    except NameError:
        value = input(description)
    return value


def getPassword():
    try:
        with open('.mkpr') as password_file:
            password = password_file.readline()
    except IOError:
        print('Please enter your github password to make pull request')
        password = custom_input()
        print('We can store the password so you don\'t do this every time?')
        confirm = custom_input("(yes/no): ")
        if (confirm[0].lower() == 'y'):
            with open('.mkpr', mode='w+') as password_file:
                password_file.write(password)
        return password
    else:
        return password


if '--continue' in options:
    continueFromUserEnd()
else:
    index = 0
    write_pr(index, 'w')
