from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
from pydantic import BaseModel, Field, validator
from ..utils.progress_tracker import track_usage

class CleaningConfig(BaseModel):
    """Configuration for point cloud cleaning operations."""
    statistical_outlier: Dict[str, float] = Field(default={
        'neighbors': 30,
        'std_ratio': 1.5
    })
    radius_outlier: Dict[str, float] = Field(default={
        'radius': 0.05,
        'min_neighbors': 10
    })
    
class ThinningConfig(BaseModel):
    """Configuration for point cloud thinning/optimization."""
    method: str = Field(default="voxel", description="Thinning method: voxel, adaptive, or random")
    voxel_size: float = Field(default=0.01, description="Voxel size in meters for voxel-based thinning")
    target_points: Optional[int] = Field(default=None, description="Target number of points")
    preserve_boundaries: bool = Field(default=True, description="Preserve edge points during thinning")

class ReflectionConfig(BaseModel):
    """Configuration for glass/reflection detection."""
    intensity_available: bool = Field(default=False)
    intensity_threshold: float = Field(default=0.95, description="Threshold for glass detection")
    glass_detection: bool = Field(default=True)
    clustering_epsilon: float = Field(default=0.02, description="DBSCAN epsilon for reflection clustering")

class ScannerConfig(BaseModel):
    """Scanner-specific configuration."""
    name: str
    typical_noise: float = Field(description="Typical noise level in meters")
    max_range: Optional[float] = Field(default=None, description="Maximum range in meters")
    angular_resolution: Optional[float] = Field(default=None, description="Angular resolution in degrees")
    intensity_range: Optional[tuple] = Field(default=None, description="Min/max intensity values")

class ProcessingConfig(BaseModel):
    """Complete processing configuration."""
    scanner: ScannerConfig
    cleaning: CleaningConfig = Field(default_factory=CleaningConfig)
    thinning: ThinningConfig = Field(default_factory=ThinningConfig)
    reflection: ReflectionConfig = Field(default_factory=ReflectionConfig)
    
    @validator('thinning')
    def validate_thinning_method(cls, v):
        if v.method not in ['voxel', 'adaptive', 'random']:
            raise ValueError("Thinning method must be 'voxel', 'adaptive', or 'random'")
        return v

