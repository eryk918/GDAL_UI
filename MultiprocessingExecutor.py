# -*- coding: utf-8 -*-

import json
import sys
import tempfile
from multiprocessing import Pool, cpu_count
from typing import List, Tuple

from utils import universal_executor


class MultiprocessingExecutor:
    def __init__(self, cmds=List[List[str]]):
        self.cmds = cmds

    def process(self, command: List[str]) -> Tuple[str, str, int, str]:
        return universal_executor(command)

    def launcher(self) -> List[Tuple[str, str, int, str]]:
        pool = Pool(processes=int(cpu_count() / 2))
        return pool.starmap(self.process, [cmd for cmd in self.cmds])

    def run(self) -> List[Tuple[str, str, int, str]]:
        return self.launcher()


if __name__ == '__main__':
    _, temp = tempfile.mkstemp()
    cmd_list = json.load(open(sys.argv[1]))
    executor = MultiprocessingExecutor(cmd_list)
    with open(temp, 'w') as file:
        json.dump(executor.run(), file)
    print(temp)
