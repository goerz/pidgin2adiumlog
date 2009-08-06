#!/usr/bin/python

import sys
import re
import os
import codecs
from xml.sax.saxutils import escape

outdir = '.'
myalias = ""

fn_pattern = re.compile(
    r'''(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})\.
        (?P<hour>[0-9]{2})(?P<minute>[0-9]{2})(?P<second>[0-9]{2})
        (?P<offset>[+-][0-9]{4})
        (?P<timezone>[A-Z]{2,4})\.txt''', re.X)
firstline_pattern = re.compile(
    r'''Conversation \s+ with \s+ (?P<contactname>.*) \s+
        at \s+ (?P<weekday>[A-Z][a-z]{2}) \s+ [0-9]{2} \s+
        [A-Za-z]+ \s+ [0-9]{4} \s+ [0-9]{2}:[0-9]{2}:[0-9]{2} \s+
        [A-Z ]+ \s+ on \s+
        (?P<myname>[^/]+)(/(?P<resource>[^()]+))? \s+
        \((?P<protocol>[^()]+)\)''', re.X)
msgline_pattern = re.compile(
    r'''\((?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2}])
        ([ ](?P<am_pm>AM|PM))?\)[ ](?P<nickname>[^:]+):[ ]
        (?P<message>.*)''', re.X)
statuschange_pattern = re.compile(
    r'''\((?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2}])
        ([ ](?P<am_pm>AM|PM))?\)[ ](?P<nickname>[^:]+)[ ]
        (?P<change>has[ ]gone.*|is[ ]no[ ]longer.*)''', re.X)

def add_adium_logline():
    if message != '':
        adium_logfh.write('<message sender="xxx@xxx.com" ')
        adium_logfh.write('time="%s-%s-%sT%s:%s:%s%s" ' % (
                          fn_match.group("year"),
                          fn_match.group("month"),
                          fn_match.group("day"),
                          msgline_match.group("hour"),
                          msgline_match.group("minute"),
                          fn_match.group("offset")))
        adium_logfh.write('alias="%s">' % msgline_match.group("nickname"))
        adium_logfh.write('%s</message>' % msgline_match.group("message"))
        adium_logfh.write("\n")


pidgin_logfile = sys.argv[1]
fn_match = fn_pattern.search(pidgin_logfile)
message = u''
if fn_match:
    pidgin_logfh = open(pidgin_logfile)
    firstline = pidgin_logfh.readline() 
    firstline_match = firstline_pattern.search(firstline)
    if firstline_match:
        adium_logfile = "%s (%s-%s-%sT%s.%s.%s%s).xml" % (
                        firstline_match.group("contactname"),
                        fn_match.group("year"),
                        fn_match.group("month"),
                        fn_match.group("hour"),
                        fn_match.group("minute"),
                        fn_match.group("second"),
                        fn_match.group("offset"))
        adium_logfolder = adium_logfile.replace(".xml", ".chatlog")
        os.mkdir(adium_logfolder)
        adium_logfh = codecs.open("%s/%s" %(adium_logfolder, adium_logfile), 
                                   "w", "utf-8")
        print >>adium_logfh, r'<?xml version="1.0" encoding="UTF-8" ?>'
        adium_logfh.write('<chat xmlns="http://purl.org/net/ulf/ns/0.4-02" ')
        adium_logfh.write('account="%s" ' % firstline_match.group("myname"))
        adium_logfh.write('service="%s">'% firstline_match.group("protocol"))
        adium_logfh.write("\n")
        for line in pidgin_logfh:
            statuschange_match = statuschange_pattern.search(line)
            if statuschange_match:
                continue
            msgline_match = msgline_pattern.search(line)
            if msgline_match:
                if message != '':
                    add_adium_logline()
                message = msgline_match.group('message')
            else:
                message += line
        add_adium_logline()
    else:
        print >>sys.stderr, "First line did not match"
    pidgin_logfh.close()
else:
    print >>sys.stderr, "Filename did not match"

