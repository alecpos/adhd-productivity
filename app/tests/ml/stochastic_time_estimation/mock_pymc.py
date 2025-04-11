"""
Mock PyMC3 module for testing

This module provides mock implementations of PyMC3 classes and functions
to allow tests to run without requiring the actual PyMC3 module.
"""

import numpy as np
import sys
from types import ModuleType
from unittest.mock import MagicMock

# Add missing numpy types
np.bool = bool  # Fix for numpy bool error

# Create mock modules
class MockTheano:
    """Mock implementation of theano."""
    compile = MagicMock()
    tensor = MagicMock()

    def __init__(self):
        self.compile = MagicMock()
        self.tensor = MagicMock()

# Fix for numpy bool issue
class MockNumpy:
    """Mock implementation for numpy specific attributes."""
    bool_ = bool

# Patch the modules
sys.modules['theano'] = MockTheano()
sys.modules['theano.tensor'] = MagicMock()

# Add the bool_ attribute to numpy to fix the AttributeError
try:
    if not hasattr(np, 'bool_'):
        np.bool_ = bool
except ImportError:
    pass

class MockModel:
    """Mock implementation of PyMC3 Model class"""
    def __init__(self, *args, **kwargs):
        self.named_vars = {}
        self.free_RVs = []
        self.observed_RVs = []
        self.deterministics = []
        self.potentials = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

class MockTrace:
    """Mock implementation of PyMC3 Trace class"""
    def __init__(self, *args, **kwargs):
        self.varnames = []
        self._straces = {}

    def get_values(self, varname, **kwargs):
        """Return mock values for variable"""
        return np.random.normal(size=(100,))

    def __len__(self):
        return 100

class MockSample:
    """Mock implementation of PyMC3 sample results"""
    @staticmethod
    def sample(*args, **kwargs):
        """Return a mock trace"""
        return MockTrace()

# Create a proper module structure for theano
theano_module = ModuleType('theano')
theano_module.compile = lambda *args, **kwargs: (lambda *args, **kwargs: np.random.normal(size=(10,)))
theano_module.config = ModuleType('theano.config')
theano_module.config.floatX = 'float64'
theano_module.config.compute_test_value = 'off'

# Create tensor submodule
tensor_module = ModuleType('theano.tensor')
theano_module.tensor = tensor_module

# Add tensor functions
tensor_module.as_tensor_variable = lambda *args, **kwargs: np.array([])
tensor_module.dtensor3 = lambda *args, **kwargs: np.random.normal(size=(3, 3, 3))
tensor_module.dmatrix = lambda *args, **kwargs: np.random.normal(size=(3, 3))
tensor_module.dvector = lambda *args, **kwargs: np.random.normal(size=(3,))
tensor_module.iscalar = lambda *args, **kwargs: 1
tensor_module.dscalar = lambda *args, **kwargs: 1.0

# Add tensor classes as functions
class dscalar:
    """Mock implementation of Theano dscalar"""
    def __init__(self, *args, **kwargs):
        self.ndim = 0

class dvector:
    """Mock implementation of Theano dvector"""
    def __init__(self, *args, **kwargs):
        self.ndim = 1

class dmatrix:
    """Mock implementation of Theano dmatrix"""
    def __init__(self, *args, **kwargs):
        self.ndim = 2

# Add the classes to the tensor module
tensor_module.dscalar = dscalar
tensor_module.dvector = dvector
tensor_module.dmatrix = dmatrix
tensor_module.shape = property(lambda self: (None, None))

# Create a shared module
tensor_shared_module = ModuleType('theano.tensor.sharedvar')
theano_module.tensor.sharedvar = tensor_shared_module

# Add theano.shared function to main module
theano_module.shared = lambda *args, **kwargs: np.array([])

# Create mock PyMC3 module structure
NUTS = lambda *args, **kwargs: None
find_MAP = lambda *args, **kwargs: {"x": 0.0}
sample = MockSample.sample
traceplot = lambda *args, **kwargs: None
summary = lambda *args, **kwargs: None
Model = MockModel

# Mock distribution classes
class Normal:
    """Mock Normal distribution"""
    def __init__(self, *args, **kwargs):
        self.mean = kwargs.get('mu', 0.0)
        self.sd = kwargs.get('sd', 1.0)

class Gamma:
    """Mock Gamma distribution"""
    def __init__(self, *args, **kwargs):
        self.alpha = kwargs.get('alpha', 1.0)
        self.beta = kwargs.get('beta', 1.0)

class Beta:
    """Mock Beta distribution"""
    def __init__(self, *args, **kwargs):
        self.alpha = kwargs.get('alpha', 1.0)
        self.beta = kwargs.get('beta', 1.0)

class Uniform:
    """Mock Uniform distribution"""
    def __init__(self, *args, **kwargs):
        self.lower = kwargs.get('lower', 0.0)
        self.upper = kwargs.get('upper', 1.0)

class HalfNormal:
    """Mock HalfNormal distribution"""
    def __init__(self, *args, **kwargs):
        self.sd = kwargs.get('sd', 1.0)

# Add more distribution classes
class StudentT:
    """Mock StudentT distribution"""
    def __init__(self, *args, **kwargs):
        self.nu = kwargs.get('nu', 1.0)
        self.mu = kwargs.get('mu', 0.0)
        self.sd = kwargs.get('sd', 1.0)

class Exponential:
    """Mock Exponential distribution"""
    def __init__(self, *args, **kwargs):
        self.lam = kwargs.get('lam', 1.0)

class Poisson:
    """Mock Poisson distribution"""
    def __init__(self, *args, **kwargs):
        self.mu = kwargs.get('mu', 1.0)

# Mock sampling methods
class ADVI:
    """Mock ADVI method"""
    def __init__(self, *args, **kwargs):
        pass

    def fit(self, *args, **kwargs):
        return self

    def sample(self, *args, **kwargs):
        return MockTrace()

# Export mock theano as a proper module
theano = theano_module

# Add math module to prevent related errors
math_module = ModuleType('pymc3.math')
math_module.exp = np.exp
math_module.log = np.log
math_module.sqrt = np.sqrt
math = math_module

# Add additional PyMC3 classes/functions that might be imported
Deterministic = lambda *args, **kwargs: 0.0
Potential = lambda *args, **kwargs: None
DensityDist = lambda *args, **kwargs: None
