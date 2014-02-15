#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Started : 2012/11/20
license: GPL

@version: 1.0.0
@author: steven <ramsessk@gmail.com>

SMI have this format!
===================================================================================================

SRT have this format!
===================================================================================================
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
__date__ = "2012/11/24"
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__license__ = "GCQVista's NDA"

###################################################################################################
import os
import sys
import re
from operator import itemgetter, attrgetter

###################################################################################################
def usage(msg=None, exit_code=1):
	print_msg = """
usage %s Encoding smifile.smi [...]
	convert smi into srt subtitle file with same filename.
	By MoonChang Chae <mcchae@gmail.com>
""" % os.path.basename(sys.argv[0])
	if msg:
		print_msg += '%s\n' % msg
	print print_msg
	sys.exit(exit_code)

###################################################################################################
def usage_smi2txt(msg=None, exit_code=1):
	print_msg = """
usage %s Encoding TxtFileName
	convert smi files in current directory into ONE text file 
	which have 'TxtFileName'.
	You may have srt files as well.
	Origin of smi2srt.py : by MoonChang Chae <mcchae@gmail.com>
	By steven (ramsessk@gmail.com)
	
	Encoding : such as CP949, EUC_KR, UTF-8,...
	example : $python smi2txt.py cp949 spider_man
""" % os.path.basename(sys.argv[0])
	if msg:
		print_msg += '%s\n' % msg
	print print_msg
	sys.exit(exit_code)


###################################################################################################
#
#			SMI to SRT
#
###################################################################################################

###################################################################################################
class smiItem(object):
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
		self.contents = re.sub(r'(<br>)+', '\n', self.contents, flags=re.IGNORECASE)
		# 5) find all tags
		fndx = self.contents.find('<')
		if fndx >= 0:
			contents = self.contents
			sb = self.contents[0:fndx]
			contents = contents[fndx:]
			while True:
				m = re.match(r'</?([a-z]+)[^>]*>([^<>]*)', contents, flags=re.IGNORECASE)
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
		s = '%d:%d:<%s>:%d' % (self.start_ms, self.end_ms, self.contents, self.linecount)
		return s

###################################################################################################
def convertSMI(smi_file, encoding):
	if not os.path.exists(smi_file):
		sys.stderr.write('Cannot find smi file <%s>\n' % smi_file)
		return False
	rndx = smi_file.rfind('.')
	srt_file = '%s.srt' % smi_file[0:rndx]

	ifp = open(smi_file)
	smi_sgml = ifp.read()#.upper()
	ifp.close()
	chdt = encoding # chardet.detect(smi_sgml)
	#if chdt['encoding'] != 'UTF-8':
	if chdt != 'utf-8':
		try:
			smi_sgml = unicode(smi_sgml, chdt) # chdt['encoding'].lower()).encode('iso-8859-1') #'utf-8')
		except:
			print "Error : unicode(smi_sgml, chdt) ", smi_file
			return False
			
	#print smi_sgml
	# skip to first starting tag (skip first 0xff 0xfe ...)
	try:
		fndx = smi_sgml.find('<SYNC')
	except Exception, e:
		print chdt
		raise e
	if fndx < 0:
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
		line = line.encode('UTF-8')
		#print linecnt, line
		sndx = line.upper().find('<SYNC')
		if sndx >= 0:
			m = re.search(r'<sync\s+start\s*=\s*(\d+)>(.*)$', line, flags=re.IGNORECASE)
			if not m:
				#raise Exception('Invalid format tag of <Sync start=nnnn> with "%s"' % line)
				print 'Invalid format tag of <Sync start=nnnn> with "%s"' % line
				return False
			sync_cont += line[0:sndx]
			last_si = si
			if last_si != None:
				last_si.end_ms = long(m.group(1))
				last_si.contents = sync_cont
				srt_list.append(last_si)
				last_si.linecount = linecnt
				#print '[%06d] %s' % (linecnt, last_si)
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
		#print si
		sistr = '%d\n%s --> %s\n%s\n\n' % (ndx, si.start_ts, si.end_ts, si.contents)
		#sistr = unicode(sistr, 'utf-8').encode('euc-kr')
		ofp.write(sistr)
		#print sistr,
		ndx += 1
	ofp.close()
	return True

