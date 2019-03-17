import os
import re
import sys

#
# %times sched_switch is called per cpu
#

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
	ret_val = os.system("grep -e sched_switch.*iperf_1Gbps.*5020  "+ftrace_log_file+" > found2.txt")
	print "found lines with return val",ret_val
	FOUT = open("diff_"+ftrace_log_file+"___.txt",'w')

	raise_count=0		#the number of softirq raises
	#entry_list = []		#list with details about entry
	entry_timestamp = 0
	entry_timestamps=[]	#list with entry time stamp
	sum_of_diffs = 0	#sum of entry and exit diffs
	diff_count = 0		# number diffs 
	num_of_lines=0;
	exit_no_match = 0	# number of exits without match
	entry_no_match = 0	# number of exits without match
	cpu_counter = [0]*8		#per cpu counter
	# no of entries without match = entry_list size at end
	#
	#read line by line
	with open('found2.txt','r') as FIN:
		for line in FIN:
			num_of_lines = num_of_lines + 1
			if re.match(r'.*next_comm=iperf_1Gbps next_pid=5020.*',line):
				#print "ENTRY  ", line
				parts = line.split(": sched_switch:")
				words = parts[0].split(' ')
				words = [ x for x in words if x ]	#remove empty stings
				#print "entry", words[-1]
				entry_timestamp = float(words.pop(-1))
				words.pop(-1)		#ignore irqs, etc aaaaaaaaaaaaaaaaaaaaaaa
				entry_no_match = entry_no_match + 1
				cpu = line[24:27:1]
				#print "cpu1", cpu
				cpu = int(cpu)
				#print "cpu3", cpu
				cpu_counter[cpu] = cpu_counter[cpu] + 1
				#entry_list.append(' '.join(words))
				#print entry_list 
				#print entry_timestamps 
			elif re.match(r'.*prev_comm=iperf_1Gbps prev_pid=5020 .*',line):
				#print "EXIT    ", line
				parts = line.split(": sched_switch:")
				words = parts[0].split(' ')
				words = [ x for x in words if x ]	#remove empty stings
				#print "exit ", words
				exit_timestamp = float(words.pop(-1))
				words.pop(-1)		#ignore irqs, etc aaaaaaaaaaaaaaaaaaaaaa
				exit_string=' '.join(words)
				found_match = 0
				if entry_timestamp == 0:
					exit_no_match = exit_no_match + 1
				else:
					diff = exit_timestamp - entry_timestamp
					#print diff
					sum_of_diffs = sum_of_diffs + diff
					diff_count = diff_count + 1
					entry_no_match = entry_no_match - 1
				#for ii in range(len(entry_list)):
				#	if entry_list[ii]==exit_string:
				#		found_match = 1
				#		diff = exit_timestamp - entry_timestamps[ii]
				#		entry_list.pop(ii)
				#		entry_timestamps.pop(ii)
				#		sum_of_diffs = sum_of_diffs + diff
				#		diff_count = diff_count + 1
				#		#print "DIFF   ", diff
				#		FOUT.write(str(diff) + "\n");
				#		break;
				#if found_match == 0:
				#	exit_no_match = exit_no_match + 1
			#if line_count == 20:		# for stoping early to check
			#	break;
	#printing
	print "A. NUMBER OF RAISES = ",raise_count
	print "B. Entry-Exit pairs = ",diff_count
	print "C. sum of diffs     = ", sum_of_diffs
	print "C. Avg diff         = ", sum_of_diffs/diff_count
	print "D. Unmatched exits  = ", exit_no_match
	print "E. Unmatched entries= ", entry_no_match
	print "total lines      = ", num_of_lines
	print "A + 2B + D + E      = ", raise_count + 2*diff_count + exit_no_match + entry_no_match
	print "***********************************************\n"
	print "A. sched_switch (%) = ","\t".join([str(int(float(x*100)/sum(cpu_counter))) for x in cpu_counter]),"\t=",sum(cpu_counter)
	#close files
	FIN.close()
	os.system('rm found2.txt')
	FOUT.close()
	

