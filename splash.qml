import QtQuick
import QtQuick.Window


Item {
    id: splashScreen
    width: 600
    height: 400
    

    Rectangle {
        anchors.fill: parent
        color: "#23272e"

        Column {
            anchors.centerIn: parent
            spacing: 20
            width: parent.width

            Text {
            text: "Rivridis Assistant"
            color: "white"
            font.pixelSize: 32
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width
            }

            Text {
            text: "Loading..."
            color: "white"
            font.pixelSize: 24
            horizontalAlignment: Text.AlignHCenter
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width
            }
        }
    }
}
