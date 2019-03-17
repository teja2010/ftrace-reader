# ftrace_reader

python files to parse ftrace logs.

### reader.py :
Basic python script, prints NET_RX stats

### reader_recv_skbs_btw_Sirqs.py:
print the number of receive skbs transmitted between each raise.
edit variable 'The_string' to change device and choose between RX&TX stats
e.g. if
The_string = 'grep "NET_RX\|netif_receive_skb: dev=rmnet_data0"'
           => RX on rmnet_data0
The_string = 'grep "NET_TX\|net_dev_xmit: dev=rmnet_ipa0" ' => TX on rmnet_ipa0

### reader_sched_switch.py:
print %times sched_switch is called per cpu
edit the comm and pid at three places.
the default one has will track iperf_1Gbps comm, with 5020 pid
TODO: clean up comments.
TODO: make a new var for this.

### sched_check.py:
print number of enqueues and dequeues of the pid.
change search_term="iperf" to track a comm.
TODO: add pid

### sched_switch.py:
print number of enqueues &dequeues. print time spent on each CPU.
change search_term="clatd" and provide PID as input.
TODO: clean up


### reader_sched_switch2.py:
a modified version of reader_sched_switch.py. will print UDP packets stats
along with sched_switch and sched enqueue/dequeue stats.

