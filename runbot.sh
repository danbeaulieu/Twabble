#!/bin/bash
# POSIX (maybe Bourne?)
 lockdir=~/webapps/django/Twabble/myscript.lock
 if mkdir "$lockdir"
 then
     echo >&2 "successfully acquired lock on $lockdir at $(date)"
     /usr/local/bin/python2.5 /home/daninma/webapps/django/Twabble/twabblebot.py
     echo >&2 "removing lock"
     # Remove lockdir when the script finishes, or when it receives a signal
     trap 'rm -rf "$lockdir"' 0    # remove directory when script finishes
     trap "exit 2" 1 2 3 15        # terminate script when receiving signal
     
     # Optionally create temporary files in this directory, because
     # they will be removed automatically:
     tmpfile=$lockdir/filelist

 else
     echo >&2 "cannot acquire lock, giving up on $lockdir"
     exit 0
 fi

