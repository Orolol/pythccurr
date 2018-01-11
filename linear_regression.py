import numpy as np
from numpy.random import normal, uniform
from scipy.stats import multivariate_normal as mv_norm
import matplotlib.pyplot as plt

import ccxt
import time
import datetime

# %matplotlib inline


def real_function(a_0, a_1, noise_sigma, x):
    """
    Evaluates the real function
    """
    N = len(x)
    if noise_sigma==0:
        # Recovers the true function
        return a_0 + a_1*x
    else:
        return a_0 + a_1*x + normal(0, noise_sigma, N)


class LinearBayes(object):
    """
    A class that holds parameter prior/posterior and handles 
    the hyper-parameter updates with new data
    
    Note:  variables starting with "v_" indicate Nx1 dimensional 
        column vectors, those starting with "m_" indicate 
        matrices, and those starting with "a_" indicate 
        1xN dimensional arrays.
    
    Args:
        a_m0 (np.array): prior mean vector of size 1xM
        m_S0 (np.ndarray): prior covariance matrix of size MxM
        beta (float): known real-data noise precision
        
    """
    def __init__(self, a_m0, m_S0, beta):
        self.prior = mv_norm(mean=a_m0, cov=m_S0)
        self.v_m0 = a_m0.reshape(a_m0.shape + (1,)) #reshape to column vector
        self.m_S0 = m_S0
        self.beta = beta
        
        self.v_mN = self.v_m0
        self.m_SN = self.m_S0
        self.posterior = self.prior
           
    def get_phi(self, a_x):
        """
        Returns the design matrix of size (NxM) for a feature vector v_x.
        In this case, this function merely adds the phi_0 dummy basis
        that's equal to 1 for all elements.
        
        Args:
            a_x (np.array): input features of size 1xN
        """
        m_phi = np.ones((len(a_x), 2))
        m_phi[:, 1] = a_x
        return m_phi
        
    def set_posterior(self, a_x, a_t):
        """
        Updates mN and SN given vectors of x-values and t-values
        """
        # Need to convert v_t from an array into a column vector
        # to correctly compute matrix multiplication
        v_t = a_t.reshape(a_t.shape + (1,))

        m_phi = self.get_phi(a_x)
        
        self.m_SN = np.linalg.inv(np.linalg.inv(self.m_S0) + self.beta*m_phi.T.dot(m_phi))
        self.v_mN = self.m_SN.dot(np.linalg.inv(self.m_S0).dot(self.v_m0) + \
                                      self.beta*m_phi.T.dot(v_t))
        
        self.posterior = mv_norm(mean=self.v_mN.flatten(), cov=self.m_SN)

    
    def prediction_limit(self, a_x, stdevs):
        """
        Calculates the limit that's "stdevs" standard deviations
        away from the mean at a given value of x.
        
        Args:
            a_x (np.array): x-axis values of size 1xN
            stdevs (float): Number of standard deviations away from
                the mean to calculate the prediction limit
        
        Returns:
            np.array: the prediction limit "stdevs" standard deviations
                away from the mean corresponding to x-values in "v_x"
        
        """
        N = len(a_x)
        m_x = self.get_phi(a_x).T.reshape((2, 1, N))
        
        predictions = []
        for idx in range(N):
            x = m_x[:,:,idx]
            sig_sq_x = 1/self.beta + x.T.dot(self.m_SN.dot(x))
            mean_x = self.v_mN.T.dot(x)
            predictions.append((mean_x+stdevs*np.sqrt(sig_sq_x)).flatten())
        return np.concatenate(predictions)
    
    def generate_data(self, a_x):
        N = len(a_x)
        m_x = self.get_phi(a_x).T.reshape((2, 1, N))

        
        predictions = []
        for idx in range(N):
            x = m_x[:,:,idx]
            sig_sq_x = 1/self.beta + x.T.dot(self.m_SN.dot(x))
            mean_x = self.v_mN.T.dot(x)
            predictions.append(normal(mean_x.flatten(), np.sqrt(sig_sq_x)))
        return np.array(predictions)
    

# Real function parameters
# a_0 = -0.3
# a_1 = 0.5
# noise_sigma = 0.2
# beta = 1/noise_sigma**2
# # Generate input features from uniform distribution
# np.random.seed(20) # Set the seed so we can get reproducible results
# x_real = uniform(-1, 1, 1000)
# # Evaluate the real function for training example inputs
# t_real = real_function(a_0, a_1, noise_sigma, x_real)

# # print(x_real)
# # # print(t_real)

# alpha = 2.0
# v_m0 = np.array([0., 0.])
# m_S0 = 1/alpha*np.identity(2)

# linbayes = LinearBayes(v_m0, m_S0, beta)

# N=1000

# a_x = np.linspace(-1, 1, 1000)
# linbayes.make_scatter(x_real[0:N], t_real[0:N], real_parms=[a_0, a_1])
# print(linbayes.generate_data(a_x))

exchange = ccxt.bitfinex()

ohlcvs = exchange.fetch_ohlcv('EOS/USD', '1m', (time.time() - 6000 ) * 1000)
mean_CVPMS = 0;
last_price = ohlcvs[-1][4]
first_price = ohlcvs[0][1]
opening = []
closing = []
for x in ohlcvs:
    opening.append(x[1])
    closing.append(x[4])
print(ohlcvs[-1])
  
npopening = np.array(opening)
npclosing = np.array(closing)

print('npopening', npopening)
print('npclosing' , npclosing)

N = len(opening)

alpha = 1.
v_m0 = np.array([0., 0.])


m_S0 = 1/alpha*np.identity(2)
noise_sigma = 0.1
beta = 1/noise_sigma**2

print(beta)

linbayes = LinearBayes(v_m0, m_S0, beta)

linbayes.set_posterior(npopening, npclosing)
# 

# # linbayes.generate_data(opening)
# print("PREDITCION LIMIT")
prediction = linbayes.prediction_limit(npopening, 1.)

test = np.array(npopening[-10:-1])
testc = npclosing[-11:-1]
x = 0
# for t in test:
#     arrt = np.array([t])
#     print(arrt)
#     y = linbayes.generate_data(arrt)
#     print(t, ' GENERATE ', y, ' REALITY ', testc[x])
#     if t > y[0]:
#         print('DOWN')
#     else:
#         print('UP')
#     if t > testc[x]:
#         print('REAL DOWN')
#     else:
#         print('REAL UP')
#     x += 1
start = npclosing[-10]
tstart = start
while True:
    total = 0
    for it in range(1, 1000):
        start = npclosing[-11]
        for x in range(1, 10):
            arrt = np.array([start])
            y = linbayes.generate_data(arrt)
            start = y
            x +=1
        total += start
        it += 1

    print('START ', tstart, 'REALITY ', npclosing[-1] , 'MEAN : ', total / 1000)    

# print("GENERATE")
# print(linbayes.generate_data(test))


