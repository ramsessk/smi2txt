#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''

2012.12.02
Process Sequence
1. convert all smi at current directory to srt
2. convert all srt at current directory to txt
3. Concatenate all txt files at current directory
4. Delete temp files 

Converted srt file is UTF-8
Converted txt file is UTF-8


Started : 2012/11/20
license: GPL

@version: 1.1.0
@author: steven <ramsessk@gmail.com>

SMI have this format!
===============================================================================

SRT have this format!
===============================================================================
1
00:00:12,000 --> 00:00:15,123
This is the first subtitle

2
00:00:16,000 --> 00:00:18,000
Another subtitle demonstrating tags:
<b>bold</b>, <i>italic</i>, <u>underlined</u>
<font color="#ff0000">red text</font>

3
00:00:20,000 --> 00:00:22,000  X1:40 X2:600 Y1:20 Y2:50
Another subtitle demonstrating position.
'''
__author__ = "steven <mcchae@gmail.com>"
__date__ = "2014/02/15"
__version__ = "1.2.1"
__version_info__ = (1, 2, 1)
__license__ = "GCQVista's NDA"

import os
import sys
import re
from operator import itemgetter, attrgetter #@UnusedImport
import logging
try:
    import chardet
except:
    print '''chardet python package not found. Please install it using
