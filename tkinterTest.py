
import Tkinter
from Tkinter import *
from ttk import Frame, Button, Style
from animation import PropertyAnimation
from gaussianinterpolator import GaussInterpolator
from discretegrid import Observations


class Line(object):
	def __init__(self, id_, canvas):
		self._id = id_
		self._canvas = canvas
		
	
	def update_xy(self, xy):
		self._canvas.coords(self._id, Tkinter._flatten(xy))
		
	@property
	def line_color(self):
		return self._canvas.itemget(self._id, fill)
		
		
	@line_color.setter
	def line_color(self, red_col):
		col = "#%02x%02x%02x" % (int(red_col), 0, 0)
		self._canvas.itemconfig(self._id, fill = col)
		
	
	@property
	def id(self):
		return self._id
		
		

class ObsCanvas(object, Canvas):
	def __init__(self, parent, obs):
		Canvas.__init__(self, parent)
		self.parent         = parent
		self._obs           = obs
		self._scale 		= 1.0
		self._obs_radius    = 6
		self._selection     = None
		self._mean_line     = None
		self.config(bg='#000000')
		self.init_binders()
		self._create_mean_line()
		
		
	def init_binders(self):
		self.bind('<Button-1>', self.handle_left_button_click)
		self.bind('<Configure>', self.handle_configure)
		self.bind('<Button-3>', self.handle_right_button_click)
		self.bind('<Key>', self.handle_key)
		
		
	def handle_left_button_click(self, event):
		ylogic = self.y_screen_to_logic(event.y)
		if self.check_select_seen_obs(event):
			self.itemconfig(self._selection, fill='green')
		elif not self._selection is None:
			pass
			## TODO: check if new position is valid
			#self.coords(self._selection, 
		else:
			self.add_seen_obs(event)
		self.update_obs()
		self.update_mean_line()
		self.focus_set()
			
			
	def handle_right_button_click(self, event):
		"""cancel selection"""
		if not self._selection is None:
			self.itemconfig(self._selection, fill='yellow')
			self._selection = None
		self.focus_set()
			
	
	def handle_key(self, event):
		if event.char == "d":
			if self._selection != None:
				self.itemconfig(self._selection, state=Tkinter.HIDDEN)
				self._obs.remove_seen(self._selection)
				self.update_obs()
				self.update_mean_line()
				self._selection = None


	def check_select_seen_obs(self, event):
		for oval in self._obs.ovals:
			coords = self.coords(oval)
			if self.is_point_in_box([event.x, event.y], coords):
				self._selection = oval
				return True
		self._selection = None
		return False
	
		
	def handle_configure(self, event):
		""" called when size of canvas is changed"""
		for oval, xy in self._obs.ovals.iteritems():
			#print xy
			bbox = self.coords(oval)
			newX = self.x_logic_to_screen(xy[0])
			newY = self.y_logic_to_screen(xy[1])
			bbox[0] = newX - self._obs_radius
			bbox[1] = newY - self._obs_radius
			bbox[2] = newX + self._obs_radius
			bbox[3] = newY + self._obs_radius
			self.coords(oval, bbox[0], bbox[1], bbox[2], bbox[3])
		self.update_mean_line()
		
	
	def update_obs(self):
		self._obs.update()
	
	
	def update_mean_line(self):
		xy = self.logic_coords_to_screen(self._obs.xy)
		self._mean_line.update_xy(xy)
		
		
	def add_seen_obs(self, event):
		x_logic = self.x_screen_to_logic(event.x)
		y_logic = self.y_screen_to_logic(event.y)
		oval_id = self.create_oval(event.x - self._obs_radius, event.y - self._obs_radius, event.x+self._obs_radius, event.y+self._obs_radius, fill='yellow')
		self._obs.add_seen(x_logic, y_logic, oval_id)
		
		
	def _create_mean_line(self):
		line_color  = "#%02x%02x%02x" % (128, 192, 200)
		self._mean_line = Line(self.create_line(0.0,0.0,0.0,0.0, fill=line_color, width=3), self)
		
		
	def x_screen_to_logic(self, x_screen):
		win_width = self.winfo_width()
		x_logic = 1.0 * x_screen / win_width
		return x_logic
		
		
	def x_logic_to_screen(self, x_logic):
		win_width = self.winfo_width()	
		x_screen = int(x_logic * win_width)
		return x_screen
	
		
	def y_screen_to_logic(self, y_screen):
		mid_height = self.winfo_height() / 2.0
		y_logic = (mid_height - y_screen) * self._scale / mid_height
		return y_logic
		
		
	def y_logic_to_screen(self, y_logic):		
		mid_height = self.winfo_height() / 2.0
		y_screen = int((mid_height - y_logic / self._scale * mid_height))
		return y_screen
		
		
	def logic_coords_to_screen(self, logic_coords):
		screen_coords = []
		for xy in logic_coords:
			screen_coords.append((self.x_logic_to_screen(xy[0]), self.y_logic_to_screen(xy[1])))
		return screen_coords
		
	
	def is_point_in_box(self, point, box):
		if point[0] >= box[0] and point[0] <= box[2]:
			if point[1] >= box[1] and point[1] <= box[3]:
				return True
		return False
		
		
	def sample(self):
		if self._obs.nseen < 2:
			return
		line = Line(self.create_line(0.0,0.0,0.0,0.0, fill='red', width=3, smooth=1), self)
		self.tag_lower(line.id, self._mean_line.id)
		x = self._obs.hidden_x()
		y = self._obs.gauss.sample()
		logic_coords = zip(x,y)
		line.update_xy(self.logic_coords_to_screen(logic_coords))
		pa = PropertyAnimation(line, "line_color")
		pa.start_values(255, 0, 1)
		pa.start()
		self.update_idletasks()
		


class GaussianFrame(object, Frame):
  
	def __init__(self, parent, obs):
		Frame.__init__(self, parent)          
		self.parent = parent       
		self.initUI(obs)
		self.init_binders()
		
        
	def initUI(self, obs):    
		self.parent.title("Gaussian Interpolator")
		self.style = Style()
		self.style.theme_use("default")
		self.pack(fill=BOTH, expand=1)

		self.columnconfigure(1, weight=1)      
		self.rowconfigure(3, weight=1)
		self.rowconfigure(5, pad=7)
                     
		self._canvas = ObsCanvas(self, obs)
		self._canvas.grid(row=1, column=0, columnspan=2, rowspan=4, 
			padx=5, sticky=E+W+S+N)
                       
		self._sbtn = Button(self, text="sample")
		self._sbtn.grid(row=5, column=0, padx=5, columnspan=2, sticky=W+E) 


	def init_binders(self):
		self._sbtn.bind('<Button-1>', self._sample_line)


	def _sample_line(self, event):
		self._canvas.sample()



def main(): 
	root = Tk()
	root.geometry("800x600+300+100")
	D = 100
	gauss = GaussInterpolator(D)
	obs = Observations(gauss)
	app = GaussianFrame(root, obs)
	root.mainloop()  


if __name__ == '__main__':
	main()  
