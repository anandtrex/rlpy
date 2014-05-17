"""Greedy-GQ(lambda) learning agent"""
from .Agent import Agent, DescentAlgorithm
from rlpy.Tools import addNewElementForAllActions, count_nonzero
import numpy as np
from copy import copy

__copyright__ = "Copyright 2013, RLPy http://www.acl.mit.edu/RLPy"
__credits__ = ["Alborz Geramifard", "Robert H. Klein", "Christoph Dann",
               "William Dabney", "Jonathan P. How"]
__license__ = "BSD 3-Clause"
__author__ = "Alborz Geramifard"


class Greedy_GQ(DescentAlgorithm, Agent):
    lambda_ = 0  # lambda Parameter in SARSA [Sutton Book 1998]
    eligibility_trace = []
    # eligibility trace using state only (no copy-paste), necessary for dabney
    # decay mode
    eligibility_trace_s = []

    def __init__(
            self, domain, policy, representation, initial_learn_rate=.1,
            lambda_=0, BetaCoef=1e-6, **kwargs):
        self.eligibility_trace = np.zeros(
            representation.features_num *
            domain.actions_num)
        # use a state-only version of eligibility trace for dabney decay mode
        self.eligibility_trace_s = np.zeros(representation.features_num)
        self.lambda_ = lambda_
        super(
            Greedy_GQ,
            self).__init__(
            domain,
            policy,
            representation,
            **kwargs)
        self.GQWeight = copy(self.representation.theta)
        # The beta in the GQ algorithm is assumed to be learn_rate * THIS CONSTANT
        self.secondLearningRateCoef = BetaCoef

    def learn(self, s, p_actions, a, r, ns, np_actions, na, terminal):
        self.representation.pre_discover(s, False, a, ns, terminal)
        discount_factor = self.representation.domain.discount_factor
        theta = self.representation.theta
        phi_s = self.representation.phi(s, False)
        phi = self.representation.phi_sa(s, False, a, phi_s)
        phi_prime_s = self.representation.phi(ns, terminal)
        na = self.representation.bestAction(
            ns,
            terminal,
            np_actions,
            phi_prime_s)  # Switch na to the best possible action
        phi_prime = self.representation.phi_sa(
            ns,
            terminal,
            na,
            phi_prime_s)
        nnz = count_nonzero(phi_s)    # Number of non-zero elements

        expanded = (- len(self.GQWeight) + len(phi)) / self.domain.actions_num
        if expanded:
            self._expand_vectors(expanded)
        # Set eligibility traces:
        if self.lambda_:
            self.eligibility_trace *= discount_factor * self.lambda_
            self.eligibility_trace += phi

            self.eligibility_trace_s *= discount_factor * self.lambda_
            self.eligibility_trace_s += phi_s

            # Set max to 1
            self.eligibility_trace[self.eligibility_trace > 1] = 1
            self.eligibility_trace_s[self.eligibility_trace_s > 1] = 1
        else:
            self.eligibility_trace = phi
            self.eligibility_trace_s = phi_s

        td_error                     = r + \
            np.dot(discount_factor * phi_prime - phi, theta)
        self.updateLearnRate(
            phi_s,
            phi_prime_s,
            self.eligibility_trace_s,
            discount_factor,
            nnz,
            terminal)

        if nnz > 0:  # Phi has some nonzero elements, proceed with update
            td_error_estimate_now = np.dot(phi, self.GQWeight)
            Delta_theta                 = td_error * self.eligibility_trace - \
                discount_factor * td_error_estimate_now * phi_prime
            theta += self.learn_rate * Delta_theta
            Delta_GQWeight = (
                td_error - td_error_estimate_now) * phi
            self.GQWeight               += self.learn_rate * \
                self.secondLearningRateCoef * Delta_GQWeight

        expanded = self.representation.post_discover(
            s,
            False,
            a,
            td_error,
            phi_s)
        if expanded:
            self._expand_vectors(expanded)
        if terminal:
            self.episodeTerminated()

    def _expand_vectors(self, num_expansions):
        """
        correct size of GQ weight and e-traces when new features were expanded
        """
        new_elem = np.zeros((self.domain.actions_num, num_expansions))
        self.GQWeight = addNewElementForAllActions(
            self.GQWeight,
            self.domain.actions_num,
            new_elem)
        if self.lambda_:
            # Correct the size of eligibility traces (pad with zeros for new
            # features)
            self.eligibility_trace = addNewElementForAllActions(
                self.eligibility_trace,
                self.domain.actions_num,
                new_elem)
            self.eligibility_trace_s = addNewElementForAllActions(
                self.eligibility_trace_s, 1, np.zeros((1, num_expansions)))