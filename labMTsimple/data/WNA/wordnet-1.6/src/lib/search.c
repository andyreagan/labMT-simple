/*
  
  search.c - WordNet library of search code
  
*/

#ifdef WINDOWS
#include <windows.h>
#include <windowsx.h>
#endif
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "wn.h"
#include "setutil.h"

static char *Id = "$Id: search.c,v 1.134 1997/11/07 16:27:36 wn Exp $";

/* For adjectives, indicates synset type */

#define DONT_KNOW	0
#define DIRECT_ANT	1	/* direct antonyms (cluster head) */
#define INDIRECT_ANT	2	/* indrect antonyms (similar) */
#define PERTAINYM	3	/* no antonyms or similars (pertainyms) */

#define ALLWORDS	0	/* print all words */
#define SKIP_ANTS	0	/* skip printing antonyms in printsynset() */
#define PRINT_ANTS	1	/* print antonyms in printsynset() */
#define SKIP_MARKER	0	/* skip printing adjective marker */
#define PRINT_MARKER	1	/* print adjective marker */

/* Trace types used by printspaces() to determine print sytle */

#define TRACEP		1	/* traceptrs */
#define TRACEC		2	/* tracecoords() */
#define TRACEI		3	/* traceinherit() */

#define DEFON 1
#define DEFOFF 0

/* Forward function declarations */

static void WNOverview(char *, int);
static void findsisters(IndexPtr), findtwins(IndexPtr), findcousins(IndexPtr),
            findverbgroups(IndexPtr);
static void add_relatives(int, IndexPtr, int, int);
static void free_rellist(void);
static int read_cousintops(void);
static void printsynset(char *, SynsetPtr, char *, int, int, int, int);
static void printantsynset(SynsetPtr, char *, int, int);
static char *printant(int, SynsetPtr, int, char *, char *);
static void printbuffer(char *);
static void printsns(SynsetPtr, int);
static void printsense(SynsetPtr, int);
static void catword(char *, SynsetPtr, int, int, int);
static void printspaces(int, int);
static void printrelatives(IndexPtr, int);
static int HasHoloMero(IndexPtr, int);
static int HasPtr(SynsetPtr, int);
static int getsearchsense(SynsetPtr, int);
static int depthcheck(int, SynsetPtr);
static int groupexc(unsigned long, unsigned long);
static void interface_doevents();

/* Static variables */

static int prflag, sense, prlexid;
static int overflag = 0;	/* set when output buffer overflows */
static char searchbuffer[SEARCHBUF];
static int lastholomero;	/* keep track of last holo/meronym printed */
#define TMPBUFSIZE 1024*8
static char tmpbuf[TMPBUFSIZE];	/* general purpose printing buffer */
static char wdbuf[WORDBUF];	/* general purpose word buffer */
static char msgbuf[256];	/* buffer for constructing error messages */
static int adj_marker;


/* Find word in index file and return parsed entry in data structure.
   Input word must be exact match of string in database. */

IndexPtr index_lookup(char *word, int dbase)
{
    char *ptrtok;
    IndexPtr idx = NULL;
    int j;
    FILE *fp;
    char *line;

    if ((fp = indexfps[dbase]) == NULL) {
	sprintf(msgbuf, "WordNet library error: %s indexfile not open\n",
		partnames[dbase]);
	display_message(msgbuf);
	return(NULL);
    }

    if ((line = bin_search(word, fp)) != NULL) {
        idx = (IndexPtr)malloc(sizeof(Index));
        assert(idx);
	
        idx->wd='\0';
        idx->pos='\0';
        idx->off_cnt=0;
	idx->tagged_cnt = 0;
        idx->sense_cnt=0;
        idx->offset='\0';
        idx->ptruse_cnt=0;
        idx->ptruse='\0';
	
	/* get the word */
	ptrtok=strtok(line," \n");
	
	idx->wd = malloc(strlen(ptrtok) + 1);
	assert(idx->wd);
	strcpy(idx->wd, ptrtok);
	
	/* get the part of speech */
	ptrtok=strtok(NULL," \n");
	idx->pos = malloc(strlen(ptrtok) + 1);
	assert(idx->pos);
	strcpy(idx->pos, ptrtok);
	
	/* get the collins count */
	ptrtok=strtok(NULL," \n");
	idx->sense_cnt = atoi(ptrtok);
	
	/* get the number of pointers types */
	ptrtok=strtok(NULL," \n");
	idx->ptruse_cnt = atoi(ptrtok);

	if (idx->ptruse_cnt) {
	    idx->ptruse = (int *) malloc(idx->ptruse_cnt * (sizeof(int)));
	    assert(idx->ptruse);
	
	    /* get the pointers types */
	    for(j=0;j < idx->ptruse_cnt; j++) {
		ptrtok=strtok(NULL," \n");
		idx->ptruse[j] = getptrtype(ptrtok);
	    }
	}
	
	/* get the number of offsets */
	ptrtok=strtok(NULL," \n");
	idx->off_cnt = atoi(ptrtok);

	if (!strcmp(wnrelease, "1.6")) {
	    /* get the number of senses that are tagged */
	    ptrtok=strtok(NULL," \n");
	    idx->tagged_cnt = atoi(ptrtok);
	} else {
	    idx->tagged_cnt = -1;
	}
	
	/* make space for the offsets */
	idx->offset = (long *) malloc(idx->off_cnt * (sizeof(long)));
	assert(idx->offset);
	
	/* get the offsets */
	for(j=0;j<idx->off_cnt;j++) {
	    ptrtok=strtok(NULL," \n");
	    idx->offset[j] = atol(ptrtok);
	}
    }
    return(idx);
}

/* 'smart' search of index file.  Find word in index file, trying different
   techniques - replace hyphens with underscores, replace underscores with
   hyphens, strip hyphens and underscores, strip periods. */

IndexPtr getindex(char *searchstr, int dbase)
{
    int i, j, k;
    char c;
    IndexPtr idx;
    char strings[MAX_FORMS][WORDBUF]; /* vector of search strings */
    static IndexPtr offsets[MAX_FORMS];
    static int offset;
    
    /* This works like strrok(): if passed with a non-null string,
       prepare vector of search strings and offsets.  If string
       is null, look at current list of offsets and return next
       one, or NULL if no more alternatives for this word. */

    if (searchstr != NULL) {

	offset = 0;
	strtolower(searchstr);
	for (i = 0; i < MAX_FORMS; i++) {
	    strcpy(strings[i], searchstr);
	    offsets[i] = 0;
	}

	strsubst(strings[1], '_', '-');
	strsubst(strings[2], '-', '_');

	/* remove all spaces and hyphens from last search string, then
	   all periods */
	for (i = j = k = 0; (c = searchstr[i]) != '\0'; i++) {
	    if (c != '_' && c != '-')
		strings[3][j++] = c;
	    if (c != '.')
		strings[4][k++] = c;
	}
	strings[3][j] = '\0';
	strings[4][k] = '\0';

	/* Get offset of first entry.  Then eliminate duplicates
	   and get offsets of unique strings. */

	offsets[0] = index_lookup(strings[0], dbase);

	for (i = 1; i < MAX_FORMS; i++)
	    if (strcmp(strings[0], strings[i]))
		offsets[i] = index_lookup(strings[i], dbase);
    }


    for (i = offset; i < MAX_FORMS; i++)
	if (offsets[i]) {
	    offset = i + 1;
	    return(offsets[i]);
	}

    return(NULL);
}

/* Read synset from data file at byte offset passed and return parsed
   entry in data structure. */

SynsetPtr read_synset(int dbase, long boffset, char *word)
{
    FILE *fp;

    if((fp = datafps[dbase]) == NULL) {
	sprintf(msgbuf, "WordNet library error: %s datafile not open\n",
		partnames[dbase]);
	display_message(msgbuf);
	return(NULL);
    }
    
    fseek(fp, boffset, 0);	/* position file to byte offset requested */

    return(parse_synset(fp, dbase, word)); /* parse synset and return */
}

/* Read synset at current byte offset in file and return parsed entry
   in data structure. */

