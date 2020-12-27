import logging
from migen_axi.platforms import redpitaya
from misoc.integration import cpu_interface
import shutil
import os
from pathlib import Path
from .soc import StemlabSoc
from ...core.migen import MigenModule


logger = logging.getLogger(__name__)


class StemlabBuilder:
    _build_dir = "build"
    _result_dir = "out/stemlab"
    _build_results = ["bitstream.bin", "csr.csv"]

    def __init__(self, Top):
        self._create_platform()
        self.top = MigenModule(Top, platform=self._platform)
        self.soc = StemlabSoc(platform=self._platform, top=self.top)

    def _create_platform(self):
        logger.debug("Creating platform")
        self._platform = redpitaya.Platform()
        self._platform.toolchain.bitstream_commands.extend(["set_property BITSTREAM.GENERAL.COMPRESS True [current_design]"])
        self._platform.toolchain.additional_commands.extend([
            "write_cfgmem -force -format BIN -size 2 -interface SMAPx32 -disablebitswap -loadbit \"up 0x0 ./top.bit\" ./bitstream.bin",
        ])

    def _write_csr_file(self):
        with open(f"{self._build_dir}/csr.csv", "w") as f:
            f.write(cpu_interface.get_csr_csv(self.soc.get_csr_regions()))

    def build(self):
        logger.debug("Running vivado build...")
        self.soc.build(build_dir=self._build_dir)
        self._write_csr_file()
        logger.debug(f"Finished build for {self.__class__.__name__}.")
        # copy all build results
        Path(self._result_dir).mkdir(parents=True, exist_ok=True)
        for result in self._build_results:
            shutil.copy(Path(self._build_dir) / result, Path(self._result_dir) / result)