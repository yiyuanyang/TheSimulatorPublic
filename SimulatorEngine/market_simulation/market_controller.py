"""
    ============ Market Controller ================
    A singleton object that exist in the simulation
    in the server version to allow easy handling
    of the simulation objects and etc.
    ===============================================
"""

from simulator_base.required_setup import required_setup
from market_simulation.market_setup import market_setup
from market_simulation.objects.object_mapping import get_mapped_obj_cls
from datetime import datetime, timedelta


class MarketController:
    """
        A singleton object that exist in the simulation
        in the server version to allow easy handling
        of the simulation objects and etc.
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(MarketController, cls).__new__(cls)
            cls.__instance._orchestrator, cls.__instance.end_time = \
                required_setup()
            market_setup()
            cls.__instance._orchestrator.setup_object_mapping(
                get_mapped_obj_cls
            )
        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = MarketController()
        return cls.__instance

    def get_orchestrator(cls):
        """
            Get the orchestrator instance.
        """
        return cls.__instance._orchestrator

    def progress_time(self, time: timedelta):
        self._orchestrator.progress_time(time)

    def progress_until_time(self, end_time: datetime):
        """
            Progress the simulation until a given end time.
        """
        self._orchestrator.progress_until_time(end_time)

    def tick(self):
        """
            Tick the simulation.
        """
        self._orchestrator.tick()

    def pause_simulation(self):
        self._orchestrator.pause_simulation()

    def unpause_simulation(self):
        self._orchestrator.unpause_simulation()

    def remove_object(self, obj_id: str):
        """
            Remove an object from the simulation.
        """
        agents = self._orchestrator.get_all_objects()
        for agent in agents:
            if agent.id == obj_id:
                agent.destroy()

    def remove_advertiser(self, advertiser_id: str):
        """
            Remove an advertiser from the simulation.
        """
        self._orchestrator.remove_object(advertiser_id)
