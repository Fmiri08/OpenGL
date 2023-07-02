from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import math
import random
import numpy
import pyrr
from enum import Enum
from Engine.Texture import Texture

class TypeOfObject(Enum):
    NOTHING = 0,
    WALL = 1,
    TREE = 2

class Map:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.cellSize = 20

        self.table = [[TypeOfObject.NOTHING for _ in range(
            self.width)] for _ in range(self.height)]

        for i in range(0, self.height):
            self.table[i][0] = TypeOfObject.WALL
            self.table[i][self.width - 1] = TypeOfObject.WALL

        for i in range(0, self.width):
            self.table[0][i] = TypeOfObject.WALL
            self.table[self.height - 1][i] = TypeOfObject.WALL

        index = 10
        while index < self.height:
            rnd = random.randint(0,2)
            if rnd == 2:
                self.table[index][1] = TypeOfObject.TREE
                self.table[index][2] = TypeOfObject.TREE 
                self.table[index][3] = TypeOfObject.TREE
                index +=5
            else:
                index+=1

        self.cube_vertices = self.getBoxVertices()
        self.tree_vertices = self.getTreeVertices()

        # kocka
        self.cube_vertices = numpy.array(self.cube_vertices, dtype=numpy.float32)
        self.tree_vertices = numpy.array(self.tree_vertices, dtype=numpy.float32)
        self.buffer = glGenBuffers(1)
        #glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        #glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes,
        #             cube_vertices, GL_STATIC_DRAW)
        #glBindBuffer(GL_ARRAY_BUFFER, 0)

        with open("Shaders/map.vert") as f:
            vertex_shader = f.read()

        with open("Shaders/map.frag") as f:
            fragment_shader = f.read()

        # A fajlbol beolvasott stringeket leforditjuk, es a ket shaderbol egy shader programot gyartunk.
        self.shader = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(
                fragment_shader, GL_FRAGMENT_SHADER))
        
        self.wallTexture = Texture("Images/Map/wall.png")
        self.treeTexture = Texture("Images/Tree/tree.png")

    def setLightPos(self, x, y, z):
        self.lightX = x
        self.lightY = y
        self.lightZ = z

    def render(self, camera, projectionMatrix):

        glUseProgram(self.shader)

        materialAmbientColor_loc = glGetUniformLocation(
            self.shader, "materialAmbientColor")
        materialDiffuseColor_loc = glGetUniformLocation(
            self.shader, "materialDiffuseColor")
        materialSpecularColor_loc = glGetUniformLocation(
            self.shader, "materialSpecularColor")
        materialEmissionColor_loc = glGetUniformLocation(
            self.shader, "materialEmissionColor")
        materialShine_loc = glGetUniformLocation(self.shader, "materialShine")
        glUniform3f(materialAmbientColor_loc, 0.25, 0.25, 0.25)
        glUniform3f(materialDiffuseColor_loc, 0.4, 0.4, 0.4)
        glUniform3f(materialSpecularColor_loc, 0.774597, 0.774597, 0.774597)
        glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
        glUniform1f(materialShine_loc, 76.8)

        lightAmbientColor_loc = glGetUniformLocation(
            self.shader, "lightAmbientColor")
        lightDiffuseColor_loc = glGetUniformLocation(
            self.shader, "lightDiffuseColor")
        lightSpecularColor_loc = glGetUniformLocation(
            self.shader, "lightSpecularColor")

        glUniform3f(lightAmbientColor_loc, 1.0, 1.0, 1.0)
        glUniform3f(lightDiffuseColor_loc, 1.0, 1.0, 1.0)
        glUniform3f(lightSpecularColor_loc, 1.0, 1.0, 1.0)

        lightPos_loc = glGetUniformLocation(self.shader, 'lightPos')
        viewPos_loc = glGetUniformLocation(self.shader, 'viewPos')
        glUniform3f(lightPos_loc, self.lightX, self.lightY, self.lightZ)
        glUniform3f(viewPos_loc, camera.x, camera.y, camera.z)

        proj_loc = glGetUniformLocation(self.shader, 'projection')
        view_loc = glGetUniformLocation(self.shader, 'view')
        world_loc = glGetUniformLocation(self.shader, 'world')
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projectionMatrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, camera.getMatrix())

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, self.cube_vertices.nbytes,
                     self.cube_vertices, GL_STATIC_DRAW)

        position_loc = glGetAttribLocation(self.shader, 'in_position')
        glEnableVertexAttribArray(position_loc)
        glVertexAttribPointer(position_loc, 3, GL_FLOAT,
                              False, 4 * 8, ctypes.c_void_p(0))

        normal_loc = glGetAttribLocation(self.shader, 'in_normal')
        glEnableVertexAttribArray(normal_loc)
        glVertexAttribPointer(normal_loc, 3, GL_FLOAT,
                              False, 4 * 8, ctypes.c_void_p(12))

        texture_loc = glGetAttribLocation(self.shader, 'in_texture')
        glEnableVertexAttribArray(texture_loc)
        glVertexAttribPointer(texture_loc, 2, GL_FLOAT,
                              False, 4 * 8, ctypes.c_void_p(24))


        Texture.enableTexturing()
        # fal renderelese
        self.wallTexture.activate()
        for row in range(0, self.height):
            for col in range(0, self.width):
                if self.table[row][col] == TypeOfObject.WALL:
                    transMat = pyrr.matrix44.create_from_translation(
                        pyrr.Vector3([col*self.cellSize, -10, row*self.cellSize]))
                    scaleMat = pyrr.matrix44.create_from_scale(
                        [self.cellSize, self.cellSize, self.cellSize])
                    worldMat = pyrr.matrix44.multiply(scaleMat, transMat)
                    glUniformMatrix4fv(world_loc, 1, GL_FALSE, worldMat)
                    glDrawArrays(GL_QUADS, 0, 24)
        

        glBufferData(GL_ARRAY_BUFFER, self.tree_vertices.nbytes,
                     self.tree_vertices, GL_STATIC_DRAW)

        self.treeTexture.activate()
        for row in range(0, self.height):
            for col in range(0, self.width):
                if self.table[row][col] == TypeOfObject.TREE:
                    transMat = pyrr.matrix44.create_from_translation(
                        pyrr.Vector3([col*self.cellSize+10, -10, row*self.cellSize]))
                    scaleMat = pyrr.matrix44.create_from_scale(
                        [self.cellSize, self.cellSize/2, self.cellSize])
                    worldMat = pyrr.matrix44.multiply(scaleMat, transMat)
                    glUniformMatrix4fv(world_loc, 1, GL_FALSE, worldMat)
                    glDrawArrays(GL_TRIANGLES, 0, 24)
                
        glBindBuffer(GL_ARRAY_BUFFER, 0)



    def getCellType(self, row, col):
        if row <= -1 or col <= -1 or row >= self.height or col >= self.width:
            return TypeOfObject.NOTHING
        return self.table[row][col]

    def isSomething(self, row, col):
        if self.table[row][col] == TypeOfObject.NOTHING:
            return False
        return True
    
    def getBoxVertices(self):
        return     [0.0, 1.0, 1.0,  0, 1, 0, 0, 0,
                    1.0, 1.0, 1.0,  0, 1, 0, 0, 1,
                    1.0, 1.0, 0.0,  0, 1, 0, 1, 1,
                    0.0, 1.0, 0.0,  0, 1, 0, 1, 0,

                    0.0, 0.0, 1.0,  0, -1, 0, 0, 0,
                    1.0, 0.0, 1.0,  0, -1, 0, 0, 1,
                    1.0, 0.0, 0.0,  0, -1, 0, 1, 1,
                    0.0, 0.0, 0.0,  0, -1, 0, 1, 0,

                    1.0, 0.0, 1.0,  1, 0, 0, 0, 0,
                    1.0, 0.0, 0.0,  1, 0, 0, 0, 1,
                    1.0, 1.0, 0.0,  1, 0, 0, 1, 1,
                    1.0, 1.0, 1.0,  1, 0, 0, 1, 0,

                    0.0, 0.0, 1.0,  -1, 0, 0, 0, 0,
                    0.0, 0.0, 0.0,  -1, 0, 0, 0, 1,
                    0.0, 1.0, 0.0,  -1, 0, 0, 1, 1,
                    0.0, 1.0, 1.0,  -1, 0, 0, 1, 0,

                    0.0,  0.0,  1.0, 0, 0, 1, 0, 0,
                    1.0,  0.0,  1.0, 0, 0, 1, 0, 1,
                    1.0,  1.0,  1.0, 0, 0, 1, 1, 1,
                    0.0,  1.0,  1.0, 0, 0, 1, 1, 0,

                    0.0,  0.0,  0.0, 0, 0, -1, 0, 0,
                    1.0,  0.0,  0.0, 0, 0, -1, 0, 1,
                    1.0,  1.0,  0.0, 0, 0, -1, 1, 1,
                    0.0,  1.0,  0.0, 0, 0, -1, 1, 0]
    
    def getTreeVertices(self):
        return      [-1,-1,-1,  0, 0,-1,  0,0,
                      1,-1,-1,  0, 0,-1,  1,0,
                      0, 1, 0,  0, 0,-1, 0.5,1,

                     -1,-1, 1,  0, 0, 1,   0,0,
                      1,-1, 1,  0, 0, 1,   1,0,
                      0, 1, 0,  0, 0, 1, 0.5,1,

                     -1,-1,-1, -1, 0, 0,   0,1,
                     -1,-1, 1, -1, 0, 0,   0,0,
                      0, 1, 0, -1, 0, 0, 0.5,1,

                      1,-1,-1,  1, 0, 0,   0,1,
                      1,-1, 1,  1, 0, 0,   0,0,
                      0, 1, 0,  1, 0, 0, 0.5,1,

                      1,-1,-1,  0,-1, 0,   1,1,
                      1,-1, 1,  0,-1, 0,   1,0,
                      0, 1, 0,  0,-1,0,  0.5,1,
                     
                     -1,-1, 1,  0, 1, 0,   0,0,
                     -1,-1,-1,  0, 1, 0,   0,1,
                      0, 1, 0,  0, 1, 0, 0.5,1]