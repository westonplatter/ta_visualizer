CONDA_ENV ?= ta_visualizer

test:
	@pytest -s .

release:
	@python setup.py sdist
	@twine upload dist/*

env.create:
	@conda create -y -n ${CONDA_ENV} python=3.7

env.update:
	@conda env update -n ${CONDA_ENV} -f environment.yml
	@conda env update -n ${CONDA_ENV} -f ../ta_scanner/environment.yml

