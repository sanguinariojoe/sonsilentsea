#    Copyright (c) 2013, 2014
#    Jose Luis Cercos-Pita <jlcercos@gmail.com>
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from os import path

try:
    import bgui
except:
    print('Warning! Can not import bgui')
import bge
from bge import logic as g
from bge import texture
from math import *
from mathutils import *

# Get the ship
controller = g.getCurrentController()
owner      = controller.owner
ship       = owner.parent

# Get the GUI manager (if exist)
scene   = g.getCurrentScene()
objects = scene.objects
camera  = scene.active_camera
gui     = None
if 'gui' in camera:
		# Create our system and show the mouse
		gui = camera['gui']

# Get the images path
blend_file  = path.dirname(__file__)
images_path = path.join(path.dirname(blend_file), 'GUI')

gui_shipZ     = 11.0
gui_minZ      = 1.0

speed_angles = (radians(0.0),
                radians(43.0),
                radians(85.0),
                radians(127.0))
rudder_angles = (radians(0.0),
                 radians(1.0/3.0*19.0),
                 radians(2.0/3.0*19.0),
                 radians(19.0))
d_angle      = radians(1.0)

depth_limits = (0.0, 260.0)
depth_angles = (radians(130.0), radians(-130.0))

# Compute de widgets dimensions
widget_dims  = [0.25,0.25]
image_dims   = [0.05,0.05]
w = bge.render.getWindowWidth()
h = bge.render.getWindowHeight()
aspect_ratio = h / w
if aspect_ratio > 1.0:
	widget_dims[1] /= aspect_ratio
	image_dims[0]  *= aspect_ratio
else:
	widget_dims[0] *= aspect_ratio
	image_dims[1]  /= aspect_ratio
pbar_dims  = [0.25,0.025]



# Create the widgets
if gui:
	widget = bgui.ProgressBar(gui, "player_visibility", percent=0.0, size=[pbar_dims[0], pbar_dims[1]],
	                    pos=[0.975-pbar_dims[0], pbar_dims[1] + image_dims[1]],
	                    sub_theme='RedGUI', options = bgui.BGUI_DEFAULT)
	widget = bgui.ProgressBar(gui, "player_noise", percent=0.0, size=[pbar_dims[0], pbar_dims[1]],
	                    pos=[0.975-pbar_dims[0], pbar_dims[1]],
	                    sub_theme='RedGUI', options = bgui.BGUI_DEFAULT)
	img = path.join(images_path,'depth.blender.png')
	widget = bgui.Image(gui, 'player_depth', img,
	         size=[widget_dims[0], widget_dims[1]], pos=[0.1*widget_dims[0], 0.1*widget_dims[1]],
	         options = bgui.BGUI_DEFAULT|bgui.BGUI_CACHE)
	img = path.join(images_path,'depth.blender.Indicator.png')
	bgui.Image(widget, 'player_depth_indicator', img,
               size=[1.0, 1.0], pos=[0.0, 0.0],
	           options = bgui.BGUI_DEFAULT|bgui.BGUI_CACHE)
	img = path.join(images_path,'throttle_rudder.blender.png')
	widget = bgui.Image(gui, 'player_throttle', img,
                        size=[widget_dims[0], widget_dims[1]], pos=[1.2*widget_dims[0], 0.1*widget_dims[1]],
	                    options = bgui.BGUI_DEFAULT|bgui.BGUI_CACHE)
	img = path.join(images_path,'throttle.blender.Indicator.png')
	bgui.Image(widget, 'player_throttle_indicator', img,
               size=[1.0, 1.0], pos=[0.0, 0.0],
	           options = bgui.BGUI_DEFAULT|bgui.BGUI_CACHE)
	img = path.join(images_path,'rudder.Indicator.png')
	bgui.Image(widget, 'player_rudder_indicator', img,
               size=[1.0, 1.0], pos=[0.0, 0.0],
	           options = bgui.BGUI_DEFAULT|bgui.BGUI_CACHE)
	img = path.join(images_path,'Actions-layer-visible-off-icon.png')
	widget = bgui.Image(gui, 'player_visibility_img', img, size=[image_dims[0], image_dims[1]],
	                    pos=[0.975-pbar_dims[0]-image_dims[0], pbar_dims[1] + image_dims[1]],
	                    options = bgui.BGUI_DEFAULT|bgui.BGUI_CACHE)
	img = path.join(images_path,'Actions-speaker-icon.png')
	widget = bgui.Image(gui, 'player_noise_img', img, size=[image_dims[0], image_dims[1]],
	                    pos=[0.975-pbar_dims[0]-image_dims[0], pbar_dims[1]],
	                    options = bgui.BGUI_DEFAULT|bgui.BGUI_CACHE)

def update_speed():
	""" Update the speed indicator
	@note Call this method each frame
	"""
	if not gui:
		return
	throttle   = ship['speed']
	widget     = gui.children['player_throttle']
	subwidget  = widget.children['player_throttle_indicator']
	angle      = subwidget.rotation
	objective  = copysign(speed_angles[abs(throttle)], -throttle)
	if (angle < objective + d_angle) and (angle > objective - d_angle):
		return
	rot = copysign(d_angle, objective - angle)
	subwidget.rotation = angle + rot

def update_rudder():
	""" Update the speed indicator
	@note Call this method each frame
	"""
	if not gui:
		return
	rudder     = ship['rudder']
	widget     = gui.children['player_throttle']
	subwidget  = widget.children['player_rudder_indicator']
	angle      = subwidget.rotation
	objective  = copysign(rudder_angles[abs(rudder)], -rudder)
	if (angle < objective + d_angle) and (angle > objective - d_angle):
		return
	rot = copysign(d_angle, objective - angle)
	subwidget.rotation = angle + rot

def update_depth():
	""" Update the depth indicator
	@note Call this method each frame
	"""
	if not gui:
		return
	# Rotate the indicator
	h = -ship.worldPosition[2]
	f = (h - depth_limits[0]) / (depth_limits[1] - depth_limits[0])
	if f < 0.0:
		f = 0.0
	if f > 1.0:
		f = 1.0
	angle = (1.0-f)*depth_angles[0] + f*depth_angles[1]
	widget     = gui.children['player_depth']
	subwidget  = widget.children['player_depth_indicator']
	subwidget.rotation = angle

def update():
	""" Update the GUI manager
	@note Call this method each frame
	"""
	if not gui:
		return
	update_speed()
	update_rudder()
	update_depth()

