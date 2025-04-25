#?attr CLIENT

"""
This module contains the Icon class, which is used to create an icon for the GUI system.
"""

from components.widget import Widget
from components.datatypes import *



class Icon(Widget):
    """ Represents an icon widget. It renders an icon on the screen using a specified image. """
    
    def __init__(self, name, position, size, material, layer=0, visible=True, subwidgets = {}, subwidget_offsets = {}, subwidget_alignments = {}):
        """
        For more information about the parameters, refer to the Widget class.
        Args:
            material: Material object representing the icon image.
        """
        super().__init__(name, position, size, Color(0, 0, 0, 0), layer, visible, subwidgets, subwidget_offsets, subwidget_alignments)

        self.material = material


    @property
    def surface(self):
        surface = super().surface
        surface.blit(self.material.get_surface(self.size), (0, 0))
        return surface
    

