from qdrant_client import QdrantClient
from functions import flist
import features
from functions import *
from messages import message, message_main, response_format, response_google, message_google, message_summary
import pywhatkit


class AssistantModel:
    def __init__(self):
        self.client = QdrantClient(path="./assistant.db")
        self.docs = flist
        self.metadata = [
            {"source": "search-function"},
            {"source": "weather-function"},
            {"source": "play-function"}
        ]
        self.ids = [1, 2, 3]

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
        )

        content = results[0].metadata['document']

        message_main[0]["content"] =  message_main[0]["content"].split("MAIN")[0]
        message_main[0]["content"] += "\nMAIN" + "\n"
        message_main[0]["content"] += str(self.chat_memory) + "\n"
        
        message[1]["content"] = inp
        message[0]["content"] = message[0]["content"].split("MAIN")[0]
        message[0]["content"] += "\nMAIN" + "\n"
        message[0]["content"] += content
        message[0]["content"] += self.chat_memory

        # Generate a response
        response = llm.chat.completions.create(
            model ='gpt-4o-mini',
            messages= message,
            response_format= response_format,
        )

        func = eval(response.choices[0].message.content)
        print(func)
        # Extract and print the JSON response

        function_result = ""
        if func.get("function_called") == "search":
            query = func.get("function_value")
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
            
            self.chat_memory += " User Message:" + inp + "\n"
            self.chat_memory += " Assistant Response:" + summary + "\n"
            if len(self.chat_memory) > 5000:
                self.chat_memory = self.chat_memory[-5000:]
            with open("memory.txt", "w") as f:
                f.write(self.chat_memory)
            return(summary)

        if  func.get("function_called") == "music":
            match = func.get("function_value")
            print(match)
            pywhatkit.playonyt(str(match))
            function_result += f"Function Result: Song has been changed to {match}, which is playing now.\n"
        
        if  func.get("function_called") == "youtube":
            match = func.get("function_value")
            print(match)
            pywhatkit.playonyt(str(match))
            function_result += f"Function Result: Youtube search video result is {match}, which is playing now.\n"

        if func.get("function_called") == "weather":
            location = func.get("function_value")
            if location == "":
                location = "Tokyo, Japan"
            weather_data = features.weather(location)
            print(weather_data)
            function_result += f"Interpret this weather data {str(weather_data)} in a user readable format\n"


        if func.get("function_called") == "none":
            function_result += " No function called, please answer the user's question"


        message_main[0]["content"] += function_result + "\n"
        message_main[1]["content"] += inp + "\n"
        print(message_main[1]["content"])

        if len(self.chat_memory) > 5000:
            self.chat_memory = self.chat_memory[-5000:]


        response = llm.chat.completions.create(
            model ='gpt-4o-mini',
            messages= message_main,
        )

        out = response.choices[0].message.content

        self.chat_memory += " User Message:" + inp + "\n"
        self.chat_memory += " Assistant Response:" + out + "\n"


        if len(self.chat_memory) > 5000:
                self.chat_memory = self.chat_memory[-5000:]
        print(self.chat_memory)

        with open("memory.txt", "w") as f:
            f.write(self.chat_memory)
        return(out)
