In addition to the notes in these docs, about how to make the docs...

To create the version that able to be included in a reasonable LaTeX file,
copy the one made from `make latexpdf` to this directory and do the following:

1. remove everything before the begin document, remove the last chapter
2. section -> subsection
3. chapter -> section
4. alltt -> lstlisting
5. code -> lstinline
6. textbackslash{} ->

That should do it!
