#?attr CLIENT
from components.datatypes import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
import pygame
import numpy as np



# ---- Shader sources ----
VERTEX_SHADER_SRC = """
#version 330 core
layout (location = 0) in vec2 position;
layout (location = 1) in vec2 texcoord;
out vec2 Texcoord;
uniform mat4 projection;
void main(){
    gl_Position = projection * vec4(position, 0.0, 1.0);
    Texcoord = texcoord;
}
"""


FRAGMENT_SHADER_SRC = """
#version 330 core
in vec2 Texcoord;
out vec4 outColor;
uniform sampler2D tex;
void main(){
    outColor = texture(tex, Texcoord);
}
"""




class GLWrapper:
    shader_program = None  # Will be set in init_shaders()


    @staticmethod
    def init():
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    @staticmethod
    def init_shaders():
        # Compile and link shader program
        vertex_shader = shaders.compileShader(VERTEX_SHADER_SRC, GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(FRAGMENT_SHADER_SRC, GL_FRAGMENT_SHADER)
        GLWrapper.shader_program = shaders.compileProgram(vertex_shader, fragment_shader)
        glUseProgram(GLWrapper.shader_program)
        # Set default sampler uniform to texture unit 0.
        glUniform1i(glGetUniformLocation(GLWrapper.shader_program, "tex"), 0)
        glUseProgram(0)


    @staticmethod
    def update_resolution(resolution):
        if not GLWrapper.shader_program:
            GLWrapper.init_shaders()

        width, height = resolution
        glViewport(0, 0, width, height)
        # Build an orthographic projection matrix.
        # Note: Here we use a simple orthographic projection.
        proj = np.array([
            [2/width, 0, 0, -1],
            [0, 2/height, 0, -1],
            [0, 0, -1, 0],
            [0, 0, 0, 1],
        ], dtype=np.float32)
        glUseProgram(GLWrapper.shader_program)
        loc = glGetUniformLocation(GLWrapper.shader_program, "projection")
        glUniformMatrix4fv(loc, 1, GL_TRUE, proj)
        glUseProgram(0)


    @staticmethod
    def load_texture(surface):
        texture_data = pygame.image.tostring(surface, "RGBA", True)
        width, height = surface.get_size()
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)
        return tex_id


    @staticmethod
    def delete_texture(tex_id):
        glDeleteTextures(int(tex_id))


    @staticmethod
    def draw_quad(x, y, w, h):
        # Legacy quad drawing (unused in our shader method)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex2f(x, y)
        glTexCoord2f(1.0, 0.0); glVertex2f(x + w, y)
        glTexCoord2f(1.0, 1.0); glVertex2f(x + w, y + h)
        glTexCoord2f(0.0, 1.0); glVertex2f(x, y + h)
        glEnd()


    @staticmethod
    def draw_texture(tex_id, x, y, w, h):
        glBindTexture(GL_TEXTURE_2D, tex_id)
        GLWrapper.draw_quad(x, y, w, h)
        glBindTexture(GL_TEXTURE_2D, 0)


    @staticmethod
    def draw_colored_quad(x, y, w, h, color):
        glColor4f(*color.normalized)
        GLWrapper.draw_quad(x, y, w, h)


    @staticmethod
    def clear():
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()



class QuadBatch:
    def __init__(self):
        self.vbo_id = glGenBuffers(1)
        self.ebo_id = glGenBuffers(1)  # Create an Element Buffer Object
        self.vertex_data = []
        self.index_data = []
        self.count_quads = 0
        self.__create_vao_and_vbo()

    def add_quad(self, x, y, w, h, u0=0.0, v0=0.0, u1=1.0, v1=1.0):
        # Append 4 vertices for the quad.
        base_index = self.count_quads * 4
        self.vertex_data.extend([x,       y,      u0, v0,   # bottom-left
                                 x + w,   y,      u1, v0,   # bottom-right
                                 x + w,   y + h,  u1, v1,   # top-right
                                 x,       y + h,  u0, v1])  # top-left
        # Append indices to form two triangles: [0, 1, 2, 0, 2, 3]
        self.index_data.extend([base_index, base_index+1, base_index+2,
                                base_index, base_index+2, base_index+3])
        self.count_quads += 1
        return self.count_quads - 1

    def upload(self):
        # Upload vertex data
        arr = np.array(self.vertex_data, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id)
        glBufferData(GL_ARRAY_BUFFER, arr.nbytes, arr, GL_STATIC_DRAW)
        # Upload index data
        idx_arr = np.array(self.index_data, dtype=np.uint32)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo_id)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx_arr.nbytes, idx_arr, GL_STATIC_DRAW)

    def __create_vao_and_vbo(self):
        # Create and bind VAO
        self.vao_id = glGenVertexArrays(1)
        glBindVertexArray(self.vao_id)
        # Bind VBO for vertex data
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id)
        # Set up vertex attributes (stride = 16 bytes)
        glEnableVertexAttribArray(0)  # position
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)  # texcoord
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
        # Bind EBO (this association with the VAO remains)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo_id)
        glBindVertexArray(0)

    def draw(self, texture_id):
        glUseProgram(GLWrapper.shader_program)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glBindVertexArray(self.vao_id)
        # Now use glDrawElements with count = total indices
        glDrawElements(GL_TRIANGLES, len(self.index_data), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)

    def clear(self):
        self.vertex_data.clear()
        self.index_data.clear()
        self.count_quads = 0


