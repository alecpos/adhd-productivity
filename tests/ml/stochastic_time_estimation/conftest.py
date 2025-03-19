"""
Pytest configuration for Stochastic Time Estimation Engine tests.

This module sets up the test environment, including mocking external dependencies
that are problematic for testing.
"""

import pytest
import sys
from unittest.mock import MagicMock

# Import our mock PyMC3 module
from app.tests.ml.stochastic_time_estimation.mock_pymc import *

# Create a mock for PyMC3
mock_pymc3 = MagicMock()
mock_pymc3.Model = Model
mock_pymc3.Normal = Normal
mock_pymc3.Gamma = Gamma
mock_pymc3.Beta = Beta
mock_pymc3.Uniform = Uniform
mock_pymc3.HalfNormal = HalfNormal
mock_pymc3.NUTS = NUTS
mock_pymc3.find_MAP = find_MAP
mock_pymc3.sample = sample
mock_pymc3.traceplot = traceplot
mock_pymc3.summary = summary
mock_pymc3.ADVI = ADVI
mock_pymc3.theano = theano

# Apply the mocks
sys.modules['pymc3'] = mock_pymc3
sys.modules['theano'] = theano 