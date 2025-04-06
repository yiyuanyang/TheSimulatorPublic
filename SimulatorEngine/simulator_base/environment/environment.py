"""
    ====== Abstract Class : Environment =========
    An Environment object, similar to agent,
    is a stateful and sometimes independently
    acting object in the simulation.
    It is evaluated first in the event loop,
    to represent slowly evolving
    conditions that affects a great number of
    objects. Environment objects would persist
    throughout the simulation, and would not be
    removed or added. A simulation can have multiple
    environment objects, to represent the context
    faced by different groups of agents, or diverse
    set of conditions by the same agent / object.
    ================================================
"""

from ..object_base.independent_object import IndependentObject


class Environment(IndependentObject):
    def __init__(self, environment_type: str):
        super().__init__('Environment', environment_type)
        self._simulate_on_first_tick = True

    def required_objects(self):
        """
            Return the list of objects required by
            this environment to simulate.
        """
        return []
