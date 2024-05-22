"""
Event validation.

This module contains the logic used to validate event definitions. It runs in CI to validate pull requests,
but can and should also be ran locally.

In order to run, install dependencies from 'events/requirements.txt'.

We check that each event directory satisfies the following:
* Contains 'meta.md', `banners/` and 'server_icons/' with at least 1 file inside each
* The 'meta.md' file either registers the event as fallback, or specifies the start and end dates
* The 'meta.md' file contains an event description between 1 and 2048 characters in length

If all events are set up correctly, we also validate that:
* There is exactly 1 fallback event
* Non-fallback events do not collide in time

If a problem in event configuration is detected, the program will print information to stdout and stop with an
exit code of 1. Otherwise, exit code 0 indicates that events are set up correctly.
"""

import sys
import typing as t
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import frontmatter
except ImportError:
    print("Please install the dependencies specified in 'events/requirements.txt'")
    sys.exit(1)

# Arbitrary year in which we do date checks (note: intentionally leap to allow Feb 29)
ARBITRARY_YEAR = 2020


class Misconfiguration(Exception):
    """Indication of event misconfiguration."""

    pass


class Event(t.NamedTuple):
    """Runtime representation of a correctly defined event."""

    name: str
    fallback: bool
    start_date: t.Optional[date]
    end_date: t.Optional[date]
    description: str


def make_event(name: str, from_dir: Path) -> Event:
    """
    Construct an `Event` instance from `from_dir`.

    This function performs all necessary validation to ensure that the event is configured properly. If a problem
    is encountered, `Misconfiguration` will be raised with an explanation.

    An `Event` instance is returned only if the event is entirely valid.
    """
    server_icons = Path(from_dir, "server_icons")
    banners = Path(from_dir, "banners")
    meta = Path(from_dir, "meta.md")

    asset_requirements = [
        ("server_icons", server_icons.is_dir()),
        ("banners", banners.is_dir()),
        ("meta.md", meta.is_file()),
    ]
    missing_assets = ", ".join(name for name, exists in asset_requirements if not exists)

    if missing_assets:
        raise Misconfiguration(f"Missing assets: {missing_assets}")

    icons = [icon for icon in server_icons.iterdir() if icon.is_file()]
    banners = [banner for banner in banners.iterdir() if banner.is_file()]

    if not icons:
        raise Misconfiguration("No files in 'server_icons'")
    if not banners:
        raise Misconfiguration("No files in the `banners` folder")

    try:
        meta_bytes = meta.read_bytes()
        attrs, description = frontmatter.parse(meta_bytes, encoding="UTF-8")
    except Exception as parse_exc:
        raise Misconfiguration(f"Failed to parse 'meta.md': {parse_exc}")

    if not description:
        raise Misconfiguration("No description in 'meta.md'")

    if not len(description) <= 2048:
        raise Misconfiguration(f"Description too long ({len(description)} characters), must be <= 2048")

    fallback = attrs.get("fallback", False)

    if not isinstance(fallback, bool):
        raise Misconfiguration(f"Value under 'fallback' key must be a boolean")

    if fallback:
        return Event(name=name, fallback=True, start_date=None, end_date=None, description=description)

    missing_dates = {"start_date", "end_date"} - attrs.keys()

    if missing_dates:
        as_string = ", ".join(missing_dates)
        raise Misconfiguration(f"Non-fallback event must have attributes: {as_string}")

    date_fmt = "%B %d %Y"  # Ex: July 10 2020

    start_date = attrs["start_date"]
    try:
        start_date = datetime.strptime(f"{start_date} {ARBITRARY_YEAR}", date_fmt).date()
    except Exception as exc:
        raise Misconfiguration(f"Attribute 'start_date' with value '{start_date}' failed to parse: {exc}")

    end_date = attrs["end_date"]
    try:
        end_date = datetime.strptime(f"{end_date} {ARBITRARY_YEAR}", date_fmt).date()
    except Exception as exc:
        raise Misconfiguration(f"Attribute 'end_date' with value '{end_date}' failed to parse: {exc}")


    return Event(name=name, fallback=False, start_date=start_date, end_date=end_date, description=description)


def active_days(event: Event) -> t.Iterator[date]:
    """
    Generate all days in which `event` is active.

    All dates returned will be in the same year.

    This can only be called for non-fallback events. The fallback event does not have start and end dates.
    """
    if None in (event.start_date, event.end_date):
        raise RuntimeError("Cannot generate days: event does not have start and date!")

    state = event.start_date
    while True:
        yield state
        if state == event.end_date:
            break
        state += timedelta(days=1)
        # Wrap around to the same year, so comparisons only compare day and month.
        state = state.replace(year=ARBITRARY_YEAR)


def find_collisions(events: t.List[Event]) -> t.Dict[date, t.List[Event]]:
    """
    Find the mapping of dates to colliding events, if any.

    The `events` arg cannot contain the fallback event.
    """
    schedule = defaultdict(list)

    for event in events:
        for day in active_days(event):
            schedule[day].append(event)

    return {day: events for day, events in schedule.items() if len(events) > 1}


def check_date_configuration(events: t.List[Event]) -> None:
    """
    Ensure that start and end dates of `events` do not collide.

    Additionally, this also verifies that there is exactly 1 fallback event.

    Raise `Misconfiguration` with a listing of colliding events, if any are found.
    """
    fallback_events = [event for event in events if event.fallback]

    if not fallback_events:
        raise Misconfiguration(f"There is no fallback event")

    if len(fallback_events) > 1:
        as_string = ", ".join(event.name for event in fallback_events)
        raise Misconfiguration(f"There are multiple fallback events: {as_string} (must be exactly 1)")

    non_fallback_events = [event for event in events if not event.fallback]
    collisions = find_collisions(non_fallback_events)

    if not collisions:
        return

    report_lines = []

    for day, collision in collisions.items():
        date_string = day.strftime("%B %d")  # Ex: January 24
        event_string = ", ".join(event.name for event in collision)

        report_lines.append(f"{date_string}: {event_string}")

    collision_report = "\n".join(report_lines)
    raise Misconfiguration(f"Event collision detected:\n{collision_report}")


def main() -> None:
    """
    Discover and validate all events.

    We first validate individual events and load them into `Event` instances.

    If all events are configured properly, we proceed with cross-event validation, checking for the existence
    of the fallback event and finding any conflicts between non-fallback events.

    If any issues are encountered, stop the program with a return code of 1, and otherwise 0.
    """
    parent = Path(__file__).parent
    event_directories = [directory for directory in parent.iterdir() if directory.is_dir()]

    events: t.List[Event] = []

    for directory in event_directories:
        event_name = directory.name
        try:
            event = make_event(event_name, directory)
        except Misconfiguration as misconfiguration:
            print(f"[FAIL] [{event_name}] {misconfiguration}")
        else:
            print(f"[PASS] [{event_name}]")
            events.append(event)

    if len(events) != len(event_directories):
        print("Dates will not be verified until all events pass validation!")
        sys.exit(1)

    try:
        check_date_configuration(events)
    except Misconfiguration as misconfiguration:
        print(f"[FAIL] {misconfiguration}")
        sys.exit(1)

    print(f"[PASS] All {len(events)} events passed validation")


if __name__ == "__main__":
    main()
