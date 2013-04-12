#!/usr/bin/python

"""
This utility allows for the conversion of a P2G archive into an mp4 video file.
Two methods of usage:
1 - >python converter.py target_directory
where target directory is an unziped P2G archive
2 - >python converter.py
In usage 2, a prompt will allow the user to browse for the zip file

Script is only designed for use on Mac OS X.

Developed by Manan Mehta (manan309@gmail.com)
"""

import os
import re
import sys
import tkFileDialog

def getFirstBlock(xml, type, cast = str):
	opentag = '<%s>' % type
	closetag = '</%s>' % type
	intervals = zip([m.end() for m in re.finditer(opentag, xml)],[m.start() for m in re.finditer(closetag, xml)])
	x = intervals[0]
	return cast(xml[x[0]:x[1]].strip())

def getAllBlocks(xml, type, cast = str):
	opentag = '<%s>' % type
	closetag = '</%s>' % type
	intervals = zip([m.end() for m in re.finditer(opentag, xml)],[m.start() for m in re.finditer(closetag, xml)])
	return [cast(xml[x[0]:x[1]].strip()) for x in intervals]

def make_filelist(num, d):
	files = []
	for i in range(1,num+1):
		s = "%sslide_%04d_full.jpg" % (d,i)
		files.append(s)
	return files

def ms_to_ts(ms):
	return "%.3f" % (ms/1000.0)

def times_to_lengths(times,total_length):
	prev = 0
	l =  []
	for t in times:
		l.append(t-prev)
		prev = t
	l.append(total_length-times[-1])
	delay = l.pop(0)
	return ms_to_ts(delay), [ms_to_ts(i) for i in l]

def concat_jpgs(filenames):
	fid = open('filelist.txt','w')
	for file in filenames:
		nfile = file[0:-3] + 'mp4'
		s = "file \'%s\'\n" % nfile
		fid.write(s)
	fid.close()
	os.system("./ffmpeg -f concat -i filelist.txt -c copy video.mp4")
	for file in filenames:
		nfile = file[0:-3] + 'mp4'
		cmd = 'rm \'%s\'' % nfile
		os.system(cmd)
	os.system("rm filelist.txt")
def make_mp4_from_jpg(filename, length):
	outname = filename[0:-3]+'mp4'
	cmd = "./ffmpeg -loop 1 -f image2 -i %s -an -vcodec libx264 -pix_fmt yuv420p -r 5 -t %s -y %s" % (filename,length,outname)
	os.system(cmd)
def make_audio(video):
	cmd = "./ffmpeg -i %s -vn -acodec copy audio.wma" % video
	os.system(cmd)	

def make_full_mp4(filenames, lengths, video, delay, outname):
	for i in range(len(filenames)):
		make_mp4_from_jpg(filenames[i],lengths[i])
	concat_jpgs(filenames)
	make_audio(video)
	cmd = "./ffmpeg -i video.mp4 -itsoffset %s -i audio.wma -vcodec copy -strict -2 %s" % (delay,outname)
	print cmd
	os.system(cmd)
	os.system("rm video.mp4")
	os.system("rm audio.wma")

def main():
	basedir = './'

	file_dir = 'Content/'
	xml_file = 'MediasitePresentation_50.xml'
	outname = 'lecture.mp4'
	
	if len(sys.argv)==2:
		basedir = sys.argv[1]
		outname = basedir+outname
	else:
		fullpath = tkFileDialog.askopenfilename()	
		basedir = os.path.splitext(fullpath)[0]+'/'
		outname = os.path.splitext(fullpath)[0]+'.mp4'
		cmd = 'unzip \"%s\" -d \"%s\"' % (fullpath,basedir)
		os.system(cmd)
		
	file_dir = basedir+file_dir
	xml_file = basedir+xml_file
	
	fid = open(xml_file)
	xml = fid.read()
	fid.close()
	
	times = getAllBlocks(getFirstBlock(xml, 'Slides'),'Time',int)
	video_file = getFirstBlock(xml, 'OnDemandFileName')
	total_length = getFirstBlock(xml,'MediaLength',int)
	
	video_file = file_dir+video_file
	file_list = make_filelist(len(times),file_dir)
	delay,length_list = times_to_lengths(times,total_length)
	
	make_full_mp4(file_list,length_list,video_file,delay, outname)

if __name__ == '__main__':
	main()

