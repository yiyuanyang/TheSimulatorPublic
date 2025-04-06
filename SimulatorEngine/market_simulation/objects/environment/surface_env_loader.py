"""
    ============ Surface Env Loader ===============
    Load up the surfaces that are available in the
    surfaces
    ===============================================
"""

from market_simulation.objects.environment.surface_environment import (
    SurfaceEnvironment
)
from market_simulation.objects.analytics.surface_metrics import SurfaceMetrics
from market_simulation.config.market_config import get_config
from typing import List


def load_surface_env(
    start: bool = True
) -> List[SurfaceEnvironment]:
    """
        Load up the surface environments
    """
    market_config = get_config()
    env_config = market_config.get_environment_config()
    surface_list = []
    enabled_surfaces = env_config['enabled_surfaces']
    ad_load = env_config['per_surface_ad_load']
    ad_fetch_cnt = env_config['per_surface_fetch_cnt']
    for surface in enabled_surfaces:
        new_surface = SurfaceEnvironment(
            surface,
            ad_load[surface],
            ad_fetch_cnt[surface]
        )
        surface_metrics = SurfaceMetrics()
        surface_metrics.attach(new_surface)
        new_surface.start()
        surface_list.append(new_surface)
    if start:
        for surface in surface_list:
            surface.start()
    return surface_list
