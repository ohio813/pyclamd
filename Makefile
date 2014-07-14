# pyClamd
VERSION=`python setup.py --version`
ARCHIVE=`python setup.py --fullname`


testv2:
	py.test-2.7 -v
	python2 pyclamd/pyclamd.py
	python2 example.py

testv3:
	py.test-3.2 -v
	python3 pyclamd/pyclamd.py
	python3 example.py

test: testv2 testv3

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
	@python setup.py sdist upload
	@python setup.py bdist_egg upload
	@python3 setup.py bdist_egg upload

doc:
	@pydoc -w pyclamd/pyclamd.py

.PHONY: web archive