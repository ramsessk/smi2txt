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
__version__ = "1.2.0"
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

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def usage_smi2txt(msg=None, exit_code=1):
	print_msg = """
usage: $python {0} [TxtFileName] [srt_only]
	version: {1}
	convert MULTIPLE smi files in current directory into ONE text file 
	which will have a 'TxtFileName' filename.
	This would detect encodings(EUC-KR, UTF-8) automactically and convert to
	UTF-8.
	If srt only need (convert smi to srt only), provide srt_only option.	
	
	Origin of smi2srt.py : by MoonChang Chae <mcchae@gmail.com>
	Modified by steven (ramsessk@gmail.com)
	Project location: https://github.com/ramsessk/smi2txt.git
	
	example : $python smi2txt.py spider_man
			  -> convert all smi files in CURRENT DIRECTORY and save those to
			  a spider_man.txt
			  
	          $python smi2txt.py srt_only
	          -> convert all smi files in CURRENT DIRECTORY to the srt file.
	          
	          $python smi2txt.py CHAR_CONV srt smi xxx 
	          -> convert all .srt, .smi and .xxx files in CURRENT DIRECTORY 
	          and SUB-DIRECTORIES to same file with UTF-8 encoding.
""".format(os.path.basename(sys.argv[0]), __version__)
	if msg:
		print_msg += '%s\n' % msg
	print print_msg
	sys.exit(exit_code)

#------------------------------------------------------------------------------
#
#			SMI to SRT
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
		logging.error('Cannot find smi file {0}\n'.format(smi_file))
		return False
	rndx = smi_file.rfind('.')
	srt_file = '%s.srt' % smi_file[0:rndx]

	ifp = open(smi_file)
	smi_sgml = ifp.read()#.upper()
	ifp.close()
	if encoding == "":
		chdt = chardet.detect(smi_sgml)
		logging.info("{0} encoding is {1}".format(smi_file, chdt['encoding']))
		if chdt['encoding'] != 'UTF-8':
			try:
				smi_sgml = unicode(smi_sgml, chdt['encoding'].lower())
			except:
				logging.error("Error : unicode(smi_sgml, chdt) in {0}".\
							format(smi_file))
				return False
	else:
		chdt = encoding
		logging.info("{0} encoding is {1}".format(smi_file, encoding))
		if chdt != 'UTF-8':
			try:
				smi_sgml = unicode(smi_sgml, chdt)
			except:
				logging.error("Error : unicode(smi_sgml, chdt) in {0}".\
							format(smi_file))
				return False
		
			
	# skip to first starting tag (skip first 0xff 0xfe ...)
	try:
		fndx = smi_sgml.find('<SYNC')
	except Exception, e:
		logging.debug(chdt)
		raise e
	if fndx < 0:
		logging.error("No <SYNC string found, maybe it is not smi file")
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
		#logging.debug(linecnt, line)
		line = line.encode('UTF-8')
		sndx = line.upper().find('<SYNC')
		if sndx >= 0:
			m = re.search(r'<sync\s+start\s*=\s*(\d+)>(.*)$', line, \
						flags=re.IGNORECASE)
			if not m:
				logging.error('Invalid format tag of <Sync start=nnnn> with \
				{0}'.format(line))
				continue		# ignore the wrong format line
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
		#logging.debug(si)
		sistr = '%d\n%s --> %s\n%s\n\n' % (ndx, si.start_ts, si.end_ts, \
										si.contents)
		ofp.write(sistr)
		#logging.debug(sistr)
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
			logging.info("Found:{0}".format(s))
			files.append(s)

	for s in files:
		if convertSMI(s, enc):
			logging.info("Conversion done : {0}".format(s))
		else:
			logging.info("Conversion fail : {0}".format(s))


#------------------------------------------------------------------------------
#
#			SRT to TXT
#
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def FindSrtFiles(extension=''):
	''' find srt files in the current directory
	'''
	filenames = []
	dirs = os.listdir('./')
	for s in dirs:
		if s[-4:] == extension:
			filenames.append(s)
			logging.info("Found {0}".format(s))
	return filenames
	
#------------------------------------------------------------------------------
def ReadSrtFile (fname):
	''' read srt files
	'''
	logging.info('Reading file {0}'.format(fname))
	with open(fname, 'r') as f:
		lines = f.readlines()
		count = len(lines)
	logging.info("{0} lines read".format(count))
	
	return lines
