import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image/image.dart' as img;
import 'package:image_picker/image_picker.dart';

class WallpaperEditorScreen extends StatefulWidget {
  const WallpaperEditorScreen({super.key});

  @override
  State<WallpaperEditorScreen> createState() => _WallpaperEditorScreenState();
}

class _WallpaperEditorScreenState extends State<WallpaperEditorScreen> {
  final _picker = ImagePicker();

  img.Image? _decoded;
  double _brightness = 1.0;
  double _contrast = 1.0;
  double _blur = 0.0;

  Future<void> _pick() async {
    final file = await _picker.pickImage(source: ImageSource.gallery);
    if (file == null) return;
    final bytes = await file.readAsBytes();
    final decoded = img.decodeImage(bytes);
    if (!mounted) return;
    setState(() {
      _decoded = decoded;
      _brightness = 1.0;
      _contrast = 1.0;
      _blur = 0.0;
    });
  }

  Uint8List? _renderPreview() {
    if (_decoded == null) return null;
    var out = img.copyResize(_decoded!, width: 1000);
    out = img.adjustColor(out, brightness: _brightness, contrast: _contrast);
    if (_blur > 0) {
      out = img.gaussianBlur(out, radius: (_blur * 6).round().clamp(1, 24));
    }
    return Uint8List.fromList(img.encodePng(out));
  }

  @override
  Widget build(BuildContext context) {
    final preview = _renderPreview();

    return Scaffold(
      appBar: AppBar(title: const Text('Wallpaper Editor')),
      floatingActionButton: FloatingActionButton(onPressed: _pick, child: const Icon(Icons.image_outlined)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (preview == null)
            const Text('Pick an image to start.', style: TextStyle(color: Colors.white70))
          else
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.memory(preview, fit: BoxFit.cover),
            ),
          const SizedBox(height: 12),
          _slider(
            label: 'Brightness',
            value: _brightness,
            min: 0.6,
            max: 1.6,
            onChanged: (v) => setState(() => _brightness = v),
          ),
          _slider(
            label: 'Contrast',
            value: _contrast,
            min: 0.6,
            max: 1.8,
            onChanged: (v) => setState(() => _contrast = v),
          ),
          _slider(
            label: 'Blur',
            value: _blur,
            min: 0,
            max: 1,
            onChanged: (v) => setState(() => _blur = v),
          ),
          const SizedBox(height: 10),
          const Text(
            'Applying wallpaper is platform-dependent. This editor focuses on import + filters; '
            'you can extend it with an Android-only wallpaper plugin.',
            style: TextStyle(color: Colors.white70),
          ),
        ],
      ),
    );
  }

  Widget _slider({
    required String label,
    required double value,
    required double min,
    required double max,
    required ValueChanged<double> onChanged,
  }) {
    return Card(
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: Theme.of(context).textTheme.labelLarge),
            Slider(value: value, min: min, max: max, onChanged: onChanged),
          ],
        ),
      ),
    );
  }
}

