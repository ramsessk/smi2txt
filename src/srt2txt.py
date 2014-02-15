#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import time
import os, sys
from operator import itemgetter, attrgetter
#
# 
#


###############################################################################
def usage_srt2txt(msg=None, exit_code=1):
	print_msg = """
usage %s Encoding
	convert srt files in current directory into text(utf-8) files with same
	filename.
	By steven
	Encoding : such as CP949, EUC_KR, UTF-8,...
""" % os.path.basename(sys.argv[0])
	if msg:
		print_msg += '%s\n' % msg
	print print_msg
	sys.exit(exit_code)


###############################################################################
def FindSrtFiles():
	filenames = []
	dirs = os.listdir('./')
	for s in dirs:
		if s[-4:] == '.srt':
			filenames.append(s)
	return filenames
	
###############################################################################
def ReadSrtFile (fname):
	print 'Reading file ...'
	f = open(fname, 'r')
	count = 0
	lines = f.readlines()
	count = len(lines)
	f.close()
	print count, " lines"
	return lines
###############################################################################
#--------------------------------------------
#
#	subtitles = [ ['1', '00:00 --> 00:00', 'abcdef'], ['2', '00:01 --> 00:01', 'erqwer'], ....
#
###############################################################################
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


###############################################################################
#--------------------------------------------
def SortSubtitles( subtitles ):
	subtitles = sorted(subtitles, key=itemgetter(1))
	
#	for t in subtitles:
#		for s in t:
#			print s, 
	return subtitles


###############################################################################
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

###############################################################################
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



###############################################################################
def doSrt2Txt():

	enc = sys.argv[1]
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


###############################################################################
if __name__ == '__main__':
	if len(sys.argv) <= 1:
		usage_srt2txt()

	doSrt2Txt()
