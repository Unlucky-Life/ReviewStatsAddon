from aqt.qt import *
from .history_dialog import HistoryDialog
from ..utility import add_xp, xp_to_level


class StatsDialog(QDialog):
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review Summary")
        self.setMinimumWidth(450)

        # --- Fade-In Animation ---
        self.setWindowOpacity(0)
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(400)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()
        self._anim = anim

        # --- Rounded shadow ---
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(30)
        effect.setOffset(0, 0)
        effect.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(effect)

        layout = QVBoxLayout(self)

        # --- XP SYSTEM ---
        earned_xp = stats["total_reviews"]
        new_total = add_xp(earned_xp)

        xp_label = QLabel(
            f"<b>XP earned:</b> {earned_xp}<br>"
            f"<b>Total XP:</b> {new_total}"
        )
        xp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(xp_label)

        # --- Leveling display ---
        level, progress, needed = xp_to_level(new_total)
        level_label = QLabel(f"Level: {level} — Progress: {progress}/{needed}")
        level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(level_label)

        pb = QProgressBar()
        try:
            percent = int(progress / needed * 100) if needed > 0 else 100
        except Exception:
            percent = 0
        pb.setMaximum(100)
        pb.setValue(percent)
        pb.setTextVisible(True)
        layout.addWidget(pb)

        # --- PIE CHART ---
        chart = self.create_chart(stats)
        layout.addWidget(chart)

        # --- Buttons ---
        btn_hist = QPushButton("Open Statistics History")
        btn_hist.clicked.connect(self.show_history)
        layout.addWidget(btn_hist, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

    def create_chart(self, stats):
        """Create a pie chart widget using native PyQt drawing (QPainter).

        This builds a small custom QWidget that paints a pie chart and a
        legend showing counts and percentages for the review outcomes.
        """
        class PieCanvas(QWidget):
            def __init__(self, values, colors, parent=None):
                super().__init__(parent)
                self.values = values
                self.colors = colors
                self.setMinimumSize(160, 160)
                self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

            def paintEvent(self, event):
                qp = QPainter(self)
                rect = self.rect()
                size = min(rect.width(), rect.height())
                margin = 6
                pie_rect = QRectF((rect.width()-size)/2 + margin, (rect.height()-size)/2 + margin, size - margin*2, size - margin*2)

                total = sum(self.values)
                start_angle = -90.0

                if total == 0:
                    qp.setPen(QColor('#666'))
                    qp.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), 'No data')
                    return

                for v, col in zip(self.values, self.colors):
                    span = 360.0 * (v / total) if total else 0
                    qp.setBrush(QColor(col))
                    qp.setPen(QColor(col))
                    qp.drawPie(pie_rect, int(start_angle * 16), int(span * 16))
                    start_angle += span

                qp.setPen(QColor('#333'))
                qp.drawText(pie_rect, int(Qt.AlignmentFlag.AlignCenter), str(total) + '\ncards')

        values = [stats.get('again', 0), stats.get('hard', 0), stats.get('good', 0), stats.get('easy', 0)]
        colors = ['#e74c3c', '#f39c12', '#2ecc71', '#3498db']

        container = QWidget()
        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)

        canvas = PieCanvas(values, colors)
        h.addWidget(canvas)

        legend_w = QWidget()
        lv = QVBoxLayout(legend_w)
        lv.setContentsMargins(8, 0, 0, 0)
        labels = ['Again', 'Hard', 'Good', 'Easy']
        total = sum(values)
        for lbl_text, v, col in zip(labels, values, colors):
            row = QWidget()
            row_h = QHBoxLayout(row)
            row_h.setContentsMargins(0, 0, 0, 0)
            sw = QLabel()
            sw.setFixedSize(12, 12)
            sw.setStyleSheet(f'background:{col}; border-radius:2px;')
            txt = QLabel(f"{lbl_text}: {v} ({0 if total==0 else round(v/total*100)}%)")
            row_h.addWidget(sw)
            row_h.addWidget(txt)
            row_h.addStretch()
            lv.addWidget(row)

        lv.addStretch()
        h.addWidget(legend_w)

        return container

    # --- History View ---
    def show_history(self):
        """Open the history dialog showing past session logs."""
        dlg = HistoryDialog(parent=self)
        dlg.exec()


__all__ = ["StatsDialog"]
