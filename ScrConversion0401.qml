import QtQuick 6.5
import QtQuick.Controls

Rectangle {
    id: screen04
    width: Constants.width
    height: Constants.height
    color: "#d9d9d9"

    signal nextClicked
    signal backClicked

    property string inputPath: ""
    property string selectMode: ""
    property bool isProcessing: false
    property bool isCompleted: false
    property bool isFailed: false
    property string resultMessage: ""

    Rectangle {
        id: mainPanel
        width: 1000
        height: 750
        anchors.centerIn: parent
        color: "#b3cdde"
        radius: 10
        border.color: "#ffffff"
        border.width: 2

        // ===== Header =====
        Column {
            id: headerSection
            anchors.top: parent.top
            anchors.topMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 15

            Text {
                text: "Stage 1: Extraction & Conversion"
                font.pixelSize: 22
                font.bold: true
                color: "#1976D2"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Extract and convert data from RAW to standardized WORK structure"
                font.pixelSize: 13
                color: "#555555"
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        // ===== Input Summary =====
        Rectangle {
            id: inputSummary
            anchors.top: headerSection.bottom
            anchors.topMargin: 25
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 80
            height: 120
            color: "#ffffff"
            radius: 10
            border.color: "#e0e0e0"
            border.width: 2

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 12

                Text {
                    text: "📋 Input Summary"
                    font.pixelSize: 16
                    font.bold: true
                    color: "#333333"
                }

                Row {
                    spacing: 10
                    width: parent.width - 40

                    Text {
                        text: "Source:"
                        font.pixelSize: 13
                        font.bold: true
                        color: "#555555"
                        width: 100
                    }
                    Text {
                        text: inputPath
                        font.pixelSize: 13
                        color: "#000000"
                        width: parent.width - 110
                        wrapMode: Text.WrapAnywhere
                        elide: Text.ElideMiddle
                    }
                }

                Row {
                    spacing: 10
                    width: parent.width - 40

                    Text {
                        text: "Mode:"
                        font.pixelSize: 13
                        font.bold: true
                        color: "#555555"
                        width: 100
                    }
                    Text {
                        text: selectMode === "file" ? "📄 Single File" : "📁 Folder (Recursive)"
                        font.pixelSize: 13
                        color: "#1976D2"
                    }
                }
            }
        }

        // ===== Case ID Input =====
        Rectangle {
            id: caseIdSection
            anchors.top: inputSummary.bottom
            anchors.topMargin: 20
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 80
            height: 100
            color: "#ffffff"
            radius: 10
            border.color: "#e0e0e0"
            border.width: 2

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 12

                Text {
                    text: "Case ID (for output folder):"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#333333"
                }

                TextField {
                    id: caseIdInput
                    width: parent.width - 40
                    height: 40
                    placeholderText: "e.g., CASE_2025_Android01"
                    text: "CASE_2025_Android01"
                    font.pixelSize: 13
                    enabled: !isProcessing && !isCompleted && !isFailed

                    background: Rectangle {
                        color: caseIdInput.enabled ? "#ffffff" : "#f5f5f5"
                        border.color: caseIdInput.activeFocus ? "#1976D2" : "#cccccc"
                        border.width: 2
                        radius: 5
                    }
                }
            }
        }

        // ===== Progress Section =====
        Rectangle {
            id: progressSection
            anchors.top: caseIdSection.bottom
            anchors.topMargin: 20
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 80
            height: 220
            color: "#ffffff"
            radius: 10
            border.color: "#e0e0e0"
            border.width: 2
            visible: isProcessing || isCompleted || isFailed

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15

                Text {
                    text: isCompleted ? "✅ Completed"
                        : isFailed ? "❌ Failed or Cancelled"
                        : "⚙️ Processing..."
                    font.pixelSize: 16
                    font.bold: true
                    color: isCompleted ? "#4CAF50" : isFailed ? "#F44336" : "#1976D2"
                }

                ProgressBar {
                    id: progressBar
                    width: parent.width - 40
                    height: 30
                    value: 0

                    background: Rectangle {
                        color: "#e0e0e0"
                        radius: 5
                    }

                    contentItem: Item {
                        Rectangle {
                            width: progressBar.visualPosition * parent.width
                            height: parent.height
                            color: isCompleted ? "#4CAF50" : isFailed ? "#F44336" : "#1976D2"
                            radius: 5
                        }
                    }
                }

                Text {
                    id: progressText
                    text: "Ready to start..."
                    font.pixelSize: 13
                    color: "#555555"
                    width: parent.width - 40
                    wrapMode: Text.WordWrap
                }

                // Result message area
                ScrollView {
                    width: parent.width - 40
                    height: 80
                    visible: isCompleted || isFailed

                    TextArea {
                        text: resultMessage
                        font.pixelSize: 12
                        color: "#333333"
                        wrapMode: Text.WordWrap
                        readOnly: true
                        background: Rectangle {
                            color: "#f5f5f5"
                            border.color: "#cccccc"
                            border.width: 1
                            radius: 5
                        }
                    }
                }
            }
        }

        // ===== Process Info (when not processing) =====
        Rectangle {
            id: infoSection
            anchors.top: caseIdSection.bottom
            anchors.topMargin: 20
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 80
            height: 180
            color: "#FFF3E0"
            radius: 10
            border.color: "#FFB74D"
            border.width: 2
            visible: !isProcessing && !isCompleted && !isFailed

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 10

                Text {
                    text: "ℹ️ What will happen:"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#E65100"
                }

                Text {
                    text: "• Create directory structure: RAW and WORK"
                    font.pixelSize: 12
                    color: "#555555"
                }

                Text {
                    text: "• Copy input files to RAW directory"
                    font.pixelSize: 12
                    color: "#555555"
                }

                Text {
                    text: "• Classify files by extension (.txt, .log, .xml, .json, .db, others)"
                    font.pixelSize: 12
                    color: "#555555"
                }

                Text {
                    text: "• Convert SQLite databases (.db) to CSV format"
                    font.pixelSize: 12
                    color: "#555555"
                }

                Text {
                    text: "• Generate conversion_manifest.txt for audit trail"
                    font.pixelSize: 12
                    color: "#555555"
                }
            }
        }

        // ===== Action Buttons =====
        Row {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 20

            // Back Button
            Button {
                id: backButton
                text: "← Back"
                width: 120
                height: 50
                enabled: !isProcessing

                background: Rectangle {
                    color: backButton.enabled ?
                           (backButton.hovered ? "#757575" : "#9E9E9E") :
                           "#E0E0E0"
                    radius: 8
                    border.color: "#616161"
                    border.width: 2
                }

                contentItem: Text {
                    text: backButton.text
                    font.pixelSize: 14
                    font.bold: true
                    color: backButton.enabled ? "white" : "#BDBDBD"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                onClicked: backClicked()
            }

            // Start/Cancel/Done Button
            Button {
                id: startButton
                text: isProcessing ? "Cancel" : (isCompleted ? "Done ✓" : isFailed ? "Close ✗" : "Start Extraction")
                width: 200
                height: 50
                enabled: (caseIdInput.text.trim() !== "" && !isProcessing && !isCompleted && !isFailed) || isProcessing || isCompleted || isFailed

                background: Rectangle {
                    color: {
                        if (!startButton.enabled) return "#BDBDBD"
                        if (isProcessing) return startButton.hovered ? "#D32F2F" : "#F44336"
                        if (isCompleted) return startButton.hovered ? "#388E3C" : "#4CAF50"
                        if (isFailed) return startButton.hovered ? "#B71C1C" : "#F44336"
                        return startButton.hovered ? "#1565C0" : "#1976D2"
                    }
                    radius: 8
                    border.color: {
                        if (!startButton.enabled) return "#9E9E9E"
                        if (isProcessing) return "#C62828"
                        if (isCompleted) return "#2E7D32"
                        if (isFailed) return "#B71C1C"
                        return "#0D47A1"
                    }
                    border.width: 2
                }

                contentItem: Text {
                    text: startButton.text
                    font.pixelSize: 15
                    font.bold: true
                    color: startButton.enabled ? "white" : "#757575"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                onClicked: {
                    if (isProcessing) {
                        backend.cancelExtraction()
                    } else if (isCompleted) {
                        nextClicked()
                    } else if (isFailed) {
                        isFailed = false
                        resultMessage = ""
                        progressBar.value = 0
                        progressText.text = "Ready to start..."
                        // Reset for re-run
                    } else {
                        startExtraction()
                    }
                }
            }
        }
    }

    // ===== Backend Connections =====
    Connections {
        target: backend

        function onExtractionProgress(progress, message) {
            progressBar.value = progress / 100.0
            progressText.text = message
        }

        function onExtractionFinished(success, message) {
            isProcessing = false
            resultMessage = message

            if (success) {
                isCompleted = true
                isFailed = false
                progressBar.value = 1.0
                progressText.text = "Extraction completed successfully!"
            } else {
                isCompleted = false
                isFailed = true
                progressText.text = "Extraction failed or cancelled."
            }
        }
    }

    // ===== Functions =====
    function startExtraction() {
        if (caseIdInput.text.trim() === "") {
            return
        }

        isProcessing = true
        isCompleted = false
        isFailed = false
        progressBar.value = 0
        progressText.text = "Initializing extraction..."
        resultMessage = ""

        backend.startExtraction(inputPath, caseIdInput.text.trim(), selectMode)
    }

    function setInputData(path, mode) {
        inputPath = path
        selectMode = mode
    }
}
