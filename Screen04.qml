import QtQuick
import QtQuick.Controls

Rectangle {
    id: screen04
    width: Constants.width
    height: Constants.height
    color: "#d9d9d9"

    signal nextClicked  // Signal để chuyển sang màn hình Analysis

    Rectangle {
        id: mainPanel
        width: 1150
        height: 600
        anchors.centerIn: parent
        color: "#c3bdde"
        radius: 20
        border.color: "#000000"
        border.width: 3

        // Input Artifacts Section
        Column {
            id: inputSection
            x: 50
            y: 40
            spacing: 10

            Text {
                text: "Input Artifacts:"
                font.pixelSize: 18
                font.bold: true
            }

            Row {
                spacing: 10
                Text {
                    text: "✓"
                    font.pixelSize: 16
                    color: "#7c4dff"
                    font.bold: true
                }
                Text {
                    text: "logcat.txt"
                    font.pixelSize: 16
                }
            }

            Row {
                spacing: 10
                Text {
                    text: "✓"
                    font.pixelSize: 16
                    color: "#7c4dff"
                    font.bold: true
                }
                Text {
                    text: "system.db"
                    font.pixelSize: 16
                }
            }
        }

        // Mapping Rules Panel
        Rectangle {
            id: mappingPanel
            x: 150
            y: 180
            width: 600
            height: 250
            color: "#f5f5f5"
            radius: 10
            border.color: "#cccccc"
            border.width: 1

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15

                Text {
                    text: "Mapping Rules Panel:"
                    font.pixelSize: 18
                    font.bold: true
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    text: "[Timestamp] ← log_time"
                    font.pixelSize: 16
                    font.family: "Courier New"
                }

                Text {
                    text: "[Package Name] ← app_id"
                    font.pixelSize: 16
                    font.family: "Courier New"
                }

                Text {
                    text: "[Action/Event] ← intent_action"
                    font.pixelSize: 16
                    font.family: "Courier New"
                }
            }
        }

        // Preview Normalized Table Button
        Button {
            id: previewButton
            text: "Preview Normalized Table"
            anchors.right: parent.right
            anchors.rightMargin: 50
            anchors.top: parent.top
            anchors.topMargin: 180
            width: 250
            height: 40

            background: Rectangle {
                color: previewButton.hovered ? "#e0e0e0" : "#f5f5f5"
                border.color: "#999999"
                border.width: 1
                radius: 5
            }

            contentItem: Text {
                text: previewButton.text
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                color: "#000000"
            }

            onClicked: {
                console.log("Preview table clicked")
            }
        }

        // Run Transformation Button
        Button {
            id: runButton
            text: "[Run Transformation]"
            anchors.left: parent.left
            anchors.leftMargin: 250
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 80
            width: 200
            height: 45

            background: Rectangle {
                color: runButton.hovered ? "#e0e0e0" : "#ffffff"
                border.color: "#000000"
                border.width: 2
                radius: 5
            }

            contentItem: Text {
                text: runButton.text
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                color: "#000000"
            }

            onClicked: {
                console.log("Run transformation clicked")
            }
        }

        // Next → Analysis Button
        Button {
            id: nextButton
            text: "[Next → Analysis]"
            anchors.right: parent.right
            anchors.rightMargin: 150
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 80
            width: 200
            height: 45

            background: Rectangle {
                color: "#000000"
                border.color: "#000000"
                border.width: 2
                radius: 5
            }

            contentItem: Text {
                text: nextButton.text
                font.pixelSize: 14
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                color: "#ffffff"
            }

            onClicked: {
                nextClicked()  // Phát signal để chuyển màn hình
            }
        }
    }
}
