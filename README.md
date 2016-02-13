#### on this page... ####

- info/overview
- related code
- license


#### info/overview ####

In 2005 ago the [Library](http://library.brown.edu) made a decision to privilege giving patrons as deep and wide a choice of books as possible -- rather than promoting _our_ holdings specifically.

We encouraged them to start at [WorldCat](http://www.worldcat.org) to browse and search -- our job would be to get them their chosen books with no more effort on their part.

We repurposed the WorldCat [openUrl](https://en.wikipedia.org/wiki/OpenURL) link-resolver to take a patron to a landing page under our control. (Now openUrls reach the landing page from numerous sources.) If the requested item is a book which is not available locally, it goes into an [easyBorrow](http://library.brown.edu/borrowing/easyBorrow.php) flow. This code manages that flow. The basic overview is that this code:
- checks to see if a new request exists, and if so
- attempts to request the book on behalf of the patron from consortial library-borrowing partners
    - partners: originally [VirtualCatalog](http://www.massvc.org), [inRhode](http://inrhode.uri.edu) and [BorrowDirect](http://www.borrowdirect.org) -- now BorrowDirect
- auto-submits, if none of the attempts succeeds, the book request to our [ILLiad](http://www.atlas-sys.com/illiad/) interlibrary-loan service
- finally, sends an email to the patron, letting her know the book is on its way, along with contact and transaction numbers

Each book-borrowing service has its own code-base; this code manages the calls to the other book-borrowing services and the final email to the user.

code contact: birkin_diana@brown.edu


#### related code ####

- [borrowdirect.py](https://github.com/Brown-University-Library/borrowdirect.py)
    - a python module for working with the BorrowDirect API

- [bdpyweb_code](https://github.com/Brown-University-Library/bdpyweb_code)
    - a lightweight [Flask](http://flask.pocoo.org) webservice using the borrowdirect.py module -- this easyborrow code calls the webservice

- [illiad-client](https://github.com/Brown-University-Library/illiad-client)
    - a python module that allows automated submissions, and new-user registration to ILLiad

- [illiad_webservice](https://github.com/Brown-University-Library/illiad_webservice)
    - a [django](https://www.djangoproject.com) webservice using the illiad-client module -- this easyborrow code calls the webservice
s

#### license ####

The MIT License (MIT)

Copyright (c) 2016 Brown University Library

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---
