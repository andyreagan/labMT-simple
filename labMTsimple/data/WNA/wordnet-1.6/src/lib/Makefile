SHELL=/bin/sh

# Makefile for WordNet 1.6 library

WN_ROOT = /usr/local/wordnet1.6
WN_INSTALLDIR = $(WN_ROOT)/lib

WN_FILES = libwn.a
SRC = binsrch.c morph.c search.c setutil.c wnglobal.c wnhelp.c wnrtl.c wnutil.c
OBJ = binsrch.o morph.o search.o setutil.o wnglobal.o wnhelp.o wnrtl.o wnutil.o

CC = gcc
LOCAL_CFLAGS = -O -DUNIX
CFLAGS = -I../include $(LOCAL_CFLAGS)

all: $(WN_FILES)

install: $(WN_FILES)
	@if [ ! -d $(WN_INSTALLDIR) ] ; then \
		echo "Making directory $(WN_INSTALLDIR)" ; \
		mkdir -p $(WN_INSTALLDIR) ; \
		chmod 755 $(WN_INSTALLDIR) ; \
	fi ; 
	@for file in $(WN_FILES) ; \
	 do \
		filename=$(WN_INSTALLDIR)/$$file ; \
		if [ -f $$filename ] ; then \
			echo "Cannot install $$filename: file exists" ; \
		else \
			echo "Installing $$filename" ; \
			cp -p $$file $$filename ; \
			chmod 444 $$filename ; \
		fi ; \
	 done ;
	@(cd wnres; $(MAKE) -k WN_INSTALLDIR='$(WN_INSTALLDIR)/wnres' install)
	@echo "Done installing WordNet library in $(WN_INSTALLDIR)"

uninstall:
	@for file in $(WN_FILES) ; \
	 do \
		filename=$(WN_INSTALLDIR)/$$file ; \
		if [ ! -f $$filename ] ; then \
			echo "Cannot uninstall $$filename: not present" ; \
		else \
			echo "Uninstalling $$filename" ; \
			rm -f $$filename ; \
		fi ; \
	 done ;
	@(cd wnres; $(MAKE) -k WN_INSTALLDIR='$(WN_INSTALLDIR)/wnres' install)
	@echo "Done uninstalling WordNet library from $(WN_INSTALLDIR)"

$(WN_FILES): $(OBJ)
	ar rcv $(WN_FILES) $(OBJ); ranlib $(WN_FILES)

clean:
	@rm -f $(WN_FILES) $(OBJ) core *~ "#"*

distclean: uninstall clean
