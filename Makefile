# pyClamd
VERSION=`python setup.py --version`
ARCHIVE=`python setup.py --fullname`


test:
	py.test -v
	python pyclamd.py

install:
	@python setup.py install

archive: test doc
	@python setup.py sdist
	@echo Archive is create and named dist/$(ARCHIVE).tar.gz
	@echo -n md5sum is :
	@md5sum dist/$(ARCHIVE).tar.gz

web:
	@cp dist/$(ARCHIVE).tar.gz web/
	@m4 -DVERSION=$(VERSION) -DMD5SUM=$(shell md5sum dist/pyClamd-$(VERSION).tar.gz |cut -d' ' -f1) -DDATE=$(shell date +%Y-%m-%d) web/index.gtm.m4 > web/index.gtm

license:
	@python setup.py --license

register:
	@python setup.py register

doc:
	@pydoc -w pyclamd

.PHONY: web