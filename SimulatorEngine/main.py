from simulator_base.required_setup import required_setup
from market_simulation.market_setup import market_setup
from market_simulation.objects.object_mapping import get_mapped_obj_cls


def setup():
    orchestrator, end_time = required_setup()
    # Two things are needed for custom setup:
    #    A custom setup function that adds simulated object
    #    A custom object mapping function that would help
    #    with serialize and deserialize the object.
    market_setup()
    orchestrator.setup_object_mapping(get_mapped_obj_cls)
    return orchestrator, end_time


def main():
    orchestrator, end_time = setup()
    current_time = None
    try:
        while True and (
            end_time is None
            or current_time is None
            or current_time < end_time
        ):
            orchestrator.tick()
            current_time = orchestrator.get_global_time()
    except KeyboardInterrupt:
        orchestrator.destroy()


if __name__ == "__main__":
    main()
