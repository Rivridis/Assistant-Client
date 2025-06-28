import json
import sys
from pathlib import Path
from PySide6.QtCore import QObject, Slot, Signal, QThread, QMetaObject, Qt, Q_ARG
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtQuickControls2 import QQuickStyle
from pdf_mode import PDFChatAssistant
from model import AssistantModel
from openai import OpenAI
from code_mode import Code
from PySide6.QtQuick import QQuickWindow, QQuickView

assistant = PDFChatAssistant()
models = AssistantModel()
coding = Code()
llm = None

# json file that contains host and port information
try:
    with open('api.json', 'r') as fp:
        config = json.load(fp)

except IOError:
    config = {'host':'127.0.0.1', 'port':'5001'}
    with open('api.json', 'w') as fp:
        json.dump(config, fp)

def load_model(host = config['host'], port = config['port']):
    global llm
    try:
        url = "http://" + host + ":" + port + "/v1"
        llm = OpenAI(base_url= url, api_key="sk-xxx")
        # Test connection by listing models
        llm.models.list()
        print("Successfully connected to the LLM server.")
        config['host'] = str(host)
        config['port'] = str(port)
        with open('api.json', 'w') as fp:
            json.dump(config, fp)
    except Exception as conn_exc:
        print(f"Failed to connect to the LLM server: {conn_exc}")
        llm = None
    return llm

def load_text_file(filepath="memory.txt"):
    chat_data = []
    user_msg = None
    assistant_msg = None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("User Message:"):
                    user_msg = line[len("User Message:"):].strip()
                elif line.startswith("Assistant Response:"):
                    assistant_msg = line[len("Assistant Response:"):].strip()

                # Once we have a pair, append both and reset
                if user_msg is not None and assistant_msg is not None:
                    chat_data.append({"sender": "User", "message": user_msg})
                    chat_data.append({"sender": "AI", "message": assistant_msg})
                    user_msg = None
                    assistant_msg = None

    except FileNotFoundError:
        print(f"File {filepath} not found.")
    except Exception as e:
        print(f"Error reading memory file: {e}")

    print(chat_data)
    return chat_data



QML_IMPORT_NAME = "mymodule"
QML_IMPORT_MAJOR_VERSION = 1
class Worker(QObject):
    finished = Signal()
    resultReady = Signal(str)

    @Slot(str)
    def process(self, text):
        try:
            result = models.process_chat(text, llm)
        except Exception as exc:
            result = f"Error: Lost connection to the LLM server. Details: {exc}"
        self.resultReady.emit(result)
        self.finished.emit()

    @Slot(str, str)
    def code(self, text, code):
        print(text)
        try:
            result = coding.process_chat(text, code, llm)
        except Exception as exc:
            result = f"Error: Lost connection to the LLM server. Details: {exc}"
        self.resultReady.emit(result)
        self.finished.emit()

    @Slot(str, str)
    def pdf(self, text, url):
        print(text)
        try:
            result = assistant.process_chat(text, url, llm)
        except Exception as exc:
            result = f"Error: Lost connection to the LLM server. Details: {exc}"
        self.resultReady.emit(result)
        self.finished.emit()

@QmlElement
class Backend(QObject):
    resultReady = Signal(str)

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.worker = Worker()

        self.worker.moveToThread(self.thread)
        self.worker.resultReady.connect(self.handle_result)
        self.thread.start()

    @Slot(str)
    def process(self, text):
        QMetaObject.invokeMethod(
            self.worker,
            "process",
            Qt.QueuedConnection,
            Q_ARG(str, text)
        )
    
    @Slot(str, str)
    def code(self, text, code):
        QMetaObject.invokeMethod(
            self.worker,
            "code",
            Qt.QueuedConnection,
            Q_ARG(str, text),
            Q_ARG(str, code)
        )

    @Slot(str, str)
    def pdf(self, text, url):
        QMetaObject.invokeMethod(
            self.worker,
            "pdf",
            Qt.QueuedConnection,
            Q_ARG(str, text),
            Q_ARG(str, url)
        )

    @Slot(str)
    def handle_result(self, output):
        print(f"[Backend] Result: {output}")
        self.resultReady.emit(output)

    @Slot(result='QVariant')
    def load_chat(self):
        return load_text_file()

def main_screen():
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)

def button_press(host, port):
    global llm
    try:
        llm = load_model(host, port)
    except Exception as e:
        print(f"Error loading model: {e}")
        llm = None
    if llm is not None:
        root.close()
        main_screen()
   


if __name__ == "__main__":
    
    app = QGuiApplication(sys.argv)
    QQuickStyle.setStyle("FluentWinUI3")
    engine = QQmlApplicationEngine()
    app_icon = QIcon("app_icon.ico")
    QGuiApplication.setWindowIcon(app_icon)


    splash_qml = Path(__file__).resolve().parent / "splash.qml"
    splash_view = QQuickView()
    splash_view.setFlags(splash_view.flags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    splash_view.setSource(splash_qml.as_uri())
    splash_view.setColor(Qt.transparent)
    splash_view.setModality(Qt.ApplicationModal)
    splash_view.setResizeMode(QQuickView.SizeRootObjectToView)
    
    splash_view.setFlag(Qt.WindowTransparentForInput, True)
    splash_view.show()
    app.processEvents() 

    llm = load_model()
    splash_view.close()
    
    if llm is None:
        qml_file = Path(__file__).resolve().parent / "port.qml"
        engine.load(qml_file)

        root = engine.rootObjects()[0]
        root.sendToPython.connect(button_press)

    else:
        qml_file = Path(__file__).resolve().parent / "main.qml"
        engine.load(qml_file)

    if not engine.rootObjects():
            sys.exit(-1)
    sys.exit(app.exec())



