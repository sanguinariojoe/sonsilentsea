import sys
import os
from os import path
from math import *

# So we can find the bgui module.
# Should be improved...
paths = [sys.prefix,
		 path.abspath('./')]
for p in paths:
    if not p in sys.path:
        sys.path.append(p)

import bgui
import bge

NCAMPS_PER_PAGE = 5
NMISSS_PER_PAGE = 5

GUI_MENU = ['campaigns', 'missions']

class GuiSys(bgui.System):
	"""
	A subclass to handle our game specific gui
	"""
	def __init__(self):
		# Initialize the system
		bgui.System.__init__(self, './resources/GUI')
		
		# Use an invisible frame to store all of our widgets
		self.frame = bgui.Frame(self, 'window', border=0, sub_theme='Root')

		# -----------------------------------------		
		# Create a main campaigns menu window
		# -----------------------------------------		
		self.campMenu = bgui.Frame(self, 'campaigns', size=[0.6, 0.8],
		options=bgui.BGUI_DEFAULT|bgui.BGUI_CENTERED)

		# Add the label
		bgui.Label(self.campMenu, 'campLabel', text="Select a Campaign", pos=[0.5, 0.9],
		sub_theme='Large', options = bgui.BGUI_DEFAULT | bgui.BGUI_CENTERX)

		# Create the campaingns buttons
		N  = NCAMPS_PER_PAGE
		dy = 0.8 / (3.0*N + 1.0)
		for i in range(N):
			button = bgui.FrameButton(self.campMenu, 'campButton{0}'.format(i), text='{0}:'.format(i),
			size=[0.9, 2.0*dy], pos=[0.05, 0.9 - (3 + 3*i)*dy], options = bgui.BGUI_DEFAULT)
			button.on_click = self._on_select_camp

		# Pages navigation
		self.campPag = 1
		bgui.Label(self.campMenu, 'campPages', text="1 / 1", pos=[0.5, 0.05],
		options = bgui.BGUI_DEFAULT | bgui.BGUI_CENTERX)
		button = bgui.FrameButton(self.campMenu, 'campPrev'.format(i), text='<',
		size=[0.08, 0.08], pos=[0.3, 0.025], options = bgui.BGUI_DEFAULT)
		button.on_click = self._on_prev_camp_page
		button = bgui.FrameButton(self.campMenu, 'campNext'.format(i), text='>',
		size=[0.08, 0.08], pos=[0.62, 0.025], options = bgui.BGUI_DEFAULT)
		button.on_click = self._on_next_camp_page

		# -----------------------------------------		
		# Create a missions menu window
		# -----------------------------------------		
		self.missMenu = bgui.Frame(self, 'missions', size=[0.6, 0.6],
		options=bgui.BGUI_DEFAULT|bgui.BGUI_CENTERED)

		# Add the label
		bgui.Label(self.missMenu, 'missLabel', text="Select a Mission", pos=[0.5, 0.9],
		sub_theme='Large', options = bgui.BGUI_DEFAULT | bgui.BGUI_CENTERX)

		# Create the missions buttons
		N  = NMISSS_PER_PAGE
		dy = 0.8 / (3.0*N + 1.0)
		for i in range(N):
			button = bgui.FrameButton(self.missMenu, 'missButton{0}'.format(i), text='{0}:'.format(i),
			size=[0.9, 2.0*dy], pos=[0.05, 0.9 - (3 + 3*i)*dy], options = bgui.BGUI_DEFAULT)
			button.on_click = self._on_select_miss

		# Pages navigation
		self.missPag = 1
		bgui.Label(self.missMenu, 'missPages', text="1 / 1", pos=[0.5, 0.05],
		options = bgui.BGUI_DEFAULT | bgui.BGUI_CENTERX)
		button = bgui.FrameButton(self.missMenu, 'missPrev'.format(i), text='<',
		size=[0.08, 0.08], pos=[0.3, 0.025], options = bgui.BGUI_DEFAULT)
		button.on_click = self._on_prev_miss_page
		button = bgui.FrameButton(self.missMenu, 'missNext'.format(i), text='>',
		size=[0.08, 0.08], pos=[0.62, 0.025], options = bgui.BGUI_DEFAULT)
		button.on_click = self._on_next_miss_page

		# Back to campaigns menu button
		button = bgui.FrameButton(self.missMenu, 'missBack'.format(i), text='Back',
		size=[0.15, 0.08], pos=[0.025, 0.025], options = bgui.BGUI_DEFAULT)
		button.on_click = self._on_miss_back

		# -----------------------------------------
		# Create a progress bar window (hiden)
		# -----------------------------------------
		"""
		p_bar_win = bgui.Frame(self, 'progress_bar_win', size=[0.8, 0.2],
		options=bgui.BGUI_DEFAULT|bgui.BGUI_CENTERED)
		bgui.Label(p_bar_win, 'progress_bar_label', text="", pos=[0.5, 0.75],
		sub_theme='Small', options = bgui.BGUI_DEFAULT | bgui.BGUI_CENTERX)
		bgui.ProgressBar(p_bar_win, "progress_bar_pbar", percent=0.0, size=[0.95, 0.4], pos=[0.025, 0.15],
		options=bgui.BGUI_DEFAULT | bgui.BGUI_CENTERX)											
		p_bar_win.visible = False
		"""

		# -----------------------------------------		
		# Create a keymap for keyboard input
		# -----------------------------------------		
		self.keymap = {}
		for val in dir(bge.events):
			if val.endswith('KEY') or val.startswith('PAD'):
				try:
					bgeVal  = getattr(bge.events, val)
					bguiVal = getattr(bgui, val)
					self.keymap[bgeVal] = bguiVal
				except:
					continue

		# -----------------------------------------		
		# Setup the initial GUI
		# -----------------------------------------		
		self._activeCampaign = None
		self._activeMission  = None

		# Initialize in the campaigns menu
		self.set_active_menu('campaigns')
		self._read_campaigns()
		self._setup_camp_GUI()

	def set_active_menu(self,name):
		""" Activate the GUI desired menu, use None to disable all """
		# Hide all
		for g in GUI_MENU:
			widget = self.children[g]
			widget.visible = False
		# And show only the active one
		if name == None:
			return
		self._active_menu = name
		widget = self.children[name]
		widget.visible = True

	def _on_select_camp(self,widget):
		self._activeCampaign = widget.text
		self.set_active_menu('missions')
		self._read_missions()
		self._setup_miss_GUI()

	def _on_prev_camp_page(self,widget):
		self.campPag -= 1
		self._setup_camp_GUI()

	def _on_next_camp_page(self,widget):
		self.campPag += 1
		self._setup_camp_GUI()

	def _setup_camp_GUI(self):
		# Compute the needed pages
		n      = NCAMPS_PER_PAGE
		nPages = (len(self.camps)-1) // n + 1
		nPages = max(0,nPages)
		self.campPag = max(self.campPag,1)      # Minimum page is 1
		self.campPag = min(self.campPag,nPages) # If exist
		self.campMenu.children['campPages'].text = '{0} / {1}'.format(self.campPag, nPages)
		# Froze the previous/next buttons if needed
		self.campMenu.children['campPrev'].frozen = False
		self.campMenu.children['campNext'].frozen = False
		if self.campPag <= 1:
			self.campMenu.children['campPrev'].frozen = True
		if self.campPag >= nPages:
			self.campMenu.children['campNext'].frozen = True
		# Compute the start and end campaigns indexes
		first = max(0, n*(self.campPag-1))
		last  = min(first + n, len(self.camps))
		# Activate the required buttons
		for i in range(0,last-first):
			button = self.campMenu.children['campButton{0}'.format(i)]
			button.visible = True
			button.frozen  = False
			button.text    = self.camps[first + i]
		# And Deactivate the other ones
		for i in range(last-first,n):
			button = self.campMenu.children['campButton{0}'.format(i)]
			button.visible = False
			button.frozen  = True
			button.text    = ''

	def _read_campaigns(self):
		"""Look for the available campaign directories"""
		# Setup the available paths to look for campaigns
		paths = [path.join(sys.prefix,'share/sonsilentsea/resources/Campaigns'),
		         path.join(path.abspath('./'),'resources/Campaigns'),
		         path.expanduser('~/.sonsilentsea/resources/Campaigns')]
		# Look for campaigns
		camps    = []
		campDirs = {}
		for p in paths:
			# Test if the directory exists
			if not path.isdir(p):
				continue
			# Add all the campaigns
			for f in os.listdir(p):
				if path.isdir(path.join(p,f)) and f != '__pycache__':
					camps.append(f)
					campDirs[f] = path.join(p,f)
		camps.sort()
		# Create the final names and associated folders
		self.camps    = []
		self.campDirs = {}
		for c in camps:
			# Read the name from the file
			try:
				f = open(path.join(campDirs[c],'name'))
				name = f.readline()
				f.close()
			except:
				name = c
			self.camps.append( name )
			self.campDirs[name] = campDirs[c]
		return self.camps

	def _on_select_miss(self,widget):
		self._activeMission = widget.text
		self.set_active_menu(None)
		# Get the mission directory
		miss = self._activeMission
		p    = self.missDirs[miss]
		# Extract the mission and campaign folder names
		p,m  = path.split(p)
		c    = path.basename(p)
		own['mission_manager'].load_mission(c,m)

	def _on_prev_miss_page(self,widget):
		self.missPag -= 1
		self._setup_miss_GUI()

	def _on_next_miss_page(self,widget):
		self.missPag += 1
		self._setup_miss_GUI()

	def _on_miss_back(self,widget):
		self.set_active_menu('campaigns')
		self._read_campaigns()
		self._setup_camp_GUI()

	def _setup_miss_GUI(self):
		# Compute the needed pages
		n      = NMISSS_PER_PAGE
		nPages = (len(self.misss)-1) // n + 1
		nPages = max(0,nPages)
		self.missPag = max(self.missPag,1)      # Minimum page is 1
		self.missPag = min(self.missPag,nPages) # If exist
		self.missMenu.children['missPages'].text = '{0} / {1}'.format(self.missPag, nPages)
		# Froze the previous/next buttons if needed
		self.missMenu.children['missPrev'].frozen = False
		self.missMenu.children['missNext'].frozen = False
		if self.missPag <= 1:
			self.missMenu.children['missPrev'].frozen = True
		if self.missPag >= nPages:
			self.missMenu.children['missNext'].frozen = True
		# Compute the start and end missions indexes
		first = max(0, n*(self.missPag-1))
		last  = min(first + n, len(self.misss))
		# Activate the required buttons
		for i in range(0,last-first):
			button = self.missMenu.children['missButton{0}'.format(i)]
			button.visible = True
			button.frozen  = False
			button.text    = self.misss[first + i]
		# And Deactivate the other ones
		for i in range(last-first,n):
			button = self.missMenu.children['missButton{0}'.format(i)]
			button.visible = False
			button.frozen  = True
			button.text    = ''

	def _read_missions(self):
		"""Look for the available missions in the campaign directory"""
		# Get the campaign directory
		camp = self._activeCampaign
		if camp == None:
			return[]
		p    = self.campDirs[camp]
		# Look for missions
		misss    = []
		missDirs = {}
		# Test if the directory exists
		if not path.isdir(p):
			return[]
		# Add all the missions
		for f in os.listdir(p):
			if path.isdir(path.join(p,f)) and f != '__pycache__':
				misss.append(f)
				missDirs[f] = path.join(p,f)
		misss.sort()
		# Create the final names and associated folders
		self.misss    = []
		self.missDirs = {}
		for m in misss:
			# Read the name from the file
			try:
				f = open(path.join(missDirs[m],'name'))
				name = f.readline()
				f.close()
			except:
				name = m
			self.misss.append( name )
			self.missDirs[name] = missDirs[m]
		return self.misss

	def main(self):
		"""A high-level method to be run every frame"""
		
		# Handle the mouse
		mouse = bge.logic.mouse
		
		pos = list(mouse.position)
		pos[0] *= bge.render.getWindowWidth()
		pos[1] = bge.render.getWindowHeight() - (bge.render.getWindowHeight() * pos[1])
		
		mouse_state = bgui.BGUI_MOUSE_NONE
		mouse_events = mouse.events
				
		if mouse_events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_JUST_ACTIVATED:
			mouse_state = bgui.BGUI_MOUSE_CLICK
		elif mouse_events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_JUST_RELEASED:
			mouse_state = bgui.BGUI_MOUSE_RELEASE
		elif mouse_events[bge.events.LEFTMOUSE] == bge.logic.KX_INPUT_ACTIVE:
			mouse_state = bgui.BGUI_MOUSE_ACTIVE
		
		self.update_mouse(pos, mouse_state)
		
		# Handle the keyboard
		keyboard = bge.logic.keyboard
		
		key_events = keyboard.events
		is_shifted = key_events[bge.events.LEFTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE or \
					key_events[bge.events.RIGHTSHIFTKEY] == bge.logic.KX_INPUT_ACTIVE
					
		for key, state in keyboard.events.items():
			if state == bge.logic.KX_INPUT_JUST_ACTIVATED:
				self.update_keyboard(self.keymap[key], is_shifted)
		
		# Now setup the scene callback so we can draw
		bge.logic.getCurrentScene().post_draw = [self.render]

def main(cont):
	mouse = bge.logic.mouse

	if 'gui' not in own:
		# Create our system and show the mouse
		own['gui'] = GuiSys()
		mouse.visible = True

	else:
		own['gui'].main()

cont = bge.logic.getCurrentController()
own  = cont.owner
main(cont)