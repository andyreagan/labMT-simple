Advanced Usage
==============

About Tries
-----------

For dictionary lookup of scores from phrases, the fastest benchmarks I've found and that were reasonable stable were from the libraries `datrie` and `marisatrie` which both have python bindings.

They're used in the `speedy` module in an attempt to both speed things up, and match against word stems.

Advanced Parsing
----------------

Some dictionaries use word stems to cover the multiple uses of a single word, with a single score.
We can very quickly match these word stems using a prefix match on a trie.
This is much better than using many compiled RE matches, which in my testing took a very long time.
