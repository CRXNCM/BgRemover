# Background Remover - Complete README

## 🎯 Overview

**Background Remover** is a powerful, AI-powered tool for removing backgrounds from images with exceptional precision. It offers both a user-friendly GUI application and a command-line interface, supporting batch processing and multiple AI models for optimal results.

## ✨ Key Features

### 🖥️ GUI Application Features
- **Drag & Drop Interface**: Easy file selection with visual preview
- **Real-time Processing**: See results instantly with side-by-side comparison
- **Zoom Controls**: Navigate images with zoom in/out functionality
- **Batch Processing**: Process multiple images simultaneously
- **Multiple AI Models**: Choose from 4 different AI models for optimal results
- **Alpha Matting**: Advanced edge detection for complex backgrounds
- **Custom Output**: Specify output directory and naming conventions

### ⚡ Command-Line Features
- **Batch Processing**: Process hundreds of images in parallel
- **Flexible Input**: Accept files, directories, or wildcards
- **Customizable Output**: Control naming, formats, and directories
- **Progress Tracking**: Real-time progress with progress bars
- **Error Handling**: Robust error handling with detailed reporting

### 🤖 AI Models Available
- **u2net**: General-purpose model (default)
- **u2netp**: Lightweight model for faster processing
- **u2net_human_seg**: Optimized for human subjects
- **silueta**: High-precision model for detailed edges

## 🚀 Quick Start

### GUI Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI
python bg_remover_ui.py
```

### Command-Line Usage
```bash
# Single image
python bg_remover.py image.jpg

# Batch processing
python bg_remover.py folder/ -o output/ --workers 4

# With alpha matting
python bg_remover.py *.png -a --suffix _transparent
```

## 📋 Installation

### System Requirements
- Python 3.7+
- Windows 10/11, macOS, or Linux
- 4GB+ RAM recommended
- 1GB+ disk space

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Optional: GPU Acceleration
For faster processing with CUDA support:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 🎨 GUI Usage Guide

### 1. **Getting Started**
- Launch the application: `python bg_remover_ui.py`
- The dark-themed interface opens with three main sections

### 2. **File Selection**
- Click **"Select Images"** or drag & drop files
- Supports JPG, PNG, BMP, TIFF, and WebP formats
- View selected files count in the status bar

### 3. **Preview & Settings**
- **Left Panel**: Original vs Processed comparison
- **Right Panel**: Settings and controls
- **Navigation**: Use arrow buttons or keyboard shortcuts

### 4. **Processing Options**
- **Model Selection**: Choose from dropdown menu
- **Alpha Matting**: Checkbox for edge refinement
- **Output Directory**: Browse button selection
- **File Naming**: Automatic with customizable suffix

### 5. **Processing**
- **Process Preview**: Process current image only
- **Process All**: Batch process all selected images
- **Download**: Save processed image with custom naming

## ⚙️ Command-Line Usage

### Basic Syntax
```bash
python bg_remover.py [INPUTS] [OPTIONS]
```

### Examples

#### Single Image
```bash
python bg_remover.py photo.jpg
# Output: photo_nobg.png
```

#### Batch Processing
```bash
# Process all images in a folder
python bg_remover.py photos/ -o processed/ --workers 8

# Process specific formats
python bg_remover.py *.jpg *.png -o results/
```

#### Advanced Options
```bash
# Use human segmentation model
python bg_remover.py portraits/ -m u2net_human_seg -a

# Custom naming
python bg_remover.py input.jpg -s _no_background --alpha-matting
```

### Command-Line Options
| Option | Description | Example |
|--------|-------------|---------|
| `-o, --output-dir` | Output directory | `-o ./results/` |
| `-s, --suffix` | Filename suffix | `-s _transparent` |
| `-m, --model` | AI model to use | `-m u2net_human_seg` |
| `-a, --alpha-matting` | Enable edge refinement | `--alpha-matting` |
| `--workers` | Number of threads | `--workers 4` |

## 🔧 Configuration

### GUI Settings
- **Model**: Dropdown selection in settings panel
- **Alpha Matting**: Checkbox for edge refinement
- **Output Directory**: Browse button selection
- **File Naming**: Automatic with customizable suffix

### Environment Variables
```bash
# Set default model
export BG_REMOVER_MODEL=u2net_human_seg

# Set output directory
export BG_REMOVER_OUTPUT_DIR=./processed/
```

## 📊 Performance Tips

### Optimization Guidelines
- **CPU Usage**: Use `--workers` to control thread count
- **Memory**: Process images in batches for large datasets
- **Model Selection**: Use `u2netp` for faster processing
- **Image Size**: Resize large images before processing

### Benchmarks
| Model | Speed | Quality | Use Case |
|-------|--------|---------|----------|
| u2netp | ⚡⚡⚡⚡ | ⭐⭐⭐ | Quick processing |
| u2net | ⚡⚡⚡ | ⭐⭐⭐⭐ | General purpose |
| u2net_human_seg | ⚡⚡ | ⭐⭐⭐⭐⭐ | Portraits |
| silueta | ⚡ | ⭐⭐⭐⭐⭐ | Detailed edges |

## 🐛 Troubleshooting

### Common Issues

#### "Model not found"
```bash
# Reinstall rembg
pip install --upgrade rembg
```

#### "Out of memory"
- Reduce image size before processing
- Use `u2netp` model
- Decrease `--workers` count

#### "Permission denied"
- Run as administrator (Windows)
- Use `sudo` (Linux/macOS)
- Check file permissions

### Error Codes
| Code | Description | Solution |
|------|-------------|----------|
| 101 | Model load failure | Reinstall dependencies |
| 102 | Image read error | Check file format |
| 103 | Memory error | Reduce image size |
| 104 | Write permission | Check output directory |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/your-repo/background-remover.git
cd background-remover
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests
```bash
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **rembg** library for AI-powered background removal
- **Pillow** for image processing capabilities
- **CustomTkinter** for modern GUI framework
- **PyTorch** community for AI model support

## 📞 Support
- **Phone**: +251 925254765
- **Email**: comradencm@gmail.com


---

**Made with ❤️ by yoni**
