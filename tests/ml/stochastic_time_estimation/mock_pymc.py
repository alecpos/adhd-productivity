"""
Mock PyMC3 module for testing

This module provides mock implementations of PyMC3 classes and functions
to allow tests to run without requiring the actual PyMC3 module.
"""

import numpy as np

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

class MockTheano:
    """Mock implementation of Theano functions"""
    @staticmethod
    def shared(*args, **kwargs):
        return np.array([])

    class tensor:
        """Mock implementation of Theano tensor module"""
        @staticmethod
        def as_tensor_variable(*args, **kwargs):
            return np.array([])

        class dscalar:
            """Mock implementation of Theano dscalar"""
            def __init__(self, *args, **kwargs):
                pass

        class dvector:
            """Mock implementation of Theano dvector"""
            def __init__(self, *args, **kwargs):
                pass

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
        pass

class Gamma:
    """Mock Gamma distribution"""
    def __init__(self, *args, **kwargs):
        pass

class Beta:
    """Mock Beta distribution"""
    def __init__(self, *args, **kwargs):
        pass

class Uniform:
    """Mock Uniform distribution"""
    def __init__(self, *args, **kwargs):
        pass

class HalfNormal:
    """Mock HalfNormal distribution"""
    def __init__(self, *args, **kwargs):
        pass

# Mock sampling methods
class ADVI:
    """Mock ADVI method"""
    def __init__(self, *args, **kwargs):
        pass

    def fit(self, *args, **kwargs):
        return self

    def sample(self, *args, **kwargs):
        return MockTrace()

# Export mock theano
theano = MockTheano
