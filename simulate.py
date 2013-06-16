#!/usr/bin/python

import random, time
import hashlib, string
from collections import deque
import threading, multiprocessing

NUM_NODES = 2000
# cycles per second
TIME_CONSTANT = 5
# measured in kb
SIZE_OF_BLOCK = 400
# convert size to cycles (processing time)
PROCESS_BLOCK_CONSTANT = 0.02
# convert size to cycles (transfer time)
SEND_BLOCK_CONSTANT = 0.1

def SHA256(tohash):
	return hashlib.sha256(tohash).hexdigest()

class newBlock():
	def __init__(self, parent):
		self.hash = SHA256(''.join([random.choice(string.letters) for i in range(20)]))
		self.parent = parent
		if parent == None:
			self.height = 0
		else:
			self.height = parent.height + 1
	
	def __repr__(self):
		return "%s:%s" % (self.height, self.hash[0:8])

class blockTree():
	def __init__(self):
		self.allBlocks = set()
		self.primary = None
		
	def __contains__(self, block):
		return block in self.allBlocks
		
	def haveBlock(self, block):
		return block in self.allBlocks
		
	def append(self, block):
		if not self.haveBlock(block):
			if self.primary == None or block.height > self.primary.height:
				self.primary = block
			self.allBlocks.add(block)
		
		

#class Node(threading.Thread):
class Node():
	def __init__(self, id):
		#threading.Thread.__init__(self)
		self.id = id
		self.peers = []
		self.blocksToProcess = deque()
		self.blocksRecieved = blockTree()
		self.blocksToSend = deque()
		self.numBlocks = 0
		self.queue = deque()
		self.id = id
		self.keepRunning = True
		self.go = True
		self.cycles1 = 0
		self.cycles2 = 0
		self.cycles3 = 0
		self.topBlock = None
		
	def __str__(self):
		return str(self.id)
	def __repr__(self):
		return str(self.id)
		
	def getHeight(self):
		return self.topBlock.height
		
	def getTopBlock(self):
		return self.topBlock
	
	def step1(self):
		if self.cycles1 < 0:
			self.cycles1 = 0
		if self.cycles1 == 0:
			if len(self.queue) > 0:
				block = self.queue.popleft()
				if block not in self.blocksRecieved and block not in self.blocksToProcess:
					self.blocksToProcess.append(block)
					# increment cycle counters
					# for verifying block, 2s
					c = random.randrange(0,TIME_CONSTANT*10)
					self.cycles2 += SIZE_OF_BLOCK*PROCESS_BLOCK_CONSTANT + c
		else:
			self.cycles1 -= 1
	
	def step2(self):
		if self.cycles2 < 0:
			self.cycles2 = 0
		if self.cycles2 == 0 and len(self.blocksToProcess) > 0:
			block = self.blocksToProcess.popleft()
			self.blocksRecieved.append(block)
			if self.topBlock == None or block.height > self.topBlock.height:
				self.topBlock = block
			self.numBlocks += 1
			self.blocksToSend.append(block)
			# sending + verifying
			c = random.randrange(0,TIME_CONSTANT)
			self.cycles3 += SIZE_OF_BLOCK*SEND_BLOCK_CONSTANT + c
		else:
			self.cycles2 -= 1
			
	
	def step3(self):
		if self.cycles3 < 0:
			self.cycles3 = 0
		if self.cycles3 == 0:
			if len(self.blocksToSend) > 0:
				block = self.blocksToSend.popleft()
				self.sendBlock(block)
		else:
			self.cycles3 -= 1
	
	#def run(self):
	#	while self.keepRunning:
	#		self.step1()
	#		self.step2()
	#		time.sleep(0.0001)
	
	def stop(self):
		self.keepRunning = False
	
	def addPeer(self, peerToAdd):
		if peerToAdd not in self.peers and peerToAdd != self:
			self.peers.append(peerToAdd)
			peerToAdd.addPeer(self)
	
	def hasBlock(self, block):
		return (block in self.blockRecieved)
				
	def acceptBlock(self, block):
		self.queue.append(block)
			
	def sendBlock(self, block):
		for peer in self.peers:
			peer.acceptBlock(block)
			
	# ------- misc functions, not core
	
	def numBlocks(self):
		return len(self.numBlocks)
			
class blockOverlord():
	def __init__(self, allPeers, blockTargetSecs=600):
		self.allPeers = allPeers
		self.prob = 1.0/(TIME_CONSTANT*blockTargetSecs)
		
	def genesis(self):
		self.cheatABlock(block=newBlock(None))
		
	def produceBlock(self):
		if random.random() <= self.prob:
			self.cheatABlock()
			return True
		return False
	
	def cheatABlock(self, block=None):
		# choose peer
		peer = random.choice(self.allPeers)
		if block == None:
			tempBlock = newBlock(peer.getTopBlock())
		else:
			tempBlock = block
		# send
		peer.acceptBlock(tempBlock)
			

def sample_status(allPeers):
	print ["%s:%s" % (peer.id,peer.numBlocks()) for peer in allPeers]

def print_stats(allPeers):
	topBlocks = {}
	for peer in allPeers:
		if peer.topBlock != None and peer.topBlock not in topBlocks.keys():
			topBlocks[peer.topBlock] = 1
		elif peer.topBlock != None:
			topBlocks[peer.topBlock] = topBlocks[peer.topBlock] + 1
	proportions = {}
	for block,count in topBlocks.iteritems():
		print "%s,%s:" % (block, 1.0*count/NUM_NODES),
	print
			
def main():
	print 'Setup..'
	allPeers = [Node(x) for x in range(NUM_NODES)]
	print 'Nodes created'
	print 'Linking'
	# give each node at least 7 peers
	for peer in allPeers:
		while len(peer.peers) < 7:
			peer.addPeer(allPeers[random.randint(0,NUM_NODES-1)])
	print 'Done'
	blockMaker = blockOverlord(allPeers, blockTargetSecs=600)	
	
	blockMaker.genesis()
	
	loopCounter = 0
	
	while True:
		while blockMaker.produceBlock():
			pass
		for peer in allPeers:
			peer.step1()
		for peer in allPeers:
			peer.step2()
		for peer in allPeers:
			peer.step3()
		if loopCounter % TIME_CONSTANT == 0:
			print_stats(allPeers)
		loopCounter += 1
	
	print 'Avg. peers: %s' % ( 1.0 * sum([len(peer.peers) for peer in allPeers]) / NUM_NODES )
	
	#for peer in allPeers:
	#	peer.stop()
	
if __name__ == "__main__":
	main()