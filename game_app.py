from math import sin, cos

from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import Geom, GeomNode, GeomVertexFormat, GeomVertexData
from panda3d.core import GeomVertexWriter, GeomTriangles
from panda3d.core import LPoint3, LVector3, MouseButton
from panda3d.core import WindowProperties

from player import Player


def start_game():
    class GameApp(ShowBase):
        def __init__(self):
            ShowBase.__init__(self)

            props = WindowProperties()
            props.setSize(1600, 1200)
            props.setCursorHidden(True)
            self.win.requestProperties(props)

            # Disable default mouse camera control
            self.disableMouse()

            # Initialize camera position
            self.camera.setPos(0, -20, 0)
            self.velocity = LVector3(0, 0, 0)

            # Create vertex data for the cube
            vformat = GeomVertexFormat.getV3()
            vdata = GeomVertexData('cube', vformat, Geom.UHStatic)
            vertex = GeomVertexWriter(vdata, 'vertex')

            self.crosshair = OnscreenText(text='+', pos=(0, 0), scale=0.1, fg=(1, 0, 0, 1))

            vertices = [
                [-1, -1, -1], [-1, -1, 1], [-1, 1, 1], [-1, 1, -1],
                [1, -1, -1], [1, -1, 1], [1, 1, 1], [1, 1, -1]
            ]

            for v in vertices:
                vertex.addData3f(v[0], v[1], v[2])

            # Create geometry for the cube
            geom = Geom(vdata)
            tris = GeomTriangles(Geom.UHStatic)

            indices = [
                0, 1, 2, 0, 2, 3,
                4, 7, 6, 4, 6, 5,
                0, 3, 7, 0, 7, 4,
                1, 5, 6, 1, 6, 2,
                0, 4, 5, 0, 5, 1,
                2, 6, 7, 2, 7, 3
            ]

            for i in indices:
                tris.addVertex(i)

            geom.addPrimitive(tris)

            # Create node and attach geometry
            node = GeomNode('cube')
            node.addGeom(geom)
            self.node_path = self.render.attachNewNode(node)
            self.node_path.setScale(0.5, 0.5, 0.5)
            self.node_path.setPos(0, 10, 0)

            # Initialize rotation variables
            self.lastMousePos = None
            self.rotation = LPoint3(0, 0, 0)

            # Initialize jump and gravity variables
            self.jump_velocity = 0
            self.gravity = -60  # Negative value to pull the camera downwards
            self.is_jumping = False  # To check if the camera is currently in a jump

            # Add mouse event listeners
            self.accept("mouse1", self.on_mouse_down)
            self.accept("mouse1-up", self.on_mouse_up)

            # Initialize movement variables
            self.keyMap = {"w": 0, "a": 0, "s": 0, "d": 0}

            # Add keyboard event listeners
            self.accept("w", self.updateKeyMap, ["w", 1])
            self.accept("w-up", self.updateKeyMap, ["w", 0])
            self.accept("a", self.updateKeyMap, ["a", 1])
            self.accept("a-up", self.updateKeyMap, ["a", 0])
            self.accept("s", self.updateKeyMap, ["s", 1])
            self.accept("s-up", self.updateKeyMap, ["s", 0])
            self.accept("d", self.updateKeyMap, ["d", 1])
            self.accept("d-up", self.updateKeyMap, ["d", 0])
            self.accept("space", self.trigger_jump)

            # Add task to handle mouse drag and camera movement
            self.taskMgr.add(self.handle_mouse_drag, "handle_mouse_drag")
            self.taskMgr.add(self.move_camera, "move_camera")
            self.accept('escape', self.stop_game)

            # Initialize the player
            self.player = Player(0, -20, 0)
            self.initialize_player()
            self.initialize_player_cuboid()

            # Initialize third-person view flag
            self.third_person_view = False

            # Add F5 key event listener for toggling camera view
            self.accept("f5", self.toggle_camera_view)

        def toggle_camera_view(self):
            # Toggle the third-person view flag
            self.third_person_view = not self.third_person_view

        def initialize_player(self):
            # Create a cuboid to represent the player
            node = GeomNode('player')
            geom = Geom(self.node_path.node().get_geom(0).get_vertex_data())
            node.addGeom(geom)
            self.player_node_path = self.render.attachNewNode(node)

            # Set the cuboid's initial position based on the player object
            x, y, z = self.player.position
            self.player_node_path.setPos(x, y, z)

            # Do not parent the camera to the player's node here

        def initialize_player_cuboid(self):
            # Create a cuboid to represent the player
            vformat = GeomVertexFormat.getV3()
            vdata = GeomVertexData('player_cube', vformat, Geom.UHStatic)
            vertex = GeomVertexWriter(vdata, 'vertex')

            vertices = [
                [-1, -1, -1], [-1, -1, 1], [-1, 1, 1], [-1, 1, -1],
                [1, -1, -1], [1, -1, 1], [1, 1, 1], [1, 1, -1]
            ]

            for v in vertices:
                vertex.addData3f(v[0], v[1], v[2])

            # Create geometry for the cube
            geom = Geom(vdata)
            tris = GeomTriangles(Geom.UHStatic)

            indices = [
                0, 1, 2, 0, 2, 3,
                4, 7, 6, 4, 6, 5,
                0, 3, 7, 0, 7, 4,
                1, 5, 6, 1, 6, 2,
                0, 4, 5, 0, 5, 1,
                2, 6, 7, 2, 7, 3
            ]

            for i in indices:
                tris.addVertex(i)

            geom.addPrimitive(tris)

            # Create node and attach geometry
            player_node = GeomNode('player_cuboid')
            player_node.addGeom(geom)
            self.player_cuboid = self.render.attachNewNode(player_node)
            self.player_cuboid.setScale(0.3, 0.3, 0.9)

            # Convert the tuple to LVector3 and then adjust the position to make it visible
            player_position = LVector3(*self.player.position)
            self.player_cuboid.setPos(player_position + LVector3(0, 0, 2))
            self.player_cuboid.setColor(1, 0, 0, 1)

        def trigger_jump(self):
            if not self.is_jumping:
                self.jump_velocity = 15  # Initial velocity for the jump
                self.is_jumping = True  # Set the jumping flag to True

        def stop_game(self):
            self.userExit()

        def updateKeyMap(self, key, value):
            self.keyMap[key] = value

        def on_mouse_down(self):
            if self.mouseWatcherNode.hasMouse():
                x = self.mouseWatcherNode.getMouseX()
                y = self.mouseWatcherNode.getMouseY()
                self.lastMousePos = LPoint3(x, y, 0)

        def on_mouse_up(self):
            self.lastMousePos = None

        def handle_mouse_drag(self, task):
            if self.mouseWatcherNode.hasMouse():
                x = self.mouseWatcherNode.getMouseX()
                y = self.mouseWatcherNode.getMouseY()

                currentMousePos = LPoint3(x, y, 0)

                if self.lastMousePos is not None:
                    # Calculate the difference between the last and current mouse positions
                    diff = currentMousePos - self.lastMousePos

                    # Update rotation based on mouse movement
                    self.rotation.x += diff.y * 20
                    self.rotation.y -= diff.x * 20

                    # Limit pitch to [-90, 90] degrees
                    self.rotation.x = max(min(90, self.rotation.x), -90)

                    # Set the new rotation to the camera
                    self.camera.setHpr(self.rotation.y, self.rotation.x, 0)

                    # Handle third-person view
                    if self.third_person_view:
                        # Parameters for third-person view
                        distance = 5  # distance from player
                        height = 0  # height above player
                        angle = 30  # downward angle in degrees

                        # Convert the player's heading angle to radians
                        heading = self.rotation.y * (3.14159 / 180.0)
                        pitch = angle * (3.14159 / 180.0)  # Convert downward angle to radians

                        # Calculate the camera's position relative to the player using spherical coordinates
                        x = self.player.position[0] + distance * sin(heading) * cos(pitch)
                        y = self.player.position[1] - distance * cos(heading) * cos(pitch)
                        z = self.player.position[2] + distance * sin(pitch)

                        third_person_position = LVector3(x, y, z)

                        # Set the third-person camera position
                        self.camera.setPos(third_person_position)
                    else:
                        # Reset the camera's position and rotation to the player's when not in third-person view
                        self.camera.setPos(self.player.position)
                        self.camera.setHpr(self.rotation.y, self.rotation.x, 0)

                # Center the mouse cursor
                self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)

                # Update the last mouse position to the centered position
                self.lastMousePos = LPoint3(0, 0, 0)

            return task.cont

        def move_camera(self, task):
            speed = 15  # The base speed of camera movement (increased to 10)
            alpha = 0.1  # The rate of interpolation (0 < alpha < 1)
            dt = globalClock.getDt()  # Delta time for frame-independent movement

            # Calculate the camera's orientation vector
            heading = self.camera.getH() * (3.14159 / 180.0)  # Convert to radians
            orientation = LVector3(-1 * speed * sin(heading), speed * cos(heading), 0)

            # Calculate desired movement direction based on keyMap and camera orientation
            desired_movement = LVector3(0, 0, 0)
            if self.keyMap["w"]:
                desired_movement += orientation
            if self.keyMap["s"]:
                desired_movement -= orientation
            if self.keyMap["a"]:
                desired_movement -= LVector3(orientation.y, -orientation.x, 0)
            if self.keyMap["d"]:
                desired_movement += LVector3(orientation.y, -orientation.x, 0)

            # Interpolate between the current and desired velocity for smoother motion
            self.velocity.x = (1 - alpha) * self.velocity.x + alpha * desired_movement.x
            self.velocity.y = (1 - alpha) * self.velocity.y + alpha * desired_movement.y

            # Apply gravity and jump logic
            self.jump_velocity += self.gravity * dt  # Update jump velocity based on gravity
            vertical_movement = self.jump_velocity * dt  # Calculate vertical movement

            # Update the camera's vertical position
            new_vertical_position = self.player_node_path.getPos().z + vertical_movement
            if new_vertical_position < 0:  # Check for ground collision
                new_vertical_position = 0
                self.is_jumping = False  # Reset jumping flag
                self.jump_velocity = 0  # Reset jump velocity

            # Update the camera's position based on the velocity and vertical movement
            new_position = LVector3(
                self.player_node_path.getPos().x + self.velocity.x * dt,
                self.player_node_path.getPos().y + self.velocity.y * dt,
                new_vertical_position
            )
            self.player_node_path.setPos(new_position)

            # Update the player's position based on the camera's new position
            self.player.position = self.player_node_path.getPos()

            # Update the player's cuboid position
            self.player_cuboid.setPos(self.player.position)
            self.player_cuboid.setHpr(self.rotation.y, 0, 0)

            return task.cont

    app = GameApp()
    app.run()
    return True
