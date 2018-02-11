from os import remove, system
import sys

questions = ['#### What does this PR do?',
             '#### Description of task to be completed?',
             '#### How should this be manually tested?',
             '#### Any background context you want to provide?',
             '#### Screenshots?',
             '#### Questions?',
             '#### What are the relevant pivotal tracker stories?']
answers = ['' for i in range(len(questions))]
options = [option for option in sys.argv]


def getInput(index):
    answer = ''
    while True:
        try:
            line = str(raw_input())
        except NameError:
            line = input()
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
        print('You were not on a previous operation, run `python mkpr.py` to start one')


def create_pr():
    print('==============================================')
    print('   ========================================   ')
    print('   ========================================   ')
    print('==============================================')
    if '--create' in options:
        try:
            print('create PR against what branch?')
            branch = raw_input()
        except NameError:
            branch = input()
        description_file = open('pull-request.txt')
        description = ''.join(description_file.readlines())
        description_file.close()
        try:
            print('Enter the title of the PR:')
            title = raw_input().encode('string-escape')
        except NameError:
            title = input().encode('string-escape')
        show_pr(title, branch, description)
        try:
            confirm = raw_input('This good? (yes/no): ')
        except NameError:
            confirm = input('This good? (yes/no): ')
        if (confirm[0].lower() == 'y'):
            print('1) Running bash script with admin privileges, if prompted enter computer password ')
            command_string = "sudo bash ./mkpr.bash -b \"{}\" -t \"{}\" -d '{}'"
            command = command_string.format(branch, title, description.encode('string-escape'))
            system(command)
        else:
            print('Start over `python mkpr.py` or go on github.com to make your pr directly')


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
        print('Thank you, find your PR description ready in pull-request.txt \n')
        create_pr()
        remove('pull-request.txt')
        remove('continue-pr.txt')
    except EOFError:
        continue_file = open('continue-pr.txt', mode='w')
        continue_file.write(str(index))
        continue_file.close()
        print('\n')
        print('You ended the operation, run `python mkpr.py` to start all over')
        print('You can also run `python mkpr.py --continue` to continue from where you stopped')
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


if '--continue' in options:
    continueFromUserEnd()
else:
    index = 0
    write_pr(index, 'w')