macports or pip'''
    sys.exit()
import codecs


logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#------------------------------------------------------------------------------
#
#            SMI to SRT
#
#------------------------------------------------------------------------------
class smiItem(object):
    ''' smiItem class
    convert smi to srt format.
    '''
    def __init__(self):
        self.start_ms = 0L
        self.start_ts = '00:00:00,000'
        self.end_ms = 0L
        self.end_ts = '00:00:00,000'
        self.contents = None
        self.linecount = 0
    @staticmethod
    def ms2ts(ms):
        hours = ms / 3600000L
        ms -= hours * 3600000L
        minutes = ms / 60000L
        ms -= minutes * 60000L
        seconds = ms / 1000L
        ms -= seconds * 1000L
        s = '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, ms)
        return s
    def convertSrt(self):
        if self.linecount == 4:
            i=1 #@UnusedVariable
        # 1) convert timestamp
        self.start_ts = smiItem.ms2ts(self.start_ms)
        self.end_ts = smiItem.ms2ts(self.end_ms-10)
        # 2) remove new-line
        self.contents = re.sub(r'\s+', ' ', self.contents)
        # 3) remove web string like "&nbsp";
        self.contents = re.sub(r'&[a-z]{2,5};', '', self.contents)
        # 4) replace "<br>" with '\n';
        self.contents = re.sub(r'(<br>)+', '\n', self.contents, \
                            flags=re.IGNORECASE)
        # 5) find all tags
        fndx = self.contents.find('<')
        if fndx >= 0:
            contents = self.contents
            sb = self.contents[0:fndx]
            contents = contents[fndx:]
            while True:
                m = re.match(r'</?([a-z]+)[^>]*>([^<>]*)', contents, \
                            flags=re.IGNORECASE)
                if m == None: break
                contents = contents[m.end(2):]
                #if m.group(1).lower() in ['font', 'b', 'i', 'u']:
                if m.group(1).lower() in ['b', 'i', 'u']:
                    sb += m.string[0:m.start(2)]
                sb += m.group(2)
            self.contents = sb
        self.contents = self.contents.strip()
        self.contents = self.contents.strip('\n')
    def __repr__(self):
        s = '%d:%d:<%s>:%d' % (self.start_ms, self.end_ms, self.contents, \
                            self.linecount)
        return s

#------------------------------------------------------------------------------
def convertSMI(smi_file, encoding):
    ''' convert smi file to srt format with encoding provided.
    '''
    if not os.path.exists(smi_file):
        logger.error('Cannot find smi file {0}\n'.format(smi_file))
        return False
    rndx = smi_file.rfind('.')
    srt_file = '%s.srt' % smi_file[0:rndx]

    ifp = open(smi_file)
    smi_sgml = ifp.read()#.upper()
    ifp.close()
    if encoding == "":
        chdt = chardet.detect(smi_sgml)
        logger.info("{0} encoding is {1}".format(smi_file, chdt['encoding']))
        if chdt['encoding'] != 'UTF-8':
            try:
                smi_sgml = unicode(smi_sgml, chdt['encoding'].lower())
            except:
                logger.error("Error : unicode(smi_sgml, chdt) in {0}".\
                            format(smi_file))
                return False
    else:
        chdt = encoding
        logger.info("{0} encoding is {1}".format(smi_file, encoding))
        if chdt != 'UTF-8':
            try:
                smi_sgml = unicode(smi_sgml, chdt)
            except:
                logger.error("Error : unicode(smi_sgml, chdt) in {0}".\
                            format(smi_file))
                return False
        
            
    # skip to first starting tag (skip first 0xff 0xfe ...)
    try:
        fndx = smi_sgml.find('<SYNC')
    except Exception, e:
        logger.debug(chdt)
        raise e
    if fndx < 0:
        logger.error("No <SYNC string found, maybe it is not smi file")
        return False
    smi_sgml = smi_sgml[fndx:]
    lines = smi_sgml.split('\n')
    
    srt_list = []
    sync_cont = ''
    si = None
    last_si = None
    linecnt = 0
    for line in lines:
        linecnt += 1
        #logger.debug(linecnt, line)
        line = line.encode('UTF-8')
        sndx = line.upper().find('<SYNC')
        if sndx >= 0:
            m = re.search(r'<sync\s+start\s*=\s*(\d+)>(.*)$', line, \
                        flags=re.IGNORECASE)
            if not m:
                logger.error('Invalid format tag of <Sync start=nnnn> with \
                {0}'.format(line))
                continue        # ignore the wrong format line
                #return False
            sync_cont += line[0:sndx]
            last_si = si
            if last_si != None:
                last_si.end_ms = long(m.group(1))
                last_si.contents = sync_cont
                srt_list.append(last_si)
                last_si.linecount = linecnt
            sync_cont = m.group(2)
            si = smiItem()
            si.start_ms = long(m.group(1))
        else:
            sync_cont += line
            
    ofp = open(srt_file, 'w')
    ndx = 1
    for si in srt_list:
        si.convertSrt()
        if si.contents == None or len(si.contents) <= 0:
            continue
        #logger.debug(si)
        sistr = '%d\n%s --> %s\n%s\n\n' % (ndx, si.start_ts, si.end_ts, \
                                        si.contents)
        ofp.write(sistr)
        #logger.debug(sistr)
        ndx += 1
    ofp.close()
    return True

#------------------------------------------------------------------------------
def doBatchSmi2SrtConvert(enc=""):
    '''
    batch job for coverting smi files to srt in the current directory.
    '''
    files = []
    dirs = os.listdir('./')
    for s in dirs:
        if s[-4:] == '.smi':
            logger.info("Found:{0}".format(s))
            files.append(s)

    for s in files:
        if convertSMI(s, enc):
            logger.info("Conversion done : {0}".format(s))
        else:
            logger.info("Conversion fail : {0}".format(s))


#------------------------------------------------------------------------------
#
#    subtitles = [ ['1', '00:00 --> 00:00', 'abcdef'], \
#                  ['2', '00:01 --> 00:01', 'erqwer'], ....
#
#------------------------------------------------------------------------------
def AnalysisSrt (lines, enc) :
    ''' Analysis subtiles for sorting
    '''
    logger.info('Analysis file ...')
    subtitle = []
    subtitles = []
    n = 0
    num_of_subtitles = 0
    new_line_started = True
    for line in lines:
        line.lstrip()
        line = line.replace('\r\n','\n')
        line = line.decode(enc)
        #print len(line), line,
        if len(line) > 1 :
            new_line_started = True
        elif len(line) == 1:
            new_line_started = False
            subtitles.append(subtitle)
            num_of_subtitles = num_of_subtitles +1
            #print num_of_subtitles, subtitle[0]
            #print subtitle
            subtitle = []
        if new_line_started :
            subtitle.append(line)
        
        n = n+1
    #    if num_of_subtitles > 20:
    #        break
    logger.info("{0} subtitles".format(len(subtitles)))
    
    return subtitles

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def main():
    if len(sys.argv) <= 1:
        usage_smi2txt()

    if sys.argv[1].upper() == 'CHAR_CONV':
        print "Converting files encoding to UTF8 ..."
        doBatchEncoding()
    elif sys.argv[1].upper() == 'SRT_ONLY':
        print "Converting SMI files in current directory to SRT ..."
        doBatchSmi2SrtConvert()
    else:
        print "1. Converting SMI files in current directory to SRT ..."
        doBatchSmi2SrtConvert()
        print "2. Converting SRT files in current directory to TXT ..."
        doSrt2Txt('utf-8')
        print "3. Concatenating text files"
        if sys.argv[1][-4:].upper() != '.TXT':
            output = sys.argv[1] + '.txt'
        else:
            output = sys.argv[1]
        ConcatenateTxtFiles(output)
        print "4. Deleting temporary files"
        DeleteIntermediateFiles()    

#------------------------------------------------------------------------------
if __name__ == '__main__':
    logger.basicConfig(level=logging.INFO)
    main()
