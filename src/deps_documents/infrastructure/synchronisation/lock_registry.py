from contextlib import contextmanager
from threading import Lock
from typing import Dict, Generator, Tuple


class SynchronisationRegistry:
    def __init__(self) -> None:
        self._registry: Dict[str, Tuple[int, Lock]] = {}

        self._guard = Lock()

    @contextmanager
    def named_lock(self, name: str) -> Generator[None, None, None]:
        try:
            named_lock = self._allocate_lock(name)

            with named_lock:
                yield

        finally:
            self._free_lock(name)

    def _allocate_lock(self, name: str) -> Lock:
        with self._guard:
            if name not in self._registry:
                self._registry[name] = (0, Lock())

            cnt, lock = self._registry[name]
            self._registry[name] = (cnt + 1, lock)

            return lock

    def _free_lock(self, name: str) -> None:
        with self._guard:
            if name not in self._registry:
                return

            cnt, lock = self._registry[name]

            if cnt == 1:
                self._registry.pop(name)
            else:
                self._registry[name] = (cnt - 1, lock)
