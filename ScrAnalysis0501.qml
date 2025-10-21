import QtQuick 6.5
import QtQuick.Controls

Rectangle {
    id: screen05
    anchors.fill: parent
    color: "#b3cdde"

    signal nextClicked
    signal backClicked

    property string workPath: ""
    property bool isAnalyzing: false
    property bool isCompleted: false
    property bool isFailed: false
    property string resultMessage: ""

    // Main scrollable content
    Flickable {
        anchors.fill: parent
        anchors.margins: 50
        contentHeight: mainColumn.height
        clip: true

        Column {
            id: mainColumn
            width: parent.width
            spacing: 25

            // ===== Header =====
            Column {
                id: headerSection
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 15

                Text {
                    text: "Stage 2: Analysis & Detection"
                    font.pixelSize: 22
                    font.bold: true
                    color: "#1976D2"
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    text: "Analyze extracted data and detect malicious behavior patterns"
                    font.pixelSize: 13
                    color: "#555555"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }

            // ===== Analysis Configuration =====
            Rectangle {
                id: configSection
                anchors.horizontalCenter: parent.horizontalCenter
                width: Math.min(900, parent.width)
                height: 280
                color: "#ffffff"
                radius: 10
                border.color: "#e0e0e0"
                border.width: 2

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 15

                    Text {
                        text: "⚙️ Analysis Configuration"
                        font.pixelSize: 16
                        font.bold: true
                        color: "#333333"
                    }

                    Rectangle {
                        width: parent.width - 40
                        height: 1
                        color: "#e0e0e0"
                    }

                    // Analysis Methods
                    Column {
                        spacing: 10
                        width: parent.width - 40

                        Text {
                            text: "Select Analysis Methods:"
                            font.pixelSize: 13
                            font.bold: true
                            color: "#555555"
                        }

                        CheckBox {
                            id: timelineCheck
                            text: "Timeline Consistency Analysis"
                            checked: true
                            enabled: !isAnalyzing && !isCompleted
                            font.pixelSize: 12
                        }

                        CheckBox {
                            id: behaviorCheck
                            text: "Behavior Pattern Recognition"
                            checked: true
                            enabled: !isAnalyzing && !isCompleted
                            font.pixelSize: 12
                        }

                        CheckBox {
                            id: anomalyCheck
                            text: "Anomaly Detection"
                            checked: true
                            enabled: !isAnalyzing && !isCompleted
                            font.pixelSize: 12
                        }

                        CheckBox {
                            id: correlationCheck
                            text: "Cross-Artifact Correlation"
                            checked: true
                            enabled: !isAnalyzing && !isCompleted
                            font.pixelSize: 12
                        }
                    }

                    Rectangle {
                        width: parent.width - 40
                        height: 1
                        color: "#e0e0e0"
                    }

                    // Sensitivity Level
                    Row {
                        spacing: 15
                        width: parent.width - 40

                        Text {
                            text: "Detection Sensitivity:"
                            font.pixelSize: 13
                            font.bold: true
                            color: "#555555"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        ComboBox {
                            id: sensitivityCombo
                            width: 200
                            enabled: !isAnalyzing && !isCompleted
                            model: ["Low (Conservative)", "Medium (Balanced)", "High (Aggressive)"]
                            currentIndex: 1

                            background: Rectangle {
                                color: sensitivityCombo.enabled ? "#ffffff" : "#f5f5f5"
                                border.color: sensitivityCombo.activeFocus ? "#1976D2" : "#cccccc"
                                border.width: 1
                                radius: 5
                            }
                        }
                    }
                }
            }

            // ===== Progress Section =====
            Rectangle {
                id: progressSection
                anchors.horizontalCenter: parent.horizontalCenter
                width: Math.min(900, parent.width)
                height: 220
                color: "#ffffff"
                radius: 10
                border.color: "#e0e0e0"
                border.width: 2
                visible: isAnalyzing || isCompleted || isFailed

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 15

                    Text {
                        text: isCompleted ? "✅ Analysis Completed"
                            : isFailed ? "❌ Analysis Failed"
                            : "🔍 Analyzing..."
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
                        text: "Ready to analyze..."
                        font.pixelSize: 13
                        color: "#555555"
                        width: parent.width - 40
                        wrapMode: Text.WordWrap
                    }

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

            // ===== Analysis Info =====
            Rectangle {
                id: infoSection
                anchors.horizontalCenter: parent.horizontalCenter
                width: Math.min(900, parent.width)
                height: 220
                color: "#E8F5E9"
                radius: 10
                border.color: "#66BB6A"
                border.width: 2
                visible: !isAnalyzing && !isCompleted && !isFailed

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 10

                    Text {
                        text: "ℹ️ Analysis Process:"
                        font.pixelSize: 14
                        font.bold: true
                        color: "#2E7D32"
                    }

                    Text {
                        text: "• Parse and load all converted data from WORK directory"
                        font.pixelSize: 12
                        color: "#555555"
                    }

                    Text {
                        text: "• Build temporal timeline from timestamps in artifacts"
                        font.pixelSize: 12
                        color: "#555555"
                    }

                    Text {
                        text: "• Identify behavioral patterns and anomalies"
                        font.pixelSize: 12
                        color: "#555555"
                    }

                    Text {
                        text: "• Cross-reference data consistency across artifacts"
                        font.pixelSize: 12
                        color: "#555555"
                    }

                    Text {
                        text: "• Generate detection report with confidence scores"
                        font.pixelSize: 12
                        color: "#555555"
                    }

                    Text {
                        text: "• Create visualization and summary statistics"
                        font.pixelSize: 12
                        color: "#555555"
                    }
                }
            }

            // ===== Results Preview (visible after completion) =====
            Rectangle {
                id: resultsSection
                anchors.horizontalCenter: parent.horizontalCenter
                width: Math.min(900, parent.width)
                height: 280
                color: "#ffffff"
                radius: 10
                border.color: isCompleted ? "#4CAF50" : "#F44336"
                border.width: 2
                visible: isCompleted

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 15

                    Text {
                        text: "📊 Detection Results"
                        font.pixelSize: 16
                        font.bold: true
                        color: "#333333"
                    }

                    Rectangle {
                        width: parent.width - 40
                        height: 1
                        color: "#e0e0e0"
                    }

                    // Mock results - will be replaced with real data
                    Row {
                        spacing: 40
                        anchors.horizontalCenter: parent.horizontalCenter

                        Column {
                            spacing: 8
                            Rectangle {
                                width: 120
                                height: 120
                                radius: 60
                                color: "#FFEBEE"
                                border.color: "#F44336"
                                border.width: 3

                                Text {
                                    anchors.centerIn: parent
                                    text: "3"
                                    font.pixelSize: 48
                                    font.bold: true
                                    color: "#F44336"
                                }
                            }
                            Text {
                                text: "Threats Detected"
                                font.pixelSize: 12
                                color: "#555555"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }

                        Column {
                            spacing: 8
                            Rectangle {
                                width: 120
                                height: 120
                                radius: 60
                                color: "#FFF3E0"
                                border.color: "#FF9800"
                                border.width: 3

                                Text {
                                    anchors.centerIn: parent
                                    text: "5"
                                    font.pixelSize: 48
                                    font.bold: true
                                    color: "#FF9800"
                                }
                            }
                            Text {
                                text: "Warnings"
                                font.pixelSize: 12
                                color: "#555555"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }

                        Column {
                            spacing: 8
                            Rectangle {
                                width: 120
                                height: 120
                                radius: 60
                                color: "#E8F5E9"
                                border.color: "#4CAF50"
                                border.width: 3

                                Text {
                                    anchors.centerIn: parent
                                    text: "87%"
                                    font.pixelSize: 36
                                    font.bold: true
                                    color: "#4CAF50"
                                }
                            }
                            Text {
                                text: "Confidence Score"
                                font.pixelSize: 12
                                color: "#555555"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }

                    Rectangle {
                        width: parent.width - 40
                        height: 1
                        color: "#e0e0e0"
                    }

                    Text {
                        text: "✓ Detailed report saved to: WORK/analysis_report.html"
                        font.pixelSize: 12
                        color: "#555555"
                        width: parent.width - 40
                        wrapMode: Text.WordWrap
                    }
                }
            }

            // ===== Action Buttons =====
            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 20

                Button {
                    id: backButton
                    text: "← Back"
                    width: 120
                    height: 50
                    enabled: !isAnalyzing

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

                Button {
                    id: analyzeButton
                    text: isAnalyzing ? "⏸ Pause" : (isCompleted ? "View Report →" : "🔍 Start Analysis")
                    width: 200
                    height: 50
                    enabled: !isAnalyzing && !isFailed || isCompleted

                    background: Rectangle {
                        color: {
                            if (!analyzeButton.enabled) return "#BDBDBD"
                            if (isCompleted) return analyzeButton.hovered ? "#388E3C" : "#4CAF50"
                            return analyzeButton.hovered ? "#1565C0" : "#1976D2"
                        }
                        radius: 8
                        border.color: {
                            if (!analyzeButton.enabled) return "#9E9E9E"
                            if (isCompleted) return "#2E7D32"
                            return "#0D47A1"
                        }
                        border.width: 2
                    }

                    contentItem: Text {
                        text: analyzeButton.text
                        font.pixelSize: 15
                        font.bold: true
                        color: analyzeButton.enabled ? "white" : "#757575"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: {
                        if (isCompleted) {
                            nextClicked()
                        } else {
                            startAnalysis()
                        }
                    }
                }

                Button {
                    id: exportButton
                    text: "📥 Export"
                    width: 120
                    height: 50
                    enabled: isCompleted
                    visible: isCompleted

                    background: Rectangle {
                        color: exportButton.enabled ?
                               (exportButton.hovered ? "#0288D1" : "#03A9F4") :
                               "#E0E0E0"
                        radius: 8
                        border.color: exportButton.enabled ? "#0277BD" : "#9E9E9E"
                        border.width: 2
                    }

                    contentItem: Text {
                        text: exportButton.text
                        font.pixelSize: 14
                        font.bold: true
                        color: exportButton.enabled ? "white" : "#BDBDBD"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: {
                        console.log("Export report clicked")
                    }
                }
            }
        }
    }

    // ===== Functions =====
    function startAnalysis() {
        isAnalyzing = true
        isCompleted = false
        isFailed = false
        progressBar.value = 0
        progressText.text = "Initializing analysis engine..."
        resultMessage = ""

        // Simulate analysis process
        analysisTimer.start()
    }

    function setWorkPath(path) {
        workPath = path
    }

    // ===== Simulation Timer (replace with actual backend call) =====
    Timer {
        id: analysisTimer
        interval: 100
        repeat: true
        running: false

        property int step: 0
        property var messages: [
            "Loading data from WORK directory...",
            "Parsing XML files...",
            "Analyzing JSON artifacts...",
            "Processing database extracts...",
            "Building timeline...",
            "Detecting behavioral patterns...",
            "Running anomaly detection...",
            "Cross-referencing artifacts...",
            "Calculating confidence scores...",
            "Generating report...",
            "Analysis completed!"
        ]

        onTriggered: {
            if (step < messages.length) {
                progressBar.value = step / messages.length
                progressText.text = messages[step]
                step++
            } else {
                stop()
                step = 0
                isAnalyzing = false
                isCompleted = true
                progressBar.value = 1.0
                resultMessage = "Analysis completed successfully!\n\nThreats: 3 detected\nWarnings: 5 found\nConfidence: 87%\n\nFull report: WORK/analysis_report.html"
            }
        }
    }
}