SynsetPtr parse_synset(FILE *fp, int dbase, char *word)
{
    static char line[LINEBUF];
    char tbuf[SMLINEBUF];
    char *ptrtok;
    char *tmpptr;
    int foundpert = 0;
    char wdnum[3];
    int i;
    SynsetPtr synptr;
    long loc;			/* sanity check on file location */

    loc = ftell(fp);

    if ((tmpptr = fgets(line, LINEBUF, fp)) == NULL)
	return(NULL);
    
    synptr = (SynsetPtr)malloc(sizeof(Synset));
    assert(synptr);
    
    synptr->hereiam = 0;
    synptr->sstype = DONT_KNOW;
    synptr->fnum = 0;
    synptr->pos = '\0';
    synptr->wcount = 0;
    synptr->words = '\0';
    synptr->whichword = 0;
    synptr->ptrcount = 0;
    synptr->ptrtyp = '\0';
    synptr->ptroff = '\0';
    synptr->ppos = '\0';
    synptr->pto = '\0';
    synptr->pfrm = '\0';
    synptr->fcount = 0;
    synptr->frmid = '\0';
    synptr->frmto = '\0';
    synptr->defn = '\0';
    synptr->nextss = NULL;
    synptr->nextform = NULL;
    synptr->searchtype = -1;
    synptr->ptrlist = NULL;
    synptr->headword = NULL;
    synptr->headsense = 0;

    ptrtok = line;
    
    /* looking at offset */
    ptrtok = strtok(line," \n");
    synptr->hereiam = atol(ptrtok);

    /* sanity check - make sure starting file offset matches first field */
    if (synptr->hereiam != loc) {
	sprintf(msgbuf, "WordNet library error: no synset at location %d\n",
		loc);
	display_message(msgbuf);
	return(NULL);
    }
    
    /* looking at FNUM */
    ptrtok = strtok(NULL," \n");
    synptr->fnum = atoi(ptrtok);
    
    /* looking at POS */
    ptrtok = strtok(NULL, " \n");
    synptr->pos = malloc(strlen(ptrtok) + 1);
    assert(synptr->pos);
    strcpy(synptr->pos, ptrtok);
    if (getsstype(synptr->pos) == SATELLITE)
	synptr->sstype = INDIRECT_ANT;
    
    /* looking at numwords */
    ptrtok = strtok(NULL, " \n");
    synptr->wcount = strtol(ptrtok, NULL, 16);
    
    synptr->words = (char **)malloc(synptr->wcount  * sizeof(char *));
    assert(synptr->words);
    synptr->wnsns = (int *)malloc(synptr->wcount * sizeof(int));
    assert(synptr->wnsns);
    synptr->lexid = (int *)malloc(synptr->wcount * sizeof(int));
    assert(synptr->lexid);
    
    for (i = 0; i < synptr->wcount; i++) {
	ptrtok = strtok(NULL, " \n");
	synptr->words[i] = malloc(strlen(ptrtok) + 1);
	assert(synptr->words[i]);
	strcpy(synptr->words[i], ptrtok);
	
	/* is this the word we're looking for? */
	
	if (word && !strcmp(word,strtolower(ptrtok)))
	    synptr->whichword = i+1;
	
	ptrtok = strtok(NULL, " \n");
	sscanf(ptrtok, "%x", &synptr->lexid[i]);
    }
    
    /* get the pointer count */
    ptrtok = strtok(NULL," \n");
    synptr->ptrcount = atoi(ptrtok);

    if (synptr->ptrcount) {

	/* alloc storage for the pointers */
	synptr->ptrtyp = (int *)malloc(synptr->ptrcount * sizeof(int));
	assert(synptr->ptrtyp);
	synptr->ptroff = (long *)malloc(synptr->ptrcount * sizeof(long));
	assert(synptr->ptroff);
	synptr->ppos = (int *)malloc(synptr->ptrcount * sizeof(int));
	assert(synptr->ppos);
	synptr->pto = (int *)malloc(synptr->ptrcount * sizeof(int));
	assert(synptr->pto);
	synptr->pfrm = (int *)malloc(synptr->ptrcount * sizeof(int));
	assert(synptr->pfrm);
    
	for(i = 0; i < synptr->ptrcount; i++) {
	    /* get the pointer type */
	    ptrtok = strtok(NULL," \n");
	    synptr->ptrtyp[i] = getptrtype(ptrtok);
	    /* For adjectives, set the synset type if it has a direct
	       antonym */
	    if (dbase == ADJ &&	synptr->sstype == DONT_KNOW) {
		if (synptr->ptrtyp[i] == ANTPTR)
		    synptr->sstype = DIRECT_ANT;
		else if (synptr->ptrtyp[i] == PERTPTR)
		    foundpert = 1;
	    }

	    /* get the pointer offset */
	    ptrtok = strtok(NULL," \n");
	    synptr->ptroff[i] = atol(ptrtok);
	
	    /* get the pointer part of speech */
	    ptrtok = strtok(NULL, " \n");
	    synptr->ppos[i] = getpos(ptrtok);
	
	    /* get the lexp to/from restrictions */
	    ptrtok = strtok(NULL," \n");
	
	    tmpptr = ptrtok;
	    strncpy(wdnum, tmpptr, 2);
	    wdnum[2] = '\0';
	    synptr->pfrm[i] = strtol(wdnum, (char **)NULL, 16);
	
	    tmpptr += 2;
	    strncpy(wdnum, tmpptr, 2);
	    wdnum[2] = '\0';
	    synptr->pto[i] = strtol(wdnum, (char **)NULL, 16);
	}
    }

    /* If synset type is still not set, see if it's a pertainym */

    if (dbase == ADJ && synptr->sstype == DONT_KNOW && foundpert == 1)
	synptr->sstype = PERTAINYM;

    /* retireve optional information from verb synset */
    if(dbase == VERB) {
	ptrtok = strtok(NULL," \n");
	synptr->fcount = atoi(ptrtok);
	
	/* allocate frame storage */
	
	synptr->frmid = (int *)malloc(synptr->fcount * sizeof(int));  
	assert(synptr->frmid);
	synptr->frmto = (int *)malloc(synptr->fcount * sizeof(int));  
	assert(synptr->frmto);
	
	for(i=0;i<synptr->fcount;i++) {
	    /* skip the frame pointer (+) */
	    ptrtok = strtok(NULL," \n");
	    
	    ptrtok = strtok(NULL," \n");
	    synptr->frmid[i] = atoi(ptrtok);
	    
	    ptrtok = strtok(NULL," \n");
	    synptr->frmto[i] = atoi(ptrtok);
	}
    }
    
    /* get the optional definition */
    
    ptrtok = strtok(NULL," \n");
    if (ptrtok) {
	ptrtok = strtok(NULL," \n");
	sprintf(tbuf, "");
	while (ptrtok != NULL) {
	    strcat(tbuf,ptrtok);
	    ptrtok = strtok(NULL, " \n");
	    if(ptrtok)
		strcat(tbuf," ");
	}
	assert((1 + strlen(tbuf)) < sizeof(tbuf));
	synptr->defn = malloc(strlen(tbuf) + 4);
	assert(synptr->defn);
	sprintf(synptr->defn,"(%s)",tbuf);
    }

    return(synptr);
}

/* Free a synset linked list allocated by findtheinfo_ds() */

void free_syns(SynsetPtr synptr)
{
    SynsetPtr cursyn, nextsyn;

    if (synptr) {
	cursyn = synptr;
	nextsyn = synptr->nextss;
	while(cursyn) {
	    nextsyn = cursyn->nextss;
	    free_synset(cursyn);
	    cursyn = nextsyn;
	} 
    }
}

/* Free a synset */

void free_synset(SynsetPtr synptr)
{
    int i;
    
    free(synptr->pos);
    for (i = 0; i < synptr->wcount; i++){
	free(synptr->words[i]);
    }
    free(synptr->words);
    free(synptr->wnsns);
    free(synptr->lexid);
    if (synptr->ptrcount) {
	free(synptr->ptrtyp);
	free(synptr->ptroff);
	free(synptr->ppos);
	free(synptr->pto);
	free(synptr->pfrm);
    }
    if (synptr->fcount) {
	free(synptr->frmid);
	free(synptr->frmto);
    }
    if (synptr->defn)
	free(synptr->defn);
    if (synptr->headword)
	free(synptr->headword);
    if (synptr->ptrlist)
	free_syns(synptr->ptrlist); /* changed from free_synset() */
    free(synptr);
}

/* Free an index structure */

void free_index(IndexPtr idx)
{
    free(idx->wd);
    free(idx->pos);
    if (idx->ptruse)
	free(idx->ptruse);
    free(idx->offset);
    free(idx);
}

/* Recursive search algorithm to trace a pointer tree */

static void traceptrs(SynsetPtr synptr, int ptrtyp, int dbase, int depth)
{
    int i;
    int extraindent = 0;
    SynsetPtr cursyn;
    char prefix[40], tbuf[20];

    interface_doevents();
    if (abortsearch)
	return;

    if (ptrtyp < 0) {
	ptrtyp = -ptrtyp;
	extraindent = 2;
    }
    
    for (i = 0; i < synptr->ptrcount; i++) {
	if((synptr->ptrtyp[i] == ptrtyp) &&
	   ((synptr->pfrm[i] == 0) ||
	    (synptr->pfrm[i] == synptr->whichword))) {

	    if(!prflag) {	/* print sense number and synset */
		printsns(synptr, sense + 1);
		prflag = 1;
	    }
	    printspaces(TRACEP, depth + extraindent);

	    switch(ptrtyp) {
	    case PERTPTR:
		if (dbase == ADV) 
		    sprintf(prefix, "Derived from %s ",
			    partnames[synptr->ppos[i]]);
		else
		    sprintf(prefix, "Pertains to %s ",
			    partnames[synptr->ppos[i]]);
		break;
	    case PPLPTR:
		sprintf(prefix, "Participle of verb ");
		break;
	    case HASMEMBERPTR:
		sprintf(prefix, "   HAS MEMBER: ");
		break;
	    case HASSTUFFPTR:
		sprintf(prefix, "   HAS SUBSTANCE: ");
		break;
	    case HASPARTPTR:
		sprintf(prefix, "   HAS PART: ");
		break;
	    case ISMEMBERPTR:
		sprintf(prefix, "   MEMBER OF: ");
		break;
	    case ISSTUFFPTR:
		sprintf(prefix, "   SUBSTANCE OF: ");
		break;
	    case ISPARTPTR:
		sprintf(prefix, "   PART OF: ");
		break;
	    default:
		sprintf(prefix, "=> ");
		break;
	    }

	    /* Read synset pointed to */
	    cursyn=read_synset(synptr->ppos[i], synptr->ptroff[i], "");

	    /* For Pertainyms and Participles pointing to a specific
	       sense, indicate the sense then retrieve the synset
	       pointed to and other info as determined by type.
	       Otherwise, just print the synset pointed to. */

	    if ((ptrtyp == PERTPTR || ptrtyp == PPLPTR) &&
		synptr->pto[i] != 0) {
		sprintf(tbuf, " (Sense %d)\n",
			getsearchsense(cursyn, synptr->pto[i]));
		printsynset(prefix, cursyn, tbuf, DEFOFF, synptr->pto[i],
			    SKIP_ANTS, PRINT_MARKER);
		if (ptrtyp == PPLPTR) { /* adjective pointing to verb */
		    printsynset("      =>", cursyn, "\n",
				DEFON, ALLWORDS, PRINT_ANTS, PRINT_MARKER);
		    traceptrs(cursyn, HYPERPTR, getpos(cursyn->pos), 0);
		} else if (dbase == ADV) { /* adverb pointing to adjective */
		    printsynset("      =>", cursyn, "\n",DEFON, ALLWORDS, 
				((getsstype(cursyn->pos) == SATELLITE)
				 ? SKIP_ANTS : PRINT_ANTS), PRINT_MARKER);
#ifdef FOOP
 		    traceptrs(cursyn, HYPERPTR, getpos(cursyn->pos), 0);
#endif
		} else {	/* adjective pointing to noun */
		    printsynset("      =>", cursyn, "\n",
				DEFON, ALLWORDS, PRINT_ANTS, PRINT_MARKER);
		    traceptrs(cursyn, HYPERPTR, getpos(cursyn->pos), 0);
		}
	    } else 
		printsynset(prefix, cursyn, "\n", DEFON, ALLWORDS,
			    PRINT_ANTS, PRINT_MARKER);

	    /* For HOLONYMS and MERONYMS, keep track of last one
	       printed in buffer so results can be truncated later. */

	    if (ptrtyp >= ISMEMBERPTR && ptrtyp <= HASPARTPTR)
		lastholomero = strlen(searchbuffer);

	    if(depth) {
		depth = depthcheck(depth, cursyn);
		traceptrs(cursyn, ptrtyp, getpos(cursyn->pos), (depth+1));

		free_synset(cursyn);
	    } else
		free_synset(cursyn);
	}
    }
}

