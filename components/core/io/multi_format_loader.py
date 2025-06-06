from pathlib import Path
from typing import Optional, Union
import numpy as np
from ..utils.progress_tracker import track_usage

try:
    import open3d as o3d
    HAS_OPEN3D = True
except ImportError:
    HAS_OPEN3D = False
    print("Warning: open3d not available, some functionality will be limited")

try:
    import laspy
    HAS_LASPY = True
except ImportError:
    HAS_LASPY = False
    print("Warning: laspy not available, LAS/LAZ support disabled")

@track_usage("cloudforge.io.loader")
class PointCloudLoader:
    """
    Unified loader for all point cloud formats.
    Auto-detects format and handles edge cases.
    """
    
    supported_formats = ['.ply', '.pcd', '.las', '.laz', '.e57', '.pts']
    
    def __init__(self):
        self.last_loaded_info = {}
    
    def load(self, filepath: Union[str, Path]):
        """
        Load point cloud from file with automatic format detection.
        
        Args:
            filepath: Path to the point cloud file
            
        Returns:
            Point cloud object or None if loading failed
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Point cloud file not found: {filepath}")
        
        suffix = filepath.suffix.lower()
        
        if suffix not in self.supported_formats:
            raise ValueError(f"Unsupported format: {suffix}. Supported: {self.supported_formats}")
        
        try:
            if suffix in ['.ply', '.pcd']:
                return self._load_open3d_format(filepath)
            elif suffix in ['.las', '.laz']:
                return self._load_las_format(filepath)
            elif suffix == '.e57':
                return self._load_e57_format(filepath)
            elif suffix == '.pts':
                return self._load_pts_format(filepath)
        except Exception as e:
            raise RuntimeError(f"Failed to load {filepath}: {str(e)}")
    
    def _load_open3d_format(self, filepath: Path):
        """Load PLY or PCD files using Open3D."""
        pcd = o3d.io.read_point_cloud(str(filepath))
        
        if len(pcd.points) == 0:
            raise ValueError(f"No points found in {filepath}")
        
        self.last_loaded_info = {
            'format': filepath.suffix,
            'points': len(pcd.points),
            'has_colors': len(pcd.colors) > 0,
            'has_normals': len(pcd.normals) > 0
        }
        
        return pcd
    
    def _load_las_format(self, filepath: Path):
        """Load LAS/LAZ files using laspy."""
        las_file = laspy.read(filepath)
        
        # Extract XYZ coordinates
        points = np.vstack([las_file.x, las_file.y, las_file.z]).T
        
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        # Add colors if available (RGB or intensity)
        if hasattr(las_file, 'red') and hasattr(las_file, 'green') and hasattr(las_file, 'blue'):
            colors = np.vstack([las_file.red, las_file.green, las_file.blue]).T / 65535.0
            pcd.colors = o3d.utility.Vector3dVector(colors)
        elif hasattr(las_file, 'intensity'):
            # Convert intensity to grayscale colors
            intensity_norm = las_file.intensity / np.max(las_file.intensity)
            colors = np.column_stack([intensity_norm, intensity_norm, intensity_norm])
            pcd.colors = o3d.utility.Vector3dVector(colors)
        
        self.last_loaded_info = {
            'format': filepath.suffix,
            'points': len(points),
            'has_colors': len(pcd.colors) > 0,
            'has_intensity': hasattr(las_file, 'intensity'),
            'las_version': f"{las_file.header.version_major}.{las_file.header.version_minor}"
        }
        
        return pcd
    
    def _load_e57_format(self, filepath: Path):
        """Load E57 files (placeholder - requires pye57 library)."""
        # Note: E57 support requires additional dependency
        raise NotImplementedError("E57 format support requires pye57 library - implement when needed")
    
    def _load_pts_format(self, filepath: Path):
        """Load simple PTS text files (X Y Z [I] [R G B])."""
        try:
            data = np.loadtxt(filepath)
        except Exception as e:
            raise ValueError(f"Could not parse PTS file: {e}")
        
        if data.shape[1] < 3:
            raise ValueError("PTS file must have at least X, Y, Z columns")
        
        points = data[:, :3]
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        # Handle intensity and/or colors
        if data.shape[1] == 4:  # X Y Z I
            intensity = data[:, 3]
            intensity_norm = intensity / np.max(intensity)
            colors = np.column_stack([intensity_norm, intensity_norm, intensity_norm])
            pcd.colors = o3d.utility.Vector3dVector(colors)
        elif data.shape[1] >= 6:  # X Y Z R G B or X Y Z I R G B
            color_start = 3 if data.shape[1] == 6 else 4
            colors = data[:, color_start:color_start+3]
            # Normalize if values are in 0-255 range
            if np.max(colors) > 1.0:
                colors = colors / 255.0
            pcd.colors = o3d.utility.Vector3dVector(colors)
        
        self.last_loaded_info = {
            'format': filepath.suffix,
            'points': len(points),
            'columns': data.shape[1],
            'has_colors': len(pcd.colors) > 0
        }
        
        return pcd
    
    def get_load_info(self) -> dict:
        """Get information about the last loaded point cloud."""
        return self.last_loaded_info.copy()