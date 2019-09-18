import copy

class Block:
	def __init__(self,blocksize):
		self.data = bytearray(blocksize)


class BlockMetaData:
	def __init__(self, id=-1, isfree=True, isassigned=False):
		self.id = id
		self.isfree = isfree
		self.isassigned = isassigned
		
class Disk:
	def __init__(self,diskSize):
		self.diskSize = diskSize
		self.blockaddr = [-1 for i in range(diskSize)]
		self.snaps = {}

class FileSystem:
	def __init__(self,blocksize):
		self.blocksize = blocksize
		self.diskA = [Block(blocksize) for i in range(200)]
		self.diskB = [Block(blocksize) for i in range(300)]
		self.FileMetaData = [BlockMetaData() for i in range(500)]
		self.currentsnap = 0
		self.disks = {}
		
		# id with list

	def read(self,blockId,block_inf):
		if(blockId < 0 or blockId >= 500):
			print("Out of Index Error")
			return False
		if(self.FileMetaData[blockId].isfree == True):
			# print("Not yet written")
			return False

		lentoread = min(len(block_inf), self.blocksize)
		if(blockId < 200):
			block_inf[0:lentoread] = self.diskA[blockId].data[0:lentoread]
			return True

		if(blockId < 500):
			block_inf[0:lentoread] = self.diskB[blockId-200].data[0:lentoread]
			return True

	def write(self,blockId,block_inf):
		if(blockId < 0 or blockId >= 500):
			print("Out of Index Error")
			return False

		if(len(block_inf) > self.blocksize):
			print("Can't write in one block")
			return False

		if(blockId < 200):
			self.diskA[blockId].data[0:len(block_inf)] = block_inf[0:len(block_inf)]
			self.FileMetaData[blockId].isfree = False
			return True

		if(blockId < 500):
			self.diskB[blockId-200].data[0:len(block_inf)] = block_inf[0:len(block_inf)]
			self.FileMetaData[blockId].isfree = False
			return True

	def checkcontiguous(self,diskSize):
		start = -1
		flag = 0
		count = 0
		for i in range(500):
			if(self.FileMetaData[i].isassigned == False):
				if(flag == 0):
					start = i
					count = 1
					flag = 1
				else:
					count += 1
					if(count == diskSize):
						return start
			else:
				flag = 0
		return -1

	def CreateDisk(self,diskId,diskSize):
		# check contiguous
		if(diskId in self.disks):
			print("Given DiskId already exists")
			return False

		startingindex = self.checkcontiguous(diskSize)
		if(startingindex != -1):
			diskm = Disk(diskSize)
			for i in range(diskSize):
				self.FileMetaData[startingindex+i].isassigned = True
				self.FileMetaData[startingindex+i].id = diskId
			diskm.blockaddr[0:diskSize] = [startingindex+i for i in range(diskSize)]
			self.disks[diskId] = diskm

		else:
			# print("handle fragmentation")
			diskm = Disk(diskSize)
			index = 0
			for i in range(500):
				if(self.FileMetaData[i].isassigned == False):
					diskm.blockaddr[index] = i
					index += 1
					if(index == diskSize):
						break
			if(index != diskSize):
				print("Not enough memory to allocate disk")
				return False
			for i in range(diskSize):
				s = self.FileMetaData[diskm.blockaddr[i]]
				s.isassigned = True
				s.id = diskId
			self.disks[diskId] = diskm
			return True

	def DeleteDisk(self,diskId):
		if(diskId not in self.disks):
			print("Given Disk does not exist")
			return False

		diskm = self.disks[diskId]
		for i in range(diskm.diskSize):
			s = self.FileMetaData[diskm.blockaddr[i]]
			s.isassigned = False
			s.id = -1
		self.disks.pop(diskId)
		return True

	def readBlock(self,diskId,blockId,block_inf):
		if(diskId not in self.disks):
			print("Disk of given Id doesn't exist")
			return False
		if(blockId < 0 or blockId >= self.disks[diskId].diskSize):
			print("Accessing out of index Block Id")
			return False

		# print("bypass")
		physicalId = self.disks[diskId].blockaddr[blockId]
		self.read(physicalId,block_inf)
		return True

	def writeBlock(self,diskId,blockId,block_inf):
		if(diskId not in self.disks):
			print("Disk of given Id doesn't exist")
			return False
		if(blockId < 0 or blockId >= self.disks[diskId].diskSize):
			print("Accessing out of index Block Id")
			return False
		physicalId = self.disks[diskId].blockaddr[blockId]
		self.write(physicalId,block_inf)
		return True

	def checkPoint(self, diskId):
		if not diskId in self.disks:
			print("Disk of given Id dosn't exist")
			return -1
		
		self.currentsnap += 1
		newsnap = []
		count=0
		for block in self.disks[diskId].blockaddr :
			blockdata = bytearray(self.blocksize)
			self.readBlock(diskId, count, blockdata)
			newsnap.append((blockdata, copy.deepcopy(self.FileMetaData[block])))
			count +=1
		self.disks[diskId].snaps[self.currentsnap] = newsnap
		return self.currentsnap

	def rollBack(self, diskId, snapId):
		if not diskId in self.disks:
			print("Disk of given Id dosn't exist")
			return False
		if not snapId in self.disks[diskId].snaps:
			print("Snap of given Id dosn't exist")
			return False

		returnsnap = self.disks[diskId].snaps[snapId]
		count = 0
		for block in self.disks[diskId].blockaddr:
			(blockdata, blockMeta) = returnsnap[count]
			self.writeBlock(diskId, count, blockdata)
			count += 1
			self.FileMetaData[block] = blockMeta

		return True

