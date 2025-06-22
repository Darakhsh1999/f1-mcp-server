import fastf1
import gradio as gr
import pandas as pd
from PIL import Image
from typing import Union
from fastf1.core import Session

# Local modules
from utils import parser_utils, track_utils
from utils.constants import (
    AVAILABLE_SESSION_TYPES,
    DRIVER_DETAILS,
    CONSTRUCTOR_DETAILS,
    CURRENT_YEAR
)

# Custom types
gp = Union[str, int]
session_type = Union[str, int, None]

### FastF1 tools ###

def get_session(year: int, round: gp, session_type: session_type) -> Session:
    """Retrieve a specific Formula 1 session.
    
    Args:
        year (int): The season year (e.g., 2024)
        round (str | int): The race round number or name (e.g., 1 or 'Monaco')
        session_type (str | int | None): Type of session (e.g., 'FP1', 'Q', 'R')
        
    Returns:
        Session: A FastF1 Session object for the specified parameters
        
    Note:
        If session_type is a string and not in AVAILABLE_SESSION_TYPES,
        returns an error message string instead.
    """

    # Check if session type is valid
    if isinstance(session_type, str):
        if session_type.lower() not in AVAILABLE_SESSION_TYPES:
            return f"Session type {session_type} is not available. Supported session types: {AVAILABLE_SESSION_TYPES}"
    
    if isinstance(round, str) and round.isnumeric():
        round = int(round)

    return fastf1.get_session(year, round, session_type)

def get_season_calendar(year: int) -> str:
    """Get the complete race calendar for a specific F1 season.
    
    Args:
        year (int): The season year to get the calendar for
        
    Returns:
        str: Formatted string containing the season calendar
    """
    season_calendar = fastf1.get_event_schedule(year)
    return parser_utils.parse_season_calendar(season_calendar)

def get_event_info(year: int, round: gp, format: str) -> str:
    """Retrieve information about a specific Formula 1 event.
    
    Args:
        year (int): The season year
        round (str | int): The race round number or name
        format (str): Output format ('human' for readable text, 'LLM' for structured data)
        
    Returns:
        str: Formatted event information based on the specified format
    """

    if isinstance(round, str) and round.isnumeric():
        round = int(round)

    event = fastf1.get_session(year, round, "race").event # Event object is the same for all sessions, so hardcode "race"
    if format == "human":
        data_interval = f"{event['Session1DateUtc'].date()} - {event['Session5DateUtc'].date()}"
        event_string = f"Round {event['RoundNumber']} : {event['EventName']} - {event['Location']}, {event['Country']} ({data_interval})"
        return event_string
    elif format == "LLM":
        return parser_utils.parse_event_info(event)

def driver_championship_standings(year: int, driver_name: str) -> str:
    """Get the championship standing for a specific driver in a given year.
    
    Args:
        year (int): The season year
        driver_name (str): Full name of the driver (e.g., 'Lewis Hamilton')
        
    Returns:
        str: Formatted string with driver's position, points, and wins
    """

    ergast = fastf1.ergast.Ergast()
    driver_standings = ergast.get_driver_standings(year).content[0]
    driver_standing = driver_standings[["position", "points", "wins", "givenName", "familyName"]].reset_index(drop=True)
    driver_standing = driver_standing[(driver_standing["givenName"] + " " + driver_standing["familyName"]) == driver_name]
    if driver_standing.empty:
        return f"Could not find stats for {driver_name}"
    suffix = "st" if driver_standing['position'].iloc[0] == 1 else "nd" if driver_standing['position'].iloc[0] == 2 else "rd" if driver_standing['position'].iloc[0] == 3 else "th"
    is_was = "is" if year == CURRENT_YEAR else "was"
    standings_string = f"{driver_name} {is_was} {int(driver_standing['position'].iloc[0])}{suffix} with {int(driver_standing['points'].iloc[0])} points and {int(driver_standing['wins'].iloc[0])} wins"
    return standings_string
    
def constructor_championship_standings(year: int, constructor_name: str) -> str:
    """Get the championship standing for a specific constructor in a given year.
    
    Args:
        year (int): The season year
        constructor_name (str): Name of the constructor team (e.g., 'Mercedes')
        
    Returns:
        str: Formatted string with constructor's position, points, and wins
    """

    ergast = fastf1.ergast.Ergast()
    constructor_standings = ergast.get_constructor_standings(year).content[0]
    constructor_standing = constructor_standings[["position", "points", "wins", "constructorName"]].reset_index(drop=True)
    constructor_standing = constructor_standing[constructor_standing["constructorName"] == constructor_name]
    suffix = "st" if constructor_standing['position'].iloc[0] == 1 else "nd" if constructor_standing['position'].iloc[0] == 2 else "rd" if constructor_standing['position'].iloc[0] == 3 else "th"
    are_were = "are" if year == CURRENT_YEAR else "were"
    standings_string = f"{constructor_name} {are_were} {int(constructor_standing['position'].iloc[0])}{suffix} with {int(constructor_standing['points'].iloc[0])} points and {int(constructor_standing['wins'].iloc[0])} wins"
    return standings_string

