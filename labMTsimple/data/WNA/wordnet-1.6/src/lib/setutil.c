
/* Implementation of sets. (c) 1995 Paul Bagyenda.*/
#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include  "setutil.h"

typedef unsigned int bucket_t;
struct set_tag {
     unsigned max_elem;
     bucket_t buckets[1];
};

#define BUCKET_SIZE     (sizeof (bucket_t))
#define BITS_PER_BUCKET (8*BUCKET_SIZE)
#define NBUCKETS(n)     (((n) +  BITS_PER_BUCKET - 1)/BITS_PER_BUCKET)


/*create and initialise a set object that can hold up to max distinct objs*/
Set_t set_create(unsigned max_elem)
{
     Set_t s = calloc(1, sizeof *s + 
		      (NBUCKETS(max_elem) - 1)*BUCKET_SIZE);
     
     assert(s);
     s->max_elem = max_elem;
     return s;
} 


Set_t set_resize(Set_t s, unsigned new_max_elem)
{
     unsigned n, m;

     assert(s);
     n = NBUCKETS(s->max_elem);
     m = NBUCKETS(new_max_elem);
     if (m != n) {
	  s = realloc(s, sizeof *s  + m*BUCKET_SIZE);
	  assert(s);
	  if (m > n)
	       memset(s->buckets + n, 0, (m - n)*BUCKET_SIZE);
     }
     s->max_elem = new_max_elem;
     return s;
}

void set_destroy(Set_t s)
{
     assert(s);
     free(s);
}

void set_addobj(Set_t s, unsigned objnum)
{
     assert(s);
     assert(objnum < s->max_elem);
     
     s->buckets[objnum/BITS_PER_BUCKET] |= 1 << (objnum % BITS_PER_BUCKET);
}

void removeobj(Set_t s, unsigned objnum)
{
     assert(s);
     assert(objnum < s->max_elem);
     
     s->buckets[objnum/BITS_PER_BUCKET] &= ~(1 << (objnum % BITS_PER_BUCKET));
}
 
void set_union(Set_t u, Set_t a, Set_t b)
{
     unsigned i;
     
     assert(a);
     assert(b);
     assert(u);
     assert(a->max_elem == b->max_elem);
     assert(u->max_elem >= a->max_elem);
     
     for (i = 0; i < NBUCKETS(a->max_elem); i++)
	  u->buckets[i] = a->buckets[i] | b->buckets[i];
     for ( ; i < NBUCKETS(u->max_elem); i++)
	  u->buckets[i] = 0;
}

void set_intersection(Set_t n, Set_t a, Set_t b)
{
     unsigned i;

     assert(a);
     assert(b);
     assert(n);
     assert(a->max_elem == b->max_elem);
     assert(n->max_elem >= a->max_elem);
 
     for (i = 0; i < NBUCKETS(a->max_elem); i++)
	  n->buckets[i] = a->buckets[i] & b->buckets[i];
     for ( ; i < NBUCKETS(n->max_elem); i++)
	  n->buckets[i] = 0;
}

static int bitcount(bucket_t n)
{
     int i, count;
     
     for (count = 0, i = 0; i < BITS_PER_BUCKET - 1; i++)
	  if (n & (1 << i)) count++;

     return count;
}

int set_nelem(Set_t s)
{
     unsigned i, n;

     assert(s);

     for (i = 0, n = 0; i < NBUCKETS(s->max_elem); i++)
	  n += bitcount(s->buckets[i]);
     return n;
}

int set_isempty(Set_t s)
{
     int i;
     assert(s);
     
     for (i = 0; i < NBUCKETS(s->max_elem); i++)
	  if (s->buckets[i])
	       return 0;
     return 1;
}

int set_haselem(Set_t s, unsigned objnum)
{
     assert(s);
     assert(objnum < s->max_elem);

     return 
	  s->buckets[objnum/BITS_PER_BUCKET] & 
	       (1 << (objnum % BITS_PER_BUCKET));
}

int set_maxelem(Set_t s)
{
     assert(s);
     return s->max_elem;
}
