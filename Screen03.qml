import QtQuick
import QtQuick.Controls

Rectangle {
    id: screen03
    signal nextClicked
    width: Constants.width
    height: Constants.height
    color: "#d9d9d9"

    Rectangle {
        id: mainPanel
        width: 869
        height: 578
        anchors.centerIn: parent
        color: "#b3cdde"
        radius: 10
        border.color: "#ffffff"
        border.width: 2

        // Label
        Text {
            id: inputLabel
            text: "[Select Input]"
            font.pixelSize: 16
            anchors.top: parent.top
            anchors.topMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter
        }

        // ComboBox để chọn loại file
        ComboBox {
            id: inputTypeCombo
            anchors.top: inputLabel.bottom
            anchors.topMargin: 10
            anchors.horizontalCenter: parent.horizontalCenter
            width: 300
            height: 40
            model: [
                "Android Image (.img)",
                "Log Files (.txt, .logcat)",
                "SQLite / CSV"
            ]
        }

        // Nút Next
        Button {
            id: nextButton
            text: "Next → Transformation"
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter
            width: 200
            height: 50
            onClicked: {
                        nextClicked()
            }
        }
    }
}
