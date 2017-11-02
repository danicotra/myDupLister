#!/usr/bin/env python

#This script originates from the need to give an answer to this question on SoftwareRecs:
#https://softwarerecs.stackexchange.com/questions/45293/check-for-folder-subfolders-duplicates-in-another-folder-subfolder-but-not-check
#Credit goes to Kodiologist for having deeply inspired and motivated me with his answer: https://softwarerecs.stackexchange.com/a/45316
#(this script is based on his code)

#This uses scandir and requires Python >= 3.5

from os import scandir, path
from time import ctime
from datetime import datetime

class element_hashed(object):
    __slots__ = ('path', 'name', 'size', 'modate')
    def __repr__(self):
        return "<element_hashed path:%s name:%s size:%s lmdate:%s>" % (self.path, self.name, self.size, datetime.fromtimestamp(self.modate))
    def __str__(self):
        return "element_hashed: path is %s, name is %s, size is %s, last_mod_date is %s" % (self.path, self.name, self.size, ctime(self.modate))

#Source dir data structure:
#dict[files size&+#HASH key] -> dict[id_1...n] -> element_hashed('path', 'name', 'size', 'modate')

#Repository dir data structure:
#dict[files size&+#HASH key] -> dict[id_1...n] -> "a found item" # just a simple filler, this information isn't really important for the purpose

srcdir = 'A'
repdir = 'B'
zero_excluded = True
hashing_lib = 'CRC32'
dcount = 0

def hashes(topdir, repository=False):
    for entry in scandir(topdir):

        #I'm not going to follow symlinks, I want only "effective" files/directory
        #https://www.python.org/dev/peps/pep-0471/
        #there was basic consensus among the most involved participants, and this PEP's author [...] to warrant following symlinks by default
        #it's straightforward to call the relevant methods with follow_symlinks=False if the other behaviour is desired.

        if entry.is_dir(follow_symlinks=False):
            yield from hashes(entry.path)

        elif entry.is_file(follow_symlinks=False):
            size = path.getsize(entry.path)
            if size == 0 and zero_excluded: continue
            with open(entry.path, "rb") as o:
                if repository:
                    eh = "a found item"
                else:
                    eh = element_hashed()
                    eh.path = topdir
                    eh.name = entry.name
                    eh.size = size
                    eh.modate = path.getmtime(entry.path)
                yield eh, str(size) + "#" + (sha256(o.read()).hexdigest() if hashing_lib == "SHA256" else hex(crc32(o.read())))


if __name__ == '__main__':
    from argparse import ArgumentParser
    from argparse import RawDescriptionHelpFormatter
    parser = ArgumentParser(description='my dups lister\n'
    + 'looks for duplicate files on source directory (dir_A) that have a match on source directory itself or in repository directory (dir_B) keeping out of listing files that only have matches on repository directory itself', formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("aDir", metavar="dir_A", help="source_directory (relative paths may be used)")
    parser.add_argument("bDir", metavar="dir_B", help="repository_directory (relative paths may be used)")
    parser.add_argument("-0", dest="zero_included", default=False, action='store_true', help="do not exclude files whose size=0 (not taken in account by default)")
    parser.add_argument("-H", "--hash", dest="hashing_lib", metavar="LIBRARY", choices=["CRC32", "SHA256"], default="CRC32", type=str.upper, help="hashing mode: CRC32 (default) || SHA256")
    args = parser.parse_args()

    if not (path.isdir(args.aDir) and path.isdir(args.bDir)):
        parser.error("one or both non-existent directory!")

    if args.hashing_lib == "CRC32":
        from zlib import crc32
    elif args.hashing_lib == "SHA256":
        from hashlib import sha256
    else: #if args.hashing_lib not in ("CRC32", "SHA256"):
        parser.error("unsupported hashing library " + args.hashing_lib) # (this'll never be anyway 'cause argparse won't let it happen, so "pleonastic coding")

    srcdir = args.aDir
    repdir = args.bDir
    zero_excluded = not args.zero_included
    hashing_lib = args.hashing_lib

source_hashes = dict()

for eh, key in hashes(path.abspath(srcdir)): #use source absolute path always
    if not key in source_hashes:
        source_hashes[key] = dict()
    source_hashes[key][path.join(eh.path, eh.name)] = eh

for _, h in hashes(path.abspath(repdir), True): #use repository absolute path always
    if h in source_hashes: # found _ 1b|2b type _ dup. item
        if len(source_hashes[h]) > 1:
            for eh in source_hashes[h]:
                print("Type 2a dup. :=> ", eh)
                dcount += 1
        else:
            print("Type 1a dup. :=> ", next(iter(source_hashes[h])))
            dcount += 1
        source_hashes.pop(h, None)

#now the remainders are all the "srcdir" files that don't have any duplicate in "repdir" = unique ones + type 3a dupes. I'm only interested in the latter
for fn in source_hashes.values():
    if len(fn) > 1:
        for eh in fn:
            print("Type 3a dup. :=> ", eh)
            dcount += 1

print("\nFound ", dcount, " dupes")
