# Bitcoin (any cryptocoin) network simulation - block propogation

To run the script:
  python simulate.py

Every console output represents 1s.

Console shows the current top block as a proportion of all nodes on the network in the format `<blockHeight>:<hash[0:8]>,<proportionOfNetwork>: ` which is repeated for each block.

In this way the simulation shows blockchain-forks.

The purpose of this program is to simulate the network to investigate the propogation of nodes under different block target times.

Variables to alter:
* Block Target Time
* Size of block
* Processing time (based on size of block)
* Transmission time (based on size of block)

The latter two require some real data to get an accurate simulation

Currently the simulation seems to produce to few blocks for the supposed number of seconds, but this can be calibrated.

## time to cylces
every time measurement must be scaled to a number of cycles

av time between blocks = 10 min = 600 sec 
* this is the benchmark for cycles. set 600 cycles to 10 minutes or 1s per cycle
av time to verify a block = 
