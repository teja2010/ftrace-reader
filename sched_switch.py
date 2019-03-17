import os
import re

ftrace_file = raw_input("name of the log file?\n")
proc_pid = raw_input("pid of the process?\n")
search_term="clatd"
#search_term="iperfL"
#search_term="iperf"
print "search  term : ", search_term

os.system('grep  sched_switch  '+ftrace_file+' > grep_switch.txt');
os.system('grep  comm="'+search_term+'"   grep_switch.txt > greped_search_sw.txt');

num_of_lines = 0
enqued_on_cpu=[0]*8
time_on_cpu=[0]*8
raises_on_cpu=[0]*8
enqs_on_cpu=[0]*8
deqs_on_cpu=[0]*8
print enqued_on_cpu

with open('greped_search_sw.txt','r') as FIN:
	print "hello"
	for line in FIN:
		#print line
		num_of_lines = num_of_lines + 1
		cpu_num = line.split('[')
		cpu_num = cpu_num[1].split(']')
		cpu_num = int(cpu_num[0])
		if re.match(r'.*prev_comm='+search_term+'.*prev_pid='+proc_pid+'.*', line):
			parts=line.split(": sched_switch: ")
			#print parts
			time_stamp = parts[0].split(' ')
			time_stamp = [x for x in time_stamp if x] #rem empty strings
			time_stamp = float(time_stamp.pop(-1))
			#print time_stamp
			enqued_on_cpu[cpu_num] = time_stamp
			enqs_on_cpu[cpu_num] = enqs_on_cpu[cpu_num] + 1
		elif re.match(r'.*next_comm='+search_term+'.*next_pid='+proc_pid+'.*', line):
			parts=line.split(": sched_switch: ")
			#print parts
			time_stamp = parts[0].split(' ')
			time_stamp = [x for x in time_stamp if x] #rem empty strings
			time_stamp = float(time_stamp.pop(-1))
			#print time_stamp
			diff = time_stamp - enqued_on_cpu[cpu_num]
			#print "diff = ",diff
			deqs_on_cpu[cpu_num] = deqs_on_cpu[cpu_num] + 1
			######## WORKING
			if diff<0:
				print "UMATCHED WARN"
				#print line
				#break
			elif enqued_on_cpu[cpu_num] == 0:
				print "UMATCHED WARN2"
				#print line
			else:
				time_on_cpu[cpu_num] = time_on_cpu[cpu_num] + diff
				raises_on_cpu[cpu_num] = raises_on_cpu[cpu_num] + 1
				enqued_on_cpu[cpu_num] = 0
			#time_stamp = time_stamp
		#if num_of_lines > 10:
		#	break

print "**********************************************"
print " for process"+ search_term
print "               CPU    = ","\t".join([str(x) for x in range(8)])," sum ="
print "  enqs on each cpu    = ","\t".join([str(x) for x in enqs_on_cpu])," sum =",sum(enqs_on_cpu)
print "  deqs on each cpu    = ","\t".join([str(x) for x in deqs_on_cpu])," sum =",sum(deqs_on_cpu)
print "  time on each cpu(%) = ","\t".join([str(round(float(x)*100/sum(time_on_cpu),2)) for x in time_on_cpu])
print "  total time          = ",sum(time_on_cpu),"***** is wrong if you have multiple pids ***** "
print "  raises on each cpu  = ","\t".join([str(round(float(x)*100/sum(raises_on_cpu),2)) for x in raises_on_cpu])
print "   check ",num_of_lines," = ",sum(enqs_on_cpu) + sum(deqs_on_cpu), \
		"  = ",sum(enqs_on_cpu)," + ",sum(deqs_on_cpu)
