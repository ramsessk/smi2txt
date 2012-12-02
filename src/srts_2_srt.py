# -*- coding: utf-8 -*-

'''
2012.12.02

srt which have multiple language subtitles(ex:english+korean), it will be separated 
with individual language srt files(english and korean srt file).
If srt file is xxx.srt then generated files will be xxx_1.srt, xxx_2.srt, ....

usage : $python srts_2_srt.py encoding <ENTER>
	encoding : utf-8, cp949

By steven <ramsessk@gmail.com>

'''


#import time
import os, sys
from operator import itemgetter, attrgetter


def FindSrtFiles():
	filenames = []
	dirs = os.listdir('./')
	for s in dirs:
		#print "s=", s, s[-4:]
		if s[-4:] == '.srt':
			print "found:", s
			filenames.append(s[0:-4])
	return filenames

###################################################################################################
def ReadSrtFile (fname):
	print 'Reading file ...'
	fname = fname + '.srt'
	f = open(fname, 'r')
	count = 0
	lines = f.readlines()
	count = len(lines)
	f.close()
	print count, " lines"
	return lines
###################################################################################################
#	subtitles = [ ['1', '00:00 --> 00:00', 'abcdef'], ['2', '00:01 --> 00:01', 'erqwer'], ....

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
			subtitle = []
		if new_line_started :
			subtitle.append(line)
		n = n+1
	#	if num_of_subtitles > 20:
	#		break
	print len(subtitles), 'subtiles'
	return subtitles

###################################################################################################
# Find out whether this subtitles is multiple language subtitles.
def isMultipleLanguageSubtitle( subtitles ):
	prev_stime = 0
	eng_title_started = 0
	for title in subtitles:
		#print title
		tstamp_str = title[1]
		#print tstamp_str
		tstamp_str = tstamp_str.replace(':',' ')
		tstamp_str = tstamp_str.replace(',', ' ')
		tstamp_str = tstamp_str.replace(' --> ', ' ')
		tstamp_str = tstamp_str.split(' ')
		tstamp = []
		for s in tstamp_str:
			tstamp.append(int(s))
		stime = tstamp[0]*24 + tstamp[1]*60 + tstamp[2]
		#print stime, tstamp
		if( stime < prev_stime ) :
			break
		prev_stime = stime
		eng_title_started = eng_title_started + 1
	if eng_title_started == len(subtitles):
		eng_title_started = 1;
		return False
	return True;


###################################################################################################
#	subtitles = [ ['1', '00:00 --> 00:00', 'abcdef'], ['2', '00:01 --> 00:01', 'erqwer'], ....
#	subtitles[0] = ['1', '00:00 --> 00:00', 'abcdef']
#
def WriteNewSrtFiles(fname, subtitles):
	print 'writing to file...'
	
	if isMultipleLanguageSubtitle(subtitles) == False:
		print "Nothing to do"
		return 0
	
	num_of_lang = 1
	wfname = fname + '_' + str(num_of_lang) + '.srt'
	f = open(wfname, 'w')
	n = 1
	line_no = 1
	prev_stime = 0
	for title in subtitles:
		#	title = ['1', '00:00 --> 00:00', 'abcdef']
		#print title
		tstamp_str = title[1]
		#print tstamp_str
		tstamp_str = tstamp_str.replace(':',' ')
		tstamp_str = tstamp_str.replace(',', ' ')
		tstamp_str = tstamp_str.replace(' --> ', ' ')
		tstamp_str = tstamp_str.split(' ')
		tstamp = []
		for s in tstamp_str:
			tstamp.append(int(s))
		stime = tstamp[0]*24 + tstamp[1]*60 + tstamp[2]
		#print stime, tstamp

		if( stime < prev_stime ) :
			f.close()
			# start new language subtitle
			num_of_lang = num_of_lang + 1
			wfname = fname + '_' + str(num_of_lang) + '.srt'
			f = open(wfname, 'w')
			line_no = 1
			prev_stime = 0
			stime = 0
		else:
			#st = subtitles[n]
			title[0] = str(line_no)+'\n'
			for s in title:
				f.write(s.encode('utf-8'))
				#print s,
			f.write('\n'.encode('utf-8'))
			line_no = line_no + 1
		
		prev_stime = stime
		if( n >= len(subtitles)): # last line 
			f.close()
			break
		n = n + 1

###################################################################################################
def CopyBackup(src):
	destfile = src + '.old'
	while os.path.exists(destfile):
		destfile = destfile + '.old'
		if( len(destfile) > 256 ):
			print "cannot make backup file..too long filename"
			return;

	cmd = 'cp ' + src + ' ' + destfile
	os.system(cmd)

###################################################################################################
def doSeparateSrt(enc):
	fnames = FindSrtFiles()
	for s in fnames:
		print s

	for src in fnames:
		print "--------------------------------"
		print "start :", src
	
		dest = src
		lines = ReadSrtFile(src)
		subtitles = AnalysisSrt(lines, enc)
		print "Writing files ..."
		#CopyBackup(src)
		WriteNewSrtFiles(dest, subtitles)

###################################################################################################
def usage(msg=None, exit_code=1):
	print_msg = """
	usage %s encoding
	convert current directory srt file which have multiple langes data to individual srt files
	By steven <ramsessk@gmail.com>
""" % os.path.basename(sys.argv[0])
	if msg:
		print_msg += '%s\n' % msg
	print print_msg
	sys.exit(exit_code)

###################################################################################################
def main():
	if len(sys.argv) <= 1:
		usage()
	print "Converting SRTs to SRT. All srt files in current directory will be converted"
	doSeparateSrt(sys.argv[1])

###################################################################################################
if __name__ == '__main__':
	main()