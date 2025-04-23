#?attr CLIENT

"""
Renderer module for the game engine.
"""

from components.datatypes import *
from components.actor import Actor
from components.widget import Widget
from components.background import Background

import pygame

import time



class Renderer:
    """
    Renderer class for managing the Pygame display and rendering.
    This class handles everything related to the display.
    """


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
        self.__screen = None
        self.__fullscreen = False
        self.__windowed = True

        self.resolution = Vector(width, height)
        self.title = title
        self.camera_width = camera_width
        self.fullscreen = fullscreen
        self.windowed = windowed
        self.camera_position = camera_position

        self.__actors_to_draw = {}
        self.__widgets_to_draw = []

        print("[Client] Renderer initialized")


    @property
    def resolution(self):
        """
        Vector - The window dimensions represented as a vector (width, height). This value is used to set the display mode.
        """
        return self.__resolution


    @resolution.setter
    def resolution(self, value):
        if isinstance(value, Vector) and value.x > 0 and value.y > 0:
            self.__resolution = value
            self.__screen = pygame.display.set_mode((value.x, value.y),
                                                    pygame.FULLSCREEN if self.fullscreen else 0 |
                                                    pygame.NOFRAME if not self.windowed else 0 |
                                                    pygame.DOUBLEBUF | pygame.HWSURFACE)
        else:
            raise TypeError("Width must be a positive integer:", value)
        

    @property
    def title(self):
        """
        str - The title of the window. This value is used to set the window caption.
        """
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
        """
        Vector - The position of the camera in the game world. This value is used to determine the rendering offset.
        """
        return self.__camera_position
    

    @camera_position.setter
    def camera_position(self, value):
        if isinstance(value, Vector):
            self.__camera_position = value
        else:
            raise TypeError("Camera position must be a Vector:", value)
        

    @property
    def camera_width(self):
        """
        float - The width of the camera in game world units. This value is used to scale the rendering of actors and widgets.
        """
        return self.__camera_width
    

    @camera_width.setter
    def camera_width(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__camera_width = value
        else:
            raise TypeError("Camera width must be a positive number:", value)
        

    @property
    def fullscreen(self):
        """
        bool - Indicates whether the display is in fullscreen mode. If True, the display occupies the entire screen.
        It also overrides resolution and windowed settings.
        """
        return self.__fullscreen
    

    @fullscreen.setter
    def fullscreen(self, value):
        if isinstance(value, bool):
            self.__fullscreen = value
            self.__resolution = Vector(pygame.display.Info().current_w, pygame.display.Info().current_h) if value else self.resolution
            self.__screen = pygame.display.set_mode((self.resolution.x, self.resolution.y),
                                                    pygame.FULLSCREEN if value else 0 |
                                                    pygame.NOFRAME if not self.windowed else 0 |
                                                    pygame.DOUBLEBUF | pygame.HWSURFACE)
        else:
            raise TypeError("Fullscreen must be a bool:", value)
        

    @property
    def windowed(self):
        """
        bool - Indicates whether the display is in windowed mode. If True, the window header is shown.
        """
        return self.__windowed
    

    @windowed.setter
    def windowed(self, value):
        if isinstance(value, bool):
            self.__windowed = value
            self.__screen = pygame.display.set_mode((self.resolution.x, self.resolution.y),
                                                    pygame.FULLSCREEN if self.fullscreen else 0 |
                                                    pygame.NOFRAME if not value else 0 |
                                                    pygame.DOUBLEBUF | pygame.HWSURFACE)
        else:
            raise TypeError("Windowed must be a bool:", value)
        

    @property
    def screen(self):
        """
        pygame.display - The Pygame display surface.
        """
        return self.__screen
    

    @property
    def actors_to_draw(self):
        """
        dict[int, set[Actor]] - Dictionary of actors to draw, where key is the render layer and value is a set of actors.
        """
        return self.__actors_to_draw
    

    @property
    def widgets_to_draw(self):
        """
        Returns:
            list[Widget] - List of widgets to draw for current frame.
        """
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
        """
        Called only by engine at the beginning of the frame.
        This method clears buffers from previous frame.
        """
        self.__widgets_to_draw.clear()


    def render(self):
        """
        Called only by the engine after background is drawn.
        It draws actors and widgets.\n
        Returns:
            tuple[float, float] - Time taken to draw actors and widgets respectively.
        """
        camera_ratio = self.resolution.x / self.camera_width
        
        time_start = time.time()

        magic_scale = camera_ratio * 2 * 1.0005 ** self.camera_width * 1.003 ** ((1600 / self.resolution.y) ** 1.8 - 1) # Magic number to prevent gaps between tiles
        layers = sorted(self.actors_to_draw.keys())
        for layer in layers:
            actors = self.actors_to_draw[layer]
            for a in actors:
                top_left_position = (
                    camera_ratio * (a.position.x - a.half_size.x - self.camera_position.x) + self.resolution.x / 2,
                    camera_ratio * -(a.position.y + a.half_size.y - self.camera_position.y) + self.resolution.y / 2 # Invert the y-axis
                )

                surface = a.material.get_surface(a.half_size * magic_scale)
                self.screen.blit(surface, top_left_position)

        time_actors = time.time()

        self.__widgets_to_draw.sort(key = lambda w: w.layer)
        for w in self.widgets_to_draw:
            self.__draw_widget(w)

        time_widgets = time.time()

        pygame.display.flip()

        return (time_actors - time_start, time_widgets - time_actors)


    def draw_background(self, background: Background):
        """
        Called only by engine at the beginning of the frame after buffers are cleared.
        It draws background.
        """
        bg_surface = background.get_bg_surface(self.camera_position, self.resolution, self.camera_width)
        self.screen.blit(bg_surface, (0, 0))


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



