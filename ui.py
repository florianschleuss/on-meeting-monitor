import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QStyle, QTextEdit, QWidget, QVBoxLayout, QPushButton, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QCloseEvent
from win10toast import ToastNotifier

from omm import TeamsState, TeamsStateWatchdog

'''
For conversion to .exe: pyinstaller --onefile --windowed --name "OnMeeting Monitor" ui.py
'''


class ConsoleRedirect:
    def __init__(self, widget, stream):
        self.widget = widget
        self.stream = stream

    def write(self, text):
        self.widget.moveCursor(self.widget.textCursor().End)
        self.widget.insertPlainText(text)

    def flush(self):
        pass


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.teams_watchdog = TeamsStateWatchdog()

        self.init_ui()
        print('AUTOSTART')
        self.start_action()

    def closeEvent(self, event: QCloseEvent):
        """
        Override the close event to minimize the window instead of closing it.

        Parameters:
        - event (QCloseEvent): The close event.
        """
        event.ignore()
        self.minimize_action()

    def on_state_update(self):
        toaster = ToastNotifier()
        if self.teams_watchdog.old_state is not TeamsState.START:
            toaster.show_toast(
                title=f"Teams Status: {self.teams_watchdog.state.value}",
                msg=f"Changed from {self.teams_watchdog.old_state.value} -> {self.teams_watchdog.state.value}",
                duration=1,  # Notification will disappear after 10 seconds
                icon_path='',
                threaded=True
            )
        self.tray_icon.setToolTip(f"Teams: {self.teams_watchdog.state.value}")
        self.round_text.setText(self.teams_watchdog.state.value)
        if self.teams_watchdog.state in [TeamsState.BUSY, TeamsState.DONOTDISTURB, TeamsState.ONTHEPHONE, TeamsState.PRESENTING]:
            self.round_text.setStyleSheet(
                "background-color: red; border-radius: 50px; color: white; font-size: 12px;")
        elif self.teams_watchdog.state in [TeamsState.AWAY, TeamsState.BERIGHTBACK]:
            self.round_text.setStyleSheet(
                "background-color: yellow; border-radius: 50px; color: white; font-size: 12px;")
        elif self.teams_watchdog.state in [TeamsState.OFFLINE, TeamsState.NEWACTIVITY]:
            self.round_text.setStyleSheet(
                "background-color: grey; border-radius: 50px; color: white; font-size: 12px;")
        else:
            self.round_text.setStyleSheet(
                "background-color: green; border-radius: 50px; color: white; font-size: 12px;")

    def init_ui(self):
        self.setWindowTitle('OnMeeting Monitor Watchdog')

        self.teams_watchdog.update_hook = self.on_state_update

        # Create round text field
        self.round_text = QLabel(TeamsState.OFFLINE.value, self)
        self.round_text.setFixedWidth(100)
        self.round_text.setFixedHeight(100)
        self.round_text.setStyleSheet(
            "background-color: grey; border-radius: 50px; color: white; font-size: 12px;")
        self.round_text.setAlignment(Qt.AlignCenter)
        self.round_text.setWordWrap(True)

        # Create buttons
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_action)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_action)

        self.exit_button = QPushButton('Exit', self)
        self.exit_button.clicked.connect(self.exit_action)

        # Create console widget
        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(200)
        # Redirect sys.stdout to the console
        sys.stdout = ConsoleRedirect(self.console, sys.stdout)

      # Create layout
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.exit_button)

        upper_row = QHBoxLayout()
        upper_row.addLayout(button_layout)
        upper_row.addWidget(self.round_text)

        main_layout = QVBoxLayout()
        main_layout.addLayout(upper_row)
        main_layout.addWidget(self.console)

        self.setLayout(main_layout)

        # Set up system tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            self.style().standardIcon(QStyle.SP_ComputerIcon))
        tray_menu = QMenu(self)
        restore_action = tray_menu.addAction('Open')
        exit_action = tray_menu.addAction('Exit')

        restore_action.triggered.connect(self.restore_action)
        exit_action.triggered.connect(self.exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.hide()
        self.tray_icon.show()

    def start_action(self):
        self.teams_watchdog.start(wait_time=30)

    def stop_action(self):
        self.teams_watchdog.stop()

    def update_action(self):
        self.teams_watchdog.refresh()
        # if self.teams_watchdog.state_has_changed():
        #     self.teams_watchdog.update()

    def minimize_action(self):
        # Minimize to system tray
        self.hide()
        self.tray_icon.show()

    def restore_action(self):
        # Restore from system tray
        self.show()
        self.tray_icon.hide()

    def exit_action(self):
        # Exit application from system tray
        self.tray_icon.hide()
        sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(app.style().standardIcon(QStyle.SP_ComputerIcon))
    ex = App()
    sys.exit(app.exec_())