static void tracecoords(SynsetPtr synptr, int ptrtyp, int dbase, int depth)
{
    int i;
    SynsetPtr cursyn;

    interface_doevents();
    if (abortsearch)
	return;

    for(i = 0; i < synptr->ptrcount; i++) {
	if((synptr->ptrtyp[i] == HYPERPTR) &&
	   ((synptr->pfrm[i] == 0) ||
	    (synptr->pfrm[i] == synptr->whichword))) {
	    
	    if(!prflag) {
		printsns(synptr, sense + 1);
		prflag = 1;
	    }
	    printspaces(TRACEC, depth);

	    cursyn = read_synset(synptr->ppos[i], synptr->ptroff[i], "");

	    printsynset("-> ", cursyn, "\n", DEFON, ALLWORDS,
			SKIP_ANTS, PRINT_MARKER);

	    traceptrs(cursyn, ptrtyp, getpos(cursyn->pos), depth);
	    
	    if(depth) {
		depth = depthcheck(depth, cursyn);
		tracecoords(cursyn, ptrtyp, getpos(cursyn->pos), (depth+1));
		free_synset(cursyn);
	    } else
		free_synset(cursyn);
	}
    }
}

/* Trace through the hypernym tree and print all MEMBER, STUFF
   and PART info. */

static void traceinherit(SynsetPtr synptr, int ptrbase, int dbase, int depth)
{
    int i;
    SynsetPtr cursyn;

    interface_doevents();
    if (abortsearch)
	return;
    
    for(i=0;i<synptr->ptrcount;i++) {
	if((synptr->ptrtyp[i] == HYPERPTR) &&
	   ((synptr->pfrm[i] == 0) ||
	    (synptr->pfrm[i] == synptr->whichword))) {
	    
	    if(!prflag) {
		printsns(synptr, sense + 1);
		prflag = 1;
	    }
	    printspaces(TRACEI, depth);
	    
	    cursyn = read_synset(synptr->ppos[i], synptr->ptroff[i], "");

	    printsynset("=> ", cursyn, "\n", DEFON, ALLWORDS,
			SKIP_ANTS, PRINT_MARKER);
	    
	    traceptrs(cursyn, ptrbase, NOUN, depth);
	    traceptrs(cursyn, ptrbase + 1, NOUN, depth);
	    traceptrs(cursyn, ptrbase + 2, NOUN, depth);
	    
	    if(depth) {
		depth = depthcheck(depth, cursyn);
		traceinherit(cursyn, ptrbase, getpos(cursyn->pos), (depth+1));
		free_synset(cursyn);
	    } else
		free_synset(cursyn);
	}
    }

    /* Truncate search buffer after last holo/meronym printed */
    searchbuffer[lastholomero] = '\0';
}

static void partsall(SynsetPtr synptr, int ptrtyp)
{
    int ptrbase;
    int i, hasptr = 0;
    
    ptrbase = (ptrtyp == HMERONYM) ? HASMEMBERPTR : ISMEMBERPTR;
    
    /* First, print out the MEMBER, STUFF, PART info for this synset */

    for (i = 0; i < 3; i++) {
	if (HasPtr(synptr, ptrbase + i)) {
	    traceptrs(synptr, ptrbase + i, NOUN, 1);
	    hasptr++;
	}
	interface_doevents();
	if (abortsearch)
	    return;
    }

    /* Print out MEMBER, STUFF, PART info for hypernyms on
       HMERONYM search only */
	
    if (hasptr && ptrtyp == HMERONYM) {
	lastholomero = strlen(searchbuffer);
	traceinherit(synptr, ptrbase, NOUN, 1);
    }
}

static void traceadjant(SynsetPtr synptr)
{
    SynsetPtr newsynptr;
    int i, j;
    int anttype = DIRECT_ANT;
    SynsetPtr simptr, antptr;
    static char similar[] = "        => ";

    /* This search is only applicable for ADJ synsets which have
       either direct or indirect antonyms (not valid for pertainyms). */
    
    if (synptr->sstype == DIRECT_ANT || synptr->sstype == INDIRECT_ANT) {
	printsns(synptr, sense + 1);
	printbuffer("\n");
	
	/* if indirect, get cluster head */
	
	if(synptr->sstype == INDIRECT_ANT) {
	    anttype = INDIRECT_ANT;
	    i = 0;
	    while (synptr->ptrtyp[i] != SIMPTR) i++;
	    newsynptr = read_synset(ADJ, synptr->ptroff[i], "");
	} else
	    newsynptr = synptr;
	
	/* find antonyms - if direct, make sure that the antonym
	   ptr we're looking at is from this word */
	
	for (i = 0; i < newsynptr->ptrcount; i++) {

	    if (newsynptr->ptrtyp[i] == ANTPTR &&
		((anttype == DIRECT_ANT &&
		  newsynptr->pfrm[i] == newsynptr->whichword) ||
		 (anttype == INDIRECT_ANT))) {
		
		/* read the antonym's synset and print it.  if a
		   direct antonym, print it's satellites. */
		
		antptr = read_synset(ADJ, newsynptr->ptroff[i], "");
    
		if (anttype == DIRECT_ANT) {
		    printsynset("", antptr, "\n", DEFON, ALLWORDS,
				PRINT_ANTS, PRINT_MARKER);
		    for(j = 0; j < antptr->ptrcount; j++) {
			if(antptr->ptrtyp[j] == SIMPTR) {
			    simptr = read_synset(ADJ, antptr->ptroff[j], "");
			    printsynset(similar, simptr, "\n", DEFON,
					ALLWORDS, SKIP_ANTS, PRINT_MARKER);
			    free_synset(simptr);
			}
		    }
		} else
		    printantsynset(antptr, "\n", anttype, DEFON);

		free_synset(antptr);
	    }
	}
	if (newsynptr != synptr)
	    free_synset(newsynptr);
    }
}


/* fetch the given example sentence from the example file and print it out */
void getexample(char *offset, char *wd)
{
    char *line;
    char sentbuf[512];
    
    if (vsentfilefp != NULL) {
	if (line = bin_search(offset, vsentfilefp)) {
	    while(*line != ' ') 
		line++;

	    printbuffer("          EX: ");
	    sprintf(sentbuf, line, wd);
	    printbuffer(sentbuf);
	}
    }
}

/* find the example sentence references in the example sentence index file */
int findExample(SynsetPtr synptr)
{
    char tbuf[256], *temp, *offset;
    int wdnum;
    int found = 0;
    
    if (vidxfilefp != NULL) {
	wdnum = synptr->whichword - 1;

	sprintf(tbuf,"%s%%%-1.1d:%-2.2d:%-2.2d::",
		synptr->words[wdnum],
		getpos(synptr->pos),
		synptr->fnum,
		synptr->lexid[wdnum]);

	if ((temp = bin_search(tbuf, vidxfilefp)) != NULL) {

	    /* skip over sense key and get sentence numbers */

	    temp += strlen(synptr->words[wdnum]) + 11;
	    strcpy(tbuf, temp);

	    offset = strtok(tbuf, " ,\n");

	    while (offset) {
		getexample(offset, synptr->words[wdnum]);
		offset = strtok(NULL, ",\n");
	    }
	    found = 1;
	}
    }
    return(found);
}

static void printframe(SynsetPtr synptr, int prsynset)
{
    int i;

    if (prsynset)
	printsns(synptr, sense + 1);
    
    if (!findExample(synptr)) {
	for(i = 0; i < synptr->fcount; i++) {
	    if ((synptr->frmto[i] == synptr->whichword) ||
		(synptr->frmto[i] == 0)) {
		if (synptr->frmto[i] == synptr->whichword)
		    printbuffer("          => ");
		else
		    printbuffer("          *> ");
		printbuffer(frametext[synptr->frmid[i]]);
		printbuffer("\n");
	    }
	}
    }
}

static void printseealso(SynsetPtr synptr)
{
    SynsetPtr cursyn;
    int i, first = 1;
    int svwnsnsflag;
    static char firstline[] = "          Also See-> ";
    static char otherlines[] = "; ";
    char *prefix = firstline;

    /* Find all SEEALSO pointers from the searchword and print the
       word or synset pointed to. */

    for(i = 0; i < synptr->ptrcount; i++) {
	if ((synptr->ptrtyp[i] == SEEALSOPTR) &&
	    ((synptr->pfrm[i] == 0) ||
	     (synptr->pfrm[i] == synptr->whichword))) {

	    cursyn = read_synset(synptr->ppos[i], synptr->ptroff[i], "");

	    svwnsnsflag = wnsnsflag;
	    wnsnsflag = 1;
	    printsynset(prefix, cursyn, "", DEFOFF,
			synptr->pto[i] == 0 ? ALLWORDS : synptr->pto[i],
			SKIP_ANTS, SKIP_MARKER);
	    wnsnsflag = svwnsnsflag;

	    free_synset(cursyn);

	    if (first) {
		prefix = otherlines;
		first = 0;
	    }
	}
    }
    if (!first)
	printbuffer("\n");
}

