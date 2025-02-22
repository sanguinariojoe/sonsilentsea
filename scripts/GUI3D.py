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

import bge
from bge import logic as g
from mathutils import *
from math import *

def update():
	""" Updates the indicator.
	"""
	controller = g.getCurrentController()
	own        = controller.owner

	v_dir      = own['to'] - own['from']
	l          = v_dir.length
	a          = atan2(v_dir.y,v_dir.x)
	own.worldScale       = Vector((l,1.0,1.0))
	own.worldOrientation = Euler((0.0, 0.0, a), 'XYZ')
	own.worldPosition    = Vector((own['from'].x,own['from'].y,own.worldPosition.z))

def load():
	""" Register some variables for the object
	"""
	controller = g.getCurrentController()
	own        = controller.owner

	if 'from' not in own:
		own['from'] = Vector((0.0, 0.0))
	if 'to' not in own:
		own['to'] = Vector((1.0, 0.0))

