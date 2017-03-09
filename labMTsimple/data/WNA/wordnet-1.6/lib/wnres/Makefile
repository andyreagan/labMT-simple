SHELL=/bin/sh

# Makefile for WordNet 1.6 "wnb" resources

WN_ROOT = /usr/local/wordnet1.6
WN_INSTALLDIR = $(WN_ROOT)/lib/wnres

WN_FILES = license.txt wn.xbm wngloss.man wnb.man

all: $(WN_FILES)

install: $(WN_FILES)
	@if [ ! -d $(WN_INSTALLDIR) ] ; then \
		echo "Making directory $(WN_INSTALLDIR)" ; \
		mkdir -p $(WN_INSTALLDIR) ; \
		chmod 755 $(WN_INSTALLDIR) ; \
	fi ; 
	@echo "Installing resource files in $(WN_INSTALLDIR)"
	@for file in $(WN_FILES) ; \
	 do \
		filename=$(WN_INSTALLDIR)/$$file ; \
		if [ -f $$filename ] ; then \
			echo "Cannot install $$filename: file exists" ; \
		else \
			echo "Installing $$filename" ; \
			cp -p $$file $$filename ; \
		fi ; \
	 done ;
	@echo "Done installing resource files in $(WN_INSTALLDIR)"

uninstall:
	@echo "Uninstalling resource files from $(WN_INSTALLDIR)"
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
	@echo "Done uninstalling resource files from $(WN_INSTALLDIR)"

clean:
	@rm -f *~ "#"*
