from fastf1.events import EventSchedule, Event

def skip_key(key: str) -> bool:
    return True if (key == "F1ApiSupport" or key.endswith("Date")) else False

def parse_event_info(event: Event) -> str:
    return "Event info:\n"+"\n".join(f"{k}: {v}" for (k, v) in event.items() if not skip_key(k))

def parse_season_calendar(schedule: EventSchedule) -> str:

    events = []
    for idx in range(len(schedule)):
        e = schedule.iloc[idx]
        data_interval = f"{e['Session1DateUtc'].date()} - {e['Session5DateUtc'].date()}"
        event_string = f"Round {e['RoundNumber']} : {e['EventName']} - {e['Location']}, {e['Country']} ({data_interval})"
        events.append(event_string)

    return "Season calendar:\n"+"\n".join(events)