static void freq_word(IndexPtr index)
{
    int familiar=0;
    int cnt;
    static char *a_an[] = {
	"", "a noun", "a verb", "an adjective", "an adverb" };
    static char *freqcats[] = {
	"extremely rare","very rare","rare","uncommon","common",
	"familiar","very familiar","extremely familiar"
    };

    if(index) {
	cnt = index->sense_cnt;
	if (cnt == 0) familiar = 0;
	if (cnt == 1) familiar = 1;
	if (cnt == 2) familiar = 2;
	if (cnt >= 3 && cnt <= 4) familiar = 3;
	if (cnt >= 5 && cnt <= 8) familiar = 4;
	if (cnt >= 9 && cnt <= 16) familiar = 5;
	if (cnt >= 17 && cnt <= 32) familiar = 6;
	if (cnt > 32 ) familiar = 7;
	
	sprintf(tmpbuf,
		"%s used as %s is %s (polysemy count = %d)\n",
		index->wd, a_an[getpos(index->pos)], freqcats[familiar], cnt);
	printbuffer(tmpbuf);
    }
}

void wngrep (char *word_passed, int pos) {
   FILE *inputfile;
   char word[256];
   int wordlen, linelen, loc;
   char line[1024];
   int count = 0;

   inputfile = indexfps[pos];
   if (inputfile == NULL) {
      sprintf (msgbuf, "WordNet library error: Can't perform compounds "
         "search because %s index file is not open\n", partnames[pos]);
      display_message (msgbuf);
      return;
   }
   rewind(inputfile);

   strcpy (word, word_passed);
   strsubst (word, ' ', '_');	/* replace spaces with underscores */
   wordlen = strlen (word);

   while (fgets (line, 1024, inputfile) != NULL) {
      for (linelen = 0; line[linelen] != ' '; linelen++) {}
      if (linelen < wordlen)
	  continue;
      line[linelen] = '\0';
      strstr_init (line, word);
      while ((loc = strstr_getnext ()) != -1) {
         if (
            /* at the start of the line */
            (loc == 0) ||
            /* at the end of the line */
            ((linelen - wordlen) == loc) ||
            /* as a word in the middle of the line */
            (((line[loc - 1] == '-') || (line[loc - 1] == '_')) &&
            ((line[loc + wordlen] == '-') || (line[loc + wordlen] == '_')))
         ) {
            strsubst (line, '_', ' ');
            sprintf (tmpbuf, "%s\n", line);
            printbuffer (tmpbuf);
            break;
         }
      }
      if (count++ % 2000 == 0) {
         interface_doevents ();
         if (abortsearch) break;
      }
   }
}

/* Stucture to keep track of 'relative groups'.  All senses in a relative
   group are displayed together at end of search.  Transitivity is
   supported, so if either of a new set of related senses is already
   in a 'relative group', the other sense is added to that group as well. */

struct relgrp {
    int senses[MAXSENSE];
    struct relgrp *next;
};
static struct relgrp *rellist;

static struct relgrp *mkrellist(void);

void trace_hyperptrs(SynsetPtr, void (*)(unsigned long, void *), void *, int);

#define HASHTABSIZE	1223	/* Prime number. Must be > 2*MAXTOPS */
#define MAXTOPS 	300	/* Maximum number of lines in cousin.tops */

static struct {
    int topnum;			/* Unique id assigned to this top node */
    Set_t rels;			/* set of top nodes this one is paired with */
    unsigned long offset;	/* Offset read from cousin.tops file */
} cousintops[HASHTABSIZE];

/* Simple hash function */
#define hash(n) ((n) % HASHTABSIZE)

/* Find relative groups for all senses of target word in given part
   of speech. */

static void relatives(IndexPtr idx, int dbase)
{
    rellist = NULL;

    switch(dbase) {
    case NOUN:
	findsisters(idx);
	interface_doevents();
	if (abortsearch)
	    break;
	findtwins(idx);
	interface_doevents();
	if (abortsearch)
	    break;
	findcousins(idx);
	interface_doevents();
	if (abortsearch)
	    break;
	printrelatives(idx, NOUN);
	break;
    case VERB:
	findverbgroups(idx);
	interface_doevents();
	if (abortsearch)
	    break;
	printrelatives(idx, VERB);
	break;
    default:
	break;
    }

    free_rellist();
}

/* Look for 'twins' - synsets with 3 or more words in common. */

static int word_idx(char *wd, char *wdtable[], int nwords)
{
     for ( ; --nwords >= 0 && strcmp(wd, wdtable[nwords]); )
	  ;
     return nwords;
}

static int add_word(char *wd, char *wdtable[], int nwords)
{
     wdtable[nwords] = (char *)strdup(wd);
     return nwords;
}

#define MAXWRDS 300

static void findtwins(IndexPtr idx)
{
     char *words[MAXWRDS];
     Set_t s[MAXSENSE], n;
     SynsetPtr synset;
     int i, j, nwords;

     assert(idx);
     nwords = 0;
     for (i = 0; i < idx->off_cnt; i++) {

	  synset = read_synset(NOUN, idx->offset[i], "");

	  s[i] = set_create(MAXWRDS);
	  if (synset->wcount >=  3)
	       for (j = 0; j < synset->wcount; j++) {
		    char buf[256];
		    int k;
		    strtolower(strcpy(buf, synset->words[j]));
		    k = word_idx(buf, words, nwords);
		    if (k < 0) {
			 k = add_word(buf, words, nwords);
			 assert(nwords < MAXWRDS);
			 nwords++;
		    }
		    set_addobj(s[i], k);
	       }
	  
	  free_synset(synset);
     }
     
     n = set_create(MAXWRDS);
     for (i = 0; i < idx->off_cnt; i++)
	  for (j = i + 1; j < idx->off_cnt; j++)
	       if (set_intersection(n, s[i], s[j]),
		   set_nelem(n) >= 3)
		    add_relatives(NOUN, idx, j, i);
     
     set_destroy(n);
     for (i = 0; i < idx->off_cnt; i++)
	  set_destroy(s[i]);
     for (i = 0; i < nwords; i++)
	  free(words[i]);
}

/* Look for 'sisters' - senses of the search word with a common parent. */

static void findsisters(IndexPtr idx)
{
     int i, j, id = 0;
     SynsetPtr synset;
     Set_t syns[MAXSENSE], n;
     struct {int id; unsigned long off;} hypers[HASHTABSIZE] = {{0}};

     assert(idx);

     /*Read all synsets and list all hyperptrs.*/

     for (i = 0; i < idx->off_cnt; i++) {
	  synset = read_synset(NOUN, idx->offset[i], idx->wd);
	  assert(synset);
	  syns[i] = set_create(4*MAXSENSE);
	  assert(syns[i]);
	  
	  for (j = 0; j < synset->ptrcount; j++)  
	       if (synset->ptrtyp[j] == HYPERPTR) { 
		    int l = hash(synset->ptroff[j]);
		    
		    for ( ; hypers[l].off != synset->ptroff[j]; l++)
			 if (hypers[l].off == 0) {
			      hypers[l].off = synset->ptroff[j];
			      hypers[l].id  =  id++;
			      break;
			 }
			 else if (l == HASHTABSIZE - 1) l = -1;
		    
		    /*Found or inserted it.*/
		    set_addobj(syns[i], hypers[l].id);
	       }
	  free_synset(synset);
     }
     n = set_create(4*MAXSENSE);
     assert(n);
     
     for (i = 0; i < idx->off_cnt; i++)
	  for (j = i+1; j < idx->off_cnt; j++)
	       if (set_intersection(n, syns[i], syns[j]),
		   !set_isempty(n))
		    add_relatives(NOUN, idx, i, j);
     
     set_destroy(n);
     for (i = 0; i < idx->off_cnt; i++)
	  set_destroy(syns[i]);
}

/* Look for 'cousins' - two senses, each under a different predefined
   top node pair.  Top node offset pairs are stored in cousin.tops. */

/* Return index of topnode if it exists */

static int find_topnode(unsigned long offset)
{
     int hashval = hash(offset), i;

     for (i = hashval; i < HASHTABSIZE; i++)
	 if (cousintops[i].offset == offset)
	     return(i);
     for (i = 0; i < hashval; i++)
	 if (cousintops[i].offset == offset)
	     return(i);
     return(-1);		/* not found */
 }

/* Return an empty slot for <offset> to be placed in. */

static int new_topnode(unsigned long offset)
{
     int hashval = hash(offset), i;

     for (i = hashval; i < HASHTABSIZE; i++)
	 if (!cousintops[i].rels)
	     return(i);
     for (i = 0; i < hashval; i++)
	 if (!cousintops[i].rels)
	     return(i);
     return(-1);		/* table is full */
}

static void add_topnode(int index, int id, Set_t s, unsigned long offset)
{
    if ((index >= 0) && (index < HASHTABSIZE)) {
	cousintops[index].rels   = s;
	cousintops[index].topnum = id;
	cousintops[index].offset = offset;
    }
}

static void clear_topnodes()
{
    int i;

    for (i = 0; i < HASHTABSIZE; i++)
	cousintops[i].offset = 0;
}

/* Read cousin.tops file (one time only) and store in different form. */

static int read_cousintops(void)
{
     static char done = 0;
     int id = 0;
     unsigned long top1, top2;
     int tidx1, tidx2;

     if (done) return(0);
     
     rewind(cousinfp);
     clear_topnodes();
     
     while (fscanf(cousinfp, "%ld %ld\n", &top1, &top2) != EOF) {
	 if ((tidx1 = find_topnode(top1)) < 0)
	     if ((tidx1 = new_topnode(top1)) != -1) {
		 add_topnode(tidx1, id++, set_create(MAXTOPS), top1);
	     } else {
		 display_message("WordNet library error: cannot create topnode table for grouped sarches\n");
		 return(-1);
	     }
	 
	 if ((tidx2 = find_topnode(top2)) < 0)
	     if ((tidx2 = new_topnode(top2)) != -1) {
		 add_topnode(tidx2, id++, set_create(MAXTOPS), top2);
	     } else {
		 display_message("WordNet library error: cannot create topnode table for grouped sarches\n");
		 return(-1);
	     }
	 
	 set_addobj(cousintops[tidx1].rels,
		    cousintops[tidx2].topnum);
	 set_addobj(cousintops[tidx2].rels,
		    cousintops[tidx1].topnum);
     }
     done = 1;
     return(0);
}

