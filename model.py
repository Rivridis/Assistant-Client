import textwrap
from qdrant_client import QdrantClient
from functions import flist
import features
from functions import *
from messages import message, message_main, response_format, response_google, message_google, message_summary, intent_format
import pywhatkit


class AssistantModel:
    def __init__(self):
        self.client = QdrantClient(path="./assistant.db")
        self.docs = flist
        self.metadata = [
            {"source": "search-function"},
            {"source": "weather-function"},
            {"source": "play-function"},
            {"source": "app-open-function"}
        ]
        self.ids = [1, 2, 3, 4]

        self.client.add(
            collection_name="assistant",
            documents=self.docs,
            metadata=self.metadata,
            ids=self.ids
        )

        with open("memory.txt", "r") as f:
            self.chat_memory = f.read()

    def process_chat(self,text,llm):
        print(text)
        message_main[1]["content"] = ""
        inp = text
        results = self.client.query(
        collection_name="assistant",
        query_text=inp,
        limit=2,
        )

        content = results[0].metadata['document'] + results[1].metadata['document']
        function_names =  self.metadata[(results[0].id)-1]['source'] + " " + self.metadata[(results[1].id)-1]['source']
        print(content)
        
        message[1]["content"] = inp
        message[0]["content"] = message[0]["content"].split("MAIN")[0]
        message[0]["content"] += "\nMAIN" + "\n"
        message[0]["content"] += content
        message[0]["content"] += self.chat_memory

        # Intent classification LLM call
        intent_classifier_prompt = [
            {
            "role": "system",
            "content": f"""
                You are an intent classifier for an assistant.
                Functions Available: {function_names}
                Given the chat history and the latest user input, classify the intent as one of:
                - tool_call: The user wants to use a tool/function and has provided enough details. This also used when the user has clarified the function call in chat history. Only use this when the user query can be solved using the available functions. Use chat if the user is asking for something that cannot be done with the available functions. \n
                - clarify: When the user wants to use a tool/function but has not provided enough details to call the function properly, so clarification is needed. Used for tools calls that need more information like dates, locations, like booking/planning something, searching for something, playing something etc. Check the chat history before using this intent. \n
                - chat: The user just wants to chat with the assistant or is asking general questions, no tool call is needed. Also used when the user is asking you to reccomend something. This is also used when the user query can't be answered with the given functions.\n
                Respond ONLY in JSON with this format: {{"intent": "tool_call|clarify|chat"}}
                Examples:
                User: What's the weather in Paris?
                Output: {{"intent": "tool_call"}}
                User: Play a song.
                Output: {{"intent": "clarify"}}
                User: How are you today?
                Output: {{"intent": "chat"}}
                
                Chat history:
                {self.chat_memory}
            """
            },
            {
            "role": "user",
            "content": f"""{text}"""
            }
        ]

        intent_response = llm.chat.completions.create(
            model='gpt-4o-mini',
            messages=intent_classifier_prompt,
            response_format=intent_format,
        )
        intent_json = intent_response.choices[0].message.content
        print("Intent classification:", intent_json)

        func = eval(intent_json)
        if func.get("intent") == "chat":
            # Handle chat intent
            Final = ""
            pass

        elif func.get("intent") == "clarify":
        
            # Ask the user for more details to clarify the function call
            clarify_prompt = [
                {
                    "role": "system",
                    "content": f""" You are an AI assistant that asks the user for more details regarding their query. Please use the chat history to understand the user's query and check if enough details are provided. If the details are not enough, ask the user for more specific details such as  date, time location or relevant information. If the details are enough, ask if the user wants to proceed with the function call.
                    CHAT MEMORY:
                    {self.chat_memory}"""
                },
                {
                    "role": "user",
                    "content": f"{text}\n"
                }
            ]
            response = llm.chat.completions.create(
                model='gpt-4o-mini',
                messages=clarify_prompt,
            )
            clarification = response.choices[0].message.content
            self.chat_memory += f" User Message: {inp}\n Assistant Response: {clarification}\n"
            if len(self.chat_memory) > 5000:
                self.chat_memory = self.chat_memory[-5000:]
            with open("memory.txt", "w") as f:
                f.write(self.chat_memory)
            
            return clarification
        
        elif func.get("intent") == "tool_call":

            tool_response = llm.chat.completions.create(
                model='gpt-4o-mini',
                messages=message,
                response_format=response_format,
            )

            dedented_string = textwrap.dedent(tool_response.choices[0].message.content)
            func = eval(dedented_string)
            print(func)
            
            functions = func.get("functions")
            Final = ""
            
            for i in range(len(functions)):
                function_called = functions[i].get("function_called")
                function_value = functions[i].get("function_value")

                if function_called == "search":
                    query = function_value
                    query_output = features.internet_search(query)
                    message_google[1]["content"] = str(query_output)
                    
                    response = llm.chat.completions.create(
                    model ='gpt-4o-mini',
                    messages= message_google,
                    response_format= response_google,
                    )

                    value = response.choices[0].message.content
                    print(value)
                    selected_url = query_output[int(value)]
                    url = selected_url["url"]

                    website_data = features.read_website(url)
                    print(website_data)
                    website_data = website_data[:4000]

                    message_summary[1]["content"] = str(inp) + "\n" + str(website_data)

                    response = llm.chat.completions.create(
                    model ='gpt-4o-mini',
                    messages= message_summary,
                    )

                    summary = response.choices[0].message.content
                    
                    if len(self.chat_memory) > 5000:
                        self.chat_memory = self.chat_memory[-5000:]
                    
                    Final += f"Function Result: {summary}\n"
                    Final += f"Function Result: The url of the website used in the summary is {url}, which is to be provided to the user.\n"

                if function_called == "music":
                    match = function_value
                    print(match)
                    pywhatkit.playonyt(str(match))
                    Final += f"Function Result: Call is successful. Song has been changed to {match}, which is playing now.\n"

                if  function_called == "youtube":
                    match = function_value
                    print(match)
                    pywhatkit.playonyt(str(match))
                    Final += f"Function Result: Video has been set to {match}, which is playing now.\n No need to reccomend any videos to the user."

                if function_called == "weather":
                    location = function_value
                    if location == "":
                        location = "Tokyo, Japan"
                    weather_data = features.weather(location)
                    print(weather_data)
                    Final += f"Function Result: {str(weather_data)}. Show this to the user in a user readable format.\n"
                
                if function_called == "app_open":
                    app_name = function_value
                    print(app_name)
                    features.open_app(app_name)
                    Final += f"Function Result: The application {app_name} has been opened successfully.\n"

        message_main[0]["content"] =  message_main[0]["content"].split("MAIN")[0]
        message_main[0]["content"] += "\nMAIN" + "\n"
        message_main[0]["content"] += str(self.chat_memory) + "\n"
        message_main[1]["content"] += Final + "\n"

        # Add chat memory to message_main before generating the response
        message_main[1]["content"] += inp + "\n"
        print(message_main[1]["content"])

        if len(self.chat_memory) > 5000:
            self.chat_memory = self.chat_memory[-5000:]

        response = llm.chat.completions.create(
            model='gpt-4o-mini',
            messages=message_main,
        )

        out = response.choices[0].message.content

        self.chat_memory += " User Message:" + inp + "\n"
        self.chat_memory += " Assistant Response:" + out + "\n"

        if len(self.chat_memory) > 5000:
            self.chat_memory = self.chat_memory[-5000:]
        print(self.chat_memory)

        with open("memory.txt", "w") as f:
            f.write(self.chat_memory)
        return out
