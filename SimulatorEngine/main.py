from simulator_base.required_setup import required_setup
from market_simulation.market_setup import market_setup


def setup():
    orchestrator = required_setup()
    if not orchestrator.simulation_loaded():
        market_setup()
    return orchestrator


def main():
    orchestrator = setup()
    try:
        orchestrator.run_simulation()
    except KeyboardInterrupt:
        orchestrator.destroy()


if __name__ == "__main__":
    main()
