#!/usr/bin/env python3

import sys
import ctypes
import numpy

from OpenGL import GL
from OpenGL.GL import shaders

import sdl2
from sdl2 import video

VERTEX_SHADER = \
"""
#version 330 core
layout (location=0) in vec4 position;
layout (location=1) in vec4 inColor;

// uniform transform
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec4 outColorF;
void main()
{

	// compute mvp
	mat4 mvp = projection * view * model;

	gl_Position = mvp * position;
	outColorF = inColor;
}
"""

FRAGMENT_SHADER = \
"""
#version 330 core
in vec4 outColorF;
out vec4 outColor;
void main()
{
	outColor = outColorF;
}
"""

def run():
	if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
		print(sdl2.SDL_GetError())
		return -1

	windowWidth = 800
	windowHeight = 600
	window = sdl2.SDL_CreateWindow( b"OpenGL demo",
								   sdl2.SDL_WINDOWPOS_CENTERED,
								   sdl2.SDL_WINDOWPOS_CENTERED, 
								   windowWidth, windowHeight,
								   sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE )
	if not window:
		print(sdl2.SDL_GetError())
		return -1

	# Force OpenGL 3.3 'core' context.
	# Must set *before* creating GL context!
	video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
	video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_MINOR_VERSION, 3)
	video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_PROFILE_MASK,
		video.SDL_GL_CONTEXT_PROFILE_CORE)
	context = sdl2.SDL_GL_CreateContext(window)

	# Setup GL shaders, data, etc.
	shaderProgram = None
	VAO = None
	VBO = None
	EBO = None

	vertexShader = shaders.compileShader( VERTEX_SHADER, GL.GL_VERTEX_SHADER )
	fragmentShader = shaders.compileShader( FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER )
	shaderProgram = shaders.compileProgram( vertexShader, fragmentShader, validate=False )

	vertexData = numpy.array([
	# Vertex Positions        # color
		-0.5, -0.5, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0,
		-0.5,  0.5, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0,
		 0.5,  0.5, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0,
		 0.5, -0.5, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0,

	], dtype=numpy.float32)

	indicesData = numpy.array( [ 0, 1, 2, 2, 3, 0 ], dtype=numpy.uint32 )

	# Core OpenGL requires that at least one OpenGL vertex array be bound
	VAO = GL.glGenVertexArrays(1)
	GL.glBindVertexArray(VAO)

	# Need VBO for triangle vertices and colours
	VBO = GL.glGenBuffers(1)
	GL.glBindBuffer( GL.GL_ARRAY_BUFFER, VBO )
	GL.glBufferData( GL.GL_ARRAY_BUFFER, 
				 		vertexData.nbytes, 
						vertexData,
						GL.GL_STATIC_DRAW )
	
	EBO = GL.glGenBuffers(1)
	GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, EBO)
	GL.glBufferData( GL.GL_ELEMENT_ARRAY_BUFFER, 
				 		indicesData.nbytes, 
						indicesData,
						GL.GL_STATIC_DRAW )
	
	# enable array and set up data
	GL.glEnableVertexAttribArray(0)
	GL.glEnableVertexAttribArray(1)

	# number of vertex
	numVertex = 4
	numColor = 4
	glFloatSize = 4

	# set vertex attribute
	GL.glVertexAttribPointer( 0, 
						  		numVertex, 
								GL.GL_FLOAT, 
								GL.GL_FALSE, 
								( numVertex + numColor ) * glFloatSize,
								None )
	
	# set color attribute
	# NOTE: the last parameter is a pointer
	GL.glVertexAttribPointer( 1, 
						  		numColor, 
								GL.GL_FLOAT, 
								GL.GL_FALSE, 
								( numVertex + numColor ) * glFloatSize,
								ctypes.c_void_p( numVertex * glFloatSize ) )

	GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
	GL.glBindVertexArray(0)

	# define event
	event = sdl2.SDL_Event()
	running = True

	while running:

		# wait event 
		sdl2.SDL_WaitEvent( ctypes.byref( event ) )
		
		if event.type == sdl2.SDL_QUIT:
			running = False

		# setup viewport
		GL.glViewport( 0, 0, windowWidth, windowHeight )

		# render
		GL.glClearColor(0, 0, 0, 1)
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

		# active shader program
		GL.glUseProgram(shaderProgram)
		GL.glBindVertexArray(VAO)

		# set mvp for this object
		# get model, view and project location
		model_m4 = numpy.identity( 4 )
		view_m4 = numpy.identity( 4 )
		projection_m4 = numpy.identity( 4 )
		GL.glUniformMatrix4fv(  GL.glGetUniformLocation( shaderProgram, "model" ), 
								1, 
								GL.GL_FALSE, 
								model_m4.T )
		GL.glUniformMatrix4fv(  GL.glGetUniformLocation( shaderProgram, "view" ), 
								1, 
								GL.GL_FALSE, 
								view_m4.T )
		GL.glUniformMatrix4fv(  GL.glGetUniformLocation( shaderProgram, "projection" ), 
								1, 
								GL.GL_FALSE, 
								projection_m4.T )
		
		# draw triangle
		GL.glDrawElements( GL.GL_TRIANGLES, len(indicesData), GL.GL_UNSIGNED_INT, None )

		# unbind
		GL.glBindVertexArray(0)
		GL.glUseProgram(0)

		sdl2.SDL_GL_SwapWindow(window)
		sdl2.SDL_Delay(10)

	sdl2.SDL_GL_DeleteContext(context)
	sdl2.SDL_DestroyWindow(window)
	sdl2.SDL_Quit()
	return 0

if __name__ == "__main__":
	sys.exit(run())