import random
class Block:
	def __init__(self,blocksize):
		self.data = bytearray(blocksize)

class BlockMetaData:
	def __init__(self, id=-1, isfree=True, isassigned=False,iscorrupted=False):
		self.id = id
		self.isfree = isfree
		self.isassigned = isassigned
		self.iscorrupted = iscorrupted
		
class Disk:
	def __init__(self,diskSize):
		self.diskSize = diskSize
		self.blockaddr = [-1 for i in range(diskSize)]

class FileSystem:
	def __init__(self,blocksize):
		self.blocksize = blocksize
		self.diskA = [Block(blocksize) for i in range(200)]
		self.diskB = [Block(blocksize) for i in range(300)]
		self.FileMetaData = [BlockMetaData() for i in range(500)]
		self.diskprimary = {}
		self.disksecondary = {}
		# id with list

	def read(self,blockId,block_inf):
		if(blockId < 0 or blockId >= 500):
			print("Out of Index Error")
			return False
		if(self.FileMetaData[blockId].isfree == True):
			print("Not yet written")
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
		if(diskId in self.diskprimary):
			print("Given DiskID already exists")
			return False

		startingindex = self.checkcontiguous(2*diskSize)
		if(startingindex != -1):
			diskp = Disk(diskSize)
			disks = Disk(diskSize)
			for i in range(2*diskSize):
				self.FileMetaData[startingindex+i].isassigned = True
				self.FileMetaData[startingindex+i].id = diskId
			diskp.blockaddr[0:diskSize] = [startingindex+i for i in range(diskSize)]
			disks.blockaddr[0:diskSize] = [startingindex+diskSize+i for i in range(diskSize)]
			self.diskprimary[diskId] = diskp
			self.disksecondary[diskId] = disks
			return True

		else:
			# print("Handle fragmentation")
			diskp = Disk(diskSize)
			disks = Disk(diskSize)
			index = 0
			i = 0
			for i in range(500):
				if(self.FileMetaData[i].isassigned == False):
					diskp.blockaddr[index] = i
					index += 1
					if(index == diskSize):
						break
			for i in range(i+1,500):
				if(self.FileMetaData[i].isassigned == False):
					disks.blockaddr[index-diskSize] = i
					index += 1
					if(index == 2*diskSize):
						break

			if(index != 2*diskSize):
				print("Not enough memory to allocate disk")
				return False
			for i in range(diskSize):
				s = self.FileMetaData[diskp.blockaddr[i]]
				t = self.FileMetaData[disks.blockaddr[i]]
				s.isassigned = True
				t.isassigned = True
				s.id = diskId
				t.id = diskId
			self.diskprimary[diskId] = diskp
			self.disksecondary[diskId] = disks
			return True

	def DeleteDisk(self,diskId):
		if(diskId not in self.diskprimary):
			print("Given Disk does not exist")
			return False

		diskp = self.diskprimary[diskId]
		disks = self.disksecondary[diskId]

		for i in range(diskp.diskSize):
			s = self.FileMetaData[diskp.blockaddr[i]]
			t = self.FileMetaData[disks.blockaddr[i]]
			s.isassigned = False
			t.isassigned = False
			s.id = -1
			t.id = -1
		self.diskprimary.pop(diskId)
		self.disksecondary.pop(diskId)
		return True

	def findEmptyloc(self):
		for i in range(500):
			if(self.FileMetaData[i].isassigned == False and self.FileMetaData[i].iscorrupted == False):
				return i
		return -1

	def readBlock(self,diskId,blockId,block_inf):
		if(diskId not in self.diskprimary):
			print("Disk of given Id doesn't exist")
			return False
		if(blockId < 0 or blockId >= self.diskprimary[diskId].diskSize):
			print("Accessing out of index Block Id")
			return False

		# print("bypass")
		primaryId = self.diskprimary[diskId].blockaddr[blockId]
		if(self.FileMetaData[primaryId].iscorrupted == False):
			self.read(primaryId,block_inf)
			# print("primary not corrupted")
			return True
		else:
			secondaryId = self.disksecondary[diskId].blockaddr[blockId]
			if(self.FileMetaData[secondaryId].iscorrupted):
				print("Both replicas corrupted")
				# print("Can't fetch correct block data")
				return False
			# print("primary corrupted")
			self.read(secondaryId,block_inf)
			emptyloc = self.findEmptyloc()
			self.diskprimary[diskId].blockaddr[blockId] = emptyloc
			self.FileMetaData[emptyloc].isassigned = True
			self.FileMetaData[emptyloc].id = diskId
			copy = bytearray(self.blocksize)
			self.read(secondaryId,copy)
			self.write(emptyloc,copy)


	def writeBlock(self,diskId,blockId,block_inf):
		if(diskId not in self.diskprimary):
			print("Disk of given Id doesn't exist")
			return False
		if(blockId < 0 or blockId >= self.diskprimary[diskId].diskSize):
			print("Accessing out of index Block Id")
			return False

		primaryId = self.diskprimary[diskId].blockaddr[blockId]
		secondaryId = self.disksecondary[diskId].blockaddr[blockId]

