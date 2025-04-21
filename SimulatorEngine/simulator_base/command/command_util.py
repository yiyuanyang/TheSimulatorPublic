"""
    ========== Command Util ==============
    For each command in the command queue
    we have corresponding utility function
    for it
    ======================================
"""

from simulator_base.orchestrator.orchestrator import get_orchestrator


def pause_simulation():
    get_orchestrator().pause_simulation()


def resume_simulation():
    get_orchestrator().unpause_simulation()


def stop_simulation():
    get_orchestrator().stop_simulation()