/* Record all top nodes found for synset. */

static void record_topnode(unsigned long hyperptr, void *sets)
{
     int i;
     assert(sets);
     
     if ((i = find_topnode(hyperptr)) >= 0) {
	 set_addobj(((Set_t *)sets)[0], cousintops[i].topnum);
	 set_union(((Set_t *)sets)[1], ((Set_t *)sets)[1], cousintops[i].rels);
     }
}

static void findcousins(IndexPtr idx)
{
     int i, j, nsyns;
     SynsetPtr synset;
     Set_t n, syns_tops[MAXSENSE][2];
     
     assert(idx);
     if (read_cousintops() != 0)
	 return;

     /* First read all the synsets */

     for (nsyns = 0; nsyns < idx->off_cnt; nsyns++) { /*why -1 in orig?*/
	  synset = read_synset(NOUN, idx->offset[nsyns], "");
	  syns_tops[nsyns][0] = set_create(MAXTOPS);
	  syns_tops[nsyns][1] = set_create(MAXTOPS);

	  record_topnode(idx->offset[nsyns], (void *)syns_tops[nsyns]);

	  trace_hyperptrs(synset, 
			  record_topnode, 
			  syns_tops[nsyns], 1);
	  free_synset(synset);
     }
     
     n = set_create(MAXTOPS);
     assert(n);
     for (i = 0; i < nsyns; i++)
	  for (j = i + 1; j < nsyns; j++)
	       if (set_intersection(n, syns_tops[i][0], syns_tops[j][1]),
		   !set_isempty(n))
		    add_relatives(NOUN, idx, i, j);
     
     for (i = 0; i < nsyns; i++) { 
	  set_destroy(syns_tops[i][0]);
	  set_destroy(syns_tops[i][1]);
     }
     set_destroy(n);
}

/* Trace through HYPERPTRs up to MAXDEPTH, running `fn()' on each one. */ 

void trace_hyperptrs(SynsetPtr synptr, 
		     void (*fn)(unsigned long hyperptr, void *cp),
		     void *cp, int depth)
{
     SynsetPtr s;
     int i;
     
     if (depth >= MAXDEPTH)
	  return;
     for (i = 0; i < synptr->ptrcount; i++)
	  if (synptr->ptrtyp[i] == HYPERPTR) {
	       fn(synptr->ptroff[i], cp);
	       
	       s = read_synset(synptr->ppos[i], synptr->ptroff[i], "");
	       trace_hyperptrs(s, fn, cp, depth+1);
	       free_synset(s);
	  }
}

static void findverbgroups(IndexPtr idx)
{
     int i, j, k;
     SynsetPtr synset;

     assert(idx);

     /* Read all senses */
     
     for (i = 0; i < idx->off_cnt; i++) {

	 synset = read_synset(VERB, idx->offset[i], idx->wd);
	
	 /* Look for VERBGROUP ptr(s) for this sense.  If found,
	    create group for senses, or add to existing group. */

	 for (j = 0; j < synset->ptrcount; j++) {
	       if (synset->ptrtyp[j] == VERBGROUP) {
		   /* Need to find sense number for ptr offset */
		   for (k = 0; k < idx->off_cnt; k++) {
		       if (synset->ptroff[j] == idx->offset[k]) {
			   add_relatives(VERB, idx, i, k);
			   break;
		       }
		   }
	       }
	   }
	 free_synset(synset);
     }
}

static void add_relatives(int pos, IndexPtr idx, int rel1, int rel2)
{
    int i;
    struct relgrp *rel, *last, *r;

    /* First make sure that senses are not on the excpetion list */
    if (pos == NOUN && groupexc(idx->offset[rel1], idx->offset[rel2]))
	return;

    /* If either of the new relatives are already in a relative group,
       then add the other to the existing group (transitivity).
       Otherwise create a new group and add these 2 senses to it. */

    for (rel = rellist; rel; rel = rel->next) {
	if (rel->senses[rel1] == 1 || rel->senses[rel2] == 1) {
	    rel->senses[rel1] = rel->senses[rel2] = 1;

	    /* If part of another relative group, merge the groups */
	    for (r = rellist; r; r = r->next) {
		if (r != rel &&
		    (r->senses[rel1] == 1 || r->senses[rel2] == 1)) {
		    for (i = 0; i < MAXSENSE; i++)
			rel->senses[i] |= r->senses[i];
		}
	    }
	    return;
	}
	last = rel;
    }
    rel = mkrellist();
    rel->senses[rel1] = rel->senses[rel2] = 1;
    if (rellist == NULL)
	rellist = rel;
    else
	last->next = rel;
}
    
static int groupexc(unsigned long off1, unsigned long off2)
{
    char buf[8], *p, linebuf[1024];

    sprintf(buf, "%8.8lu", (off1 < off2 ? off1 : off2));

    if ((p = bin_search(buf, cousinexcfp)) != NULL) {
	sprintf(buf, "%8.8lu", (off2 > off1 ? off2 : off1));
	strcpy(linebuf, p + 9); /* don't copy key */
	linebuf[strlen(linebuf) - 1] = '\0'; /* strip off newline */
	p = strtok(linebuf, " ");
	while (p && strcmp(p, buf))
	    p = strtok(NULL, " ");
    }
    return(p ? 1 : 0);
}

static struct relgrp *mkrellist(void)
{
    struct relgrp *rel;
    int i;

    rel = (struct relgrp *) malloc(sizeof(struct relgrp));
    assert(rel);
    for (i = 0; i < MAXSENSE; i++)
	rel->senses[i] = 0;
    rel->next = NULL;
    return(rel);
}

static void free_rellist(void)
{
    struct relgrp *rel, *next;

    rel = rellist;
    while(rel) {
	next = rel->next;
	free(rel);
	rel = next;
    }
}

static void printrelatives(IndexPtr idx, int dbase)
{
    SynsetPtr synptr;
    struct relgrp *rel;
    int i, flag;
    int outsenses[MAXSENSE];

    for (i = 0; i < idx->off_cnt; i++)
	outsenses[i] = 0;
    prflag = 1;

    for (rel = rellist; rel; rel = rel->next) {
	flag = 0;
	for (i = 0; i < idx->off_cnt; i++) {
	    if (rel->senses[i] && !outsenses[i]) {
		flag = 1;
		synptr = read_synset(dbase, idx->offset[i], "");
		printsns(synptr, i + 1);
		traceptrs(synptr, HYPERPTR, dbase, 0);
		outsenses[i] = 1;
		free_synset(synptr);
	    }
	}
	if (flag)
	    printbuffer("--------------\n");
    }

    for (i = 0; i < idx->off_cnt; i++) {
	if (!outsenses[i]) {
	    synptr = read_synset(dbase, idx->offset[i], "");
	    printsns(synptr, i + 1);
	    traceptrs(synptr, HYPERPTR, dbase, 0);
	    printbuffer("--------------\n");
	    free_synset(synptr);
	}
    }
}

/*
  Search code interfaces to WordNet database

  findtheinfo() - print search results and return ptr to output buffer
  findtheinfo_ds() - return search results in linked list data structrure
*/

