import QtQuick
import QtQuick.Controls

Rectangle {
    id: rectangle
    width: Constants.width
    height: Constants.height
    color: "#d9d9d9"

    signal loadingCompleted  // Signal để thông báo loading hoàn tất

    Rectangle {
        id: mainPanel
        anchors.centerIn: parent
        width: 457
        height: 546
        color: "#b3cdde"

        Text {
            id: loadingLabel
            x: 32
            y: 425
            text: "Loading"
            font.pixelSize: 16
        }

        ProgressBar {
            id: progressBar
            x: 54
            y: 479
            width: 350
            value: 0
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
                    loadingCompleted()  // Phát signal khi loading xong
                }
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

        Text {
            id: text2
            x: 133
            y: 75
            width: 172
            height: 60
            text: qsTr("Text....")
            font.pixelSize: 22
        }
    }

    Component.onCompleted: {
        progressBar.value = 0
        progressTimer.start()
    }
}
