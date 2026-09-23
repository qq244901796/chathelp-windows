"""Generation tokens protect UI results and fill actions across context changes."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Ticket:
    generation: int
    chat: str
    revision: int
    target: str | None


class Session:
    def __init__(self):
        self.generation = 0

    def invalidate(self):
        self.generation += 1

    def ticket(self, chat, revision, target):
        return Ticket(self.generation, chat, revision, target)

    def accepts(self, ticket, chat, revision, target):
        return ticket == self.ticket(chat, revision, target)
