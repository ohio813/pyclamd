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
	@(cd /home/xael/ESPACE_KM/xael.org/web/xael.org/www.xael.org/html/norman/python ; make)
	@(cd /home/xael/ESPACE_KM/xael.org/web/xael.org/www.xael.org/html/norman/ ; make ftp-all)


license:
	@python setup.py --classifiers |grep ^License

register: archive
	@python setup.py register
	@python setup.py upload

doc:
	@pydoc -w pyclamd

.PHONY: web