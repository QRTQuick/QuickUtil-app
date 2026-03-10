use a very good color combination pls try black ,red  any other fiting color then work on thr ui tab and menu and toolpilt and shortcut arrange ment so it is visualy appilng and morden Build a modern cross-platform desktop utility application that combines productivity tools and system monitoring features into one unified interface. The application should run on Windows, Linux, and macOS and be built using Python with PySide6 for the graphical interface.

The application should have a clean dashboard UI with a sidebar navigation menu that allows users to switch between different utility modules.

Core Modules to Implement
1. System Performance Analyzer

Create a system monitoring dashboard that displays real-time system information including:

CPU usage percentage

CPU model / processor type

GPU name and GPU usage (if available)

RAM usage and total memory

Disk usage

System uptime

Active drivers and hardware information

Use Python libraries such as:

psutil

platform

GPUtil

subprocess

Display the information using progress bars, charts, and statistics cards.

2. Calendar and Event Manager

Implement a built-in calendar utility that allows users to:

View monthly calendar

Add events

Edit events

Delete events

Save events locally using SQLite

3. Alarm and Reminder System

Create an alarm module where users can:

Set alarms

Set reminders

Enable/disable alarms

Trigger desktop notifications when alarms go off

4. Notification Center

Implement a simple notification hub inside the application that:

Shows alerts

Displays reminders

Displays system warnings (high CPU usage, low memory)

5. Wallpaper Editor

Create a wallpaper customization module that allows users to:

Import an image

Apply filters (blur, brightness, contrast)

Crop images

Save edited wallpapers

Apply wallpaper to desktop

Use Pillow (PIL) for image processing.

User Interface Requirements

Modern dark theme UI

Sidebar navigation

Dashboard overview screen

Responsive layouts

Icon-based navigation

System stats displayed using progress bars and graphs

Suggested Project Structure
desktop-utils-app
│
├── main.py
├── ui
│   ├── dashboard.py
│   ├── calendar_module.py
│   ├── alarm_module.py
│   ├── wallpaper_editor.py
│   └── notifications.py
│
├── system
│   ├── cpu_monitor.py
│   ├── gpu_monitor.py
│   ├── ram_monitor.py
│   └── drivers_info.py
│
├── database
│   └── events.db
│
├── assets
│   ├── icons
│   └── wallpapers
│
└── requirements.txt
Extra Features (Optional but Recommended)

Real-time system graphs

Startup performance check

Battery monitoring (for laptops)

Export system report

Theme customization

Final Goal

Create a professional desktop utility suite that acts as a central hub for productivity tools and system diagnostics, combining:

System monitoring

Personal utilities

Device customization

The app should be modular, scalable, and easy to extend with additional features later.  Build a modern cross-platform mobile utility application using Flutter (Dart) that combines productivity tools and system monitoring features in one application. The app should run smoothly on Android and iOS and provide a clean, responsive, and user-friendly interface.You are a senior software engineer tasked with building a cross-platform desktop utility application written in Python. The project must include a fully automated GitHub Actions CI/CD pipeline that compiles the application into Windows (.exe) and macOS (.app) builds on GitHub’s cloud runners, not locally.

Your output must include:

Production-ready Python code

Clean project architecture

Dependency management

A fully functional, error-free GitHub Actions workflow

Packaging using PyInstaller

Automatic artifact uploads for compiled builds

The workflow must work without requiring the developer to build locally.
The application should include a bottom nav You are a senior mobile software engineer and DevOps engineer. Your task is to build a cross-platform mobile utility application using Flutter (Dart) and configure a fully automated GitHub Actions CI/CD pipeline that compiles the application for:

Android (APK + AAB)

iOS (IPA or iOS build)

All builds must occur on GitHub Actions runners, not locally.

The generated code must include:

production-ready Flutter code

modular architecture

dependency management

error-free GitHub Actions workflow

automated artifact uploads

The workflow must work without requiring the developer to compile locally.igation bar or tab navigation for switching between different modules.

Core Features
1. System Performance Analyzer

Create a system monitoring page that displays real-time device information such as:

CPU usage

Processor type

RAM usage

Storage usage

Battery health and battery level

Device model and OS version

Use Flutter plugins such as:

device_info_plus

battery_plus

system_info

cpu_info

Display system information using:

progress indicators

performance cards

real-time updating charts

2. Calendar and Event Manager

Implement a calendar utility where users can:

view a monthly calendar

add events

edit events

delete events

receive reminders

Use local storage such as:

sqflite (SQLite)

or hive

3. Alarm and Reminder System

Create a module where users can:

set alarms

schedule reminders

receive notifications when alarms trigger

Use packages like:

flutter_local_notifications

timezone

4. Notification Center

Implement an in-app notification dashboard that shows:

reminder alerts

alarm alerts

system alerts (low battery, high CPU usage)

5. Wallpaper Editor

Create a wallpaper customization feature where users can:

import images

crop images

apply filters (brightness, blur, contrast)

save edited wallpapers

Use Flutter packages like:

image_picker

image_editor

photo_view

UI/UX Requirements

The mobile interface should include:

modern dark mode UI

bottom navigation bar

smooth animations

dashboard overview screen

clean card-based design

responsive layouts for different screen sizes

Suggested main navigation tabs:

Dashboard

System Monitor

Calendar

Utilities

Settings

Suggested Flutter Project Structure
mobile_utils_app
│
├── lib
│   ├── main.dart
│   │
│   ├── screens
│   │   ├── dashboard_screen.dart
│   │   ├── system_monitor_screen.dart
│   │   ├── calendar_screen.dart
│   │   ├── alarm_screen.dart
│   │   ├── wallpaper_editor_screen.dart
│   │
│   ├── widgets
│   │   ├── stat_card.dart
│   │   ├── system_chart.dart
│   │
│   ├── services
│   │   ├── system_service.dart
│   │   ├── notification_service.dart
│   │
│   ├── models
│   │   ├── event_model.dart
│   │
│   ├── database
│   │   └── database_helper.dart
│
├── assets
│   ├── icons
│   ├── images
│
└── pubspec.yaml
Additional Advanced Features (Optional)

automatic wallpaper changer

performance alerts

battery usage analytics

device temperature monitoring

export device diagnostic report

cloud sync for calendar events

Final Goal

Create a powerful mobile utility suite that helps users:

manage their daily productivity

monitor device performance

customize device appearance

receive smart reminders and notifications

The app should be modular, scalable, and easy to extend with new features in future updates.