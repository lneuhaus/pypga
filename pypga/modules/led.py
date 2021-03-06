from migen import *
from misoc.interconnect.csr import *
from ..core import Module, logic, Register


def SingleLed(counter_width=32, default_rate=2**6):
    class _SingleLed(Module):
        rate: Register.custom(size=counter_width, reset=default_rate)

        @logic
        def _blink(self, platform):
            self.counter = Signal(counter_width)
            self.sync += [self.counter.eq(self.counter + self.rate.storage_full)]
            self.sync += [platform.request("user_led").eq(self.counter[-1])]

    return _SingleLed


class FourLeds(Module):
    led0: SingleLed(default_rate=2**4)
    led1: SingleLed(default_rate=2**5)
    led2: SingleLed(default_rate=2**6)
    led3_on: Register.custom(reset=1)

    @logic
    def _control_led(self, platform):
        self.sync += [platform.request("user_led").eq(self.led3_on.storage_full)]