# Assumption : In case of corruption, we can always get an unassigned and uncorrupted block

		if(self.FileMetaData[primaryId].iscorrupted == False):
			self.write(primaryId,block_inf)
		else:
			emptyloc = self.findEmptyloc()
			self.diskprimary[diskId].blockaddr[blockId] = emptyloc
			self.FileMetaData[emptyloc].isassigned = True
			self.FileMetaData[emptyloc].id = diskId

		if(self.FileMetaData[secondaryId].iscorrupted == False):
			self.write(secondaryId,block_inf)
		else:
			emptyloc = self.findEmptyloc()
			self.disksecondary[diskId].blockaddr[blockId] = emptyloc
			self.FileMetaData[emptyloc].isassigned = True
			self.FileMetaData[emptyloc].id = diskId
		return True

	def corruptRandom(self,diskId,blockId,isprimary):
		if(random.randint(0,100)<10):
			if(isprimary):
				physicalId = self.diskprimary[diskId].blockaddr[blockId]
			else:
				physicalId = self.disksecondary[diskId].blockaddr[blockId]
			self.FileMetaData[physicalId].iscorrupted = True
			return True
		return False

	def corrupt_surely(self,diskId,blockId,isprimary):
		if(isprimary):
			physicalId = self.diskprimary[diskId].blockaddr[blockId]
		else:
			physicalId = self.disksecondary[diskId].blockaddr[blockId]
		self.FileMetaData[physicalId].iscorrupted = True

def runtestcases():
	fileA = FileSystem(100)
	fileA.CreateDisk(1,120)
	fileA.CreateDisk(2,30)
	fileA.CreateDisk(3,50)
	fileA.DeleteDisk(2)
	fileA.CreateDisk(4,60)
	fileA.DeleteDisk(3)
	# print(fileA.checkcontiguous(100))
	wd1 = bytearray(b'checkpoint')
	wd2 = bytearray(b'snapshot')
	wd3 = bytearray(b'screenshot')
	wd4 = bytearray(b'roll back')
	rd1 = bytearray(10)
	rd2 = bytearray(8)
	rd3 = bytearray(10)
	rd4 = bytearray(9)

# disks of (id,size) - (1,120), (4,60)

# initial write, then read with no error
	fileA.writeBlock(1,4,wd1)
	fileA.readBlock(1,4,rd1)
	print(rd1,"wd1 should be equals rd1")

# check the location of physical block before and after corruption
	print("Initial Primary Physical Id: ", fileA.diskprimary[1].blockaddr[4])
	fileA.corrupt_surely(1,4,True)
	fileA.readBlock(1,4,rd2)
	print("After corruption, Primary Physical Id: ", fileA.diskprimary[1].blockaddr[4])
	print(rd2)

	fileA.writeBlock(4,10,wd3)
	fileA.corrupt_surely(4,10,True)
	fileA.corrupt_surely(4,10,False)
	fileA.readBlock(4,10,rd3)
	print("It should give and error\n",rd3)


	fileA.writeBlock(4,25,wd4)
	print("Initial Secondary Physical Id: ", fileA.disksecondary[4].blockaddr[25])
	fileA.corrupt_surely(4,25,False)
	fileA.readBlock(4,25,rd4)
	print("After corruption, Secondary Physical Id: ", fileA.disksecondary[4].blockaddr[25])
	print(rd4)

def main():
	runtestcases()

if __name__ == "__main__":
		main()
