from dataclasses import dataclass, field
from threading import Lock


@dataclass
class RequestMetrics:
    total_requests: int = 0
    total_errors: int = 0
    _lock: Lock = field(default_factory=Lock, repr=False)

    def record_request(self, *, is_error: bool = False) -> None:
        with self._lock:
            self.total_requests += 1
            if is_error:
                self.total_errors += 1


request_metrics = RequestMetrics()
