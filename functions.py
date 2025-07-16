search_function = """Search Function
Takes in a query string and returns search results.
Use this when the user asks factual, date-based, or real-time questions, or if the user asks you to retrieve information.
This includes things like:
- Birthdays
- Historical facts
- Upcoming events or festivals
- News or current information
- Details about a person or place
- Booking details, schedules, timings and travel information.

The function value must contain a question or the user's query converted into a search query that passed to the search engine.
Example:
{
    "function_called": "search",
    "function_value": "How far is the moon from the earth"
}
"""

weather_function = """Weather Function
Takes in a location string and returns weather, temperature, and pressure data.
Default location is Tokyo, Japan if not provided by the user.
Use this when the user asks about the weather. Strictly follow the format given below, and make sure the function value is a location string.

Example:
{
    "function_called": "weather",
    "function_value": "Tokyo, Japan"
}
"""

play_functions = """

Music Function
Takes a music name with the artist and plays it.
Use this when the user asks to play a specific song or requests music.
If the user asks for a recommendation, provide a popular song.
Also, ask the user for a song before calling this function. If the user does not provide the function value, which is the song name, default to a popular song name as function value, something from Taylor swift, Billie Eilish, or even Jpop like Hatsune Miku songs or Anime songs like Demon Slayer, Attack on Titan, etc. Do not use this function for youtube vidoes, and use the youtube function instead. Never leave function value empty.
Example:
{
    "function_called": "music",
    "function_value": "The Nights - Avicii"
}

YouTube Function
Takes a query string and returns YouTube video results.
Use when the user asks to watch or explore videos (not music).
Examples include:
- Animal videos
- Tutorials
- Entertainment content

Example:
{
    "function_called": "youtube",
    "function_value": "cute cat videos"
}
"""
app_open_function = """
App Open Function
Takes the name of an application in windows, and opens it for the user. This is used when the user asks to open an application on their computer.
Use this when the user asks to open an application on their computer, like Recycle Bin, Discord, or any other installed or system application.
Make sure the function value is the name of the application to open, and it should be a valid application name that can be opened on the user's computer.

Example:
{
    "function_called": "app_open",
    "function_value": "File Explorer"
}

"""

flist = [search_function, weather_function,play_functions, app_open_function]