def track_visualization(year: int, round: gp, visualization_type: str) -> Image.Image:
    """Generate a visualization of the track with specified data.
    
    Args:
        year (int): The season year
        round (str | int): The race round number or name
        visualization_type (str): Type of visualization ('speed', 'corners', or 'gear')
        
    Returns:
        Image.Image: A PIL Image object containing the visualization
    """
    if isinstance(round, str) and round.isnumeric():
        round = int(round)

    session = get_session(year, round, "race")
    session.load()

    if visualization_type == "speed":
        return track_utils.create_track_speed_visualization(session)
    elif visualization_type == "corners":
        return track_utils.create_track_corners_visualization(session)
    elif visualization_type == "gear":
        return track_utils.create_track_gear_visualization(session)

def get_session_results(year: int, round: gp, session_type: session_type) -> pd.DataFrame:
    """Retrieve and format the results of a specific session.
    
    Args:
        year (int): The season year
        round (str | int): The race round number or name
        session_type (str | int | None): Type of session (e.g., 'Q', 'R', 'Sprint')
        
    Returns:
        pd.DataFrame: DataFrame containing the session results
        
    Raises:
        ValueError: If the session type is invalid
    """
    if isinstance(round, str) and round.isnumeric():
        round = int(round)

    try:
        session = get_session(year, round, session_type)
        session.load(telemetry=False)
        # Create a proper copy of the results DataFrame
        df = session.results[['DriverNumber', 'Abbreviation', 'FullName', 'Position', 
                            'GridPosition', 'Points', 'Status', 'Q1', 'Q2', 'Q3']].copy()
    except ValueError as e:
        raise gr.Error(f"Session type {session_type} is not supported for the specified round. This Grand Prix most likely did not include a sprint race/quali.")

    # Now we can safely modify the DataFrame
    df["Name"] = df.apply(lambda row: f"{row['FullName']} ({row['Abbreviation']} • {row['DriverNumber']})", axis=1)
    df = df.drop(columns=["FullName", "Abbreviation", "DriverNumber"])
    df = df.rename(columns={"Position": "Pos", "GridPosition": "Grid Pos"})

    # Process results based on session type
    if session_type in ["race", "sprint"]:
        df = df[["Pos", "Name", "Points", "Grid Pos", "Status"]]
    elif "qualifying" in session_type:
        df[["Q1", "Q2", "Q3"]] = df[["Q1", "Q2", "Q3"]].apply(lambda x: x.dt.total_seconds().apply(lambda y: f"{int(y//60):02d}:{int(y%60):02d}.{int(y%1*1000):03d}" if pd.notna(y) else "-"))
        df = df[["Pos", "Name", "Q1", "Q2", "Q3"]]
    return df

def get_driver_info(driver_name: str) -> str:
    """Retrieve detailed information about a specific driver.
    
    Args:
        driver_name (str): Full name of the driver (e.g., 'Max Verstappen')
        
    Returns:
        str: Formatted string with driver's details including name, team, number,
             nationality, and a brief summary
    """
    driver = DRIVER_DETAILS[driver_name]
    driver_info_string = f"{driver_name} ({driver['birth_date']}) {driver['nationality']}\n{driver['team']} #{driver['number']}\n\n{driver['summary']}"
    return driver_info_string

def get_constructor_info(constructor_name: str) -> str:
    """Retrieve detailed information about a specific constructor.
    
    Args:
        constructor_name (str): Full name of the constructor (e.g., 'Red Bull Racing')
        
    Returns:
        str: Formatted string with constructor's details including name, team, number,
             nationality, and a brief summary
    """
    constructor = CONSTRUCTOR_DETAILS[constructor_name]
    constructor_info_string = f"{constructor['team_name']} ({constructor_name})\n{constructor['base']}\nTeam principle: {constructor['team_principal']}\nDriver(s): {constructor['drivers'][0]} & {constructor['drivers'][1]}\nPower unit: {constructor['power_unit']}\nChassis: {constructor['chassis']}"
    return constructor_info_string
    

if __name__ == "__main__":
    session = get_session(2024, 1, "fp1")
    session.load()