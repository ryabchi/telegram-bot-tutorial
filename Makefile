CODE = likebot showroombot templatebot

.PHONY: format lint

pip:
	pip3 install -r requirements.txt

format:
	black --skip-string-normalization $(CODE)
	isort $(CODE)

lint:
	pylint --rcfile=setup.cfg $(CODE)
	mypy $(CODE)