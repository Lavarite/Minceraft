from math import sin, cos
from panda3d.core import Geom, GeomNode, GeomVertexFormat, GeomVertexData
from panda3d.core import GeomVertexWriter, GeomTriangles
from panda3d.core import LPoint3, LVector3


# Function to render a single block at a given position
def render_block(render, x, y, z, block_type):
    vformat = GeomVertexFormat.getV3()
    vdata = GeomVertexData('block', vformat, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, 'vertex')

    # Define the vertices for a unit cube
    vertices = [
        [x, y, z], [x + 1, y, z], [x + 1, y + 1, z], [x, y + 1, z],
        [x, y, z + 1], [x + 1, y, z + 1], [x + 1, y + 1, z + 1], [x, y + 1, z + 1]
    ]

    # Add these vertices to the vertex data
    for v in vertices:
        vertex.addData3f(v[0], v[1], v[2])

    # Create the geometry for the cube
    geom = Geom(vdata)
    tris = GeomTriangles(Geom.UHStatic)

    # Define the indices for the triangles
    indices = [
        0, 1, 2, 0, 2, 3,
        4, 7, 6, 4, 6, 5,
        0, 3, 7, 0, 7, 4,
        1, 5, 6, 1, 6, 2,
        0, 4, 5, 0, 5, 1,
        2, 6, 7, 2, 7, 3
    ]

    # Add these indices to the index data
    for i in indices:
        tris.addVertex(i)

    geom.addPrimitive(tris)

    # Create a node and attach the geometry to it
    node = GeomNode(block_type)
    node.addGeom(geom)
    node_path = render.attachNewNode(node)
    node_path.setPos(x, y, z)


# Function to render an entire chunk
def render_chunk(render_node, chunk, chunk_x, chunk_y, player_position, view_distance):
    for x in range(16):
        for y in range(16):
            for z in range(256):
                block = chunk.blocks[x][y][z]
                if block is not None:
                    block_position = (chunk_x * 16 + x, chunk_y * 16 + y, z)
                    if is_block_in_sight(player_position, block_position, view_distance, chunk, x, y, z):
                        render_block(render_node, block, block_position)


# Occlusion and View Functions
def is_block_occluded(chunk, x, y, z):
    directions = [
        (0, 0, 1),  # Up
        (0, 0, -1),  # Down
        (0, 1, 0),  # North
        (0, -1, 0),  # South
        (1, 0, 0),  # East
        (-1, 0, 0)  # West
    ]

    for dx, dy, dz in directions:
        neighbor_x, neighbor_y, neighbor_z = x + dx, y + dy, z + dz

        # If any neighboring block is not solid, this block is not occluded
        if not chunk.is_solid(neighbor_x, neighbor_y, neighbor_z):
            return False

    return True


def is_block_in_sight(player_position, block_position, view_distance, chunk, x, y, z):
    distance = (player_position - block_position).length()
    return distance <= view_distance and not is_block_occluded(chunk, x, y, z)
# Example usage
# chunk = ...  # Assume this is a Chunk object with blocks already set
# render = ...  # Assume this is the render node in Panda3D
# render_chunk(render, chunk, 0, 0)
