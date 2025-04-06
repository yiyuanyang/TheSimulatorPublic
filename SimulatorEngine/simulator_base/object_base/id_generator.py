"""
    =========== ID Generator ==============
    Singleton class that generates unique
    IDs for objects in the simulation. 
    This helps with counterfactual analysis
    to track objects across simulation runs
    =======================================
"""

import numpy as np


class IDGenerator:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls._instance = super(IDGenerator, cls).__new__(cls)
            cls._instance._id_counter = 0
        return cls._instance

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, 'instance'):
            cls._instance = IDGenerator()
        return cls._instance

    def next_id(self, prefix: str = "") -> str:
        self._id_counter += 1
        base = np.random.randint(1e9)
        return f"{prefix}_{base}_{self._id_counter}"