def runtestsnap():
	myfs = FileSystem(100)
	myfs.CreateDisk(1,20)
	myfs.CreateDisk(2,50)
	
	d1 = bytearray(b'beginne')
	d2 = bytearray(b'schwimme')
	d3 = bytearray(b'schlafen')
	d4 = bytearray(b'bezahlen')
	d5 = bytearray(b'brayche')
	d6 = bytearray(b'braucht')
	d7 = bytearray(b'schmecke')
	d8 = bytearray(b'schwimmt')
	d9 = bytearray(b'schlafe')
	d10 = bytearray(b'reichen')

	myfs.writeBlock(1,1,d1)
	myfs.writeBlock(1,3,d2)
	myfs.writeBlock(1,5,d3)
	myfs.writeBlock(1,7,d4)

	myfs.writeBlock(2,1,d2)
	myfs.writeBlock(2,3,d4)
	myfs.writeBlock(2,5,d6)
	myfs.writeBlock(2,7,d9)
	myfs.writeBlock(2,8,d10)
	
	
	readbuffer = bytearray(15)
	print("Image at snap_pt1")
	print("###########################################")
	for t in range(20):
		if(not myfs.FileMetaData[t].isfree):
			myfs.readBlock(1,t,readbuffer)
			print(t,readbuffer.decode('utf-8'))
	print("Image of disk 2")
	print("###########################################")
	for t in range(0,50):
		if(not myfs.FileMetaData[20+t].isfree):
			myfs.readBlock(2,t,readbuffer)
			print(t,readbuffer.decode('utf-8'))
	print("###########################################")

	myfs.checkPoint(1)

	myfs.writeBlock(1,2,d5)
	myfs.writeBlock(1,5,d6)
	
	myfs.checkPoint(1)

	myfs.writeBlock(1,6,d7)
	myfs.writeBlock(1,7,d8)

	print("Image at snap_pt3")
	print("###########################################")
	for t in range(20):
		if(not myfs.FileMetaData[t].isfree):
			myfs.readBlock(1,t,readbuffer)
			print(t,readbuffer.decode('utf-8'))
	print("Image of disk 2")
	print("###########################################")
	for t in range(0,50):
		if(not myfs.FileMetaData[20+t].isfree):
			myfs.readBlock(2,t,readbuffer)
			print(t,readbuffer.decode('utf-8'))
	print("###########################################")
	
	myfs.checkPoint(1)

	myfs.rollBack(1,2)
	print("Image after rollback to 2")
	print("###########################################")
	for t in range(20):
		if(not myfs.FileMetaData[t].isfree):
			myfs.readBlock(1,t,readbuffer)
			print(t,readbuffer.decode('utf-8'))
	print("Image of disk 2")
	print("###########################################")
	for t in range(0,50):
		if(not myfs.FileMetaData[20+t].isfree):
			myfs.readBlock(2,t,readbuffer)
			print(t,readbuffer.decode('utf-8'))
	print("###########################################")


	myfs.rollBack(1,1)
	print("Image after rollback to 1")
	print("###########################################")
	for t in range(20):
		if(not myfs.FileMetaData[t].isfree):
			myfs.readBlock(1,t,readbuffer)
			print(t,readbuffer.decode('utf-8'))
	print("Image of disk 2")
	print("###########################################")
	for t in range(0,50):
		if(not myfs.FileMetaData[20+t].isfree):
			myfs.readBlock(2,t,readbuffer)
			print(t,readbuffer.decode('utf-8'))
	print("###########################################")



def runtestcases2():
	fileA = FileSystem(100)
	fileA.CreateDisk(1,200)
	# fileA.CreateDisk(1,100)
	fileA.CreateDisk(2,100)
	fileA.CreateDisk(3,100)
	fileA.CreateDisk(4,100)
	fileA.DeleteDisk(2)
	fileA.DeleteDisk(4)
	fileA.CreateDisk(5,200)
	# fileA.DeleteDisk(10)
	A = bytearray(b'virtualization')
	fileA.writeBlock(5,190,A)
	B = bytearray(20)
	fileA.read(490,B)
	fileA.writeBlock(3,290,A)
	fileA.readBlock(3,12,A)
	# print("Completed")
	fileA.readBlock(5,20,B)
	print(B)
	# fileA.CreateDisk(6,1)

def runtestcases1():
	fileA = FileSystem(100)
	A = bytearray(b'Aniket')
	B = bytearray(10)
	C = bytearray(6)
	fileA.write(213,A)
	fileA.read(313,B)
	fileA.read(213,C)
	print(A)
	print(B)
	print(C)
def main():
	runtestsnap()

if __name__ == "__main__":
		main()
