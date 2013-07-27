import bisect

class Observations(object):
    
	def __init__(self, gauss):
		self._gauss  = gauss
		self._D      = gauss.D
		self._nseen  = 0 
		self._ovals  = {}
		## contains entries: [logic_x, logic_y, oval] 
		self._obs    = []
		self._create_hiddens()
		
		
	def _create_hiddens(self):
		for i in range(self._D):
			self._obs.append([1.0*i/(self._D-1), 0, None])


	def add_seen(self, logic_x, logic_y, oval=None):
		insert_idx = bisect.bisect_left(self._obs, [logic_x])
		## TODO: check if point at this x-value is already present
		self._obs.insert(insert_idx, [logic_x, logic_y, oval])
		self._ovals[oval] = self._obs[insert_idx]
		self._D += 1
		self._nseen += 1

	
	def remove_seen(self, oval):
		if not self._ovals.has_key(oval):
			return
		obs_to_remove = self._ovals[oval]
		idx_to_remove = bisect.bisect_left(self._obs, obs_to_remove)
		del self._obs[idx_to_remove]	
		del self._ovals[oval]
		self._D -= 1
		self._nseen -= 1
		
		
	def _seen_idx_and_y(self):
		seen_idx = [idx for idx,elem in enumerate(self._obs) if not elem[2]==None]		
		seen_y = [self._obs[idx][1] for idx in seen_idx] 
		idx_and_y = {'idx':seen_idx, 'y':seen_y}
		return idx_and_y
		
		
	def update(self):
		if (self._nseen < 2):
			return
		self._gauss.setup(self._D)
		self._gauss.update(self._seen_idx_and_y())
		## get (hidden) y values from gauss
		## and update hidden observation y values with them
		hid_y = self._gauss.mu
		idx = 0
		for i in range(len(self._obs)):
			if self._obs[i][2] == None:
				self._obs[i][1] = hid_y[idx]
				idx += 1
				

	@property
	def xy(self):
		coords = []
		for obs in self._obs:
			coords.append((obs[0], obs[1]))			
		return coords
		
		
	@property
	def nseen(self):
		return self._nseen
	
	
	def hidden_x(self):
		x = [obs[0] for obs in self._obs if obs[2] == None]
		return x


	@property
	def gauss(self):
		return self._gauss
		

	def printD(self):
		print "D=%d" % self._D
		

	@property
	def ovals(self):
		return self._ovals
