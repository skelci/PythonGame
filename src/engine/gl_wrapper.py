#?attr CLIENT

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame



def init():
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)



def update_resolution(resolution):
    width, height = resolution
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()



def load_texture(surface):
    texture_data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_size()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    return tex_id



def draw_texture(tex_id, x, y, w, h):
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    
    # bottom-left
    glTexCoord2f(0.0, 0.0)
    glVertex2f(x, y)
    
    # bottom-right
    glTexCoord2f(1.0, 0.0)
    glVertex2f(x + w, y)
    
    # top-right
    glTexCoord2f(1.0, 1.0)
    glVertex2f(x + w, y + h)
    
    # top-left
    glTexCoord2f(0.0, 1.0)
    glVertex2f(x, y + h)
    
    glEnd()



def clear():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()


