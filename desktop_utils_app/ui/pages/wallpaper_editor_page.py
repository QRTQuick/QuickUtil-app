from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from PIL import Image, ImageEnhance, ImageFilter
from PIL.ImageQt import ImageQt

from core.app_dirs import ensure_dir, data_dir
from services.app_context import AppContext
from system.wallpaper import apply_wallpaper
from ui.widgets.crop_label import CropLabel


@dataclass
class _Filters:
    brightness: float = 1.0
    contrast: float = 1.0
    blur: float = 0.0


def _pil_to_pixmap(img: Image.Image) -> QPixmap:
    qimage = ImageQt(img.convert("RGBA"))
    return QPixmap.fromImage(qimage)


class WallpaperEditorPage(QWidget):
    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx

        self._original: Image.Image | None = None
        self._cropped_full: Image.Image | None = None
        self._cropped_preview_base: Image.Image | None = None
        self._crop_rect: tuple[int, int, int, int] | None = None  # in original coords
        self._filters = _Filters()

        self._preview_source_size: tuple[int, int] = (1, 1)
        self._preview_pixmap_source: QPixmap | None = None

        self._preview_debounce = QTimer(self)
        self._preview_debounce.setSingleShot(True)
        self._preview_debounce.setInterval(60)
        self._preview_debounce.timeout.connect(self._render_preview)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Wallpaper Editor")
        title.setStyleSheet("font-size: 20pt; font-weight: 900;")
        subtitle = QLabel("Import an image, apply filters, crop, save, and set as wallpaper.")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 11pt;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)

        self._import_btn = QPushButton("Import Image…")
        self._import_btn.setObjectName("Primary")
        self._import_btn.clicked.connect(self.import_image)

        self._crop_btn = QPushButton("Crop")
        self._crop_btn.setToolTip("Enable crop mode (drag on preview)")
        self._crop_btn.setCheckable(True)
        self._crop_btn.toggled.connect(self._toggle_crop_mode)

        self._reset_btn = QPushButton("Reset")
        self._reset_btn.clicked.connect(self.reset)

        self._save_btn = QPushButton("Save As…")
        self._save_btn.clicked.connect(self.save_as)

        self._apply_btn = QPushButton("Apply to Desktop")
        self._apply_btn.clicked.connect(self.apply_to_desktop)

        actions_layout.addWidget(self._import_btn)
        actions_layout.addWidget(self._crop_btn)
        actions_layout.addWidget(self._reset_btn)
        actions_layout.addStretch(1)
        actions_layout.addWidget(self._save_btn)
        actions_layout.addWidget(self._apply_btn)

        layout.addWidget(actions)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(14)

        self._preview = CropLabel()
        self._preview.setToolTip("Preview (toggle Crop, then drag to select).")
        self._preview.crop_selected.connect(self._on_crop_selected)
        self._preview.resized.connect(self._render_scaled_pixmap)
        body_layout.addWidget(self._preview, 1)

        controls = QWidget()
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)

        self._info = QLabel("Import an image to start.")
        self._info.setStyleSheet("color: #94a3b8;")
        self._info.setWordWrap(True)
        controls_layout.addWidget(self._info)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setVerticalSpacing(12)

        self._brightness = QSlider(Qt.Orientation.Horizontal)
        self._brightness.setRange(0, 200)
        self._brightness.setValue(100)
        self._brightness.valueChanged.connect(self._on_filters_changed)

        self._contrast = QSlider(Qt.Orientation.Horizontal)
        self._contrast.setRange(0, 200)
        self._contrast.setValue(100)
        self._contrast.valueChanged.connect(self._on_filters_changed)

        self._blur = QSlider(Qt.Orientation.Horizontal)
        self._blur.setRange(0, 20)
        self._blur.setValue(0)
        self._blur.valueChanged.connect(self._on_filters_changed)

        form.addRow("Brightness", self._brightness)
        form.addRow("Contrast", self._contrast)
        form.addRow("Blur", self._blur)
        controls_layout.addLayout(form)

        hint = QLabel("Tip: Use subtle blur + contrast for a clean desktop look.")
        hint.setStyleSheet("color: #94a3b8;")
        hint.setWordWrap(True)
        controls_layout.addWidget(hint)
        controls_layout.addStretch(1)

        body_layout.addWidget(controls, 0)
        layout.addWidget(body, 1)

        self._set_enabled(False)

    def _set_enabled(self, enabled: bool) -> None:
        for w in [self._crop_btn, self._reset_btn, self._save_btn, self._apply_btn, self._brightness, self._contrast, self._blur]:
            w.setEnabled(enabled)

    def import_image(self) -> None:
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Import Image",
            str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.bmp *.webp);;All files (*.*)",
        )
        if not file:
            return
        try:
            img = Image.open(file)
            img.load()
            self._original = img.convert("RGBA")
        except Exception as e:
            QMessageBox.critical(self, "Import failed", f"Could not open image:\n{e}")
            return

        self._crop_rect = None
        self._filters = _Filters()
        self._brightness.setValue(100)
        self._contrast.setValue(100)
        self._blur.setValue(0)

        self._rebuild_bases()
        self._set_enabled(True)
        self._info.setText(f"Loaded: {Path(file).name} • {self._original.width}×{self._original.height}")
        self._render_preview()

    def reset(self) -> None:
        if not self._original:
            return
        self._crop_btn.setChecked(False)
        self._crop_rect = None
        self._filters = _Filters()
        self._brightness.setValue(100)
        self._contrast.setValue(100)
        self._blur.setValue(0)
        self._rebuild_bases()
        self._render_preview()

    def _toggle_crop_mode(self, enabled: bool) -> None:
        self._preview.set_crop_mode(enabled)
        self._info.setText(
            "Crop mode: drag a rectangle on the preview." if enabled else (self._info.text() or "Ready.")
        )

    def _on_crop_selected(self, rect) -> None:
        if not self._original:
            return

        # rect is in preview-base coords. Convert to original coords.
        pw, ph = self._preview_source_size

        if self._crop_rect:
            base_x1, base_y1, base_x2, base_y2 = self._crop_rect
        else:
            base_x1, base_y1 = 0, 0
            base_x2, base_y2 = self._original.size

        base_w = max(1, base_x2 - base_x1)
        base_h = max(1, base_y2 - base_y1)

        sx = base_w / max(1, pw)
        sy = base_h / max(1, ph)

        x1 = base_x1 + int(rect.x() * sx)
        y1 = base_y1 + int(rect.y() * sy)
        x2 = base_x1 + int((rect.x() + rect.width()) * sx)
        y2 = base_y1 + int((rect.y() + rect.height()) * sy)

        ow, oh = self._original.size
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(ow, x2), min(oh, y2)

        if (x2 - x1) < 20 or (y2 - y1) < 20:
            self._ctx.notifications.info("Crop", "Selection too small.")
            return

        self._crop_rect = (x1, y1, x2, y2)
        self._crop_btn.setChecked(False)
        self._rebuild_bases()
        self._render_preview()
        self._ctx.notifications.info("Crop applied", f"{x2 - x1}×{y2 - y1}")

    def _on_filters_changed(self, _value: int) -> None:
        self._filters = _Filters(
            brightness=self._brightness.value() / 100.0,
            contrast=self._contrast.value() / 100.0,
            blur=float(self._blur.value()),
        )
        self._preview_debounce.start()

    def _rebuild_bases(self) -> None:
        if not self._original:
            self._cropped_full = None
            self._cropped_preview_base = None
            self._preview_source_size = (1, 1)
            return

        base = self._original
        if self._crop_rect:
            base = base.crop(self._crop_rect)

        self._cropped_full = base

        preview = base.copy()
        preview.thumbnail((1400, 900), Image.Resampling.LANCZOS)
        self._cropped_preview_base = preview
        self._preview_source_size = (preview.width, preview.height)
        self._preview.set_source_size(preview.width, preview.height)

    def _apply_filters(self, img: Image.Image) -> Image.Image:
        out = img
        if abs(self._filters.brightness - 1.0) > 1e-3:
            out = ImageEnhance.Brightness(out).enhance(self._filters.brightness)
        if abs(self._filters.contrast - 1.0) > 1e-3:
            out = ImageEnhance.Contrast(out).enhance(self._filters.contrast)
        if self._filters.blur > 0:
            out = out.filter(ImageFilter.GaussianBlur(radius=self._filters.blur))
        return out

    def _render_preview(self) -> None:
        if not self._cropped_preview_base:
            self._preview.clear()
            self._preview_pixmap_source = None
            return

        img = self._apply_filters(self._cropped_preview_base.copy())
        self._preview_pixmap_source = _pil_to_pixmap(img)
        self._render_scaled_pixmap()

    def _render_scaled_pixmap(self) -> None:
        if not self._preview_pixmap_source:
            return
        target = self._preview.size()
        pm = self._preview_pixmap_source.scaled(
            target,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._preview.setPixmap(pm)

    def _render_full(self) -> Image.Image | None:
        if not self._cropped_full:
            return None
        return self._apply_filters(self._cropped_full.copy())

    def save_as(self) -> None:
        img = self._render_full()
        if img is None:
            return

        out_dir = ensure_dir(data_dir("QuickUtil") / "wallpapers")
        file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Wallpaper",
            str(out_dir / "wallpaper.png"),
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)",
        )
        if not file:
            return

        try:
            path = Path(file)
            ext = path.suffix.lower()
            if ext in {".jpg", ".jpeg", ".bmp"}:
                img.convert("RGB").save(path)
            else:
                img.save(path)
            self._ctx.notifications.info("Saved", str(path.name))
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"Could not save image:\n{e}")

    def apply_to_desktop(self) -> None:
        img = self._render_full()
        if img is None:
            return

        out_dir = ensure_dir(data_dir("QuickUtil") / "wallpapers")
        target = out_dir / "quickutil_current_wallpaper.png"

        try:
            img.save(target)
        except Exception as e:
            QMessageBox.critical(self, "Apply failed", f"Could not write wallpaper:\n{e}")
            return

        ok, msg = apply_wallpaper(target)
        if ok:
            self._ctx.notifications.info("Wallpaper", msg, toast=True)
        else:
            QMessageBox.warning(self, "Apply failed", msg)