#------------------------------------------------------------------------------
#--------------------------------------------
#
#	subtitles = [ ['1', '00:00 --> 00:00', 'abcdef'], \
#				  ['2', '00:01 --> 00:01', 'erqwer'], ....
#
#------------------------------------------------------------------------------
def AnalysisSrt (lines, enc) :
	''' Analysis subtiles for sorting
	'''
	logging.info('Analysis file ...')
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
	logging.info("{0} subtitles".format(len(subtitles)))
	
	return subtitles

#------------------------------------------------------------------------------
def WriteTxtSubtitles(subtitles, fname):
	''' Write subtiles to text file
	'''
	sorted_subtitles = sorted(subtitles, key=itemgetter(1))
	fname = fname + '.txt'
	
	with open(fname, 'w') as f:
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
	
	logging.info("Written txt to {0}".format(fname))



#------------------------------------------------------------------------------
def doSrt2Txt(encode):
	'''write only subtiles to the text file. All time information to be
	eliminated.
	encode: text file encode
	'''
	enc = encode
	fnames = FindSrtFiles(extension='.srt')
	
	for src in fnames:
		logging.info("Start :{0}".format(src))
		
		lines = ReadSrtFile(src)
		subtitles = AnalysisSrt(lines, enc)
		sorted_subtitles = sorted(subtitles, key=itemgetter(1))
		WriteTxtSubtitles(sorted_subtitles, src)


#------------------------------------------------------------------------------
#
#			concatenate txt files
#
#------------------------------------------------------------------------------
def ConcatenateTxtFiles(fname):
	''' Concaternate txt files to fname.
	fname : extension should be .txt
	'''
	files = []
	dirs = os.listdir('./')
	n = 1
	with open(fname, 'w+') as wf:
		for s in dirs:
			if s[-4:].lower() == '.txt' and s != fname:
				logging.info("Fond txt file: {0}".format(s))
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
				wf.write(l)

def DeleteIntermediateFiles():
	''' delete temporay files
	'''
	os.system('rm *.srt.txt')


#------------------------------------------------------------------------------
def doBatchEncoding():
	''' convert file encoding to UTF-8.
    Seaching current directory and subdirectory recursively
    '''

	extensions = []
	jobs = []
	i = 2
	while i < len(sys.argv):
		extensions.append(sys.argv[i])
		i = i + 1

	if len(extensions) == 0:
		logging.error("No extensions provided")
		sys.exit(1)

	logging.info("extensions to find = {0}".format(extensions))

	# finding list of file which have extension requested and which encoding
	# is not utf-8
	cwd = os.getcwd()
	for root, _, files in os.walk(".", topdown=False, followlinks=False):
		for name in files:
			if len(root) > 1:
				fname = os.path.join(cwd, root[2:], name)
			else:
				fname = os.path.join(cwd, name)
			rndx = fname.rfind('.')
			if rndx > 0 and fname[rndx+1:] in extensions:
				logging.info("checking: {0}".format(name))
				with open(fname) as f:
					lines = f.read()
				chdt = chardet.detect(lines)
				if chdt['encoding'] != None and \
					chdt['encoding'].upper() != 'UTF-8' and \
					chdt['encoding'].upper() != 'ASCII':
						tmp = (fname, chdt['encoding'])
						logging.info('Found = {0}, encoding={1}'.format(\
									tmp[0], tmp[1]))
						jobs.append(tmp)

	# convert encoding ...
	print "Starting conversion ..."
	if len(jobs) == 0:
		logging.info("There is no file to convert")
		return
	
	for job in jobs:
		logging.info("Converting file {0}, {1}".format(job[0], job[1]))
		with open(job[0]) as f:
			lines = f.read()
		ofname = job[0] + '.tmp'
		converted = unicode(lines, job[1])
		with codecs.open(ofname, 'w+', 'utf-8') as f:
			try:
				f.write(converted)
				logging.info("writing to {0}".format(ofname))
			except BaseException as e:
				logging.error("***Error occured during writing file {0}, {1}".\
							format(ofname, str(e)))
				return
			# change the file name
			bk_name = job[0] + '.bk.000'
			while os.path.exists(bk_name):
				n = bk_name.rfind('.')
				num = int(bk_name[n+1:])
				num = num + 1
				bk_name = job[0] + '.bk.' + "{0:#03d}".format(num)
			
			cmd = 'cp ' + '\"' + job[0] + '\"' +  ' ' + '\"' + bk_name + '\"'
			logging.info("executing: {0}".format(cmd))
			os.system(cmd)
			
			cmd = 'mv ' + '\"' + ofname + '\"' + ' ' + '\"' + ofname[:-4] + '\"'
			logging.info("executing: {0}".format(cmd))
			os.system(cmd)


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
	logging.basicConfig(level=logging.INFO)
	main()
