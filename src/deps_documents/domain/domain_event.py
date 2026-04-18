from typing import Generic, List, TypeVar

from deps_message_flow.events.common import DomainEvent

T_Event = TypeVar("T_Event", bound=DomainEvent)


class AggregateWithEvents(Generic[T_Event]):
    def __init__(self):
        self.events: List[T_Event] = []

    def add_event(self, event: T_Event):
        self.events.append(event)

    def clear_events(self):
        self.events.clear()

    def pop_all_events(self):
        events = self.events[:]
        self.events.clear()
        return events
