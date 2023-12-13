# Coursework 3: The Process
# FilmReel

### Created By:
Hamza S - sc22h2s@leeds.ac.uk  
Joseph J - sc22j2j@leeds.ac.uk  
Matthew W - sc22mcw@leeds.ac.uk  
Daniel B - sc22d2b@leeds.ac.uk  
Ellis S - sc22es@leeds.ac.uk  

---

## Setting Up
For the program to be run QTCreator is required. Qt Creator is an IDE for programming C++.

## QT Download Links - *QT 15.5.2*
- Windows 10:
    - [Download](https://d13lb3tujbc8s0.cloudfront.net/onlineinstallers/qt-unified-windows-x64-4.6.1-online.exe) for Qt Creator
    - [Instructions](https://doc.qt.io/qt-6/windows.html) from Qt
- MacOS:
    - Install XCode before Qt Creator.
    - [Download](https://d13lb3tujbc8s0.cloudfront.net/onlineinstallers/qt-unified-macOS-x64-4.6.1-online.dmg) for Qt Creator
    - [Instructions](https://doc.qt.io/qt-5/macos.html) from Qt
- Linux:
    - [Download](https://www.qt.io/download-qt-installer) for Qt Creator
    - [Instructions](https://doc.qt.io/qt-5/linux.html) from Qt

---

#### Before running, Command Line Arguments must be assigned.  
Go to,  
Projects → Desktop Qt 5.15.2 → Run → Run Settings →

Command Line Arguments:
```
.../ -working directory- /videos
```
Working Directory:
```
.../ -working directory-
```

## Navigation Tree
```
.
└── Feed
    ├── Play (Video)
    ├── Capture
    │   ├── Upload
    │   │   ├── Left Video
    │   │   └── Right Video
    │   │
    │   ├── Record
    ├<──┴── Feed
    │
    ├── My Profile
    │   ├── Add Friends
    │   ├── Manage Friends
    │   ├── Other Functions
    │   ├── Languages
    │   │   ├── English
    │   │   ├── Spanish (español)
    │   │   ├── French (français)
    │   │   ├── German (Deutsch)
    │   │   └── Italian (italiano)
    │   │
    └<──┼── Feed
        └── Exit.
```
