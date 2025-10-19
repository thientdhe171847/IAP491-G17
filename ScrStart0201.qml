import QtQuick
import QtQuick.Controls

Rectangle {
    id: rectangle
    anchors.fill: parent
    color: "#b3cdde"

    signal startClicked

    Column {
        anchors.centerIn: parent
        spacing: 40

        Image {
            id: image
            width: 213
            height: 190
            source: "logo.png"
            fillMode: Image.PreserveAspectFit
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            id: text1
            width: 400
            text: qsTr("       Malicious Behavior Detection through\nCross-Artifact Consistency Analysis in Mobile Devices")
            font.pixelSize: 15
            horizontalAlignment: Text.AlignHCenter
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Rectangle {
            id: startButton
            width: 118
            height: 64
            radius: 10
            color: mouseArea.containsMouse ? "#CCCCCC" : "#1976D2"
            border.color: "white"
            border.width: 2
            anchors.horizontalCenter: parent.horizontalCenter

            Text {
                anchors.centerIn: parent
                text: "Start"
                font.pixelSize: 16
                color: "white"
            }

            MouseArea {
                id: mouseArea
                anchors.fill: parent
                hoverEnabled: true
                onClicked: startClicked()
            }
        }
    }
}
