README
======================

smi2txt.py
Convert smi files to single txt file. (for eBook)
Only smi files in current directory will be converted to txt file.
This will include smi2srt conversion as well. srt file will be located same directory.

smi2srt.py
Convert all smi file[s] located at current directory to srt file[s].
This function has been included in smi2txt.py. Practically it is not need.
This was intermediate file for smi2txt.py

srt2txt.py
Convert smi files to txt files. NO concatenation.
This was intermediate file for smi2txt.py

srts_2_srt.py
srt which have multiple language subtitles(ex:english+korean), it will be separated 
with individual language srt files(english and korean srt file).
If srt file is xxx.srt then generated files will be xxx_1.srt, xxx_2.srt, ....
This will be useful for encoding avi to mp4 with mutiple languages subtitles.