#?attr CLIENT

"""
Renderer module for the game engine.
"""

from engine.log import log_client as log
from engine.log import LogType
from engine.datatypes import *
from engine.components.actors.actor import Actor
from engine.components.ui.widget import Widget
from engine.components.background import *
from engine.components.material import Material

import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import ctypes



class QuadMesh:
    """ Mesh class for rendering quads. This class handles the OpenGL vertex array and buffer objects for rendering. """

    def __init__(self, actor):
        self.actor = actor

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        self.vbo_data_allocated = False
        self.create_vertex_array(actor) 

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(16))

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)


    def create_vertices(self, actor):
        a = actor.half_size
        p = actor.position
        r = actor.render_layer
        self.prev_actor = (p, a)

        # x, y, s, t, z
        self.vertices = np.array([
            -a.x + p.x, -a.y + p.y, 0.0, 1.0, -r / 1024,
            -a.x + p.x,  a.y + p.y, 0.0, 0.0, -r / 1024,
             a.x + p.x, -a.y + p.y, 1.0, 1.0, -r / 1024,
             a.x + p.x,  a.y + p.y, 1.0, 0.0, -r / 1024,
        ], dtype=np.float32)


    def create_vertex_array(self, actor):
        self.create_vertices(actor)
        self.vertex_count = 4

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        if not self.vbo_data_allocated:
            glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_DYNAMIC_DRAW)
            self.vbo_data_allocated = True
        else:
            glBufferSubData(GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)


    def draw(self):
        if self.prev_actor != (self.actor.position, self.actor.half_size):
            self.create_vertex_array(self.actor)
        
        self.actor.material.use()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, self.vertex_count)


    def __del__(self):
        try:
            if glDeleteVertexArrays and self.vao:
                glDeleteVertexArrays(1, [self.vao])
            if glDeleteBuffers and self.vbo:
                glDeleteBuffers(1, [self.vbo])
        except Exception:
            log("Failed to delete OpenGL buffers", LogType.ERROR)


    
class WidgetMesh(QuadMesh):
    """ Mesh class for rendering widgets. """
    def __init__(self, widget, top_left_pos, size):
        self.top_left_pos = top_left_pos
        self.size = size
        super().__init__(widget)


    def create_vertices(self, widget):
        r = -(widget.layer + 512) / 1024
        t = self.top_left_pos
        s = self.size
        
        # x, y, s, t, z
        self.vertices = np.array([
            -1 + t.x,       1 - t.y - s.y, 0, 1, r,
            -1 + t.x,       1 - t.y,       0, 0, r,
            -1 + t.x + s.x, 1 - t.y - s.y, 1, 1, r,
            -1 + t.x + s.x, 1 - t.y,       1, 0, r,
        ], dtype=np.float32)

    
    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, self.vertex_count)



class BackgroundMesh:
    """ Mesh class for rendering background layers. """

    def __init__(self, layer, screen_res, camera_width):
        layer.material.load()
        self.layer = layer

        material_half_size = self.layer.material.size / 2
        scaled_material_half_size = material_half_size / material_half_size.x * self.layer.width
        self.scaled_material_size = scaled_material_half_size * 2

        tiles = (camera_width / self.scaled_material_size * (screen_res / screen_res.x)).ceiled + 1
        half_tiles = tiles // 2
        
        self.meshes = []

        for x in range(int(-half_tiles.x), int(-half_tiles.x + tiles.x)):
            for y in range(int(-half_tiles.y), int(-half_tiles.y + tiles.y)):
                obj = Actor("actor", Vector(x, y) * scaled_material_half_size * 2, scaled_material_half_size, material=self.layer.material, render_layer=self.layer.render_layer)
                self.meshes.append(QuadMesh(obj))

        
    def draw(self, camera_pos, camer_pos_uniform):
        camera_pos = (camera_pos * self.layer.scroll_speed) % self.scaled_material_size - self.scaled_material_size
        glUniform2f(camer_pos_uniform, *camera_pos)

        for mesh in self.meshes:
            mesh.draw()