###################################################################################################
def doBatchSmi2SrtConvert(enc):
	files = []
	dirs = os.listdir('./')
	for s in dirs:
		#print "s=", s, s[-4:]
		if s[-4:] == '.smi':
			print "found:", s
			files.append(s)

	for s in files:
		if convertSMI(s, enc):
			print "Conversion done :", s
		else:
			print "Conversion fail :", s


###################################################################################################
#
#			SRT to TXT
#
###################################################################################################

###################################################################################################
def FindSrtFiles():
	filenames = []
	dirs = os.listdir('./')
	for s in dirs:
		if s[-4:] == '.srt':
			filenames.append(s)
	return filenames
	
###################################################################################################
def ReadSrtFile (fname):
	print 'Reading file ...'
	f = open(fname, 'r')
	count = 0
	lines = f.readlines()
	count = len(lines)
	f.close()
	print count, " lines"
	return lines
###################################################################################################
#--------------------------------------------
#
#	subtitles = [ ['1', '00:00 --> 00:00', 'abcdef'], ['2', '00:01 --> 00:01', 'erqwer'], ....
#
###################################################################################################
def AnalysisSrt (lines, enc) :
	print 'Analysis file ...'
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
	#	if num_of_subtitles > 20:
	#		break
	print len(subtitles), 'subtiles'
	return subtitles


###################################################################################################
#--------------------------------------------
def SortSubtitles( subtitles ):
	subtitles = sorted(subtitles, key=itemgetter(1))
	
#	for t in subtitles:
#		for s in t:
#			print s, 
	return subtitles


###################################################################################################
def PrintSubtitles(subtitles):
	
	n = 1
	for title in subtitles:
		items = 0
		for s in title:
			if items == 0:
				#print n
				n = n
			elif items == 1:
				n = n
			else:
				print s,
			items = items + 1
		n = n + 1

###################################################################################################
def WriteTxtSubtitles(subtitles, fname):

	sorted_subtitles = SortSubtitles(subtitles)
	fname = fname + '.txt'
	f = open(fname, 'w')
	n = 1
	for title in sorted_subtitles:
		items = 0
		for s in title:
			if items == 0:
				#print n
				n = n
			elif items == 1:
				n = n
			else:
				#print s,
				f.write(s.encode('utf-8'))
			items = items + 1
		n = n + 1
	
	print "Written txt to ", fname



###################################################################################################
def doSrt2Txt(encode):

	enc = encode
	fnames = FindSrtFiles()
	for s in fnames:
		print s
	
	for src in fnames:
		print "--------------------------------"
		print "start :", src
		
		#dest = src
		lines = ReadSrtFile(src)
		subtitles = AnalysisSrt(lines, enc)
		sorted_subtitles = SortSubtitles(subtitles)	
		#PrintSubtitles(sorted_subtitles)
		WriteTxtSubtitles(sorted_subtitles, src)


###################################################################################################
#
#			concatenate txt files
#
###################################################################################################
def ConcatenateTxtFiles(fname):
	files = []

	dirs = os.listdir('./')
	n = 1
	wf = open(fname, 'w+')
	for s in dirs:
		#print "s=", s, s[-4:]
		if s[-4:] == '.txt':
			#print s
			ss = str(n) + '. ' + s
			wf.write(ss)
			wf.write('\n')
			files.append(s)
			n = n+1
	wf.write('\n\n\n\n')
	
	for s in files:
		wf.write("==========================================\n")
		wf.write(s)
		wf.write('\n')
		wf.write("==========================================\n")
		rf = open(s, "r")
		lines = rf.readlines()
		rf.close()
		for l in lines:
			#print l
			wf.write(l)
	
	wf.close()


def DeleteIntermediateFiles():
	os.system('rm *.srt.txt')

###################################################################################################
def main():
	#if len(sys.argv) <= 2:
	#	usage_smi2txt()
	print "Converting SMI to SRT"
	doBatchSmi2SrtConvert('UTF-8') #sys.argv[1])
#	print "Converting SRT to TXT"
#	doSrt2Txt('utf-8')
#	print "Concatenation of text files"
#	ConcatenateTxtFiles(sys.argv[2])
#	print "Deleting temporary files"
#	DeleteIntermediateFiles()	

###################################################################################################
if __name__ == '__main__':
	main()