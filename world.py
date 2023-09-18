from chunk import Chunk


class World:
    def __init__(self, size, seed, name):
        self.chunks = [[Chunk() for _ in range(size)] for _ in range(size)]
        self.size = size
        self.seed = seed
        self.name = name

    def set_chunk(self, x, y, chunk):
        self.chunks[x][y] = chunk
