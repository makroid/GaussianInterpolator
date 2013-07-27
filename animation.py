import threading
import time


class PropertyAnimation(threading.Thread):
	def __init__(self, obj, prop):
		threading.Thread.__init__(self)
		self.event = threading.Event()
		self._object = obj
		self._prop = prop
        
	def start_values(self, start, end, time, tiks=10):
		self._start = start
		self._end = end
		self._time = time
		self._tiks = tiks
		self._wait = float(time*1.0/tiks)
		self._total = tiks

	def run(self):
		while self._tiks > 0 and not self.event.is_set():			
			new_prop_val = self._start+(self._end-self._start)*(self._total-self._tiks+1)/self._total
			setattr(self._object, self._prop, new_prop_val)
			self._tiks -= 1
			self.event.wait( self._wait )

	def stop(self):
		self.event.set()

