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
from math import *
from mathutils import *

# ----------------------------
# Ship properties
# ----------------------------

# gravity [m/s2]
grav = 9.8

# Ship displacement [kg]
# Take care on the spinbonx limits in the bullet
# physics engine
disp  = 850.0E3

# Percentage of hydrostatic lift submerging
sLift = 0.98

# Stability parameter [m]
GMT = 0.5
GML = 60.0

# Engine power [W]
# (diesel for emerged, electric for submerged)
dPower = 1.0E6
ePower = 280.0E3

# Efficiency
nu_d = 0.6
nu_m = 0.8

# Reversed march efficiency
nu_r = 0.25

controller = g.getCurrentController()
ship       = controller.owner
# Force factor due to the Blender physic properties limit
mFact = ship.mass / disp
# Register some variables
if not 'diesel_power' in ship:
	ship['diesel_power'] = dPower
if not 'electric_power' in ship:
	ship['electric_power'] = ePower


# ----------------------------
# Speed conversions
# ----------------------------
def knot_to_ms(speed):
	return 0.51444*speed

def ms_to_knot(speed):
	return 1.94386*speed

# ----------------------------
# Forces computation
# ----------------------------
def drag(speed):
	""" Computes the drag force
	@param speed Ship speed in m/s
	@return Drag force in Newtons.
	"""
	K = 0.06
	M = disp
	return K * M**0.666 * speed**3

def propulsion(power,speed):
	""" Propulsion force
	@param power Engine power applied (W).
	@param speed Ship speed in m/s
	@return Propulsion force in Newtons.
	"""
	return nu_d * nu_m * power # / speed

def force(ship):
	""" Compute the force vector
	@param ship Ship game object
	@return ship force [N]. 
	"""
	# The speed is known from the instance
	speed = ship.localLinearVelocity[0]
	# The power depends on the march
	march = ship['speed']
	if abs(march) > 3:
		march = int(copysign(3,march))
		ship['speed'] = march
	power = dPower
	if ship.worldPosition[2] < -1.0:
		# ship is submerged
		power = ePower
	m = float(march)
	if m < 0:
		power *= nu_r
		m     *= -1.0
	power *= sqrt(m/3.0)
	# Compute advancing force vector
	fx = copysign(propulsion(power, speed),march) - drag(speed)
	# Compute the lateral advancing force (turning process)
	speed = ship.localLinearVelocity[1]
	fy = - 100.0 * drag(speed)
	# Align it with the ship
	f = ship.worldOrientation * Vector((fx,fy,0.0))
	# Add the hydrostatic lift and damping
	if ship['submerging'] > 0:
		ship['submerging'] = 1
		if ship.worldPosition[2] < 0.1:
			f[2] += grav*disp
		if ship.worldPosition[2] < -0.1:
			f[2] += 0.1*grav*disp
	elif not ship['submerging']:
		f[2] += grav*disp
		speed = ship.worldLinearVelocity
		if abs(speed[2]) < 0.03:
			speed[2] = 0.0
			ship.setLinearVelocity(speed,False)
	else:
		ship['submerging'] = -1
		f[2] += sLift*grav*disp
	speed = ship.worldLinearVelocity[2]
	f[2] -= 10000.0 * drag(speed)
	return f

# ----------------------------
# Balancing motion computation
# ----------------------------
def sea(ship):
	""" Defines the moment by the sea
	@param ship Ship game object
	"""
	z = ship.worldPosition[2]
	if z < -2.0:
		return 0.0
	if z > 0.0:
		z = 0.0
	T = 11.0
	w = 2*pi/T
	A = 0.7E6 * (2.0 + z)/2.0
	return A*cos(w*ship['timer'])

def righting(ship):
	""" Defines the righting moment
	@param ship Ship game object
	"""
	st = Vector((0.0,0.0,1.0)).dot(ship.localOrientation*Vector((0.0,1.0,0.0)))
	return -disp*GMT*st

def viscous(ship):
	""" Defines the viscouss moment
	@param ship Ship game object
	"""
	w = ship.localAngularVelocity[0]
	K = 1.0E6
	return -K*w

def heading(ship):
	""" Defines the heading moment
	@param ship Ship game object
	"""
	st = -Vector((0.0,0.0,1.0)).dot(ship.localOrientation*Vector((1.0,0.0,0.0)))
	w  = ship.localAngularVelocity[1]
	K  = 1.0E7
	return -(disp*GML*st + K*w)

def yaw(ship):
	""" Defines the yaw drag moment
	@param ship Ship game object
	"""
	w  = ship.localAngularVelocity[2]
	K  = 1.0E7
	return -K*w

def moment(ship):
	""" Compute the moment vector
	@param ship Ship game object
	@return ship moment [N m]. 
	"""
	# The angular velocity is known from the ship
	w = ship.localAngularVelocity[0]
	# Compute balancing moment vector
	mx = sea(ship) + righting(ship) + viscous(ship)
	# Compute heading moment vector
	my = heading(ship)
	# Compute the yaw damping
	mz = yaw(ship)
	# Align it with the ship
	m  = Vector((mx,my,mz))
	m = ship.worldOrientation * m
	return m

def rudder(ship):
	""" Compute the rudder moment. The rudder introduce
	two moments, one to turn, and one to balance due to
	the excentric position.
	@param ship Ship game object
	@return ship moment vector [N m]. 
	"""
	r = ship['rudder']
	# Allowed 3 rudder levels
	if abs(r) > 3:
		r = int(copysign(3,r))
		ship['rudder'] = r
	if not r:
		return Vector((0.0,0.0,0.0))
	# Compute the force generated by the wings
	rad   = Vector((28.75,0.0,0.0))
	speed = ship.localLinearVelocity[0]
	K     = 2.0E3
	if(abs(speed) > 7.0):
		K = 2.0E3*max( 0.25, 1.0 - (abs(speed)-7.0)/3.0 )
	f     = K * r/3.0 * speed*abs(speed)
	m     = f*rad.zyx
	return m

def update():
	""" Update the ship motions.
	@note Call this method each frame
	"""
	# Advancing forces
	f = force(ship) * mFact
	ship.applyForce(f, False)
	
	# Balacing moments
	m = moment(ship) * mFact
	ship.applyTorque(m, False)
	
	# Rudder moments
	m = rudder(ship) * mFact
	ship.applyTorque(Vector((m[0],0.0,0.0)), False)
	ship.applyTorque(Vector((0.0,0.0,m[2])), True)

