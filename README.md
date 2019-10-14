# phototools
## Tools for managing my photo library

**Problem:**

It is often desirable to show photos taken during a trip in chronological
order. The problem is that many slideshow program display photos in the
lexical order by file name. This creates a problem when photos are taken
with multiple devices, even when such devices to time-synchronized.

**Solution:**

The solution is to prepend timestamp to the filename so that the
chronological and lexicographical order become the same.

**Implementation:**

This utility extracts the time when the photo was taken from the
EXIF metadata of the photo and renames the file by prepending the
timestamp in the "YYYYMMDDHHMMSS__" format to the filename.

