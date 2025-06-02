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

assistant = PDFChatAssistant()
models = AssistantModel()
coding = Code()

try:
    llm = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="sk-xxx")
    # Test connection by listing models
    llm.models.list()
    print("Successfully connected to the LLM server.")
except Exception as conn_exc:
    print(f"Failed to connect to the LLM server: {conn_exc}")
    raise



QML_IMPORT_NAME = "mymodule"
QML_IMPORT_MAJOR_VERSION = 1
class Worker(QObject):
    finished = Signal()
    resultReady = Signal(str)

    @Slot(str)
    def process(self, text):
        result = models.process_chat(text,llm)
        self.resultReady.emit(result)
        self.finished.emit()

    @Slot(str, str)
    def code(self, text, code):
        print(text)
        result = coding.process_chat(text, code,llm)
        self.resultReady.emit(result)
        self.finished.emit()

    @Slot(str, str)
    def pdf(self, text, url):
        print(text)
        result = assistant.process_chat(text, url,llm)
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

