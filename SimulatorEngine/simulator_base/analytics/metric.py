"""
    =============== Metrics ====================
    Metrics is an object that gets attached
    to another object in the simulation
    and periodically summarizes related data.

    This is triggered by orchestrator at the
    end of every tick. And the metrics object
    has the choice to decide whether it wants
    to update or refresh its data or not.
    ============================================
"""

from simulator_base.config.global_config import get_config
from simulator_base.object_base.simulation_object import SimulationObject
from simulator_base.orchestrator.orchestrator import (
    Orchestrator,
    get_orchestrator,
)
from abc import abstractmethod
from typing import final, List
from datetime import timedelta
import pandas as pd
import os
import random


class Metric(SimulationObject):
    def __init__(self, metric_type: str, computation_config: dict):
        super().__init__("Metric", metric_type)
        self._setup_metric(computation_config)
        self._simulate_on_first_tick = True
        self._subject: SimulationObject = None
        # only used for rehydration
        self._subject_id = None
        self._subject_type = None

    @abstractmethod
    def calculate(self) -> list:
        """
            ========= Must Implement =============
            Calculate the metric values and return
            ======================================
        """
        return []

    @abstractmethod
    def column_names(self) -> List[str]:
        """
            ========== Must Implement ============
            Column names for the metrics
            ======================================
        """
        return []

    # ================= User Accessible Public Methods ==================

    def before_destroy(self):
        self._subject = None

    @final
    def attach(self, obj: SimulationObject):
        """
            Attach the metric to an object.
        """
        self._subject = obj
        self.start()

    # ================= System Accessible Public Methods ==================

    @final
    def simulate(self):
        """
            Metric simulation
        """
        if not self._should_calculate:
            return
        if self._subject.paused:
            return
        self._calculate()
        self._calculation_cnt += 1
        if self._should_save():
            self._save()

    @final
    def validate_object(self):
        if self._subject is None:
            raise Exception(
                f"Attached object not set for metric {self.object_subtype}"
            )

    @final
    def _should_save(self):
        """
            Evaluate whether the metric should be
            saved to local CSV file or not.
        """
        if self._calculation_cnt % self._calculations_per_save == 0:
            return True
        if self._calculation_cnt == 1:
            return True
        return False

    @final
    def _column_names(self) -> list:
        """
            Column names for the metrics
        """
        return ['Aggregation Window'] + self.column_names() + [
            'Object Type',
            'Object Subtype',
            'Object ID',
            'Object Simulation Count'
        ]

    # ================= Private Helper Methods ==================

    def _setup_metric(self, computation_config: dict):
        calculation_rate = computation_config['calculation_rate']
        if random.random() < calculation_rate:
            self._should_calculate = True
        else:
            self._should_calculate = False
        self._subject = None
        computation_interval_raw_min = computation_config[
            "computation_interval"
        ]
        computation_interval = timedelta(
            minutes=computation_interval_raw_min
        )
        self.simulation_interval = computation_interval
        # a row of data per calculation time
        self._metric_values = {}
        self._calculation_cnt = 0
        self._calculations_per_save = computation_config[
            "calculations_per_save"
        ]
        aggregation_window_raw_min = computation_config[
            "aggregation_window"
        ]
        self._aggregation_window = timedelta(
            minutes=aggregation_window_raw_min
        )

    def _calculate(self):
        results = [
            self._aggregation_window
        ] + self.calculate() + self._default_calculated_columns()
        current_time = Orchestrator.get_current_time(self._subject)
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        if current_time_str not in self._metric_values:
            self._metric_values[current_time_str] = results

    @final
    def _default_calculated_columns(self) -> list:
        return [
            self._subject.object_type,
            self._subject.object_subtype,
            self._subject.id,
            self._subject.simulation_count
        ]

    @final
    def _save(self):
        """
            Save the metric to local CSV file.
        """
        object_type = self._subject.object_type
        object_subtype = self._subject.object_subtype
        metric_name = self.object_subtype
        save_path = os.path.join(
            get_config().get_exp_output_path(),
            object_type + "_metrics",
            object_subtype + "_metrics",
            str(self._subject),
        )
        os.makedirs(save_path, exist_ok=True)
        file_name = f"{metric_name}.csv"
        file_path = os.path.join(save_path, file_name)

        df = pd.DataFrame.from_dict(
            self._metric_values,
            orient="index",
            columns=self._column_names()
        )
        df.index.name = "timestamp"
        df.reset_index(inplace=True)
        df.to_csv(file_path, index=False)

    def rehydrate(self):
        """
            Metrics are rehydrated last. It just
            needs to be reattached to the subject.
        """
        orchestrator = get_orchestrator()
        self._subject = orchestrator.get_object(
            self._subject_type,
            self._subject_id
        )

    # ============ Serialization Methods ============

    def __getstate__(self):
        state = self.__dict__.copy()
        if self._subject is not None:
            state["_subject_id"] = self._subject.id
            state["_subject_type"] = self._subject.object_type
            state["_subject"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
