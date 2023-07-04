import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import compileProgram, compileShader
from Engine.Skybox import SkyBox
from Engine.Camera import Camera
from Engine.Texture import Texture
import numpy
import pyrr
from Map import Map

from Ground import Ground

xPosPrev = 0
yPosPrev = 0
firstCursorCallback = True
sensitivity = 0.05

def cursorCallback(window, xPos, yPos):
	global firstCursorCallback
	global sensitivity
	global xPosPrev, yPosPrev
	if firstCursorCallback:
		firstCursorCallback = False	
	else:
		xDiff = xPos - xPosPrev
		yDiff = yPosPrev - yPos
		camera.rotateUpDown(yDiff * sensitivity)
		camera.rotateRightLeft(xDiff * sensitivity)

	xPosPrev = xPos
	yPosPrev = yPos


if not glfw.init():
	raise Exception("glfw init hiba")
	
window = glfw.create_window(1280, 720, "Chrome is offline", None, None)
glfw.set_window_pos(window, 0, 0)

if not window:
	glfw.terminate()
	raise Exception("glfw window init hiba")
 
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
glfw.set_cursor_pos_callback(window, cursorCallback)
glfw.make_context_current(window)
glEnable(GL_DEPTH_TEST)
glViewport(0, 0, 1280, 720)

camera = Camera(50, 0, 30)
ground = Ground(0, -10, 0, 6000, 6000)
map = Map(5, 75)

with open("./shaders/texture.vert") as f:
	vertex_shader = f.read()
with open("./shaders/texture.frag") as f:
	fragment_shader = f.read()

shader = compileProgram(
	compileShader(vertex_shader, GL_VERTEX_SHADER),
	compileShader(fragment_shader, GL_FRAGMENT_SHADER),
	validate=False
)

perspMat = pyrr.matrix44.create_perspective_projection_matrix(45.0, 1280.0 / 720.0, 0.1, 1000.0)

glUseProgram(shader)

lightX = 0.0
lightY = 0.0
lightZ = 0.0
map.setLightPos(lightX, lightY, lightZ)
lightPos_loc = glGetUniformLocation(shader, 'lightPos')
viewPos_loc = glGetUniformLocation(shader, 'viewPos')

glUniform3f(lightPos_loc, lightX, lightY, lightZ)
glUniform3f(viewPos_loc, camera.x, camera.y, camera.z )

materialAmbientColor_loc = glGetUniformLocation(shader, "materialAmbientColor")
materialDiffuseColor_loc = glGetUniformLocation(shader, "materialDiffuseColor")
materialSpecularColor_loc = glGetUniformLocation(shader, "materialSpecularColor")
materialEmissionColor_loc = glGetUniformLocation(shader, "materialEmissionColor")
materialShine_loc = glGetUniformLocation(shader, "materialShine")

lightAmbientColor_loc = glGetUniformLocation(shader, "lightAmbientColor")
lightDiffuseColor_loc = glGetUniformLocation(shader, "lightDiffuseColor")
lightSpecularColor_loc = glGetUniformLocation(shader, "lightSpecularColor")

glUniform3f(lightAmbientColor_loc, 1.0, 1.0, 1.0)
glUniform3f(lightDiffuseColor_loc, 1.0, 1.0, 1.0)
glUniform3f(lightSpecularColor_loc, 1.0, 1.0, 1.0)

glUniform3f(materialAmbientColor_loc, 0.0, 0.0, 0.0)
glUniform3f(materialDiffuseColor_loc, 0.0, 0.0, 0.0)
glUniform3f(materialSpecularColor_loc, 0.0, 0.0, 0.0)
glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
glUniform1f(materialShine_loc, 10)	

perspectiveLocation = glGetUniformLocation(shader, "projection")
worldLocation = glGetUniformLocation(shader, "world")
viewLocation = glGetUniformLocation(shader, "view")
viewWorldLocation = glGetUniformLocation(shader, "viewWorld")

glUniformMatrix4fv(perspectiveLocation, 1, GL_FALSE, perspMat)

viewMat = pyrr.matrix44.create_look_at([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0])
startTime = 0
run_speed = 125 
speed = run_speed
exitProgram=False

skyBox = SkyBox(
	"./Images/Skybox/right.jpg", 
	"./Images/Skybox/left.jpg", 
	"./Images/Skybox/top.jpg", 
	"./Images/Skybox/bottom.jpg", 
	"./Images/Skybox/front.jpg", 
	"./Images/Skybox/back.jpg"
)

elapsedTime = 0
jumpDir = "none"

while not glfw.window_should_close(window) and not exitProgram:
	startTime = glfw.get_time()
	if jumpDir == "up":
		camera.y += (50*elapsedTime)
		if camera.y >= 17:
			jumpDir = "down"
	if jumpDir == "down":
		camera.y-=(50*elapsedTime)
		if camera.y <= 0:
			jumpDir = "none"
	glfw.poll_events()
	
	if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
		exitProgram = True
	if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
		speed = 0
	if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
		speed = run_speed
	if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS and jumpDir == "none":
		jumpDir = "up"

	camera.move(elapsedTime*speed)
	cellX, cellZ = camera.getCellPosition(20)

	if map.isSomething(cellZ, cellX) and camera.y < 8: # itt nézi meg hogy beleütköztél-e valamibe
		exitProgram = True
	
	glClearDepth(1.0)
	glClearColor(0, 0.1, 0.1, 1)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
	glEnable(GL_DEPTH_TEST)

	skyBox.render(perspMat, camera.getMatrixForCubemap())
	ground.render(camera.getMatrix(), perspMat)
	map.render(camera, perspMat)
	
	glUseProgram(shader)
	glUniform3f(viewPos_loc, camera.x, camera.y, camera.z )	
	skyBox.activateCubeMap(shader, 1)

	endTime = glfw.get_time()
	elapsedTime = endTime - startTime

	
	glfw.swap_buffers(window)
	
glfw.terminate()

