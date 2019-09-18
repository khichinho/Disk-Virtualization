class BlockData:
    def __init__(self, blockSize):
        self.data = bytearray(blockSize)

class BlockMetaData:
    def __init__(self, diskID):
        self.diskID = diskID
        self.isFree = False
        self.isAssigned = False

class physicalDrive:
    def __init__(self, blockSize, numBlock):
        self.data = [BlockData(blockSize) for i in range(numBlock)]
        self.size = numBlock

class Disk:
    def __init__(self, blockSize, diskID, numBlock):
        self.data = [BlockData(blockSize) for i in range(numBlock)]
        self.metadata = [BlockMetaData(diskID) for i in range(numBlock)]
        self.size = numBlock

class FileSystem:
    def __init__(self, blockSize, diskIDs, numBlocks):
        self.blockSize = blockSize
        self.physicalDrives = [physicalDrive(blockSize,i) for i in range(numBlocks)]
        self.fs = []

def main():
    pass

if __name__ == "__main__":
    main()