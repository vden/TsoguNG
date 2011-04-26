#-*- coding: utf-8 -*-

import urllib2, simplejson, urllib
BASE_URL = "http://app.tsogu.ru/shedule_new/bin/groups.py"

def get_group_code(gname):
	gname = urllib2.quote(gname.encode('utf-8'))
	r = urllib2.urlopen("%s?act=groupcode&groupname=%s"%(BASE_URL, gname)).read()
	return simplejson.loads(r)

def get_timetable(gcode):
	r = urllib2.urlopen("%s?act=json&sgroup=%s"%(BASE_URL, gcode)).read()
	return simplejson.loads(r)

def get_institutes():
	r = urllib2.urlopen("%s?act=json_institutes"%(BASE_URL)).read()
	return simplejson.loads(r)

def get_groups(id_inst):
	r = urllib2.urlopen("%s?act=json_groups&id_inst=%s"%(BASE_URL, id_inst)).read()
	return simplejson.loads(r)