@track_usage("cloudforge.config.manager")
class ConfigManager:
    """
    Manages YAML-based configuration with scanner presets.
    Handles loading, validation, and preset management.
    """
    
    def __init__(self, config_dir: Path = None):
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent.parent / "config"
        self.config_dir = Path(config_dir)
        self.presets_dir = self.config_dir / "presets"
        self.templates_dir = self.config_dir / "templates"
        
        # Ensure directories exist
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.loaded_configs: Dict[str, ProcessingConfig] = {}
    
    def load_preset(self, preset_name: str) -> ProcessingConfig:
        """
        Load a scanner preset configuration.
        
        Args:
            preset_name: Name of the preset (without .yaml extension)
            
        Returns:
            Validated ProcessingConfig object
        """
        preset_file = self.presets_dir / f"{preset_name}.yaml"
        
        if not preset_file.exists():
            available = self.list_presets()
            raise FileNotFoundError(
                f"Preset '{preset_name}' not found. Available presets: {available}"
            )
        
        with open(preset_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Validate and create config object
        config = ProcessingConfig(**config_data)
        self.loaded_configs[preset_name] = config
        
        return config
    
    def save_preset(self, preset_name: str, config: ProcessingConfig):
        """
        Save a configuration as a named preset.
        
        Args:
            preset_name: Name for the preset
            config: Configuration to save
        """
        preset_file = self.presets_dir / f"{preset_name}.yaml"
        
        # Convert to dict and save as YAML
        config_dict = config.dict()
        
        with open(preset_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
        
        self.loaded_configs[preset_name] = config
    
    def list_presets(self) -> List[str]:
        """Get list of available preset names."""
        preset_files = self.presets_dir.glob("*.yaml")
        return [f.stem for f in preset_files]
    
    def create_preset_from_template(self, 
                                    preset_name: str, 
                                    scanner_name: str,
                                    typical_noise: float,
                                    template: str = "default") -> ProcessingConfig:
        """
        Create a new preset from a template.
        
        Args:
            preset_name: Name for the new preset
            scanner_name: Human-readable scanner name
            typical_noise: Typical noise level in meters
            template: Template to base the preset on
            
        Returns:
            New ProcessingConfig object
        """
        # Load template or create default
        template_file = self.templates_dir / f"{template}.yaml"
        
        if template_file.exists():
            with open(template_file, 'r') as f:
                base_config = yaml.safe_load(f)
        else:
            # Create default configuration
            base_config = {
                'scanner': {
                    'name': scanner_name,
                    'typical_noise': typical_noise
                },
                'cleaning': {
                    'statistical_outlier': {
                        'neighbors': 30,
                        'std_ratio': 1.5
                    },
                    'radius_outlier': {
                        'radius': typical_noise * 25,  # Adaptive based on noise
                        'min_neighbors': 10
                    }
                },
                'thinning': {
                    'method': 'voxel',
                    'voxel_size': typical_noise * 5,  # Adaptive voxel size
                    'preserve_boundaries': True
                },
                'reflection': {
                    'intensity_available': False,
                    'intensity_threshold': 0.95,
                    'glass_detection': True,
                    'clustering_epsilon': typical_noise * 10
                }
            }
        
        # Update scanner info
        base_config['scanner']['name'] = scanner_name
        base_config['scanner']['typical_noise'] = typical_noise
        
        # Create and validate config
        config = ProcessingConfig(**base_config)
        
        # Save as new preset
        self.save_preset(preset_name, config)
        
        return config
    
    def get_config(self, preset_name: str) -> ProcessingConfig:
        """
        Get configuration, loading from file if not already loaded.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            ProcessingConfig object
        """
        if preset_name not in self.loaded_configs:
            return self.load_preset(preset_name)
        return self.loaded_configs[preset_name]
    
    def validate_config_file(self, config_file: Path) -> bool:
        """
        Validate a YAML configuration file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            ProcessingConfig(**config_data)
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    def export_config(self, preset_name: str, output_file: Path):
        """Export a preset configuration to a file."""
        config = self.get_config(preset_name)
        
        with open(output_file, 'w') as f:
            yaml.dump(config.dict(), f, default_flow_style=False, sort_keys=False)
    
    def get_adaptive_config(self, 
                            scanner_name: str, 
                            point_count: int, 
                            has_intensity: bool = False) -> ProcessingConfig:
        """
        Generate adaptive configuration based on scan characteristics.
        
        Args:
            scanner_name: Scanner model name
            point_count: Number of points in the scan
            has_intensity: Whether scan includes intensity data
            
        Returns:
            Optimized ProcessingConfig
        """
        # Basic noise estimation based on common scanners
        noise_map = {
            'leica': 0.002,  # 2mm
            'faro': 0.003,   # 3mm
            'riegl': 0.005,  # 5mm
            'trimble': 0.004  # 4mm
        }
        
        typical_noise = 0.005  # Default 5mm
        for scanner_type, noise in noise_map.items():
            if scanner_type.lower() in scanner_name.lower():
                typical_noise = noise
                break
        
        # Adaptive voxel size based on point density
        if point_count > 50_000_000:  # > 50M points
            voxel_size = typical_noise * 8
        elif point_count > 10_000_000:  # > 10M points  
            voxel_size = typical_noise * 5
        elif point_count > 1_000_000:   # > 1M points
            voxel_size = typical_noise * 3
        else:
            voxel_size = typical_noise * 2
        
        config_data = {
            'scanner': {
                'name': scanner_name,
                'typical_noise': typical_noise
            },
            'cleaning': {
                'statistical_outlier': {
                    'neighbors': 20 if point_count > 10_000_000 else 30,
                    'std_ratio': 1.5
                },
                'radius_outlier': {
                    'radius': typical_noise * 20,
                    'min_neighbors': 8 if point_count > 10_000_000 else 10
                }
            },
            'thinning': {
                'method': 'voxel',
                'voxel_size': voxel_size,
                'preserve_boundaries': True
            },
            'reflection': {
                'intensity_available': has_intensity,
                'intensity_threshold': 0.95,
                'glass_detection': has_intensity,
                'clustering_epsilon': typical_noise * 10
            }
        }
        
        return ProcessingConfig(**config_data)