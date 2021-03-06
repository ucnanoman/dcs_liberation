"""Objective adjacency lists."""
from __future__ import annotations

from typing import Dict, Iterator, List, Optional, TYPE_CHECKING

from game.utils import Distance

if TYPE_CHECKING:
    from game.theater import ConflictTheater, ControlPoint, MissionTarget


class ClosestAirfields:
    """Precalculates which control points are closes to the given target."""

    def __init__(self, target: MissionTarget,
                 all_control_points: List[ControlPoint]) -> None:
        self.target = target
        airfields = (c for c in all_control_points if c.runway_is_operational())
        self.closest_airfields: List[ControlPoint] = sorted(
            airfields, key=lambda c: self.target.distance_to(c)
        )

    def airfields_within(self, distance: Distance) -> Iterator[ControlPoint]:
        """Iterates over all airfields within the given range of the target.

        Note that this iterates over *all* airfields, not just friendly
        airfields.
        """
        for cp in self.closest_airfields:
            if cp.distance_to(self.target) < distance.meters:
                yield cp
            else:
                break


class ObjectiveDistanceCache:
    theater: Optional[ConflictTheater] = None
    closest_airfields: Dict[str, ClosestAirfields] = {}

    @classmethod
    def set_theater(cls, theater: ConflictTheater) -> None:
        if cls.theater is not None:
            cls.closest_airfields = {}
        cls.theater = theater

    @classmethod
    def get_closest_airfields(cls, location: MissionTarget) -> ClosestAirfields:
        if cls.theater is None:
            raise RuntimeError(
                "Call ObjectiveDistanceCache.set_theater before using"
            )

        if location.name not in cls.closest_airfields:
            cls.closest_airfields[location.name] = ClosestAirfields(
                location, cls.theater.controlpoints
            )
        return cls.closest_airfields[location.name]
