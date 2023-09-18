from block import Block


class Chunk:
    def __init__(self):
        self.blocks = [[[None for _ in range(256)] for _ in range(16)] for _ in range(16)]
        for x in range(16):
            for y in range(16):
                self.blocks[x][y][0] = Block(id=1, name="Dirt", type="dirt", interact=False, drop_id=1, transparent=False, friction=0.5)

    def set_block(self, x, y, z, block):
        self.blocks[x][y][z] = block
