test:
	black --check ./ukparliament
	flake8 ./ukparliament
#	pytest ./ukparliament

upload:
	rm -Rf ./dist
	python ./setup.py bdist_wheel
	twine upload ./dist/*
