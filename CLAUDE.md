# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CloudForge** is a scan-to-BIM point cloud processing toolkit designed to transform scattered point cloud processing scripts into a modular, scalable system for architectural workflows. The project follows a component-based architecture with intelligence layers for automated BIM element extraction.

## Architecture Overview

### Component Structure
The project is organized into a layered component architecture:

- **Core Layer**: I/O operations, configuration management, utilities
- **PointCloud Layer**: Specialized processing modules (cleaning, optimization, analysis, extraction)  
- **Visualization Layer**: Interactive viewers and quality visualization tools
- **Templates**: Reusable processing pipelines for common workflows
- **Tools**: CLI interface with scanner-specific presets

### Key Architectural Principles

1. **Modular Components**: Each processing operation is encapsulated in reusable components with clear interfaces
2. **Configuration-Driven**: YAML-based configuration system with scanner-specific presets
3. **Format Agnostic**: Unified I/O layer supporting .ply, .las, .laz, .e57, .pcd, .pts formats
4. **Performance First**: Memory-efficient batch processing with progress tracking
5. **Intelligence Integration**: ML-based adaptive parameter tuning and element classification
6. **Quality Assurance**: Built-in alignment validation and visual QA tools

## Development Commands

### Core Development
```bash
# Main CLI interface
python tools/cloudforge-cli/cloudforge.py process <input> --preset <scanner_type>
python tools/cloudforge-cli/cloudforge.py extract-bim <input> --elements walls,floors --format ifc
python tools/cloudforge-cli/cloudforge.py validate <scan1> <scan2> --report alignment.html

# Testing (when implemented)
pytest tests/ -v                    # Run all tests
pytest tests/test_processing.py -v  # Specific processing tests
pytest --cov=components             # Coverage for components

# Performance monitoring
python components/core/utils/performance_monitor.py --benchmark
```

### Configuration Management
```bash
# View available presets
cloudforge list-presets

# Create custom preset
cloudforge create-preset --name custom_scanner --based-on leica_rtc360

# Validate configuration
cloudforge validate-config config/custom.yaml
```

## Critical Implementation Details

### Processing Pipeline Flow
1. **Multi-format Loading**: Auto-detection and robust error handling for various point cloud formats
2. **Adaptive Cleaning**: Statistical and radius-based outlier removal with noise characteristic adaptation
3. **Intelligent Optimization**: Curvature-based thinning and ML-guided decimation
4. **Feature Extraction**: RANSAC plane segmentation and architectural element classification
5. **Quality Validation**: Alignment checking with heatmap visualization

### Performance Requirements
- **Target**: Process 50M+ points in < 5 minutes
- **Memory Management**: Batch processing for large datasets
- **Quality Metrics**: 95% accurate plane detection
- **Voxel Optimization**: Default 1cm voxel size for architectural scans

### Configuration System
Scanner-specific presets handle varying noise characteristics and typical parameters:
- Leica RTC360: 2mm typical noise, intensity-based glass detection
- FARO Focus: Different noise profiles and processing parameters
- Custom scanners: Template-based configuration creation

### Specialized Processing Modules

#### Glass/Mirror Detection
- Intensity threshold analysis (0.95+ for glass surfaces)
- Clustering algorithms for reflection pattern recognition
- Pass-through point identification and filtering

#### BIM Element Extraction
- RANSAC-based plane segmentation for walls/floors/ceilings
- MEP system detection using geometric and spatial analysis
- IFC format export with proper BIM relationships

#### Change Detection
- Temporal scan comparison algorithms
- Automated reporting of structural changes
- Progress tracking for construction monitoring

## Development Phases

### Phase 1: Foundation
- Multi-format I/O system with robust error handling
- YAML configuration management with preset templates  
- Progress tracking and logging framework
- Memory-efficient batch processing pipeline

### Phase 2: Intelligence Layer
- Advanced reflection and glass detection
- Adaptive parameter tuning based on scan characteristics
- Quality assurance with visual validation tools

### Phase 3: BIM Integration
- Geometric primitive extraction (planes, cylinders, etc.)
- Architectural element classification algorithms
- Web-based visualization with Three.js integration
- IFC/BIM format export capabilities

## Testing Strategy

- **Unit Tests**: Core processing algorithms and I/O operations
- **Integration Tests**: End-to-end pipeline validation
- **Performance Tests**: Memory usage and processing speed benchmarks
- **Quality Tests**: Validation against known-good reference scans

## Deployment Options

1. **Standalone CLI**: Single executable with preset configurations
2. **Python Package**: `pip install cloudforge` for programmatic use
3. **Web Service**: Docker container with FastAPI backend and WebSocket streaming
4. **Component Library**: Individual modules for custom integration

## Usage Tracking

All components include usage tracking decorators for performance monitoring and optimization guidance:
```python
@track_usage("cloudforge.cleaning.outliers")
@track_usage("cloudforge.io.loader")
```

## Configuration Templates

Each scanner type has optimized default parameters stored in `config/presets/`:
- Noise thresholds based on scanner specifications
- Optimal voxel sizes for different scan densities
- Format-specific handling (intensity availability, coordinate systems)