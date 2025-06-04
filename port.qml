//qmllint disable
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: settingsPage
    title: "Host & Port Settings"
    visible: true
    width: 400
    height: 300

    property string host: ""
    property int port: 0

    signal sendToPython(string host, string port)
    Column {
        anchors.centerIn: parent
        spacing: 20

        TextField {
            id: hostField
            width: 250
            placeholderText: "Enter host (e.g. 127.0.0.1)"
            text: settingsPage.host
            onTextChanged: settingsPage.host = text
        }

        TextField {
            id: portField
            width: 250
            placeholderText: "Enter port (e.g. 8080)"
            inputMethodHints: Qt.ImhDigitsOnly
            text: settingsPage.port === 0 ? "" : settingsPage.port.toString()
            validator: IntValidator { bottom: 1; top: 65535 }
            onTextChanged: {
                settingsPage.port = parseInt(text) || 0
            }
        }

        Row {
            width: parent.width
            spacing: 0
            Rectangle {
                width: (parent.width - saveButton.width) / 2
                height: 1
                color: "transparent"
            }
            Button {
                id: saveButton
                text: "Save"
                enabled: hostField.text.length > 0 && portField.text.length > 0
                onClicked: {
                    console.log("Host:", settingsPage.host, "Port:", settingsPage.port)
                    sendToPython(settingsPage.host, settingsPage.port)
                }
            }
            Rectangle {
                width: (parent.width - saveButton.width) / 2
                height: 1
                color: "transparent"
            }
        }
    }
}