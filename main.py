from json import load
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
from PySide6.QtWidgets import QMessageBox, QApplication

assistant = PDFChatAssistant()
models = AssistantModel()
coding = Code()

def load_model(host = "127.0.0.1", port = "5001"):
    try:
        url = "http://" + host + ":" + port + "/v1"
        llm = OpenAI(base_url= url, api_key="sk-xxx")
        # Test connection by listing models
        llm.models.list()
        print("Successfully connected to the LLM server.")
    except Exception as conn_exc:
        print(f"Failed to connect to the LLM server: {conn_exc}")
        llm = None
    return llm



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


if __name__ == "__main__":
    llm = load_model()
    if llm is None:
        app = QApplication(sys.argv)
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Connection Error")
        msg_box.setText("LLM server is not connected. \n Please launch the server and try again.")
        msg_box.exec()
        sys.exit(1)
    app = QGuiApplication(sys.argv)
    QQuickStyle.setStyle("FluentWinUI3")
    engine = QQmlApplicationEngine()
    app_icon = QIcon("app_icon.ico")
    QGuiApplication.setWindowIcon(app_icon)
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

