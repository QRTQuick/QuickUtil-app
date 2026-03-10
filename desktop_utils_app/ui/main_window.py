from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMenu,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QSystemTrayIcon,
)

from ui.pages.placeholder import PlaceholderPage
from ui.pages.dashboard import DashboardPage
from ui.pages.system_monitor import SystemMonitorPage
from ui.pages.calendar_page import CalendarPage
from ui.pages.alarms_page import AlarmsPage
from ui.pages.notifications_page import NotificationsPage
from ui.pages.wallpaper_editor_page import WallpaperEditorPage
from core.icons import svg_icon
from services.app_context import AppContext


class NavButton(QToolButton):
    def __init__(
        self,
        *,
        title: str,
        tooltip: str,
        icon_name: str,
        kind: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)
        self.setToolTip(tooltip)

        if kind == "sidebar":
            self.setObjectName("SidebarNavButton")
            self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            self.setIconSize(QSize(18, 18))
        else:
            self.setObjectName("BottomNavButton")
            self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            self.setIconSize(QSize(20, 20))

        self.setText(title)
        self.setIcon(svg_icon(icon_name, size=20))
        self.setAutoRaise(True)


@dataclass(frozen=True)
class PageDef:
    key: str
    title: str
    tooltip: str
    icon: str
    shortcut: QKeySequence | None = None


