class Block:
	def __init__(self,blocksize):
		self.data = bytearray(blocksize)


class BlockMetaData:
	def __init__(self, id=-1, isfree=True, isassigned=False):
		self.id = id
		self.isfree = isfree
		self.isassigned = isassigned
		
class FileSystem:
	def __init__(self,blocksize):
		self.blocksize = blocksize
		self.diskA = [Block(blocksize) for i in range(200)]
		self.diskB = [Block(blocksize) for i in range(300)]
		self.FileMetaData = [BlockMetaData() for i in range(500)]

	def read(self,blockId,block_inf):
		if(blockId < 0 or blockId >= 500):
			print("Out of Index Error")
			return
		if(self.FileMetaData[blockId].isfree == True):
			print("Not yet written")
			return

		lentoread = min(len(block_inf), self.blocksize)
			
		if(blockId < 200):
			block_inf[0:lentoread] = self.diskA[blockId].data[0:lentoread]
			return

		if(blockId < 500):
			block_inf[0:lentoread] = self.diskB[blockId-200].data[0:lentoread]
			return

	def write(self,blockId,block_inf):
		if(blockId < 0 or blockId >= 500):
			print("Out of Index Error")
			return

		if(len(block_inf) > self.blocksize):
			print("Can't write in one block")
			return

		if(blockId < 200):
			self.diskA[blockId].data[0:len(block_inf)] = block_inf[0:len(block_inf)]
			self.FileMetaData[blockId].isfree = False
			# print("A writing")
			return

		if(blockId < 500):
			# print("B writing")
			self.diskB[blockId-200].data[0:len(block_inf)] = block_inf[0:len(block_inf)]
			self.FileMetaData[blockId].isfree = False
			return



def runtestcases():
	fileA = FileSystem(100)
	A = bytearray(b'Andaman')
	B = bytearray(b'Nicobar')
	X = bytearray(120)
	C = bytearray(7)
	D = bytearray(7)

	fileA.write(13,A)
	fileA.read(13,B)
	print(B)

	fileA.write(329,C)
	fileA.read(329,D)
	print(D)

	fileA.write(-12,A)
	fileA.write(512,A)
	fileA.write(12,X)
	fileA.read(12,D)


def main():
	runtestcases()

if __name__ == "__main__":
		main()
