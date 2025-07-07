message = [
        {
            "role": "system",
            "content": """You are a helpful function calling AI that outputs in JSON format. Do not reply to the user's questions. Details about how to use functions are given below. Strictly follow that. Your previous response is given below. Use that to call the correct function.
            
            Function Descriptions:
            MAIN
            """,
        },
        {"role": "user", "content": ""},
    ]

message_main = [
        {
            "role": "system",
            "content": """Your name is Vivy, an assistant similar to Jarvis from Marvel who responds to the the user's questions. The function result that you called earlier will be provided before the user query. Always follow the values provided in the function result below, and don't make up your own values. Feel free to reccomend your opinion to the user, if the user asks you to reccomend something. \n
            Let the user know about the function call result. If the result is not relevant to the user's query, let the user know.
            You are provided with the chat memory of the conversation. Use it to answer the user's questions.
            EXAMPLE
            User: The value of function call is - weather is [40 celsius, 1013 hPa, Tokyo, Japan] \n
            Can you tell me the weather right now?
            
            Assistant: using the provided function result, The weather right now is 40 celsius with a pressure of 1013 hPa in Tokyo, Japan. Hope you enjoy the weather!.
            MAIN
            """,
        },
        {"role": "user", "content": ""},
    ]

message_google = [
        {
            "role": "system",
            "content": """You are an AI assistant that goes through the given list of url, title, and description of the website, and returns the index of the most relevant website to the user query that is given below. The value depends on the number of urls provided in the function value, and the number starts from 0.
            EXAMPLE
            System: How far is Jupiter from the moon?
            User:
            [{'url': 'https://en.wikipedia.org/wiki/Jupiter', 'title': 'Jupiter - Wikipedia', 'description': 'No description found'}, {'url': 'https://theskylive.com/how-far-is-jupiter', 'title': 'How Far Away Is Jupiter?', 'description': 'Precise distance of Jupiter from Moon'}]
            
            Assistant: 1.
            """,
        },
        {"role": "user", "content": ""},
    ]


response_format = {
  "type": "json_schema",
  "json_schema": {
    "name": "output_format",
    "schema": {
      "type": "object",
      "properties": {
        "functions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "function_called": {
                "type": "string",
                "enum": ["music", "weather", "search", "youtube"]
              },
              "function_value": {
                "type": "string"
              }
            },
            "required": ["function_called", "function_value"],
            "additionalProperties": False
          },
          "minItems": 1
        }
      },
      "required": ["functions"],
      "additionalProperties": False
    },
    "strict": True
  }
}

intent_format = {
  "type": "json_schema",
  "json_schema": {
    "name": "output_format",
    "schema": {
      "type": "object",
      "properties": {
        "intent": {
          "type": "string",
          "enum": ["tool_call", "clarify", "chat"]
        }
      },
      "required": ["intent"],
      "additionalProperties": False
    },
    "strict": True
  }
}

response_google = {
  "type": "json_schema",
  "json_schema": {
    "name": "output_format",
    "schema": {
      "type": "integer",
      "enum": [0, 1, 2, 3, 4]
    },
    "strict": True
  }
}

message_summary = [
        {
            "role": "system",
            "content": """You are an AI assistant that scans through the given large wall of google search results, and answers the user query using the information from the search results. If you are not able to find any relevant information, let the user know that you are not able to find any relevant information. Do not make up your own information, and do not use the information from the search results that is not relevant to the user query.
            """,
        },
        {"role": "user", "content": ""},
    ]
