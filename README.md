# taskmgr
# Task Manager - Windows XP Style for Linux

A faithful recreation of the classic Windows XP Task Manager for Linux systems, built with Python and GTK3.


## Features

- **Windows XP Authentic UI**: Classic blue title bar, gradient buttons, and tabbed interface
- **Applications Tab**: View and manage running GUI applications
- **Processes Tab**: Complete system process list with detailed information
- **Performance Tab**: Real-time CPU and memory usage monitoring
- **Process Management**: End tasks and processes with proper termination
- **New Task Dialog**: Run new applications and commands
- **Auto-refresh**: Automatic updates every 2 seconds
- **Native Integration**: Proper desktop entry and taskbar icon

## Installation

### Arch Linux

#### From AUR (Recommended)
```bash
yay -S taskmgr
```

#### From Source
```bash
git clone https://github.com/yourusername/taskmgr.git
cd taskmgr
makepkg -si
```

### Manual Installation

#### Dependencies
- Python 3.6+
- python-psutil
- python-gobject
- gtk3

#### Install on Arch-based systems:
```bash
sudo pacman -S python python-psutil python-gobject gtk3
git clone https://github.com/yourusername/taskmgr.git
cd taskmgr
sudo cp taskmgr.py /usr/local/bin/taskmgr
sudo chmod +x /usr/local/bin/taskmgr
sudo cp taskmgr.desktop /usr/share/applications/
```

#### Install on Debian/Ubuntu:
```bash
sudo apt install python3 python3-psutil python3-gi gir1.2-gtk-3.0
git clone https://github.com/yourusername/taskmgr.git
cd taskmgr
sudo cp taskmgr.py /usr/local/bin/taskmgr
sudo chmod +x /usr/local/bin/taskmgr
sudo cp taskmgr.desktop /usr/share/applications/
```

## Usage

### Launch from Application Menu
Search for "Task Manager" in your application launcher.

### Launch from Terminal
```bash
taskmgr
```

### Features Overview

#### Applications Tab
- View running GUI applications
- End misbehaving applications
- Switch between applications
- Launch new tasks

#### Processes Tab
- View all system processes
- See CPU and memory usage per process
- End processes safely
- Filter by user and status

#### Performance Tab
- Real-time CPU usage graph
- Memory usage monitoring
- System statistics

## Building from Source

### Prerequisites
- Base-devel (for Arch)
- Python 3.6+
- GTK3 development libraries

### Build Steps
```bash
git clone https://github.com/yourusername/taskmgr.git
cd taskmgr
makepkg -s
sudo pacman -U taskmgr-*.pkg.tar.*
```

## Project Structure
```
taskmgr/
├── PKGBUILD              # Arch Linux package build file
├── taskmgr.py            # Main application
├── taskmgr.desktop       # Desktop entry file
├── README.md             # This file
└── screenshots/          # Application screenshots
```

## Technical Details

- **Language**: Python 3
- **GUI Toolkit**: GTK3 with PyGObject
- **Process Management**: psutil library
- **Package Format**: Arch Linux PKGBUILD
- **Compatibility**: Linux systems with GTK3

## Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Known Issues

- "Switch To" functionality is not fully implemented
- Some system processes may require root privileges to terminate
- Window management integration is limited

## Troubleshooting

### Application won't start
- Ensure all dependencies are installed: `python-psutil`, `python-gobject`, `gtk3`
- Check Python version: `python3 --version`
- Verify executable permissions: `chmod +x /usr/local/bin/taskmgr`

### Permission errors when ending processes
- Some system processes require elevated privileges
- Run with sudo for system-wide process management (not recommended for security)

### Missing applications in Applications tab
- The app detects common GUI applications automatically
- Custom applications may need to be added to the detection list

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the classic Windows XP Task Manager
- Built with Python and GTK3 for Linux compatibility
- Uses psutil for cross-platform process management

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/taskmgr/issues) page
2. Create a new issue with detailed information
3. Include your system information and error messages

---

**Note**: This is a fan-made recreation for educational and nostalgic purposes. Windows XP and its Task Manager are trademarks of Microsoft Corporation.