char *findtheinfo(char *searchstr, int dbase, int ptrtyp, int whichsense)
{
    SynsetPtr cursyn;
    IndexPtr idx = NULL;
    int depth = 0;
    int i, offsetcnt;
    char *bufstart;
    unsigned long offsets[MAXSENSE];
    int skipit;

    /* Initializations -
       clear output buffer, search results structure, flags */

    searchbuffer[0] = '\0';

    wnresults.numforms = wnresults.printcnt = 0;
    wnresults.searchbuf = searchbuffer;
    wnresults.searchds = NULL;

    abortsearch = overflag = 0;
    for (i = 0; i < MAXSENSE; i++)
	offsets[i] = 0;

    switch (ptrtyp) {
    case OVERVIEW:
	WNOverview(searchstr, dbase);
	break;
    case FREQ:
	while ((idx = getindex(searchstr, dbase)) != NULL) {
	    searchstr = NULL;
	    wnresults.SenseCount[wnresults.numforms] = idx->off_cnt;
	    freq_word(idx);
	    free_index(idx);
	    wnresults.numforms++;
	}
	break;
    case WNGREP:
	wngrep(searchstr, dbase);
	break;
    case WNESCORT:
	sprintf(searchbuffer,
	"Sentences containing %s will be displayed in the Escort window.",
		searchstr);
	break;
    case RELATIVES:
    case VERBGROUP:
	while ((idx = getindex(searchstr, dbase)) != NULL) {
	    searchstr = NULL;
	    wnresults.SenseCount[wnresults.numforms] = idx->off_cnt;
	    relatives(idx, dbase);
	    free_index(idx);
	    wnresults.numforms++;
	}
	break;
    default:

	/* If negative search type, set flag for recursive search */
	if (ptrtyp < 0) {
	    ptrtyp = -ptrtyp;
	    depth = 1;
	}
	bufstart = searchbuffer;
	offsetcnt = 0;

	/* look at all spellings of word */

	while ((idx = getindex(searchstr, dbase)) != NULL) {

	    searchstr = NULL;	/* clear out for next call to getindex() */
	    wnresults.SenseCount[wnresults.numforms] = idx->off_cnt;
	    wnresults.OutSenseCount[wnresults.numforms] = 0;

	    /* Print extra sense msgs if looking at all senses */
	    if (whichsense == ALLSENSES)
		printbuffer(
"                                                                         \n");

	    /* Go through all of the searchword's senses in the
	       database and perform the search requested. */

	    for (sense = 0; sense < idx->off_cnt; sense++) {

		if (whichsense == ALLSENSES || whichsense == sense + 1) {
		    prflag = 0;

		    /* Determine if this synset has already been done
		       with a different spelling. If so, skip it. */
		    for (i = 0, skipit = 0; i < offsetcnt && !skipit; i++) {
			if (offsets[i] == idx->offset[sense])
			    skipit = 1;
		    }
		    if (skipit != 1) {
		    	offsets[offsetcnt++] = idx->offset[sense];
		    	cursyn = read_synset(dbase, idx->offset[sense], idx->wd);
		    	switch(ptrtyp) {
		    	case ANTPTR:
			    if(dbase == ADJ)
			    	traceadjant(cursyn);
			    else
			    	traceptrs(cursyn, ANTPTR, dbase, depth);
			    break;
		   	 
		    	case COORDS:
			    tracecoords(cursyn, HYPOPTR, dbase, depth);
			    break;
		   	 
		    	case FRAMES:
			    printframe(cursyn, 1);
			    break;
			    
		    	case MERONYM:
			    traceptrs(cursyn, HASMEMBERPTR, dbase, depth);
			    traceptrs(cursyn, HASSTUFFPTR, dbase, depth);
			    traceptrs(cursyn, HASPARTPTR, dbase, depth);
			    break;
			    
		    	case HOLONYM:
			    traceptrs(cursyn, ISMEMBERPTR, dbase, depth);
			    traceptrs(cursyn, ISSTUFFPTR, dbase, depth);
			    traceptrs(cursyn, ISPARTPTR, dbase, depth);
			    break;
			   	 
		    	case HMERONYM:
			    partsall(cursyn, HMERONYM);
			    break;
			   	 
		    	case HHOLONYM:
			    partsall(cursyn, HHOLONYM);
			    break;
			   	 
		    	case SEEALSOPTR:
			    printseealso(cursyn);
			    break;
	
#ifdef FOOP
			case PPLPTR:
			    traceptrs(cursyn, ptrtyp, dbase, depth);
			    traceptrs(cursyn, PPLPTR, dbase, depth);
			    break;
#endif
		    
		    	case SIMPTR:
		    	case SYNS:
		    	case HYPERPTR:
			    printsns(cursyn, sense + 1);
			    prflag = 1;
		    
			    traceptrs(cursyn, ptrtyp, dbase, depth);
		    
			    if (dbase == ADJ) {
			    	traceptrs(cursyn, PERTPTR, dbase, depth);
			    	traceptrs(cursyn, PPLPTR, dbase, depth);
			    } else if (dbase == ADV) {
			    	traceptrs(cursyn, PERTPTR, dbase, depth);
			    }

			    if (saflag)	/* print SEE ALSO pointers */
			    	printseealso(cursyn);
			    
			    if (dbase == VERB && frflag)
			    	printframe(cursyn, 0);
			    break;
		    
		    	default:
			    traceptrs(cursyn, ptrtyp, dbase, depth);
			    break;

		    	} /* end switch */

		    	free_synset(cursyn);

		    } /* end if (skipit) */

		} /* end if (whichsense) */

		if (skipit != 1) {
		    interface_doevents();
		    if ((whichsense == sense + 1) || abortsearch || overflag)
		    	break;	/* break out of loop - we're done */
		}

	    } /* end for (sense) */

	    /* Done with an index entry - patch in number of senses output */

	    if (whichsense == ALLSENSES) {
		i = wnresults.OutSenseCount[wnresults.numforms];
		if (i == idx->off_cnt && i == 1)
		    sprintf(tmpbuf, "\n1 sense of %s", idx->wd);
		else if (i == idx->off_cnt)
		    sprintf(tmpbuf, "\n%d senses of %s", i, idx->wd);
		else if (i > 0)	/* printed some senses */
		    sprintf(tmpbuf, "\n%d of %d senses of %s",
			    i, idx->off_cnt, idx->wd);

		/* Find starting offset in searchbuffer for this index
		   entry and patch string in.  Then update bufstart
		   to end of searchbuffer for start of next index entry. */

		if (i > 0) {
		    if (wnresults.numforms > 0) {
			bufstart[0] = '\n';
			bufstart++;
		    }
		    strncpy(bufstart, tmpbuf, strlen(tmpbuf));
		    bufstart = searchbuffer + strlen(searchbuffer);
		}
	    }

	    free_index(idx);

	    interface_doevents();
	    if (overflag || abortsearch)
		break;		/* break out of while (idx) loop */

	    wnresults.numforms++;

	} /* end while (idx) */

    } /* end switch */

    interface_doevents();
    if (abortsearch)
	printbuffer("\nSearch Interrupted...\n");
    else if (overflag)
	sprintf(searchbuffer,
		"Search too large.  Narrow search and try again...\n");

    /* replace underscores with spaces before returning */

    return(strsubst(searchbuffer, '_', ' '));
}

SynsetPtr findtheinfo_ds(char *searchstr, int dbase, int ptrtyp, int whichsense)
{
    IndexPtr idx;
    SynsetPtr cursyn;
    SynsetPtr synlist = NULL, lastsyn = NULL;
    int depth = 0;
    int newsense = 0;

    wnresults.numforms = 0;
    wnresults.printcnt = 0;

    while ((idx = getindex(searchstr, dbase)) != NULL) {

	searchstr = NULL;	/* clear out for next call */
	newsense = 1;
	
	if(ptrtyp < 0) {
	    ptrtyp = -ptrtyp;
	    depth = 1;
	}

	wnresults.SenseCount[wnresults.numforms] = idx->off_cnt;
	wnresults.OutSenseCount[wnresults.numforms] = 0;
	wnresults.searchbuf = NULL;
	wnresults.searchds = NULL;

	/* Go through all of the searchword's senses in the
	   database and perform the search requested. */
	
	for(sense = 0; sense < idx->off_cnt; sense++) {
	    if (whichsense == ALLSENSES || whichsense == sense + 1) {
		cursyn = read_synset(dbase, idx->offset[sense], idx->wd);
		if (lastsyn) {
		    if (newsense)
			lastsyn->nextform = cursyn;
		    else
			lastsyn->nextss = cursyn;
		}
		if (!synlist)
		    synlist = cursyn;
		newsense = 0;
	    
		cursyn->searchtype = ptrtyp;
		cursyn->ptrlist = traceptrs_ds(cursyn, ptrtyp, 
					       getpos(cursyn->pos),
					       depth);
	    
		lastsyn = cursyn;

		if (whichsense == sense + 1)
		    break;
	    }
	}
	free_index(idx);
	wnresults.numforms++;
    }
    wnresults.searchds = synlist;
    return(synlist);
}

/* Recursive search algorithm to trace a pointer tree and return results
   in linked list of data structures. */

SynsetPtr traceptrs_ds(SynsetPtr synptr, int ptrtyp, int dbase, int depth)
{
    int i;
    SynsetPtr cursyn, synlist = NULL, lastsyn = NULL;
    
    /* If synset is a satellite, find the head word of its
       head synset and the head word's sense number. */

    if (getsstype(synptr->pos) == SATELLITE) {
	for (i = 0; i < synptr->ptrcount; i++)
	    if (synptr->ptrtyp[i] == SIMPTR) {
		cursyn = read_synset(synptr->ppos[i],
				      synptr->ptroff[i],
				      "");
		synptr->headword = malloc(strlen(cursyn->words[0]) + 1);
		assert(synptr->headword);
		strcpy(synptr->headword, cursyn->words[0]);
		synptr->headsense = cursyn->lexid[0];
		free_synset(cursyn);
		break;
	    }
    }
	    
    for (i = 0; i < synptr->ptrcount; i++) {
	if((synptr->ptrtyp[i] == ptrtyp) &&
	   ((synptr->pfrm[i] == 0) ||
	    (synptr->pfrm[i] == synptr->whichword))) {
	    
	    cursyn=read_synset(synptr->ppos[i], synptr->ptroff[i], "");
	    cursyn->searchtype = ptrtyp;

	    for (i = 0; i < cursyn->wcount; i++)
		cursyn->wnsns[i] = getsearchsense(cursyn, i + 1);

	    if (lastsyn)
		lastsyn->nextss = cursyn;
	    if (!synlist)
		synlist = cursyn;
	    lastsyn = cursyn;

	    if(depth) {
		depth = depthcheck(depth, cursyn);
		cursyn->ptrlist = traceptrs_ds(cursyn, ptrtyp,
					       getpos(cursyn->pos),
					       (depth+1));
	    }	
	}
    }
    return(synlist);
}

static void WNOverview(char *searchstr, int pos)
{
    SynsetPtr cursyn;
    IndexPtr idx = NULL;
    char *cpstring = searchstr, *bufstart;
    int sense, i, offsetcnt;
    int svdflag, skipit;
    unsigned long offsets[MAXSENSE];

    cpstring = searchstr;
    bufstart = searchbuffer;
    for (i = 0; i < MAXSENSE; i++)
	offsets[i] = 0;
    offsetcnt = 0;

    while ((idx = getindex(cpstring, pos)) != NULL) {

	cpstring = NULL;	/* clear for next call to getindex() */
	wnresults.SenseCount[wnresults.numforms++] = idx->off_cnt;
	wnresults.OutSenseCount[wnresults.numforms] = 0;

	printbuffer(
"                                                                                                   \n");

	/* Print synset for each sense.  If requested, precede
	   synset with synset offset and/or lexical file information.*/

	for (sense = 0; sense < idx->off_cnt; sense++) {

	    for (i = 0, skipit = 0; i < offsetcnt && !skipit; i++)
		if (offsets[i] == idx->offset[sense])
		    skipit = 1;

	    if (!skipit) {
		offsets[offsetcnt++] = idx->offset[sense];
		cursyn = read_synset(pos, idx->offset[sense], idx->wd);
		sprintf(tmpbuf, "%d. ", sense + 1);

		svdflag = dflag;
		dflag = 1;
		printsynset(tmpbuf, cursyn, "\n", DEFON, ALLWORDS,
			    SKIP_ANTS, SKIP_MARKER);
		dflag = svdflag;
		wnresults.OutSenseCount[wnresults.numforms]++;
		wnresults.printcnt++;

		free_synset(cursyn);
	    }
	}

	/* Print sense summary message */

	i = wnresults.OutSenseCount[wnresults.numforms];

	if (i > 0) {
	    if (i == 1)
		sprintf(tmpbuf, "\nThe %s %s has 1 sense",
			partnames[pos], idx->wd);
	    else
		sprintf(tmpbuf, "\nThe %s %s has %d senses",
			partnames[pos], idx->wd, i);
	    if (idx->tagged_cnt > 0)
		sprintf(tmpbuf + strlen(tmpbuf),
			" (first %d from tagged texts)\n", idx->tagged_cnt);
	    else if (idx->tagged_cnt == 0) 
		sprintf(tmpbuf + strlen(tmpbuf),
			" (no senses from tagged texts)\n");

	    strncpy(bufstart, tmpbuf, strlen(tmpbuf));
	    bufstart = searchbuffer + strlen(searchbuffer);
	} else
	    bufstart[0] = '\0';

	wnresults.numforms++;
	free_index(idx);
    }
}

