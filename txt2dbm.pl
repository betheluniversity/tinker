#!/usr/bin/perl
##
##  txt2dbm -- convert txt map to dbm format
##

use SDBM_File;
use Fcntl;
($txtmap, $dbmmap) = @ARGV;
open(TXT, "<$txtmap") or die "Couldn't open $txtmap!\n";
tie (%DB, 'SDBM_File', $dbmmap,O_RDWR|O_TRUNC|O_CREAT, 0644)
  or die "Couldn't create $dbmmap!\n";
while (<TXT>) {
  next if (/^\s*#/ or /^\s*$/);
  $DB{$1} = $2 if (/^\s*(\S+)\s+(\S+)/);
}
untie %DB;
close(TXT);
exit(0);

use SDBM_File;
use Fcntl;

($txtmap, $dbmmap) = @ARGV;

open(TXT, "<$txtmap") or die "Couldn't open $txtmap!\n";
#tie (%DB, 'NDBM_File', $dbmmap,O_RDWR|O_TRUNC|O_CREAT, 0644)
#  or die "Couldn't create $dbmmap!\n";
dbmopen(%DB, $dbmmap, 0644);

while (<TXT>) {
  next if (/^\s*#/ or /^\s*$/);
  $DB{$1} = $2 if (/^\s*(\S+)\s+(\S+)/);
}

#untie %DB;
dbmclose(%DB);
close(TXT);#!/usr/bin/perl
##
##  txt2dbm -- convert txt map to dbm format
##

use SDBM_File;
use Fcntl;
($txtmap, $dbmmap) = @ARGV;
open(TXT, "<$txtmap") or die "Couldn't open $txtmap!\n";
tie (%DB, 'SDBM_File', $dbmmap,O_RDWR|O_TRUNC|O_CREAT, 0644)
  or die "Couldn't create $dbmmap!\n";
while (<TXT>) {
  next if (/^\s*#/ or /^\s*$/);
  $DB{$1} = $2 if (/^\s*(\S+)\s+(\S+)/);
}
untie %DB;
close(TXT);
exit(0);

use SDBM_File;
use Fcntl;

($txtmap, $dbmmap) = @ARGV;

open(TXT, "<$txtmap") or die "Couldn't open $txtmap!\n";
#tie (%DB, 'NDBM_File', $dbmmap,O_RDWR|O_TRUNC|O_CREAT, 0644)
#  or die "Couldn't create $dbmmap!\n";
dbmopen(%DB, $dbmmap, 0644);

while (<TXT>) {
  next if (/^\s*#/ or /^\s*$/);
  $DB{$1} = $2 if (/^\s*(\S+)\s+(\S+)/);
}

#untie %DB;
dbmclose(%DB);
close(TXT);
