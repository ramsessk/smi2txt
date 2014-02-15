README
======

smi2txt.py
Convert multiple smi files to single txt file. (for eBook)
This will detect charset automatically and conver it to UTF-8.
Only smi files in current directory will be converted to txt file.
This will include smi2srt conversion as well. srt file will be located same 
directory.
if 'srt_only' option provided then it will convert only smi to srt.
This require chardet python package. (macports or pip)

Project location: https://github.com/ramsessk/smi2txt.git


srts_2_srt.py
srt which have multiple language subtitles(ex:english+korean), it will be 
separated with individual language srt files(english and korean srt file).
If srt file is xxx.srt then generated files will be xxx_1.srt, xxx_2.srt, ....
This will be useful for encoding avi to mp4 with mutiple languages subtitles.