/* Do requested search on synset passed, returning output in buffer. */

char *do_trace(SynsetPtr synptr, int ptrtyp, int dbase, int depth)
{
    searchbuffer[0] = '\0';	/* clear output buffer */
    traceptrs(synptr, ptrtyp, dbase, depth);
    return(searchbuffer);
}

/* Set bit for each search type that is valid for the search word
   passed and return bit mask. */
  
unsigned long is_defined(char *searchstr, int dbase)
{
    IndexPtr index;
    int i;
    unsigned long retval = 0;

    wnresults.numforms = wnresults.printcnt = 0;
    wnresults.searchbuf = NULL;
    wnresults.searchds = NULL;

    while ((index = getindex(searchstr, dbase)) != NULL) {
	searchstr = NULL;	/* clear out for next getindex() call */

	wnresults.SenseCount[wnresults.numforms] = index->off_cnt;
	
	/* set bits that must be true for all words */
	
	retval |= bit(SIMPTR) | bit(FREQ) | bit(SYNS)|
	    bit(WNGREP) | bit(OVERVIEW);

	for(i = 0; i < index->ptruse_cnt; i++) {
	    
	    retval |= bit(index->ptruse[i]); /* set bit for this ptr */

	    if (dbase == NOUN) {

		/* set generic HOLONYM and/or MERONYM bit if necessary */
	    
		if(index->ptruse[i] >= ISMEMBERPTR &&
		   index->ptruse[i] <= ISPARTPTR)
		    retval |= bit(HOLONYM);
		else if(index->ptruse[i] >= HASMEMBERPTR &&
			index->ptruse[i] <= HASPARTPTR)
		    retval |= bit(MERONYM);
	    } else if (dbase == ADJ && index->ptruse[i] == SIMPTR)
		retval |= bit(ANTPTR);
	}

	if (dbase == NOUN) {
	    retval |= bit(RELATIVES);
	    if (HasHoloMero(index, HMERONYM))
		retval |= bit(HMERONYM);
	    if (HasHoloMero(index, HHOLONYM))
		retval |= bit(HHOLONYM);
	    if (retval & bit(HYPERPTR))
		retval |= bit(COORDS);
	} else if (dbase == VERB) {
	    retval |= bit(RELATIVES);
	}
	free_index(index);
	wnresults.numforms++;
    }
    return(retval);
}

/* Determine if any of the synsets that this word is in have inherited
   meronyms or holonyms. */

static int HasHoloMero(IndexPtr index, int ptrtyp)
{
    int i;
    SynsetPtr synset;
    int found=0;
    int ptrbase;
    
    ptrbase = (ptrtyp == HMERONYM) ? HASMEMBERPTR : ISMEMBERPTR;
    
    for(i = 0; i < index->off_cnt; i++) {
	synset = read_synset(NOUN, index->offset[i], "");
	found += HasPtr(synset, ptrbase);
	found += HasPtr(synset, ptrbase + 1);
	found += HasPtr(synset, ptrbase + 2);
	free_synset(synset);
    }
    return(found);
}

static int HasPtr(SynsetPtr synptr, int ptrtyp)
{
    int i;
    
    for(i = 0; i < synptr->ptrcount; i++) {
        if(synptr->ptrtyp[i] == ptrtyp) {
	    return(1);
	}
    }
    return(0);
}

/* Set bit for each POS that search word is in.  0 returned if
   word is not in WordNet. */

unsigned int in_wn(char *word, int pos)
{
    int i;
    unsigned int retval = 0;

    if (pos == ALL_POS) {
	for (i = 1; i < NUMPARTS + 1; i++)
	    if (indexfps[i] != NULL && bin_search(word, indexfps[i]) != NULL)
		retval |= bit(i);
    } else if (indexfps[pos] != NULL && bin_search(word,indexfps[pos]) != NULL)
	    retval |= bit(pos);
    return(retval);
}

static int depthcheck(int depth, SynsetPtr synptr)
{
    if(depth >= MAXDEPTH) {
	sprintf(msgbuf,
		"WordNet library error: Error Cycle detected\n   %s\n",
		synptr->words[0]);
	display_message(msgbuf);
	depth = -1;		/* reset to get one more trace then quit */
    }
    return(depth);
}

/* Strip off () enclosed comments from a word */

static char *deadjify(char *word)
{
    char *y;
    
    adj_marker = UNKNOWN_MARKER; /* default if not adj or unknown */
    
    y=word;
    while(*y) {
	if(*y == '(') {
	    if (!strncmp(y, "(a)", 3))
		adj_marker = ATTRIBUTIVE;
	    else if (!strncmp(y, "(ip)", 4))
		adj_marker = IMMED_POSTNOMINAL;
	    else if (!strncmp(y, "(p)", 3))
		adj_marker = PREDICATIVE;
	    *y='\0';
	} else 
	    y++;
    }
    return(word);
}

static int getsearchsense(SynsetPtr synptr, int whichword)
{
    IndexPtr idx;
    int i;

    strsubst(strcpy(wdbuf, synptr->words[whichword - 1]), ' ', '_');
    strtolower(wdbuf);
		       
    if (idx = index_lookup(wdbuf, getpos(synptr->pos))) {
	for (i = 0; i < idx->off_cnt; i++)
	    if (idx->offset[i] == synptr->hereiam) {
		free_index(idx);
		return(i + 1);
	    }
	free_index(idx);
    }
    return(0);
}

static void printsynset(char *head, SynsetPtr synptr, char *tail, int definition, int wdnum, int antflag, int markerflag)
{
    int i, wdcnt;
    char tbuf[SMLINEBUF];

    tbuf[0] = '\0';		/* clear working buffer */

    strcat(tbuf, head);		/* print head */

    /* Precede synset with additional information as indiecated
       by flags */

    if (offsetflag)		/* print synset offset */
	sprintf(tbuf + strlen(tbuf),"{%8.8d} ", synptr->hereiam);
    if (fileinfoflag) {		/* print lexicographer file information */
	sprintf(tbuf + strlen(tbuf), "<%s> ", lexfiles[synptr->fnum]);
	prlexid = 1;		/* print lexicographer id after word */
    } else
	prlexid = 0;
    
    if (wdnum)			/* print only specific word asked for */
	catword(tbuf, synptr, wdnum - 1, markerflag, antflag);
    else			/* print all words in synset */
	for(i = 0, wdcnt = synptr->wcount; i < wdcnt; i++) {
	    catword(tbuf, synptr, i, markerflag, antflag);
	    if (i < wdcnt - 1)
		strcat(tbuf, ", ");
	}
    
    if(definition && dflag && synptr->defn) {
	strcat(tbuf," -- ");
	strcat(tbuf,synptr->defn);
    }
    
    strcat(tbuf,tail);
    printbuffer(tbuf);
}

static void printantsynset(SynsetPtr synptr, char *tail, int anttype, int definition)
{
    int i, wdcnt;
    char tbuf[SMLINEBUF];
    char *str;
    int first = 1;

    tbuf[0] = '\0';

    if (offsetflag)
	sprintf(tbuf,"{%8.8d} ", synptr->hereiam);
    if (fileinfoflag) {
	sprintf(tbuf + strlen(tbuf),"<%s> ", lexfiles[synptr->fnum]);
	prlexid = 1;
    } else
	prlexid = 0;
    
    /* print anotnyms from cluster head (of indirect ant) */
    
    strcat(tbuf, "INDIRECT (VIA ");
    for(i = 0, wdcnt = synptr->wcount; i < wdcnt; i++) {
	if (first) {
	    str = printant(ADJ, synptr, i + 1, "%s", ", ");
	    first = 0;
	} else
	    str = printant(ADJ, synptr, i + 1, ", %s", ", ");
	if (*str)
	    strcat(tbuf, str);
    }
    strcat(tbuf, ") -> ");
    
    /* now print synonyms from cluster head (of indirect ant) */
    
    for (i = 0, wdcnt = synptr->wcount; i < wdcnt; i++) {
	catword(tbuf, synptr, i, SKIP_MARKER, SKIP_ANTS);
	if (i < wdcnt - 1)
	    strcat(tbuf, ", ");
    }
    
    if(dflag && synptr->defn && definition) {
	strcat(tbuf," -- ");
	strcat(tbuf,synptr->defn);
    }
    
    strcat(tbuf,tail);
    printbuffer(tbuf);
}

