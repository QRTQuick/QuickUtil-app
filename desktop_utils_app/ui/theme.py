from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class Theme:
    bg: str = "#0b0b0d"  # near-black
    surface: str = "#14141a"
    surface_2: str = "#1c1c24"
    surface_3: str = "#242433"
    border: str = "#2a2a35"
    text: str = "#f8fafc"
    text_muted: str = "#94a3b8"
    accent: str = "#e11d48"  # red
    accent_hover: str = "#fb7185"
    focus: str = "#ef4444"
    info: str = "#38bdf8"  # sky (secondary accent)
    warning: str = "#f59e0b"
    success: str = "#22c55e"


def _qss(t: Theme) -> str:
    # Minimal, modern dark UI tuned for black/red with soft slate borders.
    return f"""
    * {{
        color: {t.text};
        font-family: "Segoe UI", "Inter", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
        font-size: 10.5pt;
    }}

    QMainWindow {{
        background: {t.bg};
    }}

    QFrame#Sidebar {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 {t.surface},
                                    stop:1 {t.bg});
        border-right: 1px solid {t.border};
    }}

    QLabel#AppTitle {{
        font-size: 13pt;
        font-weight: 700;
        padding: 8px 12px;
        color: {t.text};
    }}

    QLabel#AppSubtitle {{
        font-size: 9.5pt;
        color: {t.text_muted};
        padding: 0 12px 8px 12px;
    }}

    QToolButton#SidebarNavButton {{
        background: transparent;
        border: 1px solid transparent;
        text-align: left;
        padding: 10px 12px;
        border-radius: 10px;
    }}
    QToolButton#SidebarNavButton:hover {{
        background: {t.surface_2};
        border: 1px solid {t.border};
    }}
    QToolButton#SidebarNavButton:checked {{
        background: rgba(225, 29, 72, 0.14);
        border: 1px solid rgba(225, 29, 72, 0.45);
    }}
    QToolButton#SidebarNavButton:checked:hover {{
        background: rgba(225, 29, 72, 0.18);
    }}
    QToolButton#SidebarNavButton QLabel#ShortcutChip {{
        color: {t.text_muted};
    }}

    QToolBar {{
        background: {t.bg};
        border: none;
        spacing: 8px;
        padding: 6px;
    }}
    QToolButton {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: 10px;
        padding: 6px 10px;
    }}
    QToolButton:hover {{
        border: 1px solid rgba(225, 29, 72, 0.55);
    }}
    QToolButton:pressed {{
        background: {t.surface_2};
    }}

    QFrame#BottomNav {{
        background: rgba(20, 20, 26, 0.96);
        border-top: 1px solid {t.border};
        padding: 8px 10px;
    }}
    QToolButton#BottomNavButton {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 12px;
        padding: 6px 10px;
        color: {t.text_muted};
    }}
    QToolButton#BottomNavButton:hover {{
        background: {t.surface_2};
        border: 1px solid {t.border};
        color: {t.text};
    }}
    QToolButton#BottomNavButton:checked {{
        background: rgba(225, 29, 72, 0.14);
        border: 1px solid rgba(225, 29, 72, 0.45);
        color: {t.text};
    }}

    QMenuBar {{
        background: {t.bg};
        border-bottom: 1px solid {t.border};
    }}
    QMenuBar::item {{
        background: transparent;
        padding: 6px 10px;
    }}
    QMenuBar::item:selected {{
        background: {t.surface};
        border-radius: 8px;
    }}
    QMenu {{
        background: {t.surface};
        border: 1px solid {t.border};
        padding: 6px;
    }}
    QMenu::item {{
        padding: 7px 10px;
        border-radius: 8px;
    }}
    QMenu::item:selected {{
        background: rgba(225, 29, 72, 0.14);
        border: 1px solid rgba(225, 29, 72, 0.35);
    }}

    QToolTip {{
        background: {t.surface_3};
        color: {t.text};
        border: 1px solid rgba(225, 29, 72, 0.35);
        padding: 8px 10px;
        border-radius: 10px;
    }}

    QStatusBar {{
        background: {t.bg};
        border-top: 1px solid {t.border};
        color: {t.text_muted};
    }}

    QLineEdit, QTextEdit, QPlainTextEdit {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: 10px;
        padding: 8px 10px;
        selection-background-color: rgba(225, 29, 72, 0.35);
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid rgba(239, 68, 68, 0.75);
    }}

    QDateTimeEdit, QSpinBox, QDoubleSpinBox {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: 10px;
        padding: 6px 10px;
        selection-background-color: rgba(225, 29, 72, 0.35);
    }}
    QDateTimeEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1px solid rgba(239, 68, 68, 0.75);
    }}

    QComboBox {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: 10px;
        padding: 6px 10px;
    }}
    QComboBox:focus {{
        border: 1px solid rgba(239, 68, 68, 0.75);
    }}
    QComboBox QAbstractItemView {{
        background: {t.surface};
        border: 1px solid {t.border};
        selection-background-color: rgba(225, 29, 72, 0.20);
        outline: 0;
        padding: 6px;
    }}

    QCalendarWidget QWidget {{
        background: {t.surface};
    }}
    QCalendarWidget QToolButton {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: 10px;
        padding: 6px 10px;
    }}
    QCalendarWidget QToolButton:hover {{
        border: 1px solid rgba(225, 29, 72, 0.55);
    }}

    QProgressBar {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: 9px;
        height: 14px;
        text-align: center;
        color: {t.text_muted};
    }}
    QProgressBar::chunk {{
        background: {t.accent};
        border-radius: 8px;
    }}

    QFrame#Card {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: 16px;
    }}
    QLabel#CardTitle {{
        color: {t.text_muted};
        font-size: 9.5pt;
        font-weight: 600;
    }}
    QLabel#CardValue {{
        font-size: 18pt;
        font-weight: 800;
    }}

    QGroupBox {{
        border: 1px solid {t.border};
        border-radius: 14px;
        margin-top: 14px;
        background: {t.surface};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: {t.text_muted};
        font-weight: 600;
    }}

    QPushButton {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: 10px;
        padding: 8px 12px;
    }}
    QPushButton:hover {{
        border: 1px solid rgba(225, 29, 72, 0.55);
    }}
    QPushButton:pressed {{
        background: {t.surface_2};
    }}
    QPushButton#Primary {{
        background: {t.accent};
        border: 1px solid rgba(225, 29, 72, 0.75);
        font-weight: 700;
    }}
    QPushButton#Primary:hover {{
        background: {t.accent_hover};
    }}
    QPushButton:disabled {{
        color: rgba(248, 250, 252, 0.35);
        border: 1px solid rgba(42, 42, 53, 0.6);
        background: rgba(20, 20, 26, 0.7);
    }}

    QListWidget, QTreeWidget, QTableWidget {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: 14px;
        padding: 6px;
        outline: 0;
        selection-background-color: rgba(225, 29, 72, 0.18);
    }}
    QListWidget::item, QTreeWidget::item, QTableWidget::item {{
        padding: 8px 10px;
        border-radius: 10px;
    }}
    QListWidget::item:selected, QTreeWidget::item:selected {{
        background: rgba(225, 29, 72, 0.18);
        border: 1px solid rgba(225, 29, 72, 0.35);
    }}
    QHeaderView::section {{
        background: {t.surface_2};
        color: {t.text_muted};
        border: none;
        padding: 8px 10px;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(148, 163, 184, 0.35);
        border-radius: 5px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: rgba(148, 163, 184, 0.55);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QTabWidget::pane {{
        border: 1px solid {t.border};
        border-radius: 14px;
        padding: 6px;
        background: {t.surface};
    }}
    QTabBar::tab {{
        background: {t.surface};
        border: 1px solid transparent;
        padding: 8px 12px;
        border-radius: 10px;
        margin-right: 6px;
        color: {t.text_muted};
    }}
    QTabBar::tab:selected {{
        background: rgba(225, 29, 72, 0.14);
        border: 1px solid rgba(225, 29, 72, 0.35);
        color: {t.text};
        font-weight: 700;
    }}
    """


def apply_dark_theme(app: QApplication, theme: Theme | None = None) -> None:
    t = theme or Theme()
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(t.bg))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(t.text))
    pal.setColor(QPalette.ColorRole.Base, QColor(t.surface))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(t.surface_2))
    pal.setColor(QPalette.ColorRole.Text, QColor(t.text))
    pal.setColor(QPalette.ColorRole.Button, QColor(t.surface))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(t.text))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(t.accent))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(t.text))
    app.setPalette(pal)
    app.setStyleSheet(_qss(t))
