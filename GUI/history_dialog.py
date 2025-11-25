from aqt.qt import *
import os
from ..utility import LOG_FILE, format_timestamp, format_duration


class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Statistics History")
        self.setMinimumWidth(700)

        layout = QVBoxLayout(self)

        # Table to show history in columns
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        headers = ["Start", "End", "Duration", "Cards", "Again", "Hard", "Good", "Easy"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Notice label shown when there's no log data
        self.notice = QLabel("No log file found.")
        self.notice.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notice.setVisible(False)

        layout.addWidget(self.notice)
        layout.addWidget(self.table)

        # Buttons: Export, Clear, Close
        btn_layout = QHBoxLayout()

        btn_export = QPushButton("Export CSV")
        btn_export.clicked.connect(self.export_csv)
        btn_layout.addWidget(btn_export)

        btn_clear = QPushButton("Clear history")
        btn_clear.clicked.connect(self.clear_history)
        btn_layout.addWidget(btn_clear)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

        # load log into the table (or show notice)
        self.load_log()


    def load_log(self):
        """(Re)load the log file and populate `self.table`."""
        if not os.path.exists(LOG_FILE):
            self.table.setRowCount(0)
            self.notice.setText("No log file found.")
            self.notice.setVisible(True)
            self.table.setVisible(False)
            return

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            raw_lines = [l.strip() for l in f if l.strip()]

        if not raw_lines:
            self.table.setRowCount(0)
            self.notice.setText("No entries in the log file.")
            self.notice.setVisible(True)
            self.table.setVisible(False)
            return

        self.notice.setVisible(False)
        self.table.setVisible(True)

        self.table.setRowCount(len(raw_lines))
        for row, line in enumerate(raw_lines):
            parts = [p.strip() for p in line.split(",")]
            # Expect: start, end, duration, cards, again, hard, good, easy
            for col in range(8):
                value = parts[col] if col < len(parts) else ""
                item = QTableWidgetItem(value)
                try:
                    float(value.replace(':', '').replace('-', '').replace(' ', ''))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                except Exception:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, col, item)


    def export_csv(self):
        """Export the current log file to a user-selected CSV path."""
        if not os.path.exists(LOG_FILE):
            QMessageBox.information(self, "Export", "No log file to export.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export as CSV", "reviewstats_log.csv", "CSV Files (*.csv);;All Files (*)")
        if not filename:
            return

        try:
            with open(LOG_FILE, "r", encoding="utf-8") as src, open(filename, "w", encoding="utf-8") as dst:
                dst.write(src.read())
            QMessageBox.information(self, "Export", f"Export successful: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting: {e}")


    def clear_history(self):
        """Clear the log file after confirmation and refresh the view."""
        reply = QMessageBox.question(self, "Clear history", "Are you sure you want to delete the statistics history?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        try:
            # truncate or remove the file
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.truncate(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not delete log file: {e}")
            return

        # refresh table
        self.load_log()


__all__ = ["HistoryDialog"]
