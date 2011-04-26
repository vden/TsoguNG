#!/bin/sh

DBNAME="tsogung"
DBUSER="tsogung"

case "$1" in
    -c)
	createdb -E UTF8 -U $DBUSER $DBNAME
	echo "DB create"
	;;
    -d)
	dropdb $DBNAME
	echo "DB drop"
	;;
    -dc)
    	dropdb -U $DBUSER $DBNAME
	echo "DB drop"
    	createdb -E UTF8 -U $DBUSER $DBNAME
	echo "DB create"
	;;
    -u)
        createuser $DBUSER
	;;
    *)
	echo "usage: $0 {-c (create)|-d (drop)|-u (createuser)}"
esac
