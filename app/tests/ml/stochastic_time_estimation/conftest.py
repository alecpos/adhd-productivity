"""
Pytest configuration file for the Stochastic Time Estimation Engine tests

This file contains pytest fixtures and configurations to set up the test environment
for the Stochastic Time Estimation Engine tests.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from types import ModuleType

# Make sure mock modules are set up before importing the tests
# Add these mocks before any test imports happen
import numpy as np
np.bool = bool  # Fix for numpy bool error

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import the mock PyMC3 module
from app.tests.ml.stochastic_time_estimation.mock_pymc import *

# Set up the theano mock module in sys.modules first
sys.modules['theano'] = theano
sys.modules['theano.tensor'] = theano.tensor
sys.modules['theano.compile'] = ModuleType('theano.compile')
sys.modules['theano.compile.sharedvalue'] = ModuleType('theano.compile.sharedvalue')
sys.modules['theano.tensor.sharedvar'] = theano.tensor.sharedvar

# Create a mock for PyMC3
mock_pymc3 = MagicMock()
mock_pymc3.Model = Model
mock_pymc3.Normal = Normal
mock_pymc3.Gamma = Gamma
mock_pymc3.Beta = Beta
mock_pymc3.Uniform = Uniform
mock_pymc3.HalfNormal = HalfNormal
mock_pymc3.StudentT = StudentT
mock_pymc3.Exponential = Exponential
mock_pymc3.Poisson = Poisson
mock_pymc3.NUTS = NUTS
mock_pymc3.ADVI = ADVI
mock_pymc3.find_MAP = find_MAP
mock_pymc3.sample = sample
mock_pymc3.traceplot = traceplot
mock_pymc3.summary = summary
mock_pymc3.theano = theano
mock_pymc3.math = math
mock_pymc3.Deterministic = Deterministic
mock_pymc3.Potential = Potential
mock_pymc3.DensityDist = DensityDist

# Add PyMC3 mock to sys.modules
sys.modules['pymc3'] = mock_pymc3

# Fixture for creating a mock task
@pytest.fixture
def mock_task():
    """Create a mock task for testing"""
    return {
        'id': '12345',
        'title': 'Test Task',
        'description': 'This is a test task for unit testing',
        'estimated_duration': 60,  # minutes
        'location': 'Home',
        'deadline': '2023-12-31T23:59:59',
        'priority': 'Medium',
        'tags': ['test', 'unit-test']
    }

# Fixture for asyncio
@pytest.fixture
def event_loop():
    """Create an event loop for testing async functions"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()