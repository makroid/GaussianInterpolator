import numpy as np
from scipy import linalg

class GaussInterpolator(object):
    
	def __init__(self, D):
		"""set up L matrix"""
		self.setup(D)
		
	
	def setup(self, D):
		self._D = D
		self._matL = np.zeros((D-2, D))
		self._matL[np.arange(self.D-2), np.arange(self.D-2)] = -1
		self._matL[np.arange(self.D-2), np.arange(self.D-2)+1] = 2
		self._matL[np.arange(self.D-2), np.arange(self.D-2)+2] = -1
		self._lambda_old = 1
		self.update_lambda(20)
        
        
	def update_lambda(self, lambda_):
		self._matL /= self._lambda_old
		self._matL *= lambda_
		self._lambda_old = lambda_
        
        
	def update(self, seen):
		"""update mean and covariance matrix of Gaussian, given observations"""
		seenIdx = seen['idx']
		seenY   = seen['y']
		if len(seenIdx) < 2: 
			return
		hidIdx = list(set(range(self.D)) - set(seenIdx))
		matLseen = self._matL[:, seenIdx]
		matLhid = self._matL[:, hidIdx]
		self._sigma = linalg.inv(matLhid.T.dot(matLhid))
		self._mu = (-1)*self._sigma.dot(matLhid.T.dot(matLseen)).dot(seenY)
        
    
	def sample(self):
		sample = np.random.multivariate_normal(self._mu, self._sigma)
		return sample
		
    
	@property    
	def mu(self): 
		return self._mu
        
       
	@property    
	def sigma(self):
		return self._sigma
        
        
	@property
	def D(self):
		return self._D
