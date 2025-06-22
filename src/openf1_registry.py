from enum import Enum
from dataclasses import dataclass
from typing import Dict, Set, List, Optional

api_endpoints = {
    "sessions": "sessions?",
    "weather": "weather?",
    "locations": "locations?",
    "drivers": "drivers?",
    "intervals": "intervals?",
    "laps": "laps?",
    "car_data": "car_data?",
    "pit": "pit?",
    "position": "position?",
    "race_control": "race_control?",
    "stints": "stints?",
    "team_radio": "team_radio?",
}

class FilterType(Enum):
    EQUALITY = "equality"       # exact match
    COMPARISON = "comparison"   # >, <, >=, <=

class DataType(Enum):
    STRING = "string"
    INTEGER = "integer"
    DATETIME = "datetime"
    BINARY = "binary"          # true/false filters

@dataclass
class FilterSpec:
    """Specification for an API filter parameter"""
    name: str
    filter_type: FilterType
    data_type: DataType
    description: str = ""
    allowed_values: Optional[List[str]] = None  # For equality filters with restricted values
    
    def get_query_examples(self) -> List[str]:
        """Generate example query parameters for this filter"""
        examples = []
        
        if self.data_type == DataType.BINARY:
            examples = [f"{self.name}=true", f"{self.name}=false"]
        
        elif self.filter_type == FilterType.EQUALITY:
            if self.allowed_values:
                examples = [f"{self.name}={val}" for val in self.allowed_values[:2]]
            elif self.data_type == DataType.STRING:
                examples = [f"{self.name}=example_value"]
            elif self.data_type == DataType.INTEGER:
                examples = [f"{self.name}=42"]
            elif self.data_type == DataType.DATETIME:
                examples = [f"{self.name}=2024-01-01T00:00:00Z", f"{self.name}=2024-01-01T10:30:00Z"]
        
        elif self.filter_type == FilterType.COMPARISON:
            if self.data_type == DataType.INTEGER:
                examples = [f"{self.name}>=10", f"{self.name}<100"]
            elif self.data_type == DataType.DATETIME:
                examples = [f"{self.name}>=2024-01-01T00:00:00Z", f"{self.name}<2024-12-31T00:00:00Z"]
            elif self.data_type == DataType.STRING:
                examples = [f"{self.name}>M", f"{self.name}<Z"]  # alphabetical comparison
        
        return examples
    
    def help_text(self) -> str:
        """Generate help text for this filter"""
        text = f"Filter: {self.name}\n"
        text += f"  Type: {self.filter_type.value} ({self.data_type.value})\n"
        
        if self.description:
            text += f"  Description: {self.description}\n"
        
        if self.allowed_values:
            text += f"  Allowed values: {', '.join(self.allowed_values)}\n"
        
        examples = self.get_query_examples()
        if examples:
            text += f"  Examples: {', '.join(examples)}"
        
        return text



class APIEndpointRegistry:
    """Registry for API endpoints and their supported filters"""
    
    def __init__(self, base_url: str = ""):
        self.base_url = base_url
        self.endpoints: Dict[str, Set[str]] = {}  # endpoint -> filter names
        self.filters: Dict[str, FilterSpec] = {}  # global filter definitions
    
    def define_filter(
        self, 
        name: str, 
        filter_type: FilterType, 
        data_type: DataType,
        description: str = "",
        allowed_values: Optional[List[str]] = None
    ) -> 'APIEndpointRegistry':
        """Define a filter that can be used by endpoints"""
        filter_spec = FilterSpec(name, filter_type, data_type, description, allowed_values)
        self.filters[name] = filter_spec
        return self
    
    def register_endpoint(self, endpoint: str, *filter_names: str) -> 'APIEndpointRegistry':
        """Register an API endpoint with its supported filters"""

        # Validate all filters exist
        for filter_name in filter_names:
            if filter_name not in self.filters:
                raise ValueError(f"Filter '{filter_name}' not defined. Use define_filter() first.")
        
        # Store endpoint -> filters mapping
        self.endpoints[endpoint] = set(filter_names)
        
        return self
    




    def get_endpoint_filters(self, endpoint: str) -> Dict[str, FilterSpec]:
        """Get all filters supported by an endpoint"""
        filter_names = self.endpoints.get(endpoint, set())
        return {name: self.filters[name] for name in filter_names}
        
    def get_filter_help(self, filter_name: str) -> str:
        """Get help text for a specific filter"""

        if filter_name in self.filters:
            return self.filters[filter_name].help_text()
        return f"Filter '{filter_name}' not found."
    
    def get_endpoint_help(self, endpoint: str) -> str:
        """Get help text for all filters supported by an endpoint"""

        filters = self.get_endpoint_filters(endpoint)
        if not filters:
            return f"Endpoint '{endpoint}' has no registered filters."
        
        help_text = f"API Endpoint: {self.base_url}{endpoint}\n"
        help_text += f"Supported filters ({len(filters)}):\n\n"
        
        for name, spec in sorted(filters.items()):
            help_text += spec.help_text() + "\n\n"
        
        return help_text.strip()
    
    def list_all_endpoints(self) -> List[str]:
        """Get list of all registered endpoints"""
        return sorted(self.endpoints.keys())
    
    def list_all_filters(self) -> List[str]:
        """Get list of all defined filters"""
        return sorted(self.filters.keys())


