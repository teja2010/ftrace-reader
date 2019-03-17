import os
import re

ftrace_file = raw_input("name of the log file")

search_term="iperf"
print "search  term : ", search_term

os.system('grep  sched_enq_deq_task  '+ftrace_file+' > grep_sched.txt');
os.system('grep  comm="'+search_term+'"   grep_sched.txt > greped_search.txt');

num_of_lines = 0
enqued_on_cpu=[0]*8
time_on_cpu=[0]*8
raises_on_cpu=[0]*8
enqs_on_cpu=[0]*8
deqs_on_cpu=[0]*8
print enqued_on_cpu

with open('greped_search.txt','r') as FIN:
	print "hello"
	for line in FIN:
		#print line
		num_of_lines = num_of_lines + 1
		if re.match(r'.*enqueue comm=.*', line):
			parts=line.split(" enqueue comm=")
			parts2 = parts[0].split(": sched_enq_deq_task:")
			#print parts2
			time_stamp = parts2[0].split(' ')
			time_stamp = [x for x in time_stamp if x] #rem empty strings
			time_stamp = float(time_stamp.pop(-1))
			#print time_stamp
			cpu_num=parts2[1].split(' cpu=')
			cpu_num = [x for x in cpu_num if x] #rem empty strings
			cpu_num = int(cpu_num[0])
			#print cpu_num
			#enqued_on_cpu[cpu_num] = time_stamp
			enqs_on_cpu[cpu_num] = enqs_on_cpu[cpu_num] + 1
			#time_stamp = time_stamp
		elif re.match(r'.*dequeue comm=.*', line):
			parts=line.split(" dequeue comm=")
			parts2 = parts[0].split(": sched_enq_deq_task:")
			#print parts2
			time_stamp = parts2[0].split(' ')
			time_stamp = [x for x in time_stamp if x] #rem empty strings
			time_stamp = float(time_stamp.pop(-1))
			#print time_stamp
			cpu_num=parts2[1].split(' cpu=')
			cpu_num = [x for x in cpu_num if x] #rem empty strings
			cpu_num = int(cpu_num[0])
			#print cpu_num
			diff = time_stamp - enqued_on_cpu[cpu_num]
			#print "diff = ",diff
			deqs_on_cpu[cpu_num] = deqs_on_cpu[cpu_num] + 1
			######## WORKING
			#if diff<0:
			#	print "UMATCHED WARN"
			#	print line
			#	#break
			#if enqued_on_cpu[cpu_num] == 0:
			#	print "UMATCHED WARN2"
			#	print line
			#else:
			#	time_on_cpu[cpu_num] = time_on_cpu[cpu_num] + diff
			#	raises_on_cpu[cpu_num] = raises_on_cpu[cpu_num] + 1
			#	enqued_on_cpu[cpu_num] = 0
			#time_stamp = time_stamp
		#if num_of_lines > 100:
		#	break

print "**********************************************"
print " for process"+ search_term
print "               CPU  = ","\t".join([str(x) for x in range(8)])
print "  enqs on each cpu  = ","\t".join([str(x) for x in enqs_on_cpu])
print "  deqs on each cpu  = ","\t".join([str(x) for x in deqs_on_cpu])
print " check ",num_of_lines," = ",sum(enqs_on_cpu) + sum(deqs_on_cpu), \
		"  = ",sum(enqs_on_cpu)," + ",sum(deqs_on_cpu)
#print "  time on each cpu  = ","\t\t".join([str(x) for x in time_on_cpu])
#print " raises on each cpu = ","\t\t".join([str(x) for x in raises_on_cpu])
