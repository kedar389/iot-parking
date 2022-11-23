from components.microcontrollers import *
from components.sensors import *

"""
    MAIN TODO's
"""
# TODO: IMPLEMENT BASIC STRUCTURE AND CONNECTIVITY -> DONE
# TODO: IMPLEMENT Thermometer                      -> DONE
# TODO: IMPLEMENT Gate                             -> DONE
# TODO: IMPLEMENT CardReader                       -> NOT DONE
# TODO: IMPLEMENT DistanceSensor                   -> NOT DONE
# TODO: IMPLEMENT Screen                           -> NOT DONE


# TODO: IF NECESSARY, IMPLEMENT TIME IN JSON

"""
    Micropython does not support abstract classes from abc library,
    therefore is used unstandard implementation of it.  
"""

"""
    May be useful in future
"""


class MicrocontrollerSet:
    def __init__(self):
        self.set = set()

    def add_controller(self, microcontroller: Microcontroller) -> None:
        self.set.add(microcontroller)

    def remove_controller(self, microcontroller: Microcontroller) -> None:
        self.set.remove(microcontroller)

    def start_controllers(self) -> None:
        for microcontroller in self.set:
            microcontroller.start_controller()

    def component_usage(self) -> None:
        for microcontroller in self.set:
            microcontroller.component_handler()

    def close_all_gates(self) -> None:
        for microcontroller in self.set:
            microcontroller.close_all_gates()


if __name__ == "__main__":
    # TODO CHANGE TO 30 OR 60 IN REAL PRODUCTION
    # CYCLE_DURATION_MICRO_SEC = 15 * 1000 * 1000
    pico = RPiPico()

    pico.add_component(InternalThermometer("location_001"), pico.pin_count)
    # pico.add_component(ExternalThermometer("location_002", 0), 0)
    pico.add_component(Gate("location_003", 1), 1)

    pico.start_controller()
    # TODO calculate cycle duration to match specific duration, for example 30s,
    # TODO maybe change gate handler to other process, because user can wait up to one full cycle before gate opening
    # TODO change pico.closeallgates() to class CardReader
    while True:
        # start_time_micro_sec = utime.time_ns() / 1000
        pico.component_handler()
        utime.sleep(5)
        pico.close_all_gates()
        # stop_time_micro_sec = utime.time_ns() / 1000

        # iteration_duration = stop_time_micro_sec - start_time_micro_sec
        # print(iteration_duration)
        # if iteration_duration < CYCLE_DURATION_MICRO_SEC:
        # utime.sleep_us(CYCLE_DURATION_MICRO_SEC - int(iteration_duration))