# Create registry with base URL
f1_api = APIEndpointRegistry("https://api.openf1.org/v1/")

# Define filters with their specifications
f1_api.define_filter("date", FilterType.COMPARISON, DataType.DATETIME, "The UTC date and time, in ISO 8601 format.")
f1_api.define_filter("driver_number", FilterType.EQUALITY, DataType.INTEGER, "The unique number assigned to an F1 driver")
f1_api.define_filter("meeting_key", FilterType.EQUALITY, DataType.STRING, "The unique identifier for the meeting. Use 'latest' to identify the latest or current meeting.")
f1_api.define_filter("session_key", FilterType.EQUALITY, DataType.STRING, "The unique identifier for the session. Use 'latest' to identify the latest or current session.")
f1_api.define_filter("speed", FilterType.COMPARISON, DataType.INTEGER, "Velocity of the car in km/h.")
f1_api.define_filter("country_code", FilterType.EQUALITY, DataType.STRING, "A code that uniquely identifies the country.")
f1_api.define_filter("first_name", FilterType.EQUALITY, DataType.STRING, "The first name of the driver.")
f1_api.define_filter("last_name", FilterType.EQUALITY, DataType.STRING, "The last name of the driver.")
f1_api.define_filter("full_name", FilterType.EQUALITY, DataType.STRING, "The full name of the driver.")
f1_api.define_filter("name_acronym", FilterType.EQUALITY, DataType.STRING, "Three-letter acronym of the driver's name.")
f1_api.define_filter("team_name", FilterType.EQUALITY, DataType.STRING, "The name of the driver's team.")
f1_api.define_filter("gap_to_leader", FilterType.COMPARISON, DataType.INTEGER, "The time gap to the race leader in seconds, +1 LAP if lapped, or null for the race leader.")
f1_api.define_filter("interval", FilterType.COMPARISON, DataType.INTEGER, "The time gap to the car ahead in seconds, +1 LAP if lapped, or null for the race leader.")
f1_api.define_filter("date_start", FilterType.COMPARISON, DataType.DATETIME, "The UTC starting date and time, in ISO 8601 format.")
f1_api.define_filter("date_end", FilterType.COMPARISON, DataType.DATETIME, "The UTC ending date and time, in ISO 8601 format.")
f1_api.define_filter("is_pit_out_lap", FilterType.EQUALITY, DataType.BINARY, "A boolean value indicating whether the lap is an out lap from the pit (true if it is, false otherwise).")
f1_api.define_filter("lap_duration", FilterType.COMPARISON, DataType.INTEGER, "The total time taken, in seconds, to complete the entire lap.")
f1_api.define_filter("lap_number", FilterType.EQUALITY, DataType.INTEGER, "The sequential number of the lap within the session (starts at 1).")
f1_api.define_filter("circuit_key", FilterType.EQUALITY, DataType.STRING, "The unique identifier for the circuit where the event takes place.")
f1_api.define_filter("circuit_short_name", FilterType.EQUALITY, DataType.STRING, "The short or common name of the circuit where the event takes place.")
f1_api.define_filter("country_key", FilterType.EQUALITY, DataType.STRING, "The unique identifier for the country where the event takes place.")
f1_api.define_filter("country_name", FilterType.EQUALITY, DataType.STRING, "The name of the country where the event takes place.")
f1_api.define_filter("location", FilterType.EQUALITY, DataType.STRING, "The city or geographical location where the event takes place.")
f1_api.define_filter("meeting_name", FilterType.EQUALITY, DataType.STRING, "The name of the meeting.")
f1_api.define_filter("meeting_official_name", FilterType.EQUALITY, DataType.STRING, "The official name of the meeting.")
f1_api.define_filter("year", FilterType.EQUALITY, DataType.INTEGER, "The year of the event.")
f1_api.define_filter("pit_duration", FilterType.COMPARISON, DataType.INTEGER, "The time spent in the pit, from entering to leaving the pit lane, in seconds.")
f1_api.define_filter("position", FilterType.EQUALITY, DataType.INTEGER, "Position of the driver (starts at 1).", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
f1_api.define_filter("category", FilterType.EQUALITY, DataType.STRING, "The category of the event (CarEvent, Drs, Flag, SafetyCar)", ["CarEvent", "Drs", "Flag", "SafetyCar"])
f1_api.define_filter("flag", FilterType.EQUALITY, DataType.STRING, "The flag displayed to the drivers.", ["Green", "Yellow", "Red", "Black", "White", "Blue", "Checkered", "White"])
f1_api.define_filter("message", FilterType.EQUALITY, DataType.STRING, "Description of the event or action.")
f1_api.define_filter("session_name", FilterType.EQUALITY, DataType.STRING, "The name of the session (Practice 1, Qualifying, Race, ...).")
f1_api.define_filter("session_type", FilterType.EQUALITY, DataType.STRING, "The type of the session (Practice, Qualifying, Race, ...).")
f1_api.define_filter("compound", FilterType.EQUALITY, DataType.STRING, "The specific compound of tyre used during the stint (SOFT, MEDIUM, HARD, ...).", ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"])
f1_api.define_filter("lap_end", FilterType.COMPARISON, DataType.INTEGER, "Number of the last completed lap in this stint.")
f1_api.define_filter("lap_start", FilterType.COMPARISON, DataType.INTEGER, "Number of the initial lap in this stint (starts at 1).")
f1_api.define_filter("stint_number", FilterType.EQUALITY, DataType.INTEGER, "The sequential number of the stint within the session (starts at 1).")
f1_api.define_filter("tyre_age_at_start", FilterType.COMPARISON, DataType.INTEGER, "The age of the tyres at the start of the stint, in laps completed.")
f1_api.define_filter("air_temperature", FilterType.COMPARISON, DataType.INTEGER, "Air temperature (°C).")
f1_api.define_filter("humidity", FilterType.COMPARISON, DataType.INTEGER, "Humidity percentage.")
f1_api.define_filter("pressure", FilterType.COMPARISON, DataType.INTEGER, "Air pressure (mbar).")
f1_api.define_filter("rainfall", FilterType.COMPARISON, DataType.INTEGER, "Whether there is rainfall.")
f1_api.define_filter("track_temperature", FilterType.COMPARISON, DataType.INTEGER, "Track temperature (°C).")
f1_api.define_filter("wind_direction", FilterType.COMPARISON, DataType.INTEGER, "Wind direction (°), from 0° to 359°.")
f1_api.define_filter("wind_speed", FilterType.COMPARISON, DataType.INTEGER, "Wind speed (m/s).")


# Register API endpoints with their supported filters
f1_api.register_endpoint("car_data", "date", "driver_number", "meeting_key", "session_key", "speed")
f1_api.register_endpoint("drivers", "session_key", "meeting_key", "country_code", "driver_number", "first_name", "last_name", "full_name", "name_acronym", "team_name")
f1_api.register_endpoint("intervals", "date", "driver_number", "meeting_key", "session_key", "gap_to_leader", "interval")
f1_api.register_endpoint("laps", "date_start", "driver_number", "meeting_key", "session_key", "lap_duration", "lap_number", "is_pit_out_lap")
f1_api.register_endpoint("location", "date", "driver_number", "meeting_key", "session_key")
f1_api.register_endpoint("meetings", "circuit_key", "circuit_short_name", "country_code", "country_key", "country_name", "date_start", "location", "meeting_key", "meeting_name", "meeting_official_name", "year")
f1_api.register_endpoint("pit", "date", "driver_number", "lap_number", "meeting_key", "session_key", "pit_duration")
f1_api.register_endpoint("position", "date", "driver_number", "meeting_key", "session_key", "position")
f1_api.register_endpoint("race_control", "category", "date", "driver_number", "meeting_key", "session_key", "flag", "message", "lap_number")
f1_api.register_endpoint("sessions", "circuit_key", "circuit_short_name", "country_code", "country_key", "country_name", "date_start", "date_end", "location", "session_name", "session_type", "session_key", "meeting_key", "year")
f1_api.register_endpoint("stints", "compound", "driver_number", "lap_end", "lap_start", "meeting_key", "session_key", "stint_number", "tyre_age_at_start")
f1_api.register_endpoint("team_radio", "date", "driver_number", "meeting_key", "session_key")
f1_api.register_endpoint("weather", "air_temperature", "date", "humidity", "pressure", "rainfall", "track_temperature", "wind_direction", "wind_speed", "meeting_key", "session_key")