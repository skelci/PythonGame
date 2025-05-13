#?attr CLIENT

"""
Renderer module for the game engine.
"""

from engine.log import log_client as log
from engine.log import LogType
from engine.datatypes import *
from engine.components.actors.actor import Actor
from engine.components.ui.widget import Widget
from engine.components.background import Background

import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import time
import ctypes



class Quad:
    def __init__(self, position):
        self.position = np.array(position, dtype=np.float32)      



class QuadMesh:
    def __init__(self):
        # x, y, s, t
        self.vertices = np.array([
            -1, -1, 0, 1,
            -1,  1, 0, 0,
             1, -1, 1, 0,

             1,  1, 1, 0,
            -1,  1, 0, 0,
             1, -1, 1, 0
        ], dtype=np.float32)

        self.vertex_count = 6

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))


    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))



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

        self.camera_width = camera_width
        self.camera_position = camera_position
        
        self.__screen = pygame.display.set_mode(self.resolution.tuple, self.window_flags)

        self.__actors_to_draw = {}
        self.__widgets_to_draw = []
        self.__screen_needs_update = False

        # OpenGL stuff
        glClearColor(*Color(0, 0, 0).normalized)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.__shader = self.__create_shader()
        glUseProgram(self.__shader)
        glUniform1i(glGetUniformLocation(self.__shader, "imageTexture"), 0)
        
        self.triangle = QuadMesh()

        log("Renderer initialized", LogType.INFO)


    def __del__(self):
        glDeleteProgram(self.__shader)


    def __create_shader(self):
        with open("src/engine/core/shaders/vertex.txt", "r") as f:
            vertex_src = f.readlines()

        with open("src/engine/core/shaders/fragment.txt", "r") as f:
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
            self.__actors_to_draw[actor.render_layer] = set()
        actor.material.load_texture()
        self.__actors_to_draw[actor.render_layer].add(actor)


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
        if actor in self.__actors_to_draw[actor.render_layer]:
            self.__actors_to_draw[actor.render_layer].remove(actor)
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
        # camera_ratio = self.resolution.x / self.camera_width
        
        time_start = time.time()

        glClear(GL_COLOR_BUFFER_BIT)

        layers = sorted(self.actors_to_draw.keys())
        for layer in layers:
            actors = self.actors_to_draw[layer]
            for a in actors:
                a.material.use()
                break
            break

        glBindVertexArray(self.triangle.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count)
        # magic_scale = camera_ratio * 2 * 1.0005 ** self.camera_width * 1.003 ** ((1600 / self.resolution.y) ** 1.8 - 1) # Magic number to prevent gaps between tiles
        #         top_left_position = (
        #             camera_ratio * (a.position.x - a.half_size.x - self.camera_position.x) + self.resolution.x / 2,
        #             camera_ratio * -(a.position.y + a.half_size.y - self.camera_position.y) + self.resolution.y / 2 # Invert the y-axis
        #         )

        #         surface = a.material.get_surface(a.half_size * magic_scale)
        #         self.screen.blit(surface, top_left_position)

        time_actors = time.time()

        # self.__widgets_to_draw.sort(key = lambda w: w.layer)
        # for w in self.widgets_to_draw:
        #     self.__draw_widget(w)

        time_widgets = time.time()

        pygame.display.flip()

        return (time_actors - time_start, time_widgets - time_actors)


    # def draw_background(self, background: Background):
    #     """ Called only by engine at the beginning of the frame after buffers are cleared. It draws background. """
        # bg_surface = background.get_bg_surface(self.camera_position, self.resolution, self.camera_width)
        # self.screen.blit(bg_surface, (0, 0))


    def __update_widget_screen_rect(self, widget, top_left_pos, camera_ratio):
        widget.screen_rect = (top_left_pos, camera_ratio)

        if hasattr(widget, "subwidgets"):
            for subwidget_key in widget.subwidgets.keys():
                subwidget_top_left_pos = widget.subwidget_pos(subwidget_key) + top_left_pos
                self.__update_widget_screen_rect(widget.subwidgets[subwidget_key], subwidget_top_left_pos, camera_ratio)


    def __draw_widget(self, widget):
        camera_ratio = self.resolution / Vector(1600, 900)
        top_left_position = camera_ratio * widget.position
        size = widget.size * camera_ratio.x

        self.__update_widget_screen_rect(widget, top_left_position, camera_ratio.x)

        surface = widget.surface
        surface = pygame.transform.scale(surface, size.tuple)

        self.screen.blit(surface, top_left_position.tuple)



