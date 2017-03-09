/*

   wnrtl.c - global variables used by WordNet Run Time Library

*/

#include <stdio.h>
#include "wnconsts.h"
#include "wntypes.h"

static char *Id = "$Id: wnrtl.c,v 1.1 1997/09/02 16:31:18 wn Exp $";

/* Search code variables and flags */

SearchResults wnresults;	/* structure containing results of search */

int fnflag = 0;			/* if set, print lex filename after sense */
int dflag = 1;			/* if set, print definitional glosses */
int saflag = 1;			/* if set, print SEE ALSO pointers */
int fileinfoflag = 0;		/* if set, print lex file info on synsets */
int frflag = 0;			/* if set, print verb frames */
int abortsearch = 0;		/* if set, stop search algorithm */
int offsetflag = 0;		/* if set, print byte offset of each synset */
int wnsnsflag = 0;		/* if set, print WN sense # for each word */

/* File pointers for database files */

int OpenDB = 0;			/* if non-zero, database file are open */
FILE *datafps[NUMPARTS + 1] = { NULL, NULL, NULL, NULL, NULL } , 
     *indexfps[NUMPARTS + 1] = { NULL, NULL, NULL, NULL, NULL } ,
     *sensefp = NULL, 
     *cousinfp = NULL, *cousinexcfp = NULL,
     *vsentfilefp = NULL, *vidxfilefp = NULL;

/* Method for interface to check for events while search is running */

void (*interface_doevents_func)(void) = NULL;
                        /* callback function for interruptable searches */
                        /* in single-threaded interfaces */

/* General error message handler - can be defined by interface.
   Default function provided in library returns -1 */

int default_display_message(char *);
int (*display_message)(char *) = default_display_message;

/*
   Revsion log: 

   $Log: wnrtl.c,v $
 * Revision 1.1  1997/09/02  16:31:18  wn
 * Initial revision
 *

*/
