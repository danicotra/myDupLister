# myDupsLister

looks recursively for duplicate files on source directory (dir_A) that have a match on source directory itself or in repository directory (dir_B) keeping out of listing files that only have matches on repository directory itself.

Nothing much more to say here...

I needed a way to list duplicates files on a directory (A) that had to be found in the directory tree itself or on a matching repository directory (B) tree BUT I didn't want to list possible duplicates on the repository itself and... that's it!

The matching is based on files size + contents hashing.

Parameters let's you choose whether or not include 0 sized files in the matching (excluded by default) and which hashing library to use between CRC32 (default) and SHA256.
