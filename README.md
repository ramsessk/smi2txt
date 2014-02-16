README
------

**smi2txt.py**

####1. Convert multiple smi files to the SINGLE txt file to make a ebook.

- This will detect charset automatically and conver it to UTF-8.
- Only smi files in CURRENT DIRECTORY will be converted to txt file.
- This will include smi2srt conversion as well. srt file will be located same 
directory.
- example:

    $python smi2txt.py spider_man  
    convert all smi files in CURRENT DIRECTORY and save those to
    a spider_man.txt

####2. Convert smi files to srt in current directory.

- This will detect charset automatically and conver it to UTF-8.
- Only smi files in CURRENT DIRECTORY will be converted to srt file.
- example:

     $python smi2txt.py srt_only  
	 convert all smi files in CURRENT DIRECTORY to the srt file.

####3. Convert encoding of specified text files to UTF-8

- This will detect charset automatically and conver it to UTF-8.
- All files in CURRENT and SUB-DIRECTORIES will be converted.
- User to specify file extension to be convereted
- example:

    $python smi2txt.py CHAR_CONV srt smi xxx   
	convert all .srt, .smi and .xxx files in CURRENT DIRECTORY 
	and SUB-DIRECTORIES to same file with UTF-8 encoding.


Project location:

https://github.com/ramsessk/smi2txt.git

