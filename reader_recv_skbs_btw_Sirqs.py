import os
import re
import sys

##
## To check the number of receive skbs transmitted between each raise
##

print "removing *___.txt"
os.system('rm *___.txt')

if len(sys.argv) > 1:
	if sys.argv[1] == '-a':
		print "nice..."
		files_here = os.listdir('.')
		files_here.pop(files_here.index('reader.py'))
		print files_here
	else:
		print "u can use only -a !"
else:
	print "use -a !"
	ftrace_log_file = raw_input('file name?\n');
	files_here=[]
	files_here.append(ftrace_log_file)
	print files_here

#file_number = 0
for ftrace_log_file in files_here:
	print "######\t" , ftrace_log_file, "\t######"
	#The_string = 'grep "NET_RX\|netif_receive_skb: dev=rmnet_data0" '
	#The_string = 'grep "NET_TX\|net_dev_xmit: dev=rmnet_data0" '
	#The_string = 'grep "NET_RX\|netif_receive_skb: dev=rmnet_ipa0" '
	The_string = 'grep "NET_TX\|net_dev_xmit: dev=rmnet_ipa0" '
	#The_string = 'grep "NET_RX\|netif_receive_skb: dev=v4-rmnet_data0" '
	#The_string = 'grep "NET_TX\|net_dev_xmit: dev=v4-rmnet_data0" '
	ret_val = os.system(The_string+ftrace_log_file+' > found2.txt')
	if ret_val != 0:
		print "found lines with return val",ret_val
	print "***********  we lookin at ",The_string,"***********"
	FOUT = open("diff_"+ftrace_log_file+"___.txt",'w')
	FOUT2 = open("recv_skbs_"+ftrace_log_file+"___.txt",'w')
	raise_count= [0]*8			#the number of softirq raises
	entry_and_exit_count= [0]*8		#the number of softirq entry and exits
	entry_list = []			#list with details about entry
	entry_timestamps=[]		#list with entry time stamp
	sum_of_diffs = 0		#sum of entry and exit diffs
	diff_count = 0			# number diffs 
	net_rx_lines = 0
	rcv_skb_lines =0
	num_of_lines=0
	exit_no_match = 0		# number of exits without match
	net_rx_counts=[0]*8		# which cpu's kthread net_rx is running on
	total_rcv_skbs_size=[0]*8	# total sum of size of the packets consumed unmatched and matched
	total_rcv_skbs_num=[0]*8   	# total num of the packets consumed
	matched_rcv_skb_size=[0]*8    	# sum of sizes of packets consumed on each cpu, only matched
	matched_rcv_skb_num=[0]*8    	# num of packets consumed on each cpu, only matched
	rcv_skb_switch=[0]*8    	# switches for each cpu. 1 => between entry and exit, only matched
	unmatched_rcv_skb_size=[0]*8	# number of skb calls called, which are unmatched
	unmatched_rcv_skb_num=[0]*8	# size of the skbs , which are unmatched.
	rps_boys = [0]*8		#ENTRY AND EXIT but not sendings, rps worked
	rps_ness = [0]*8
	# no of entries without match = entry_list size at end
	#
	#read line by line
	with open('found2.txt','r') as FIN:
		for line in FIN:
			num_of_lines = num_of_lines + 1
			cpu_number = line.split('[')
			cpu_number=cpu_number[1].split(']')
			cpu_number=int(cpu_number[0])
			#print cpu_number
			if re.match(r'.*raise: .*', line):
				#print "RAISE    ", line
				net_rx_lines = net_rx_lines + 1
				raise_count[cpu_number] = raise_count[cpu_number] + 1
			elif re.match(r'.*_entry: .*',line):
				#print "ENTRY  ", line
				net_rx_lines = net_rx_lines + 1
				entry_and_exit_count[cpu_number] = entry_and_exit_count[cpu_number] + 1
				rcv_skb_switch[cpu_number] = 1
				net_rx_counts[cpu_number] = net_rx_counts[cpu_number] + 1
				parts = line.split(": softirq_")
				words = parts[0].split(' ')
				words = [ x for x in words if x ]		#remove empty stings
				entry_timestamps.append(float(words.pop(-1)))
				words.pop(-1)		#ignore irqs, etc aaaaaaaaaaaaaaaaaaaaaaaaaaaa
				entry_list.append(' '.join(words))
				#print entry_list 
				#print entry_timestamps 
			elif re.match(r'.*_exit: .*',line):
				#print "EXIT    ", line
				net_rx_lines = net_rx_lines + 1
				#entry_and_exit_count[cpu_number] = entry_and_exit_count[cpu_number] + 0.5
				parts = line.split(": softirq_")
				words = parts[0].split(' ')
				words = [ x for x in words if x ]		#remove empty stings
				#print words
				exit_timestamp = float(words.pop(-1))
				words.pop(-1)		#ignore irqs, etc aaaaaaaaaaaaaaaaaaaaaaaaaaaa
				exit_string=' '.join(words)
				found_match = 0
				for ii in range(len(entry_list)):
					if entry_list[ii]==exit_string:
						found_match = 1
						diff = exit_timestamp - entry_timestamps[ii]
						entry_list.pop(ii)
						entry_timestamps.pop(ii)
						rcv_skb_switch[cpu_number] = 0
						if rps_ness[cpu_number] == 0:
							rps_boys[cpu_number] = rps_boys[cpu_number] + 1
						else:
							rps_ness[cpu_number] =0
						sum_of_diffs = sum_of_diffs + diff
						diff_count = diff_count + 1
						#print "DIFF   ", diff
						FOUT.write(str(diff) + "\n");
						break;
				if found_match == 0:
					exit_no_match = exit_no_match + 1
			elif re.match(r'.*dev=.*',line):
				rcv_skb_lines = rcv_skb_lines + 1
				len_of_pack = line.split(' len=')
				len_of_pack = len_of_pack[1].split('\n')
				len_of_pack = len_of_pack[0].split(' rc')
				#print len_of_pack
				the_skb_size = int(len_of_pack[0])
				rps_ness[cpu_number] = 1
				#print cpu_number
				total_rcv_skbs_size[cpu_number] = total_rcv_skbs_size[cpu_number] + the_skb_size
				total_rcv_skbs_num[cpu_number] = total_rcv_skbs_num[cpu_number] + 1
				if sum(rcv_skb_switch) > 0:
					matched_rcv_skb_size[cpu_number] = matched_rcv_skb_size[cpu_number] + the_skb_size
					matched_rcv_skb_num[cpu_number] = matched_rcv_skb_num[cpu_number] + 1
				else:
					#print "UNMATCHED"; print line
					unmatched_rcv_skb_size[cpu_number] = unmatched_rcv_skb_size[cpu_number]+the_skb_size
					unmatched_rcv_skb_num[cpu_number] = unmatched_rcv_skb_num[cpu_number] + 1
				#print "found a receive skb."
			#if sum(raise_count) == 2:		# for stoping early to check
			#	break;
	#printing
	print "A. NUMBER OF RAISES     = ","\t".join([str(x) for x in raise_count])
	print "B. Entry-Exit pairs     = ","\t".join([str(x) for x in entry_and_exit_count])
	print "   total pairs          = ", diff_count, " = " , sum(entry_and_exit_count)
	print "Z. sum of diffs         = ", sum_of_diffs
	print "C. Avg diff             = ", sum_of_diffs/diff_count
	print "D. Unmatched exits      = ", exit_no_match
	print "E. Unmatched entries    = ", len(entry_list)
	print "total softirqs          = ", net_rx_lines
	print "A + 2B + D + E          = ", sum(raise_count) + 2*diff_count + exit_no_match + len(entry_list)
	print "***********************************************\n"
	print " skb analysis         CPU   : ", "\t".join([str(x) for x in range(8)]),"\t=  sum"
	print "F. Total bytes per cpu              = ", "\t".join([str(x) for x in total_rcv_skbs_size]),"\t= ",sum(total_rcv_skbs_size)
	print "G. Total calls per cpu              = ", "\t".join([str(x) for x in total_rcv_skbs_num]),"\t= ",sum(total_rcv_skbs_num)
	print "H. Matched bytes per cpu            = ", "\t".join([str(x) for x in matched_rcv_skb_size])
	print "I. Matched calls per cpu            = ", "\t".join([str(x) for x in matched_rcv_skb_num])
	print "J. Unmatched bytes per cpu          = ", "\t".join([str(x) for x in unmatched_rcv_skb_size])
	print "M. Unmatched calls per cpu          = ", "\t".join([str(x) for x in unmatched_rcv_skb_num])
	print "K. average matched bytes per net_?x session = ", sum(matched_rcv_skb_size)/(diff_count - sum(rps_boys))
	print "L. average matched calls per net_?x session = ", sum(matched_rcv_skb_num)/(diff_count - sum(rps_boys))
	print " avgs dont the rps'ed sessions, check code"
	print " rps'ed sessions                    = ","\t".join([str(x) for x in rps_boys])
	print "  "
	print "K. average of all bytes per net_Xx session = ", sum(total_rcv_skbs_size)/(diff_count)
	print "L. average of all calls per net_Xx session = ", sum(total_rcv_skbs_num)/(diff_count)
	print "***********************************************"
	print "N. NET_RX lines + rcv_skb lines = ",net_rx_lines+rcv_skb_lines
	print "O. total lines                  = ",num_of_lines
	#close files
	FIN.close()
	#os.system('rm found2.txt')
	FOUT.close()
	
