# Filtering Features Documentation

This document describes the filtering capabilities added to the Poker Tracker analysis functions.

## Overview

All analysis functions now support filtering to help you analyze specific subsets of your poker data:
- **Cash Games**: Date and position filtering
- **Tournaments**: Date filtering  
- **Expresso**: Date filtering

## Usage

### Command Line Interface (CLI)

All CLI tools now prompt for optional filters:

```bash
# Cash game analysis with filters
python recapitulatif_cash_game.py
# You'll be prompted for:
# - Date range (YYYY-MM-DD format)
# - Positions to include (BTN, SB, BB, UTG, CO, MP, HJ)

# Tournament analysis with filters  
python recapitulatif_tournoi.py
# You'll be prompted for:
# - Date range (YYYY-MM-DD format)

# Expresso analysis with filters
python recapitulatif_expresso.py  
# You'll be prompted for:
# - Date range (YYYY-MM-DD format)
```

### Programmatic Usage

```python
from recapitulatif_cash_game import analyser_resultats_cash_game
from recapitulatif_tournoi import analyser_resultats_tournois
from recapitulatif_expresso import analyser_resultats_expresso

# Cash game with date and position filters
results = analyser_resultats_cash_game(
    directory="/path/to/files",
    user_name="YourUsername", 
    date_filter=("2024-01-01", "2024-01-31"),  # January 2024
    position_filter=["BTN", "CO"]              # Button and Cutoff only
)

# Tournament with date filter
results = analyser_resultats_tournois(
    directory="/path/to/files",
    date_filter=("2024-01-01", "2024-01-31")   # January 2024
)

# Expresso with date filter  
results = analyser_resultats_expresso(
    directory="/path/to/files",
    date_filter=("2024-01-01", "2024-01-31")   # January 2024
)
```

### GUI Usage

The GUI now has filter controls in all analysis tabs:
- Date range inputs (start and end dates)
- Position checkboxes (cash game only)
- All filters are optional and work together

## Filter Types

### Date Filters

Format: `("YYYY-MM-DD", "YYYY-MM-DD")` or `None`

Examples:
- `("2024-01-01", "2024-01-31")` - January 2024 only
- `("2024-01-01", None)` - From January 1st onwards  
- `(None, "2024-01-31")` - Up to January 31st
- `None` - No date filtering (all data)

### Position Filters (Cash Game Only)

Format: List of position strings or `None`

Available positions:
- `BTN` - Button
- `SB` - Small Blind  
- `BB` - Big Blind
- `UTG` - Under the Gun
- `CO` - Cutoff
- `MP` - Middle Position
- `HJ` - Hijack

Examples:
- `["BTN"]` - Button only
- `["BTN", "CO", "HJ"]` - Late positions
- `["UTG", "MP"]` - Early/middle positions  
- `None` - No position filtering (all positions)

## Position Detection

The cash game analyzer automatically detects player positions based on:
- Seat numbers and button position from hand history
- Number of players at the table
- Standard poker position names for different table sizes

Position detection works for tables with 2-9 players and follows standard poker conventions.

## Backward Compatibility

All filtering features are fully backward compatible:
- Existing code continues to work without modification
- All filter parameters are optional
- Default behavior (no filters) remains unchanged

## Examples

### Analyze Late Position Play
```python
# Focus on button and cutoff performance
results = analyser_resultats_cash_game(
    directory, username, 
    position_filter=["BTN", "CO"]
)
```

### Analyze Recent Performance  
```python
# Last month's tournaments
results = analyser_resultats_tournois(
    directory,
    date_filter=("2024-01-01", "2024-01-31")
)
```

### Combine Filters
```python
# Button play from last week
results = analyser_resultats_cash_game(
    directory, username,
    date_filter=("2024-01-08", "2024-01-14"),
    position_filter=["BTN"]
)
```

## Testing

Run the filtering tests to verify functionality:
```bash
python test/test_filtering.py
```

Or run the demonstration script:
```bash
python demo_filtering.py
```