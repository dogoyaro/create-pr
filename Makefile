# Make file for the create PR package

create:
	python mkpr.py

push:
	python mkpr.py --create

continue:
	python mkpr.py --continue
