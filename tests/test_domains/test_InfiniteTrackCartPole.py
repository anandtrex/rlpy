from rlpy.Representations import Tabular
from rlpy.Domains.InfiniteTrackCartPole import InfTrackCartPole, InfCartPoleBalance, InfCartPoleSwingUp
from rlpy.Agents.TDControlAgent import SARSA
import numpy as np
from rlpy.Tools import __rlpy_location__
import os

from rlpy.Policies import eGreedy
from rlpy.Experiments import Experiment
import logging

def _make_experiment(domain, exp_id=1, \
                     path="./Results/Tmp/test_InfTrackCartPole"):
    """
    Each file specifying an experimental setup should contain a
    make_experiment function which returns an instance of the Experiment
    class with everything set up.

    @param domain: the domain object to be used in the experiment
    @param id: number used to seed the random number generators
    @param path: output directory where logs and results are stored
    """

    ## Representation
    # discretization only needed for continuous state spaces, discarded otherwise
    representation  = Tabular(domain)

    ## Policy
    policy = eGreedy(representation, epsilon=0.2)

    ## Agent
    agent = SARSA(representation=representation, policy=policy,
                  discount_factor=domain.discount_factor,
                       learn_rate=0.1)
    checks_per_policy = 3
    max_steps = 50
    num_policy_checks = 3
    experiment = Experiment(**locals())
    return experiment

def _checkSameExperimentResults(exp1, exp2):
    """ Returns False if experiments gave same results, true if they match. """
    if not np.all(exp1.result["learning_steps"] == exp2.results["learning_steps"]):
        # Same number of steps before failure (where applicable)
        return False
    if not np.all(exp1.result["return"] == exp2.result["return"]):
        # Same return on each test episode
        return False
    if not np.all(exp1.result["steps"] == exp2.result["steps"]):
        # Same number of steps taken on each training episode
        return False
    return True

# def test_seed_balance():
#     """ Ensure that providing the same random seed yields same result """
#     
#     domain = InfCartPoleBalance()
#     # [[initialize and run experiment without visual]]
#     expNoVis = _make_experiment(domain=domain, exp_id=1)
#     expNoVis.run(visualize_steps=False,
#             visualize_learning=False,
#             visualize_performance=0)
#     
#     # [[initialize and run experiment with visual]]
#     expVis1 = _make_experiment(domain=domain, exp_id=1)
#     expVis1.run(visualize_steps=True,
#             visualize_learning=False,
#             visualize_performance=1)
#     
#     expVis2 = _make_experiment(domain=domain, exp_id=1)
#     expVis2.run(visualize_steps=False,
#             visualize_learning=True,
#             visualize_performance=1)
#     
#     # [[assert get same results]]
#     assert _checkSameExperimentResults(expNoVis, expVis1)
#     assert _checkSameExperimentResults(expNoVis, expVis2)
#     
# def test_seed_swingup():
#     domain = InfCartPoleSwingUp()
#     # [[initialize and run experiment without visual]]
#     expNoVis = _make_experiment(domain=domain, exp_id=1)
#     expNoVis.run(visualize_steps=False,
#             visualize_learning=False,
#             visualize_performance=0)
#     
#     # [[initialize and run experiment with visual]]
#     expVis1 = _make_experiment(domain=domain, exp_id=1)
#     expVis1.run(visualize_steps=True,
#             visualize_learning=False,
#             visualize_performance=1)
#     
#     expVis2 = _make_experiment(domain=domain, exp_id=1)
#     expVis2.run(visualize_steps=False,
#             visualize_learning=True,
#             visualize_performance=1)
#     
#     # [[assert get same results]]
#     assert _checkSameExperimentResults(expNoVis, expVis1)
#     assert _checkSameExperimentResults(expNoVis, expVis2)

def test_physicality():
    """
    Test coordinate system [vertical is 0]
        1) gravity acts in proper direction based on origin
        2) torque actions behave as expected in that frame
    """
    # Apply a bunch of non-torque actions, ensure that monotonically accelerate

    LEFT_FORCE = 0
    NO_FORCE = 1
    RIGHT_FORCE = 2
    
    domain = InfCartPoleSwingUp()
    domain.force_noise_max = 0 # no stochasticity in applied FORCE
    
    # Positive angle (right)
    s = np.array([10.0 * np.pi/180.0, 0.0]) # pendulum slightly right
    domain.state = s.copy()
    
    for i in np.arange(5): # do for 5 steps and ensure works
        domain.step(NO_FORCE)
        assert np.all(domain.state > s) # angle and angular velocity increase
        s = domain.state.copy()
    
    # Negative angle (left)
    s = np.array([-10.0 * np.pi/180.0, 0.0]) # pendulum slightly right
    domain.state = s.copy()
    
    for i in np.arange(5): # do for 5 steps and ensure works
        domain.step(NO_FORCE)
        assert np.all(domain.state < s) # angle and angular velocity increase
        s = domain.state.copy()
    
    # Ensure that reward racks up while in region
    
def test_physicality_hanging():
    """
    Test that energy does not spontaneously enter system
    """
    # Apply a bunch of non-torque actions, ensure that monotonically accelerate

    LEFT_FORCE = 0
    NO_FORCE = 1
    RIGHT_FORCE = 2
    
    domain = InfCartPoleSwingUp()
    domain.force_noise_max = 0 # no stochasticity in applied FORCE
    
    # Positive angle (right)
    s = np.array([179.6 * np.pi/180.0, 0.0]) # pendulum hanging down
    domain.state = s
    
    for i in np.arange(5): # do for 5 steps and ensure works
        domain.step(NO_FORCE)
        assert np.abs(domain.state[0]) <=179.5 # angle does not increase
        assert np.abs(domain.state[1]) <= 0.1 # angular rate does not increase
        s = domain.state