import QtQuick 6.5
import QtQuick.Controls

Window {
    id: root
    width: Constants.width
    height: Constants.height
    visible: true
    title: "Malicious Behavior Detection - CACA Mobile"

    // Store selected data
    property string selectedInputPath: ""
    property string selectedMode: ""

    Loader {
        id: screenLoader
        anchors.fill: parent
        sourceComponent: screen02  // Bắt đầu từ Screen02
    }

    // Màn hình loading (màn hình đầu tiên)
    Component {
        id: screen02
        Screen02 {
            onLoadingCompleted: {
                screenLoader.sourceComponent = screen01
            }
        }
    }

    // Màn hình Start (màn hình thứ hai)
    Component {
        id: screen01
        Screen01 {
            onStartClicked: {
                screenLoader.sourceComponent = screen03
            }
        }
    }

    // Màn hình chọn input (Screen03)
    Component {
        id: screen03
        Screen03 {
            onNextClicked: {
                // Lưu dữ liệu được chọn
                root.selectedInputPath = selectedInput
                root.selectedMode = selectMode

                // Chuyển sang màn hình Transformation
                screenLoader.sourceComponent = screen04
            }
        }
    }

    // Màn hình Transformation (Screen04)
    Component {
        id: screen04
        Screen04 {
            Component.onCompleted: {
                // Truyền dữ liệu vào Screen04
                setInputData(root.selectedInputPath, root.selectedMode)
            }

            onNextClicked: {
                // Chuyển sang màn hình Analysis (Screen05) nếu có
                console.log("Moving to Analysis screen")
                // screenLoader.sourceComponent = screen05
            }

            onBackClicked: {
                // Quay lại màn hình chọn input
                screenLoader.sourceComponent = screen03
            }
        }
    }
}