class Renderer:
    """ Renderer class for managing the Pygame display and rendering. This class handles everything related to the display. """

    def __init__(self, width: int, height: int, camera_width: float, title = "Pygame Window", fullscreen = False, windowed = True, camera_position = Vector()):
        """
        Args:
            width: Width of the window.
            height: Height of the window.
            camera_width: Width of the camera in game world units.
            title: Title of the window.
            fullscreen: If True, the display is in fullscreen mode.
            windowed: If True, the display is in windowed mode.
            camera_position: Position of the camera in the game world.
        Raises:
            TypeError: If any of the arguments are of incorrect type.
        """
        pygame.init()

        self.resolution = Vector(width, height)
        self.title = title

        self.fullscreen = fullscreen
        self.windowed = windowed
        self.resizeable = False

        self.__camera_width = camera_width
        self.camera_position = camera_position
        
        self.__screen = pygame.display.set_mode(self.resolution.tuple, self.window_flags)

        self.__actors_to_draw = {}
        self.__widgets_to_draw = []
        self.__screen_needs_update = False

        # OpenGL stuff
        glClearColor(*Color())
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.__shaders = {}

        self.__shaders["actor"] = self.__create_shader("actor_vertex.txt")
        glUseProgram(self.__shaders["actor"])

        self.__camera_pos_uniform = glGetUniformLocation(self.__shaders["actor"], "cameraPos")

        glUniform1i(glGetUniformLocation(self.__shaders["actor"], "imageTexture"), 0)
        glUniform2f(self.__camera_pos_uniform, *self.camera_position)
        glUniform2f(glGetUniformLocation(self.__shaders["actor"], "scale"), *(self.resolution.x / self.resolution / self.camera_width * 2))

        self.background = Background("default", (BackgroundLayer(Material(Color()), 4, 1), ))

        self.__shaders["widget"] = self.__create_shader("widget_vertex.txt")
        glUseProgram(self.__shaders["widget"])

        # glUniform1f(glGetUniformLocation(self.__shaders["widget"], "scale_y"), self.resolution.y / self.resolution.x)

        log("Renderer initialized", LogType.INFO)


    def __del__(self):
        glDeleteProgram(self.__shaders["actor"])
        glDeleteProgram(self.__shaders["widget"])


    def __create_shader(self, vertex_src, fragment_src = "fragment.txt"):
        with open(f"src/engine/core/shaders/{vertex_src}", "r") as f:
            vertex_src = f.readlines()

        with open(f"src/engine/core/shaders/{fragment_src}", "r") as f:
            fragment_src = f.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        return shader


    @property
    def window_flags(self):
        """ int - The window flags used to create the display. This value is used to set the display mode. """
        return (
            pygame.FULLSCREEN if self.fullscreen else 0 |
            pygame.NOFRAME if not self.windowed else 0 |
            pygame.RESIZABLE if self.__resizeable else 0 |
            pygame.DOUBLEBUF | pygame.OPENGL
        )


    @property
    def resolution(self):
        """ Vector - The window dimensions represented as a vector (width, height). This value is used to set the display mode. """
        return self.__resolution


    @resolution.setter
    def resolution(self, value):
        if isinstance(value, Vector) and value.x > 0 and value.y > 0:
            self.__resolution = value
            self.__previous_ressolution = value
            self.__screen_needs_update = True
        else:
            raise TypeError("Width must be a positive integer:", value)
        

    @property
    def title(self):
        """ str - The title of the window. This value is used to set the window caption. """
        return self.__title
    

    @title.setter
    def title(self, value):
        if isinstance(value, str):
            self.__title = value
            pygame.display.set_caption(self.__title)
        else:
            raise TypeError("Title must be a string:", value)
        

    @property
    def camera_position(self):
        """ Vector - The position of the camera in the game world. This value is used to determine the rendering offset. """
        return self.__camera_position
    

    @camera_position.setter
    def camera_position(self, value):
        if isinstance(value, Vector):
            self.__camera_position = value
        else:
            raise TypeError("Camera position must be a Vector:", value)
        

    @property
    def camera_width(self):
        """ float - The width of the camera in game world units. This value is used to scale the rendering of actors and widgets. """
        return self.__camera_width
    

    @camera_width.setter
    def camera_width(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__camera_width = value
            glUseProgram(self.__shaders["actor"])
            glUniform2f(glGetUniformLocation(self.__shaders["actor"], "scale"), *(self.resolution.x / self.resolution / self.camera_width * 2))
        else:
            raise TypeError("Camera width must be a positive number:", value)
        

    @property
    def fullscreen(self):
        """ bool - Indicates whether the display is in fullscreen mode. If True, the display occupies the entire screen. It also overrides resolution and windowed settings. """
        return self.__fullscreen
    

    @fullscreen.setter
    def fullscreen(self, value):
        if isinstance(value, bool):
            self.__fullscreen = value
            self.__screen_needs_update = True
            self.resolution = Vector(pygame.display.Info().current_w, pygame.display.Info().current_h) if value else self.__previous_ressolution
        else:
            raise TypeError("Fullscreen must be a bool:", value)
        

    @property
    def windowed(self):
        """ bool - Indicates whether the display is in windowed mode. If True, the window header is shown. """
        return self.__windowed
    

    @windowed.setter
    def windowed(self, value):
        if isinstance(value, bool):
            self.__windowed = value
            self.__screen_needs_update = True
        else:
            raise TypeError("Windowed must be a bool:", value)
        

    @property
    def resizeable(self):
        """ bool - Indicates whether the display is resizeable. If True, the window can be resized. """
        return self.__resizeable
    

    @resizeable.setter
    def resizeable(self, value):
        if isinstance(value, bool):
            self.__resizeable = value
            self.__screen_needs_update = True
        else:
            raise TypeError("Resizeable must be a bool:", value)
        

    @property
    def background(self):
        """ Background - The background object used for rendering. """
        return self.__background
    

    @background.setter
    def background(self, value):
        if isinstance(value, Background):
            self.__background = value
            self.__background_meshes = [BackgroundMesh(layer, self.resolution, self.camera_width) for layer in self.__background.layers]
        else:
            raise TypeError("Background must be a Background instance:", value)


    @property
    def screen(self):
        """ pygame.display - The Pygame display surface. """
        return self.__screen
    

    @property
    def actors_to_draw(self):
        """ dict[int, set[Actor]] - Dictionary of actors to draw, where key is the render layer and value is a set of actors. """
        return self.__actors_to_draw
    

    @property
    def widgets_to_draw(self):
        """ list[Widget] - List of widgets to draw for current frame. """
        return self.__widgets_to_draw


    def add_actor_to_draw(self, actor: Actor):
        """
        Called only by engine.
        It adds actor to the list of actors to draw.\n
        Args:
            actor: Actor to add to the list of actors to draw.
        Raises:
            TypeError: If actor is not a subclass of Actor.
        """
        if not isinstance(actor, Actor):
            raise TypeError("Actor must be a subclass of Actor:", actor)
        if actor.render_layer not in self.__actors_to_draw:
            self.__actors_to_draw[actor.render_layer] = {}
        actor.material.load()
        self.__actors_to_draw[actor.render_layer][actor.name] = QuadMesh(actor)


    def remove_actor_from_draw(self, actor: Actor):
        """
        Called only by engine.
        It removes actor from the list of actors to draw.\n
        Args:
            actor: Actor to remove from the list of actors to draw.
        Raises:
            TypeError: If actor is not a subclass of Actor.
            ValueError: If actor is not found in the list of actors to draw.
        """
        if not isinstance(actor, Actor):
            raise TypeError("Actor must be a subclass of Actor:", actor)
        if actor.name in self.__actors_to_draw[actor.render_layer]:
            self.__actors_to_draw[actor.render_layer].pop(actor.name)
        else:
            raise ValueError("Actor not found in actors to draw:", actor)
        

    def add_widget_to_draw(self, widget: Widget):
        """
        Called only by engine before rendering begins.
        It adds widget to the list of widgets to draw for current frame.\n
        Args:
            widget: Widget to add to the list of widgets to draw.
        Raises:
            TypeError: If widget is not a subclass of Widget.
        """
        if not isinstance(widget, Widget):
            raise TypeError("Widget must be a subclass of Widget:", widget)
        
        self.__widgets_to_draw.append(widget)

    
    def clear(self):
        """ Called only by engine at the beginning of the frame. This method clears buffers from previous frame. """
        self.__widgets_to_draw.clear()


    def render(self):
        """
        Called only by the engine after background is drawn.
        It draws actors and widgets.\n
        Returns:
            tuple[float, float] - Time taken to draw actors and widgets respectively.
        """
        if self.__screen_needs_update:
            self.__screen = pygame.display.set_mode(self.resolution.tuple, self.window_flags)
            self.__screen_needs_update = False
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.__shaders["actor"])
        for layer_mesh in self.__background_meshes:
            layer_mesh.draw(self.camera_position, self.__camera_pos_uniform)

        glUniform2f(self.__camera_pos_uniform, *self.camera_position)

        layers = sorted(self.__actors_to_draw.keys())
        for layer in layers:
            meshes = self.__actors_to_draw[layer].values()
            for mesh in meshes:
                mesh.draw()

        glUseProgram(self.__shaders["widget"])
        self.__widgets_to_draw.sort(key = lambda w: w.layer)
        for w in self.widgets_to_draw:
            self.__draw_widget(w)

        pygame.display.flip()


    def __update_widget_screen_rect(self, widget, top_left_pos, camera_ratio):
        widget.screen_rect = (top_left_pos, camera_ratio)

        if hasattr(widget, "subwidgets"):
            for subwidget_key in widget.subwidgets.keys():
                subwidget_top_left_pos = widget.subwidget_pos(subwidget_key) + top_left_pos
                self.__update_widget_screen_rect(widget.subwidgets[subwidget_key], subwidget_top_left_pos, camera_ratio)


    def __draw_widget(self, widget):
        camera_ratio = self.resolution / Vector(1600, 900)
        top_left_position = widget.position / Vector(1600, 900) * 2
        size = widget.size / Vector(1600, 900) * 2
        size.y *= camera_ratio.y / camera_ratio.x

        self.__update_widget_screen_rect(widget, top_left_position, camera_ratio.x)

        surface = widget.surface

        # surface = pygame.transform.scale(surface, size.tuple)

        surface_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, surface_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        width, height = surface.get_size()
        # self.__size = Vector(width, height)
        image_data = pygame.image.tostring(surface, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        widget_mesh = WidgetMesh(widget, top_left_position, size)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, surface_id)
        
        widget_mesh.draw()

        glDeleteTextures(1, [surface_id])

        # self.screen.blit(surface, top_left_position.tuple)



