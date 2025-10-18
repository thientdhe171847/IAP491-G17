import QtQuick
import QtQuick.Controls

Rectangle {
    id: rectangle
    width: Constants.width
    height: Constants.height
    color: "#d9d9d9"

    signal startClicked  // Khai báo signal

    Rectangle {
        id: mainPanel
        anchors.centerIn: parent
        width: 457
        height: 546
        color: "#b3cdde"

        Rectangle {
            id: startButton
            x: 165
            y: 392
            width: 118
            height: 64
            radius: 10
            color: mouseArea.containsMouse ? "#CCCCCC" : "#1976D2"
            border.color: "white"
            border.width: 2

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
                onClicked: startClicked()  // Phát tín hiệu khi bấm
            }
        }

        Text {
            id: text1
            x: 54
            y: 219
            width: 251
            text: qsTr("       Malicious Behavior Detection through\nCross-Artifact Consistency Analysis in Mobile Devices")
            font.pixelSize: 15
        }

        Image {
            id: image
            x: 118
            y: 8
            width: 213
            height: 190
            source: "logo.png"
            fillMode: Image.PreserveAspectFit
        }
    }
}
