import QtQuick 6.5
import QtQuick.Controls

Window {
    id: root
    width: 1920
    height: 1080
    visible: true
    title: "Mobile Malicious Behavior Detection"

    // Store selected data
    property string selectedInputPath: ""
    property string selectedMode: ""

    // Background màu xám phủ toàn bộ
    Rectangle {
        anchors.fill: parent
        color: "#d9d9d9"
    }

    Loader {
        id: screenLoader
        anchors.fill: parent
        sourceComponent: scrLoading0101
    }

    // Màn hình loading (màn hình đầu tiên)
    Component {
        id: scrLoading0101
        ScrLoading0101 {
            onLoadingCompleted: {
                screenLoader.sourceComponent = scrStart0201
            }
        }
    }

    // Màn hình Start (màn hình thứ hai)
    Component {
        id: scrStart0201
        ScrStart0201 {
            onStartClicked: {
                screenLoader.sourceComponent = scrInput0301
            }
        }
    }

    // Màn hình chọn input
    Component {
        id: scrInput0301
        ScrInput0301 {
            onNextClicked: {
                // Lưu dữ liệu được chọn
                root.selectedInputPath = selectedInput
                root.selectedMode = selectMode

                // Chuyển sang màn hình Conversion
                screenLoader.sourceComponent = scrConversion0401
            }
        }
    }

    // Màn hình Conversion
    Component {
        id: scrConversion0401
        ScrConversion0401 {
            Component.onCompleted: {
                // Truyền dữ liệu vào màn hình conversion
                setInputData(root.selectedInputPath, root.selectedMode)
            }

            onNextClicked: {
                // Chuyển sang màn hình Analysis nếu có
                console.log("Moving to Analysis screen")
                screenLoader.sourceComponent = scrAnalysis0501
            }

            onBackClicked: {
                // Quay lại màn hình chọn input
                screenLoader.sourceComponent = scrInput0301
            }
        }
    }

    // Màn hình Analysis
    Component {
        id: scrAnalysis0501
        ScrAnalysis0501 {
            Component.onCompleted: {
                setWorkPath(root.selectedInputPath + "/" + "CASE_ID/WORK")
            }

            onNextClicked: {
                console.log("Moving to Report screen")
                // screenLoader.sourceComponent = scrReport0601
            }

            onBackClicked: {
                screenLoader.sourceComponent = scrConversion0401
            }
        }
    }
}

