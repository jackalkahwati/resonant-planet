"""Stream and event-based scheduling for kernel overlap."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any, Dict, List, Optional
import time


@dataclass
class Event:
    """Synchronization event for stream dependencies."""
    name: str
    timestamp: float = 0.0
    completed: bool = False

    def record(self) -> None:
        """Record event completion time."""
        self.timestamp = time.perf_counter()
        self.completed = True

    def wait(self) -> None:
        """Block until event completes (no-op in CPU simulation)."""
        pass


@dataclass
class Stream:
    """Execution stream for asynchronous kernel dispatch."""
    stream_id: int
    priority: int = 0
    queue: List[Callable] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)

    def enqueue(self, kernel: Callable, *args: Any, **kwargs: Any) -> None:
        """Enqueue a kernel for execution."""
        self.queue.append(lambda: kernel(*args, **kwargs))

    def record_event(self, event: Event) -> None:
        """Record an event on this stream."""
        self.events.append(event)
        event.record()

    def wait_event(self, event: Event) -> None:
        """Make this stream wait for an event."""
        event.wait()

    def flush(self) -> None:
        """Execute all queued kernels."""
        for kernel in self.queue:
            kernel()
        self.queue.clear()


class Scheduler:
    """Schedule kernels across multiple streams with dependencies."""

    def __init__(self, num_streams: int = 4) -> None:
        self.streams: Dict[int, Stream] = {
            i: Stream(stream_id=i, priority=0) for i in range(num_streams)
        }
        self.events: Dict[str, Event] = {}
        self.default_stream = self.streams[0]

    def create_stream(self, priority: int = 0) -> Stream:
        """Create a new execution stream."""
        stream_id = len(self.streams)
        new_stream = Stream(stream_id=stream_id, priority=priority)
        self.streams[stream_id] = new_stream
        return new_stream

    def create_event(self, name: str) -> Event:
        """Create a synchronization event."""
        event = Event(name=name)
        self.events[name] = event
        return event

    def enqueue_kernel(
        self,
        kernel: Callable,
        *args: Any,
        stream: Optional[Stream] = None,
        wait_events: Optional[List[Event]] = None,
        **kwargs: Any,
    ) -> None:
        """Enqueue kernel with optional event dependencies."""
        target_stream = stream or self.default_stream

        if wait_events:
            for event in wait_events:
                target_stream.wait_event(event)

        target_stream.enqueue(kernel, *args, **kwargs)

    def synchronize(self, stream: Optional[Stream] = None) -> None:
        """Block until stream completes all kernels."""
        if stream:
            stream.flush()
        else:
            for s in self.streams.values():
                s.flush()

    def synchronize_all(self) -> None:
        """Block until all streams complete."""
        self.synchronize()


