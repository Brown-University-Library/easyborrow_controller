#### on this page... ####

- info/overview
- qualifier
- license


#### info/overview ####

In 2005 ago the [Library](http://library.brown.edu) made a decision to privilege giving patrons as deep and wide a choice of books as possible -- rather than promoting _our_ holdings specifically.

We encouraged them to start at [WorldCat](http://www.worldcat.org) to browse and search -- and our job would be to get them their chosen books with no more effort on their part.

We repurposed the WorldCat openUrl link-resolver to take a patron to a landing page under our control. (Now openUrls reach the landing page from numerous sources.) If the requested item is a book which is not available locally, it goes into an [easyBorrow](http://library.brown.edu/borrowing/easyBorrow.php) flow. This code manages that flow. The basic overview is that this code:
- checks to see if a new request exists, and if so
- attempts to request the book on behalf of the patron from a series of consortial library-borrowing partners (currently inRhode and BorrowDirect)
- if none of the attempts succeeds, the book request is auto-submitted to our ILLiad interlibrary-loan service
- then an email is sent to the patron, letting her know the book is on its way, along with contact and transaction numbers

Each book-borrowing service has its own code-base (links will be added here); this code manages the calls to the other book-borrowing services and the final email to the user.

code contact: birkin_diana@brown.edu


#### qualifier ####

This code is in production, _but_...
- some is ancient (before json was a part of the standard python library!)
- it was one of the programmer's first python projects (originally written in java)
- lots of code is unused either because it's old and some upgraded code has _mostly_ replaced it, or because some is upgraded code not yet used
- it uses a bunch of different settings and module architectures because of the fits and starts of improvements over ten years

In short, it needs work. It hasn't been upgraded much over the years partly due to stability, and because complete rewrites have been started a few times but never prioritized. This move to github should make improvements easier.


#### License ####

The MIT License (MIT)

Copyright (c) 2015 Brown University Library

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---
