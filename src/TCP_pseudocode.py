
Every time a packet is received, call this function.


Using the following global data structures:
list all_packets = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10...] #: list of all packets to be sent
int counter = 0 #: a counter that tells you how many packets were sent in this window.
int expected_packet = all_packets[0] #: expected packet is always the first element in the array
float window_size = 5 #: a float which keeps track of the current window size to be used.
int num_consecutive_fails = 0 #: an int which keeps track of how many wrong ack packets were receieved.

if (all_packets is not empty) {

	#First update packets accordingly
	if (received_packet == expected_packet){
		all_packets.remove(expected_packet)
		window_size += 1/window_size
		counter += 1
		expected_packet = all_packets[0]
	}

	if (received_packet != expected_packet){
		num_consecutive_fails += 1
		counter += 1
	}
	
	# This is the case where we reach the window size and reset our index to 1. 
	if (counter > window_size) {
		# if a packet is dropped ,we reduce window size by half.
		if (packet has been dropped within this window) {
			window_size = window_size / 2
		}
		# reset counter regardless
		counter = 0
	}

	# In the case index is within the range, but three wrong acks arrive consecutively,
	# we end early and reset:
	if (num_consecutive_fails >= 3) {
		window_size = window_size / 2
		counter = 0
	}

}

else {
	we are done.
}