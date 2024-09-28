/* rexx */
Member = 'NAZARE.WDEPLOY.PYTHON.LOADLIB(LGACDB01)'
parse var Member dsname '(' mbrname ')' .
/* dsname    = libray to update   */
/* mbrname   = member to update   */
userid    = ""            /* "USER3"      Userid to be updated  */
crdate    = ""            /* "yyyy/mm/dd" PDS Created date      */
moddate   = ""            /* "yyyy/mm/dd" PDS Updated date      */
modtime   = ""            /* "hh:mm:ss"   PDS Updated time      */
version   = "1"           /* "1"          PDS Updated version   */
modelevel = "10"          /* "0"          PDS Updated modelevel */
if userid    <> "" then userid    = "USER("userid")"
if crdate    <> "" then crdate    = "CREATED4("crdate")"
if moddate   <> "" then moddate   = "MODDATE4("moddate")"
if modtime   <> "" then modtime   = "MODTIME("modtime")"
if version   <> "" then version   = "VERSION("version")"
if modelevel <> "" then modelevel = "MODLEVEL("modelevel")"
Address ispexec
  "LMINIT   DATAID("lmd1") DATASET('NAZARE.WDEPLOY.DBBBUILD.GENAPP.COBOL')"
  "LMMSTATS DATAID("lmd1") MEMBER(IBACSUM)",
     userid crdate moddate modtime version modelevel
  "LMFREE   DATAID("lmd1")"

Exit
