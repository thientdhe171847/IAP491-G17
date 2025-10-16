import QtQuick 6.5
import QtQuick.Controls

Rectangle {
    id: screen03
    signal nextClicked

    width: Constants.width
    height: Constants.height
    color: "#d9d9d9"

    property string selectedInput: ""
    property string selectMode: "file"

    Rectangle {
        id: mainPanel
        width: 900
        height: 700
        anchors.centerIn: parent
        color: "#b3cdde"
        radius: 10
        border.color: "#ffffff"
        border.width: 2

        // ===== Label =====
        Text {
            id: inputLabel
            text: "[Select Input]"
            font.pixelSize: 18
            font.bold: true
            anchors.top: parent.top
            anchors.topMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter
        }

        // ===== Radio chọn File/Folder =====
        Row {
            id: rowChoose
            anchors.top: inputLabel.bottom
            anchors.topMargin: 35
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 40

            RadioButton {
                id: fileRadio
                text: "Select File"
                checked: true
                font.pixelSize: 14
                onCheckedChanged: if (checked) screen03.selectMode = "file"
            }
            RadioButton {
                id: folderRadio
                text: "Select Folder"
                font.pixelSize: 14
                onCheckedChanged: if (checked) screen03.selectMode = "folder"
            }
        }

        // ===== Nút chọn file/folder =====
        Button {
            id: chooseButton
            text: selectMode === "file" ? "📁 Choose File..." : "📂 Choose Folder..."
            anchors.top: rowChoose.bottom
            anchors.topMargin: 15
            anchors.horizontalCenter: parent.horizontalCenter
            width: 220
            height: 45

            background: Rectangle {
                color: chooseButton.hovered ? "#1565C0" : "#1976D2"
                radius: 8
                border.color: "#0D47A1"
                border.width: 2
            }

            contentItem: Text {
                text: chooseButton.text
                font.pixelSize: 15
                font.bold: true
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            onClicked: {
                backend.openFileOrFolderDialog(selectMode)
            }
        }

        // Kết nối signal backend
        Connections {
            target: backend
            function onFileOrFolderSelected(path) {
                screen03.selectedInput = path
            }
        }

        // ===== Preview Section =====
        Rectangle {
            id: previewPanel
            anchors.top: chooseButton.bottom
            anchors.topMargin: 25
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 80
            height: 300
            color: "#ffffff"
            radius: 10
            border.color: "#cccccc"
            border.width: 2

            Column {
                anchors.fill: parent
                anchors.margins: 25
                spacing: 15

                Text {
                    text: "Preview Section:"
                    font.pixelSize: 16
                    font.bold: true
                    color: "#333333"
                }

                Rectangle {
                    width: parent.width - 40
                    height: 2
                    color: "#e0e0e0"
                }

                // Selected path
                Row {
                    spacing: 10
                    width: parent.width - 40

                    Text {
                        text: "Selected Path:"
                        font.pixelSize: 14
                        font.bold: true
                        color: "#555555"
                        width: 150
                    }
                    Text {
                        text: selectedInput === "" ? "No file/folder selected" : selectedInput
                        font.pixelSize: 13
                        color: selectedInput === "" ? "#999999" : "#000000"
                        font.italic: selectedInput === ""
                        width: parent.width - 160
                        wrapMode: Text.WrapAnywhere
                        elide: Text.ElideMiddle
                    }
                }

                // Selection Mode: luôn hiển thị, đổi nội dung và style theo selectedInput
                Row {
                    spacing: 10
                    width: parent.width - 40

                    Text {
                        text: "Selection Mode:"
                        font.pixelSize: 14
                        font.bold: true
                        color: "#555555"
                        width: 150
                    }
                    Text {
                        text: selectedInput === "" ? "No file/folder selected"
                                                  : (selectMode === "file" ? "📄 File" : "📁 Folder")
                        font.pixelSize: 13
                        color: selectedInput === "" ? "#999999" : "#000000"
                        font.italic: selectedInput === ""
                        width: parent.width - 160
                        wrapMode: Text.WrapAnywhere
                        elide: Text.ElideMiddle
                    }
                }

                Rectangle {
                    width: parent.width - 40
                    height: 1
                    color: "#e0e0e0"
                }

                Column {
                    spacing: 8
                    Text {
                        text: "Note:"
                        font.pixelSize: 13
                        font.bold: true
                        color: "#555555"
                    }
                    Text {
                        text: "• File metadata will be analyzed during transformation"
                        font.pixelSize: 12
                        color: "#666666"
                    }
                    Text {
                        text: "• Timestamp range and record count will be detected automatically"
                        font.pixelSize: 12
                        color: "#666666"
                    }
                }
            }
        }

        // ===== Status Indicator =====
        Rectangle {
            id: statusIndicator
            anchors.top: previewPanel.bottom
            anchors.topMargin: 20
            anchors.horizontalCenter: parent.horizontalCenter
            width: 220
            height: 40
            color: selectedInput !== "" ? "#4CAF50" : "#FFC107"
            radius: 20

            Row {
                anchors.centerIn: parent
                spacing: 10

                Rectangle {
                    width: 12
                    height: 12
                    radius: 6
                    color: "white"
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    text: selectedInput !== "" ? "✓ Ready to Process" : "⚠ No Selection"
                    font.pixelSize: 14
                    font.bold: true
                    color: "white"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
        }

        // ===== Next Button =====
        Button {
            id: nextButton
            text: "Next → Transformation"
            width: 240
            height: 55
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter
            enabled: selectedInput !== ""

            background: Rectangle {
                color: nextButton.enabled ?
                       (nextButton.hovered ? "#388E3C" : "#4CAF50") :
                       "#BDBDBD"
                radius: 10
                border.color: nextButton.enabled ? "#2E7D32" : "#9E9E9E"
                border.width: 2
            }

            contentItem: Text {
                text: nextButton.text
                font.pixelSize: 16
                font.bold: true
                color: nextButton.enabled ? "white" : "#757575"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            onClicked: {
                if (selectedInput !== "") {
                    console.log("Selected:", selectedInput)
                    console.log("Mode:", selectMode)
                    nextClicked()
                }
            }
        }
    }
}