static void catword(char *buf, SynsetPtr synptr, int wdnum, int adjmarker, int antflag)
{
    static char vs[] = " (vs. %s)";
    static char *markers[] = {
	"",			/* UNKNOWN_MARKER */
	"(prenominal)",		/* ATTRIBUTIVE */
	"(postnominal)",	/* IMMED_POSTNOMINAL */
	"(predicate)",		/* PREDICATIVE */
    };

    /* Copy the word (since deadjify() changes original string),
       deadjify() the copy and append to buffer */
    
    strcpy(wdbuf, synptr->words[wdnum]);
    strcat(buf, deadjify(wdbuf));

    /* Print additional lexicographer information and WordNet sense
       number as indicated by flags */
	
    if (prlexid && (synptr->lexid[wdnum] != 0))
	sprintf(buf + strlen(buf), "%d", synptr->lexid[wdnum]);
    if (wnsnsflag)
	sprintf(buf + strlen(buf), "#%d", getsearchsense(synptr, wdnum + 1));

    /* For adjectives, append adjective marker if present, and
       print antonym if flag is passed */

    if (getpos(synptr->pos) == ADJ) {
	if (adjmarker == PRINT_MARKER)
	    strcat(buf, markers[adj_marker]); 
	if (antflag == PRINT_ANTS)
	    strcat(buf, printant(ADJ, synptr, wdnum + 1, vs, ""));
    }
}

static char *printant(int dbase, SynsetPtr synptr, int wdnum, char *template, char *tail)
{
    int i, j, wdoff;
    SynsetPtr psynptr;
    char tbuf[WORDBUF];
    static char retbuf[SMLINEBUF];
    int first = 1;
    
    retbuf[0] = '\0';
    
    /* Go through all the pointers looking for anotnyms from the word
       indicated by wdnum.  When found, print all the antonym's
       antonym pointers which point back to wdnum. */
    
    for (i = 0; i < synptr->ptrcount; i++) {
	if (synptr->ptrtyp[i] == ANTPTR && synptr->pfrm[i] == wdnum) {

	    psynptr = read_synset(dbase, synptr->ptroff[i], "");

	    for (j = 0; j < psynptr->ptrcount; j++) {
		if (psynptr->ptrtyp[j] == ANTPTR &&
		    psynptr->pto[j] == wdnum &&
		    psynptr->ptroff[j] == synptr->hereiam) {

		    wdoff = (psynptr->pfrm[j] ? (psynptr->pfrm[j] - 1) : 0);

		    /* Construct buffer containing formatted antonym,
		       then add it onto end of return buffer */

		    strcpy(wdbuf, psynptr->words[wdoff]);
		    strcpy(tbuf, deadjify(wdbuf));

		    /* Print additional lexicographer information and
		       WordNet sense number as indicated by flags */
	
		    if (prlexid && (psynptr->lexid[wdoff] != 0))
			sprintf(tbuf + strlen(tbuf), "%d",
				psynptr->lexid[wdoff]);
		    if (wnsnsflag)
			sprintf(tbuf + strlen(tbuf), "#%d",
				getsearchsense(psynptr, wdoff + 1));
		    if (!first)
			strcat(retbuf, tail);
		    else
			first = 0;
		    sprintf(retbuf + strlen(retbuf), template, tbuf);
		}
	    }
	    free_synset(psynptr);
	}
    }
    return(retbuf);
}

static void printbuffer(char *string)
{
    if (overflag)
	return;
    if (strlen(searchbuffer) + strlen(string) >= SEARCHBUF)
        overflag = 1;
    else 
	strcat(searchbuffer, string);
}

static void printsns(SynsetPtr synptr, int sense)
{
    printsense(synptr, sense);
    printsynset("", synptr, "\n", DEFON, ALLWORDS, PRINT_ANTS, PRINT_MARKER);
}

static void printsense(SynsetPtr synptr, int sense)
{
    char tbuf[256];

    /* Append lexicographer filename after Sense # if flag is set. */

    if (fnflag)
	sprintf(tbuf,"\nSense %d in file \"%s\"\n",
		sense, lexfiles[synptr->fnum]);
    else
	sprintf(tbuf,"\nSense %d\n", sense);

    printbuffer(tbuf);

    /* update counters */
    wnresults.OutSenseCount[wnresults.numforms]++; 
    wnresults.printcnt++;
}

static void printspaces(int trace, int depth)
{
    int j;

    for (j = 0; j < depth; j++)
	printbuffer("    ");

    switch(trace) {
    case TRACEP:		/* traceptrs() */
	if (depth)
	    printbuffer("   ");
	else
	    printbuffer("       ");
	break;

    case TRACEC:		/* tracecoords() */
	if (!depth)
	    printbuffer("    ");
	break;

    case TRACEI:			/* traceinherit() */
	if (!depth)
	    printbuffer("\n    ");
	break;
    }
}

/* Dummy function to force Tcl/Tk to look at event queue to see of
   the user wants to stop the search. */

static void interface_doevents (void) {
   if (interface_doevents_func != NULL) interface_doevents_func ();
}

/*
  Revision log: (since version 1.5)
  
  $Log: search.c,v $
 * Revision 1.134  1997/11/07  16:27:36  wn
 * cleanup calls to traceptrs
 *
 * Revision 1.133  1997/10/16  17:13:08  wn
 * fixed bug in add_topnode when index == 0
 *
 * Revision 1.132  1997/09/05  15:33:18  wn
 * change printframes to only print generic frames if specific example not found
 *
 * Revision 1.131  1997/09/02  16:31:18  wn
 * changed includes
 *
 * Revision 1.130  1997/09/02  14:43:23  wn
 * added code to test wnrelease in parse_synset and WNOverview
 *
 * Revision 1.129  1997/08/29  20:45:25  wn
 * added location sanity check on parse_synset
 *
 * Revision 1.128  1997/08/29  18:35:03  wn
 * a bunch of additional cleanups; added code to traceptrs_ds to
 * tore wordnet sense number for each word; added wnresults structure;
 * terminate holo/mero search at highest level having holo/mero
 *
 * Revision 1.127  1997/08/28  17:26:46  wn
 * Changed "n senses from tagged data" to "n senses from tagged texts"
 * in the overview.
 *
 * Revision 1.126  1997/08/27  13:26:07  wn
 * trivial change in wngrep (initialized count to zero)
 *
 * Revision 1.125  1997/08/26  21:13:14  wn
 * Grep now runs quickly because it doesn't call the doevents callback
 * after each line of the search.
 *
 * Revision 1.124  1997/08/26  20:11:23  wn
 * massive cleanups to print functions
 *
 * Revision 1.123  1997/08/26  15:04:18  wn
 * I think I got it this time; replaced goto skipit with int skipit flag
 * to make compiling easier on the Mac.
 *
 * Revision 1.122  1997/08/26  14:43:40  wn
 * In an effort to avoid compilation errors on the
 * Mac caused by the use of a "goto", I had tried to replace it with
 * an if block, but had done so improperly.  This is the restored version
 * from before.  Next check-in will have it properly replaced with flags.
 *
 * Revision 1.121  1997/08/25  15:54:21  wn
 * *** empty log message ***
 *
 * Revision 1.120  1997/08/22  21:06:02  wn
 * added code to use wnsnsflag to print wn sense number after each word
 *
 * Revision 1.119  1997/08/22  20:52:09  wn
 * cleaned up findtheinfo and other fns a bit
 *
 * Revision 1.118  1997/08/21  20:59:20  wn
 * grep now uses strstr instead of regexp searches.  the old version is
 * still there but commented out.
 *
 * Revision 1.117  1997/08/21  18:41:30  wn
 * now eliminates duplicates on search returns, but not yet in overview
 *
  Revision 1.116  1997/08/13 17:23:45  wn
  fixed mac defines

 * Revision 1.115  1997/08/08  20:56:33  wn
 * now uses built-in grep
 *
 * Revision 1.114  1997/08/08  19:15:41  wn
 * added code to read attest_cnt field in index file.
 * made searchbuffer fixed size
 * added WNOverview (OVERVIEW) search
 * added offsetflag to print synset offset before synset
 *
 * Revision 1.113  1997/08/05  14:20:29  wn
 * changed printbuffer to not realloc space, removed calls to stopsearch()
 *
 * Revision 1.112  1997/07/25  17:30:03  wn
 * various cleanups for release 1.6
 *
  Revision 1.111  1997/07/11 20:20:04  wn
  Added interface_doevents code for making searches interruptable in single-threaded environments.

 * Revision 1.110  1997/07/10  19:01:57  wn
 * changed evca stuff
 *
  Revision 1.109  1997/04/22 19:59:08  wn
  allow pertainyms to have antonyms

 * Revision 1.108  1996/09/17  20:05:01  wn
 * cleaned up EVCA code
 *
 * Revision 1.107  1996/08/16  18:34:13  wn
 * fixed minor bug in findcousins
 *
 * Revision 1.106  1996/07/17  14:02:17  wn
 * Added Kohl's verb example sentences. See getexample() and findExample().
 *
 * Revision 1.105  1996/06/14  18:49:49  wn
 * upped size of tmpbuf
 *
 * Revision 1.104  1996/02/08  16:42:30  wn
 * added some newlines to separate output and clear out tmpbuf
 * so invalid searches return empty string
 *
 * Revision 1.103  1995/11/30  14:54:53  wn
 * added grouped search for verbs
 *
 * Revision 1.102  1995/07/19  13:17:38  bagyenda
 * *** empty log message ***
 *
 * Revision 1.101  1995/07/18  19:15:30  wn
 * *** empty log message ***
 *
 * Revision 1.100  1995/07/18  18:56:24  bagyenda
 * New implementation of grouped searches --Paul.
 *
 * Revision 1.99  1995/06/30  19:21:23  wn
 * added code to findtheinfo_ds to link additional word forms
 * onto synset chain
 *
 * Revision 1.98  1995/06/12  18:33:51  wn
 * Minor change to getindex() -- Paul.
 *
 * Revision 1.97  1995/06/09  14:46:42  wn
 * *** empty log message ***
 *
 * Revision 1.96  1995/06/09  14:32:49  wn
 * changed code for PPLPTR and PERTPTR to print synsets pointed to
 *
 * Revision 1.95  1995/06/01  15:50:34  wn
 * cleanup of code dealing with various hyphenations
 * 
 */