class MainWindow(QMainWindow):
    def __init__(self, ctx: AppContext) -> None:
        super().__init__()
        self._ctx = ctx
        self.setWindowTitle("QuickUtil")
        self.setMinimumSize(1100, 720)

        self._stack = QStackedWidget()
        self._pages: dict[str, QWidget] = {}
        self._nav_buttons: dict[str, NavButton] = {}
        self._bottom_buttons: dict[str, NavButton] = {}
        self._actions_by_key: dict[str, QAction] = {}

        self._is_compact_nav = False
        self._sidebar_forced_visible = False

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._sidebar = self._build_sidebar()
        content_layout.addWidget(self._sidebar)
        content_layout.addWidget(self._stack, 1)

        self._bottom_nav = self._build_bottom_nav()

        root_layout.addWidget(content, 1)
        root_layout.addWidget(self._bottom_nav, 0)
        self.setCentralWidget(root)

        self._build_menus()
        self._build_toolbar()
        self._build_status_bar()
        self._build_tray()

        # Default page
        self.switch_to("dashboard")
        self._apply_responsive_nav()

        self._ctx.notifications.notification_added.connect(self._on_notification_added)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("QuickUtil")
        title.setObjectName("AppTitle")
        subtitle = QLabel("Utilities • Monitor • Productivity")
        subtitle.setObjectName("AppSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(6)

        page_defs = self._page_defs()
        group = QButtonGroup(self)
        group.setExclusive(True)

        for pd in page_defs:
            tooltip = pd.tooltip
            if pd.shortcut:
                tooltip = f"{tooltip}\nShortcut: {pd.shortcut.toString(QKeySequence.SequenceFormat.NativeText)}"

            btn = NavButton(
                title=pd.title,
                tooltip=tooltip,
                icon_name=pd.icon,
                kind="sidebar",
            )
            btn.clicked.connect(lambda _checked=False, key=pd.key: self.switch_to(key))
            group.addButton(btn)
            self._nav_buttons[pd.key] = btn
            layout.addWidget(btn)

            act = QAction(pd.title, self)
            act.setShortcut(pd.shortcut or QKeySequence())
            act.triggered.connect(lambda _checked=False, key=pd.key: self.switch_to(key))
            act.setIcon(svg_icon(pd.icon, size=18))
            self._actions_by_key[pd.key] = act
            if pd.shortcut:
                self.addAction(act)

        layout.addStretch(1)

        about = QPushButton("About")
        about.setToolTip("About QuickUtil")
        about.clicked.connect(self._show_about)
        layout.addWidget(about)
        return sidebar

    def _build_bottom_nav(self) -> QFrame:
        nav = QFrame()
        nav.setObjectName("BottomNav")

        layout = QHBoxLayout(nav)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        page_defs = self._page_defs()
        group = QButtonGroup(self)
        group.setExclusive(True)

        for pd in page_defs:
            tooltip = pd.tooltip
            if pd.shortcut:
                tooltip = f"{tooltip}\nShortcut: {pd.shortcut.toString(QKeySequence.SequenceFormat.NativeText)}"

            btn = NavButton(
                title=pd.title.split(" & ")[0],
                tooltip=tooltip,
                icon_name=pd.icon,
                kind="bottom",
            )
            btn.clicked.connect(lambda _checked=False, key=pd.key: self.switch_to(key))
            group.addButton(btn)
            self._bottom_buttons[pd.key] = btn
            layout.addWidget(btn, 1)

        return nav

    def _page_defs(self) -> list[PageDef]:
        return [
            PageDef(
                "dashboard",
                "Dashboard",
                "Overview of system + productivity",
                "dashboard",
                QKeySequence("Ctrl+1"),
            ),
            PageDef(
                "system",
                "System Monitor",
                "CPU/GPU/RAM/Disk + uptime",
                "system",
                QKeySequence("Ctrl+2"),
            ),
            PageDef(
                "calendar",
                "Calendar",
                "Monthly view + events",
                "calendar",
                QKeySequence("Ctrl+3"),
            ),
            PageDef(
                "alarms",
                "Alarms & Reminders",
                "Schedule alarms and reminders",
                "alarm",
                QKeySequence("Ctrl+4"),
            ),
            PageDef(
                "wallpaper",
                "Wallpaper Editor",
                "Import, edit, and apply wallpapers",
                "wallpaper",
                QKeySequence("Ctrl+5"),
            ),
            PageDef(
                "notifications",
                "Notification Center",
                "In-app alerts and warnings",
                "notifications",
                QKeySequence("Ctrl+6"),
            ),
        ]

    def _build_menus(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        nav_menu = self.menuBar().addMenu("&Navigate")
        for pd in self._page_defs():
            nav_menu.addAction(self._actions_by_key[pd.key])

        tools_menu = self.menuBar().addMenu("&Tools")
        refresh_action = QAction("Refresh", self)
        refresh_action.setToolTip("Refresh current module")
        refresh_action.setShortcut(QKeySequence("Ctrl+R"))
        refresh_action.setIcon(svg_icon("refresh", size=18))
        refresh_action.triggered.connect(self._refresh_current)
        tools_menu.addAction(refresh_action)

        view_menu = self.menuBar().addMenu("&View")
        toggle_sidebar_action = QAction("Toggle Sidebar", self)
        toggle_sidebar_action.setShortcut(QKeySequence("Ctrl+B"))
        toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)

        help_menu = self.menuBar().addMenu("&Help")
        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.setShortcut(QKeySequence("Ctrl+K"))
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _build_toolbar(self) -> None:
        tb = QToolBar("Quick Actions")
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        nav_action = QAction(svg_icon("menu", size=18), "Navigation", self)
        nav_action.setToolTip("Toggle sidebar navigation (Ctrl+B)")
        nav_action.setShortcut(QKeySequence("Ctrl+B"))
        nav_action.triggered.connect(self._toggle_sidebar)
        tb.addAction(nav_action)

        refresh_action = QAction(svg_icon("refresh", size=18), "Refresh", self)
        refresh_action.setToolTip("Refresh current module (Ctrl+R)")
        refresh_action.setShortcut(QKeySequence("Ctrl+R"))
        refresh_action.triggered.connect(self._refresh_current)
        tb.addAction(refresh_action)

        tb.addSeparator()

        calendar_action = QAction(svg_icon("plus", size=18), "New Event", self)
        calendar_action.setToolTip("Create a calendar event (Ctrl+N)")
        calendar_action.setShortcut(QKeySequence.StandardKey.New)
        calendar_action.triggered.connect(lambda _checked=False: self.switch_to("calendar"))
        tb.addAction(calendar_action)

        alarm_action = QAction("New Alarm", self)
        alarm_action.setToolTip("Create an alarm/reminder (Ctrl+Shift+A)")
        alarm_action.setShortcut(QKeySequence("Ctrl+Shift+A"))
        alarm_action.triggered.connect(lambda _checked=False: self.switch_to("alarms"))
        tb.addAction(alarm_action)

        notify_action = QAction("Notifications", self)
        notify_action.setToolTip("Open notification center (Ctrl+6)")
        notify_action.setShortcut(QKeySequence("Ctrl+6"))
        notify_action.triggered.connect(lambda _checked=False: self.switch_to("notifications"))
        tb.addAction(notify_action)

    def _build_status_bar(self) -> None:
        sb = QStatusBar()
        sb.setSizeGripEnabled(False)
        self.setStatusBar(sb)
        sb.showMessage("Ready")

    def _build_tray(self) -> None:
        self._tray = QSystemTrayIcon(svg_icon("dashboard", size=64), self)
        self._tray.setToolTip("QuickUtil")

        menu = QMenu(self)
        show_action = QAction("Show", self)
        show_action.triggered.connect(lambda _checked=False: self.showNormal())
        menu.addAction(show_action)

        menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(lambda _checked=False: self.close())
        menu.addAction(quit_action)

        self._tray_menu = menu
        self._tray.setContextMenu(self._tray_menu)
        self._tray.show()
        self._ctx.notifications.set_tray_icon(self._tray)

    @Slot(object)
    def _on_notification_added(self, n: object) -> None:
        try:
            title = getattr(n, "title", "Notification")
            msg = getattr(n, "message", "")
            self.statusBar().showMessage(f"{title}: {msg}", 4500)
        except Exception:
            self.statusBar().showMessage("Notification received", 2500)

    @Slot()
    def _toggle_sidebar(self) -> None:
        root = self.centralWidget()
        if not root:
            return
        layout = root.layout()
        if not layout or layout.count() < 1:
            return

        if self._is_compact_nav:
            self._sidebar_forced_visible = not self._sidebar_forced_visible
            self._apply_responsive_nav()
            return

        self._sidebar.setVisible(not self._sidebar.isVisible())

    @Slot()
    def _refresh_current(self) -> None:
        w = self._stack.currentWidget()
        if hasattr(w, "refresh"):
            try:
                w.refresh()  # type: ignore[call-arg]
                self.statusBar().showMessage("Refreshed", 1500)
            except Exception as e:  # pragma: no cover
                self.statusBar().showMessage(f"Refresh failed: {e}", 3000)
        else:
            self.statusBar().showMessage("Nothing to refresh here yet", 1500)

    @Slot()
    def _show_about(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("About QuickUtil")
        dlg.setModal(True)
        dlg.setMinimumWidth(520)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("QuickUtil")
        title.setStyleSheet("font-size: 18pt; font-weight: 900;")
        subtitle = QLabel("Cross-platform utility suite • Monitor • Productivity")
        subtitle.setStyleSheet("color: #94a3b8;")

        tips = QListWidget()
        tips.addItem("Use the sidebar or bottom tabs to switch modules.")
        tips.addItem("Keyboard shortcuts: Ctrl+1..6, Ctrl+R refresh, Ctrl+K shortcuts.")
        tips.addItem("This project is designed to be modular and extendable.")

        close_btn = QPushButton("Close")
        close_btn.setObjectName("Primary")
        close_btn.clicked.connect(dlg.accept)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(tips)
        layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignRight)
        dlg.exec()

    @Slot()
    def _show_shortcuts(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts")
        dlg.setModal(True)
        dlg.setMinimumWidth(620)

        grid = QGridLayout(dlg)
        grid.setContentsMargins(18, 18, 18, 18)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        header1 = QLabel("Action")
        header1.setStyleSheet("color: #94a3b8; font-weight: 700;")
        header2 = QLabel("Shortcut")
        header2.setStyleSheet("color: #94a3b8; font-weight: 700;")
        grid.addWidget(header1, 0, 0)
        grid.addWidget(header2, 0, 1)

        row = 1
        for pd in self._page_defs():
            grid.addWidget(QLabel(pd.title), row, 0)
            grid.addWidget(
                QLabel(pd.shortcut.toString(QKeySequence.SequenceFormat.NativeText) if pd.shortcut else "—"),
                row,
                1,
            )
            row += 1

        grid.addWidget(QLabel("Refresh current module"), row, 0)
        grid.addWidget(QLabel("Ctrl+R"), row, 1)
        row += 1
        grid.addWidget(QLabel("Toggle sidebar"), row, 0)
        grid.addWidget(QLabel("Ctrl+B"), row, 1)
        row += 1

        close_btn = QPushButton("Close")
        close_btn.setObjectName("Primary")
        close_btn.clicked.connect(dlg.accept)
        grid.addWidget(close_btn, row, 1, 1, 1, Qt.AlignmentFlag.AlignRight)

        dlg.exec()

    def _ensure_page(self, key: str) -> QWidget:
        if key in self._pages:
            return self._pages[key]

        if key == "dashboard":
            page = DashboardPage(self._ctx)
        elif key == "system":
            page = SystemMonitorPage()
        elif key == "calendar":
            page = CalendarPage(self._ctx)
        elif key == "alarms":
            page = AlarmsPage(self._ctx)
        elif key == "wallpaper":
            page = WallpaperEditorPage(self._ctx)
        elif key == "notifications":
            page = NotificationsPage(self._ctx)
        else:
            page = PlaceholderPage("Unknown", f"Missing module: {key}")

        self._pages[key] = page
        self._stack.addWidget(page)
        return page

    def switch_to(self, key: str) -> None:
        page = self._ensure_page(key)
        self._stack.setCurrentWidget(page)

        for k, btn in self._nav_buttons.items():
            btn.setChecked(k == key)
        for k, btn in self._bottom_buttons.items():
            btn.setChecked(k == key)

        title_map = {
            "dashboard": "Dashboard",
            "system": "System Monitor",
            "calendar": "Calendar",
            "alarms": "Alarms & Reminders",
            "wallpaper": "Wallpaper Editor",
            "notifications": "Notification Center",
        }
        self.statusBar().showMessage(f"{title_map.get(key, key)}", 1200)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._apply_responsive_nav()

    def _apply_responsive_nav(self) -> None:
        self._is_compact_nav = self.width() < 980
        self._bottom_nav.setVisible(self._is_compact_nav)

        if not self._is_compact_nav:
            self._sidebar.setVisible(True)
            self._sidebar_forced_visible = False
            return

        self._sidebar.setVisible(self._sidebar_forced_visible)
