import QtQuick 6.5
import QtQuick.Controls

Window {
    id: root
    width: Constants.width
    height: Constants.height
    visible: true
    title: "UntitledProject1"

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


    // Màn hình cuối cùng (Screen03)
    Component {
        id: screen03
        Screen03 {
            onNextClicked: {
                screenLoader.sourceComponent = screen04
            }
        }
    }

    // Màn hình Transformation (Screen04)
    Component {
        id: screen04
        Screen04 {
            onNextClicked: {
                // Chuyển sang màn hình Analysis (Screen05) nếu có
                console.log("Moving to Analysis screen")
            }
        }
    }
}
