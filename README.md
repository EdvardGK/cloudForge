# CloudForge - Scan-to-BIM Point Cloud Toolkit

A modular, scalable toolkit for processing point cloud data and extracting Building Information Modeling (BIM) elements from architectural scans.

## 🎯 Project Vision

Transform scattered point cloud processing scripts into a unified, intelligent system that automates scan-to-BIM workflows for architects and construction professionals.

## ✨ Features

### Current (Phase 1 - Foundation)
- ✅ **Multi-format Support**: PLY, PCD, LAS, LAZ, E57, PTS file formats
- ✅ **Scanner Presets**: Pre-configured settings for Leica RTC360, FARO Focus, and more
- ✅ **YAML Configuration**: Flexible, human-readable configuration system
- ✅ **Progress Tracking**: Visual progress bars and performance monitoring
- ✅ **CLI Interface**: Command-line tool with scanner-specific presets
- ✅ **Usage Analytics**: Built-in tracking for performance optimization

### Planned (Phase 2 & 3)
- 🔄 **Intelligent Cleaning**: Adaptive outlier removal and noise reduction
- 🔄 **Glass/Reflection Detection**: Advanced algorithms for mirror and glass surfaces
- 🔄 **BIM Element Extraction**: Automated wall, floor, ceiling detection
- 🔄 **MEP System Detection**: Pipes, ducts, and mechanical system identification
- 🔄 **Web Visualization**: Three.js-based interactive viewer
- 🔄 **Quality Assurance**: Alignment validation with heatmap visualization

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd pointCloud

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional libraries for full functionality
pip install open3d laspy  # For complete format support
```

### Basic Usage

```bash
# List available scanner presets
python tools/cloudforge-cli/cloudforge.py list-presets

# Process a point cloud with a preset
python tools/cloudforge-cli/cloudforge.py process scan.ply --preset leica_rtc360

# Get information about a point cloud
python tools/cloudforge-cli/cloudforge.py info scan.ply

# Create a custom scanner preset
python tools/cloudforge-cli/cloudforge.py create-preset \
    --name "my_scanner" \
    --scanner "Custom Scanner Model" \
    --noise 3.0
```

## 📋 Architecture

### Component Structure

```
components/
├── core/
│   ├── io/                     # File I/O operations
│   │   ├── multi_format_loader.py
│   │   └── export_manager.py
│   ├── config/                 # Configuration management
│   │   └── config_manager.py
│   └── utils/                  # Utilities and tracking
│       └── progress_tracker.py
├── pointcloud/                 # Processing modules
│   ├── cleaning/              # Outlier removal, noise reduction
│   ├── optimization/          # Thinning, voxel sampling
│   ├── analysis/              # Reflection detection, alignment
│   └── extraction/            # BIM element detection
└── visualization/             # Viewers and quality visualization
```

### Configuration System

Scanner-specific presets are stored in `config/presets/`:

```yaml
# config/presets/leica_rtc360.yaml
scanner:
  name: "Leica RTC360"
  typical_noise: 0.002  # 2mm at 10m
  max_range: 130.0
  intensity_range: [0, 2048]

cleaning:
  statistical_outlier:
    neighbors: 30
    std_ratio: 1.5
  radius_outlier:
    radius: 0.05
    min_neighbors: 10

thinning:
  method: "voxel"
  voxel_size: 0.01  # 1cm for architectural scans
  preserve_boundaries: true

reflection:
  intensity_available: true
  intensity_threshold: 0.95
  glass_detection: true
```

## 🔧 Development

### Adding New Scanner Presets

1. **Option 1: Use CLI**
   ```bash
   python tools/cloudforge-cli/cloudforge.py create-preset \
       --name "new_scanner" \
       --scanner "Scanner Model Name" \
       --noise 2.5  # in millimeters
   ```

2. **Option 2: Manual Configuration**
   - Copy `config/templates/default.yaml`
   - Modify scanner parameters
   - Save as `config/presets/scanner_name.yaml`

### Project Structure

- **`components/`**: Core functionality modules
- **`tools/`**: CLI interface and utilities
- **`config/`**: Scanner presets and templates
- **`tests/`**: Test files (to be implemented)
- **`templates/`**: Processing pipeline templates

### Key Design Principles

1. **Modular Components**: Each processing operation is isolated and reusable
2. **Configuration-Driven**: All behavior controlled via YAML configuration
3. **Format Agnostic**: Unified interface for all point cloud formats
4. **Performance First**: Memory-efficient processing with progress tracking
5. **Intelligence Integration**: Adaptive algorithms based on scan characteristics

## 📊 Performance Targets

- **Processing Speed**: 50M+ points in < 5 minutes
- **Accuracy**: 95% accurate plane detection for BIM extraction
- **Memory Efficiency**: Batch processing for datasets > 1GB
- **Quality**: Automated validation and visual QA tools

## 🛠️ CLI Commands

### Core Commands

```bash
# Process point clouds
cloudforge process <file> --preset <scanner> --output <path>

# Extract BIM elements (planned)
cloudforge extract-bim <file> --elements walls,floors --format ifc

# Quality validation (planned)
cloudforge validate <scan1> <scan2> --report alignment.html

# Configuration management
cloudforge list-presets
cloudforge create-preset --name <name> --scanner <model> --noise <mm>
cloudforge validate-config <config.yaml>

# Statistics and monitoring
cloudforge stats
cloudforge info <file>
```

### Configuration Options

- **`--preset`**: Scanner preset (leica_rtc360, faro_focus, etc.)
- **`--skip-cleaning`**: Skip outlier removal operations
- **`--skip-thinning`**: Skip point cloud optimization
- **`--format`**: Output format (ply, pcd, pts, xyz)

## 📚 Supported Formats

| Format | Extension | Read | Write | Notes |
|--------|-----------|------|-------|-------|
| PLY | `.ply` | ✅ | ✅ | Stanford Polygon Library format |
| PCD | `.pcd` | ✅ | ✅ | Point Cloud Data format |
| LAS | `.las/.laz` | ✅ | ❌ | LIDAR data format |
| E57 | `.e57` | 🔄 | ❌ | 3D imaging standard (planned) |
| PTS | `.pts` | ✅ | ✅ | Simple text format |
| XYZ | `.xyz` | ❌ | ✅ | Coordinates only |

## 🚦 Current Status

**Phase 1 Complete**: ✅ Foundation infrastructure
- Multi-format I/O system
- Configuration management with presets
- CLI interface with basic commands
- Progress tracking and monitoring

**Phase 2 In Progress**: 🔄 Intelligence layer
- Advanced cleaning algorithms
- Reflection detection
- Quality assurance tools

**Phase 3 Planned**: 📋 BIM integration
- Geometric primitive extraction
- Architectural element classification
- Web visualization interface

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes following the modular architecture
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🎯 Roadmap

- **Week 1-2**: ✅ Core infrastructure and CLI
- **Week 3-4**: 🔄 Advanced processing algorithms
- **Week 5-6**: 📋 BIM extraction and web visualization
- **Week 7+**: 🚀 Performance optimization and deployment