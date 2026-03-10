import 'dart:async';
import 'dart:io';

import 'package:battery_plus/battery_plus.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/material.dart';

import '../widgets/stat_card.dart';

class SystemMonitorScreen extends StatefulWidget {
  const SystemMonitorScreen({super.key});

  @override
  State<SystemMonitorScreen> createState() => _SystemMonitorScreenState();
}

class _SystemMonitorScreenState extends State<SystemMonitorScreen> {
  final _battery = Battery();
  final _deviceInfo = DeviceInfoPlugin();

  int? _batteryLevel;
  BatteryState? _batteryState;
  String _deviceLine = 'Loading…';

  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _load();
    _timer = Timer.periodic(const Duration(seconds: 12), (_) => _loadBattery());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    await Future.wait([_loadDevice(), _loadBattery()]);
  }

  Future<void> _loadBattery() async {
    try {
      final level = await _battery.batteryLevel;
      final state = await _battery.batteryState;
      if (!mounted) return;
      setState(() {
        _batteryLevel = level;
        _batteryState = state;
      });
    } catch (_) {
      // ignore
    }
  }

  Future<void> _loadDevice() async {
    try {
      String line = 'Unknown device';
      if (Platform.isAndroid) {
        final info = await _deviceInfo.androidInfo;
        line = '${info.manufacturer} ${info.model} • Android ${info.version.release}';
      } else if (Platform.isIOS) {
        final info = await _deviceInfo.iosInfo;
        line = '${info.name} • iOS ${info.systemVersion}';
      }
      if (!mounted) return;
      setState(() => _deviceLine = line);
    } catch (_) {
      // ignore
    }
  }

  @override
  Widget build(BuildContext context) {
    final batt = _batteryLevel == null ? '—' : '$_batteryLevel%';
    final state = _batteryState == null ? '—' : _batteryState!.name;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('System Monitor', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 6),
        Text(_deviceLine, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.white70)),
        const SizedBox(height: 14),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.25,
          children: [
            StatCard(
              title: 'Battery',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(batt, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
                  const SizedBox(height: 6),
                  Text('State: $state', style: const TextStyle(color: Colors.white70)),
                ],
              ),
            ),
            const StatCard(
              title: 'Performance',
              child: Text(
                'CPU/RAM metrics vary per platform.\n(Pluggable service layer ready.)',
                style: TextStyle(color: Colors.white70),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

