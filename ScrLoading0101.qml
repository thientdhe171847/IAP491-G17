import QtQuick
import QtQuick.Controls

Rectangle {
    id: rectangle
    anchors.fill: parent
    color: "#b3cdde"

    signal loadingCompleted

    Column {
        anchors.centerIn: parent
        spacing: 30

        Text {
            id: text2
            text: qsTr("Text....")
            font.pixelSize: 22
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

        Column {
            spacing: 15
            anchors.horizontalCenter: parent.horizontalCenter

            Text {
                id: loadingLabel
                text: "Loading"
                font.pixelSize: 16
                anchors.horizontalCenter: parent.horizontalCenter
            }

            ProgressBar {
                id: progressBar
                width: 350
                value: 0
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }

    Timer {
        id: progressTimer
        interval: 22
        repeat: true
        running: false
        onTriggered: {
            if (progressBar.value < 1) {
                progressBar.value += 0.05
            } else {
                progressTimer.stop()
                loadingCompleted()
            }
        }
    }

    Component.onCompleted: {
        progressBar.value = 0
        progressTimer.start()
    }
}
