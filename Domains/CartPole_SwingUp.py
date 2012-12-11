import sys, os
#Add all paths
sys.path.insert(0, os.path.abspath('..'))
from Tools import *
from Domain import *
from CartPole import *

#####################################################################
# Robert H. Klein, Alborz Geramifard at MIT, Nov. 30 2012
#####################################################################
# (See CartPole implementation in the RL Community,
# http://library.rl-community.org/wiki/CartPole)
#
# ---OBJECTIVE---
# Reward 1 is received on each timestep spent within the goal region,
# zero elsewhere.
# The episode terminates if x leaves its bounds, [-2.4, 2.4]
#
# Pendulum starts straight down, theta = pi, with the
# cart at x = 0.
# (see CartPole parent class for coordinate definitions).
#
# The objective is to get and then keep the pendulum in the goal
# region for as long as possible, with +1 reward for
# each step in which this condition is met; the expected
# optimum then is to swing the pendulum vertically and
# hold it there, collapsing the problem to Pendulum_InvertedBalance
# but with much tighter bounds on the goal region.
#
#####################################################################

class CartPole_SwingUp(CartPole):
    # Domain constants
    GOAL_REWARD         = 1             # Reward received on each step the pendulum is in the goal region
    ANGLE_LIMITS        = [-pi, pi]     # Limit on theta (used for discretization)
    ANGULAR_RATE_LIMITS = [-0, 0]       # Limits on pendulum rate, per 1Link of Lagoudakis & Parr
    POSITON_LIMITS      = [-2.4, 2.4]   # m - Limits on cart position [Per RL Community CartPole]
    VELOCITY_LIMITS     = [-6.0, 6.0]   # m/s - Limits on cart velocity [per RL Community CartPole]  
    
    def __init__(self, logger = None):
        self.statespace_limits  = array([self.ANGLE_LIMITS, self.ANGULAR_RATE_LIMITS])
        super(CartPole_SwingUp,self).__init__(logger)
    
    def s0(self):    
        # Returns the initial state, pendulum vertical
        return array([pi,0,0,0])
    
    
    ## Return the reward earned for this state-action pair
    # On this domain, reward of 1 is given for each step spent within goal region.
    # There is no specific penalty for failure.
    def _getReward(self, s, a):
        return self.GOAL_REWARD if -pi/6 < s[StateIndex.THETA] < pi/6 else 0
    
    def isTerminal(self,s):
        return not (-2.4 < s[StateIndex.X] < 2.4)
    
if __name__ == '__main__':
    random.seed(0)
    p = CartPole_SwingUp();
    p.test(1000)