# HashMe - SHA-256 Hash Comparer

HashMe is a simple GUI tool for calculating and comparing SHA-256 hash values of files and text. It uses the **GTK** library and is developed in **Python**. The tool allows users to select files, calculate their hash values, and compare them with manually entered hashes.

## Features

- Calculate SHA-256 hash values of files.
- Manually input a SHA-256 hash value.
- Compare hash values (file-to-file or file-to-manual hash).
- Option to save results to a text file.
- Built-in buttons for selecting files, resetting inputs, and saving results.
- Support for custom icons and design for an attractive user interface.

## Requirements

- **Python 3.x**
- **GTK 3** (For the GUI)
- **pygtk** (Python bindings for GTK 3)

### Install Dependencies:

Make sure the required packages are installed on your system:

1. Install Python 3 if not already installed.
2. Install GTK 3 bindings for Python. On Ubuntu/Debian, you can do so with:

```bash
sudo apt-get install python3-gi
sudo apt-get install gir1.2-gtk-3.0
