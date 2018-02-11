#!/bin/bash
# allows you to send pull requests from the command line
# usage: git req username [comparetobranch]
#    or: git req username -m 'message'
# put somewhere in your PATH as git-req and make executable

usage()
{
cat << EOF
usage: $0 options

Sends a pull request via github

OPTIONS:
-h Show this message
-f Force a pull request
-b base branch
-t title
-d descriptio
EOF
}

FORCE=

while getopts h:f:b:t:d: OPTION
do
case "${OPTION}" in
        h) usage; exit;;
        f) FORCE=1;;
        b) GITBASE=${OPTARG};;
        t) GITTITLE=${OPTARG};;
        d) GITDESCRIPTION=${OPTARG};;
    esac
done
shift $(($OPTIND - 1))

GITBRANCH=$(git symbolic-ref HEAD | cut -d/ -f3-)
GITUNPUSHED=$(git log origin/$GITBRANCH..$GITBRANCH --pretty=oneline --abbrev-commit)
if [ "$GITUNPUSHED" != '' ]
then
    echo -ne 'Error: Push your changes!\n'
    exit $?
fi

GITUNCOMMITTED=$(git status | sed -n 4p) && GITUNCOMMITTED=${GITUNCOMMITTED:0:7}
if [ "$GITUNCOMMITTED" != 'nothing' ]
then
    echo -ne 'Error: Woah, woah, woah. There are uncommitted changes!\n'
    exit $?
fi

GITUSER=$(git config user.name)
GITPROJECT=$(grep 'url =' .git/config | sed -n 1p | sed -e 's/.*url = git@github.com:'$GITUSER'.*[/]\(.*\).git$/\1/')
PROJECTURL=${GITPROJECT##*/}
PROJECT=${PROJECTURL%.*}
GITTOKEN=$(git config github.token)
if [ $(echo "${#2}") != '0' ]
then
	if [ "$2" != '-m' ]
	then
		GITCOMPR="http://github.com/$GITUSER/$GITPROJECT/compare/$2...$GITBRANCH"
	else
		GITCOMPR=$3
	fi
else
	GITCOMPR=''
fi
generate_post_data()
{
  cat <<EOF
{
 "title": "$GITTITLE",
 "base": "$GITBASE",
 "head": "$GITBRANCH",
 "body": "$GITDESCRIPTION"
}
EOF
}
echo "2 Github password"
GITPULLREQ=$(curl -s -o /dev/null -w "%{http_code}"  --user "$GITUSER" --data "$(generate_post_data)" "https://api.github.com/repos/$GITUSER/$PROJECT/pulls")
if [ $GITPULLREQ != '201' ]
then
        echo -ne 'Could not complete pull request.\n'
else
        echo -ne 'Pull request sent to '$GITBASE'.\n'
fi
