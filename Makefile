# pyClamd
VERSION=`python setup.py --version`
ARCHIVE=`python setup.py --fullname`


test:
	py.test -v
	python pyclamd.py

install:
	@python setup.py install

archive:
	@python setup.py sdist
	@echo Archive is create and named dist/$(ARCHIVE).tar.gz
	@echo -n md5sum is :
	@md5sum dist/$(ARCHIVE).tar.gz

license:
	@python setup.py --license

register:
	@python setup.py register

doc:
	@pydoc -w pyclamd