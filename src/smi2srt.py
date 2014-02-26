#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''

2014.2.25
Class for converting smi to srt including encoding.
It detect encoding of smi file and convert it to the user provided encoding.

Started : 2014/2/25
license: GPL

@version: 1.0.0
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
__version_info__ = (1, 0, 0)
__version__ = "{0}.{1}.{2}".format(__version_info__[0], __version_info__[1], \
                __version_info__[2])
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
#            SMI to SRT
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
class SMI2SRT(smiItem):
    '''
    Convert smi file to srt format with the provided encoding format.
   
    public attribute: 
    smi: smi file including .smi extension to be converted to srt format 
    encoding: encoding for srt file to be saved
    titles: srt file contents in UTF-8 even though srt file to be written
              might have the different encoding
    convereted: status of conversion
    '''
    def __init__(self, smi, encoding):
        self.smifile = smi
        self.encoding = encoding
        self.titles = []
        self.converted = False

    def convert_smi(self, srtfile=""):
        ''' convert smi file to srt format with encoding provided.
        Default srt file name is same as smi except extention which is .srt 
        
        return True or Flase
        '''
        if not self.smifile.lower().endswith('.smi'):
            logger.error("Not smi file:".format(self.smifile))
            return False
    
        if not os.path.exists(self.smifile):
            logger.error('Cannot find smi file {0}\n'.format(self.smifile))
            return False

        if srtfile == "":
            rndx = self.smifile.rfind('.')
            srt_file = '%s.srt' % self.smifile[0:rndx]
        else:
            srt_file = srtfile
    
        with open(self.smifile) as ifp:
            smi_sgml = ifp.read()
    
        chdt = chardet.detect(smi_sgml)
        logger.info("{0} encoding is {1} with condidence {2}". \
                format(self.smifile, chdt['encoding'], chdt['confidence']))
        if chdt['encoding'].lower() != 'utf-8':
            try:
                # smi_sgml with chdt['encoding'] --convert--> unicode
                smi_sgml = unicode(smi_sgml, chdt['encoding'].lower())
            except:
                logger.error("Error : unicode(smi_sgml, chdt) in {0}".\
                            format(self.smifile))
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
            
            #http://stackoverflow.com/questions/11339955/python-string-encode-decode
            # convert smi contents to utf-8 for re
            if chdt['encoding'].lower() != 'utf-8':
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
        
        # open file with required encoding        
        with codecs.open(srt_file, 'w', self.encoding) as ofp:
            ndx = 1
            for si in srt_list:
                si.convertSrt()
                if si.contents == None or len(si.contents) <= 0:
                    continue
                sistr = '%d\n%s --> %s\n%s\n\n' % (ndx, si.start_ts, \
                                        si.end_ts, si.contents)
                for s in sistr.strip().split('\n'):
                    self.titles.append(s)
                converted = unicode(sistr, 'UTF-8')
                ofp.write(converted)
                ndx += 1
            logger.info("Written file {0} in {1}".\
                        format(srt_file, self.encoding))
            self.converted = True
        return True

    def analysis_srt(self) :
        ''' Convert srt file to simplified list to use it easily.
        If smi is not converted srt yet, it will convert it first with
        default srt file name.
        
        list format to be returned would be:
        subtitles = [ ['1', '00:00 --> 00:00', 'hi steven'], 
                      ['2', '00:01 --> 00:01', 'Im' fine!], ....
        subtitles[0] = ['1', '00:00 --> 00:00', 'hi steven']
        
        if error, return empty list
        '''
        if not self.converted:
            logger.info("smi file {0} not yet converted to srt". \
                        format(self.smifile))
            if self.convert_smi(self.srtfile) == False:
                logger.error("Conversion error")
                return []

        logger.info("Analysis a srt file ...")
        subtitle = []
        subtitles = []
        new_subtitle = False
        #lines = self.contents.split('\n')
        for line in self.titles:
            line = line.strip()
            line += '\n'           
            if len(line) <= 1:      # consider '\n'
                continue
            isnumber = True
            try:
                int(line)
            except:
                isnumber = False
                pass
            
            if( len(line.split()) == 1 and new_subtitle == False and isnumber):
                new_subtitle = True
                if len(subtitle) > 0:
                    subtitles.append(subtitle)
                    subtitle = []
                subtitle.append(line)
            else:
                new_subtitle = False
                if len(line) >1:            # consider '\n'
                    subtitle.append(line)

        # save last one
        if len(subtitle) > 0:
            subtitles.append(subtitle)
        logger.info("{0} subtitles".format(len(subtitles)))

        return subtitles
   

#------------------------------------------------------------------------------
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) < 3:
        print ("Usage:")
        print ("$python smi2srt.py smifile encoding")
        sys.exit(1) 
    obj = SMI2SRT(smi=sys.argv[1], encoding=sys.argv[2])
    obj.convert_smi()
    st = obj.analysis_srt()
    print st[0]
    print st[0][2]
