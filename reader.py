import os
import re
import sys

print "removing *___.txt"
os.system('rm *___.txt')

if len(sys.argv) > 1:
	if sys.argv[1] == '-a':
		print "ALL?"
		files_here = os.listdir('.')
		files_here.pop(files_here.index('reader.py'))
		print files_here
else:
	print "use -a yo!"
	ftrace_log_file = raw_input('file name?\n');
	files_here=[]
	files_here.append(ftrace_log_file)
	print files_here

#file_number = 0
for ftrace_log_file in files_here:
	print '##  ' + ftrace_log_file
	ret_val = os.system("grep NET_RX  "+ftrace_log_file+" > found2.txt")
	print "found lines with return val",ret_val
	FOUT = open("diff_"+ftrace_log_file+"___.txt",'w')

	raise_count=0		#the number of softirq raises
	entry_list = []		#list with details about entry
	entry_timestamps=[]	#list with entry time stamp
	sum_of_diffs = 0	#sum of entry and exit diffs
	diff_count = 0		# number diffs 
	num_of_lines=0;
	exit_no_match = 0	# number of exits without match
	# no of entries without match = entry_list size at end
	#
	#read line by line
	with open('found2.txt','r') as FIN:
		for line in FIN:
			num_of_lines = num_of_lines + 1
			if re.match(r'.*raise: .*', line):
				#print "RAISE    ", line
				raise_count = raise_count + 1
			elif re.match(r'.*_entry: .*',line):
				#print "ENTRY  ", line
				parts = line.split(": softirq_")
				words = parts[0].split(' ')
				words = [ x for x in words if x ]	#remove empty stings
				entry_timestamps.append(float(words.pop(-1)))
				words.pop(-1)		#ignore irqs, etc aaaaaaaaaaaaaaaaaaaaaaa
				entry_list.append(' '.join(words))
				#print entry_list 
				#print entry_timestamps 
			elif re.match(r'.*_exit: .*',line):
				#print "EXIT    ", line
				parts = line.split(": softirq_")
				words = parts[0].split(' ')
				words = [ x for x in words if x ]	#remove empty stings
				#print words
				exit_timestamp = float(words.pop(-1))
				words.pop(-1)		#ignore irqs, etc aaaaaaaaaaaaaaaaaaaaaa
				exit_string=' '.join(words)
				found_match = 0
				for ii in range(len(entry_list)):
					if entry_list[ii]==exit_string:
						found_match = 1
						diff = exit_timestamp - entry_timestamps[ii]
						entry_list.pop(ii)
						entry_timestamps.pop(ii)
						sum_of_diffs = sum_of_diffs + diff
						diff_count = diff_count + 1
						#print "DIFF   ", diff
						FOUT.write(str(diff) + "\n");
						break;
				if found_match == 0:
					exit_no_match = exit_no_match + 1
			#if raise_count == 20:		# for stoping early to check
			#	break;
	#printing
	print "A. NUMBER OF RAISES = ",raise_count
	print "B. Entry-Exit pairs = ",diff_count
	print "C. sum of diffs     = ", sum_of_diffs
	print "C. Avg diff         = ", sum_of_diffs/diff_count
	print "D. Unmatched exits  = ", exit_no_match
	print "E. Unmatched entries= ", len(entry_list)
	print "total softirqs      = ", num_of_lines
	print "A + 2B + D + E      = ", raise_count + 2*diff_count + exit_no_match + len(entry_list)
	print "***********************************************\n"
	#close files
	FIN.close()
	os.system('rm found2.txt')
	FOUT.close()
	

