test:
	black --check -q ./ukparliament
	flake8 ./ukparliament
	mypy ./ukparliament
#	pytest ./ukparliament

upload:
	rm -Rf ./dist
	python3 ./setup.py bdist_wheel
	twine upload ./dist/*
