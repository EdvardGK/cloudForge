from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
from ..utils.progress_tracker import track_usage

try:
    import open3d as o3d
    HAS_OPEN3D = True
except ImportError:
    HAS_OPEN3D = False

@track_usage("cloudforge.io.exporter")
class PointCloudExporter:
    """
    Unified exporter for multiple point cloud formats.
    Handles format-specific optimizations and metadata preservation.
    """
    
    supported_formats = ['.ply', '.pcd', '.pts', '.xyz']
    
    def __init__(self):
        self.export_stats = {}
    
    def export(self, 
               pcd, 
               filepath: Path, 
               **kwargs) -> bool:
        """
        Export point cloud to specified format.
        
        Args:
            pcd: Open3D PointCloud to export
            filepath: Output file path
            **kwargs: Format-specific options
            
        Returns:
            True if export successful, False otherwise
        """
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()
        
        if suffix not in self.supported_formats:
            raise ValueError(f"Unsupported export format: {suffix}")
        
        # Ensure output directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if suffix in ['.ply', '.pcd']:
                return self._export_open3d_format(pcd, filepath, **kwargs)
            elif suffix == '.pts':
                return self._export_pts_format(pcd, filepath, **kwargs)
            elif suffix == '.xyz':
                return self._export_xyz_format(pcd, filepath, **kwargs)
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def _export_open3d_format(self, 
                              pcd, 
                              filepath: Path, 
                              **kwargs) -> bool:
        """Export using Open3D's built-in writers."""
        
        # PLY-specific options
        if filepath.suffix.lower() == '.ply':
            write_ascii = kwargs.get('ascii', False)
            write_vertex_normals = kwargs.get('write_normals', len(pcd.normals) > 0)
            write_vertex_colors = kwargs.get('write_colors', len(pcd.colors) > 0)
            
            success = o3d.io.write_point_cloud(
                str(filepath), 
                pcd,
                write_ascii=write_ascii,
                write_vertex_normals=write_vertex_normals,
                write_vertex_colors=write_vertex_colors
            )
        else:
            # PCD format
            success = o3d.io.write_point_cloud(str(filepath), pcd)
        
        if success:
            self._record_export_stats(pcd, filepath)
        
        return success
    
    def _export_pts_format(self, 
                           pcd, 
                           filepath: Path, 
                           **kwargs) -> bool:
        """Export to simple PTS text format (X Y Z [R G B])."""
        
        points = np.asarray(pcd.points)
        
        # Build output array
        if len(pcd.colors) > 0:
            colors = np.asarray(pcd.colors)
            # Scale colors to 0-255 range if requested
            if kwargs.get('scale_colors', True):
                colors = (colors * 255).astype(np.uint8)
            data = np.column_stack([points, colors])
            fmt = '%.6f %.6f %.6f %d %d %d'
        else:
            data = points
            fmt = '%.6f %.6f %.6f'
        
        try:
            np.savetxt(filepath, data, fmt=fmt, delimiter=' ')
            self._record_export_stats(pcd, filepath)
            return True
        except Exception:
            return False
    
    def _export_xyz_format(self, 
                           pcd, 
                           filepath: Path, 
                           **kwargs) -> bool:
        """Export to simple XYZ format (coordinates only)."""
        
        points = np.asarray(pcd.points)
        
        try:
            np.savetxt(filepath, points, fmt='%.6f %.6f %.6f', delimiter=' ')
            self._record_export_stats(pcd, filepath)
            return True
        except Exception:
            return False
    
    def _record_export_stats(self, pcd, filepath: Path):
        """Record statistics about the exported point cloud."""
        self.export_stats = {
            'output_file': str(filepath),
            'format': filepath.suffix,
            'points_exported': len(pcd.points),
            'has_colors': len(pcd.colors) > 0,
            'has_normals': len(pcd.normals) > 0,
            'file_size_mb': filepath.stat().st_size / (1024 * 1024) if filepath.exists() else 0
        }
    
    def get_export_stats(self) -> Dict[str, Any]:
        """Get statistics about the last export operation."""
        return self.export_stats.copy()
    
    def batch_export(self, 
                     pcd, 
                     base_path: Path, 
                     formats: list = None) -> Dict[str, bool]:
        """
        Export the same point cloud to multiple formats.
        
        Args:
            pcd: Point cloud to export
            base_path: Base path without extension
            formats: List of formats to export (default: all supported)
            
        Returns:
            Dictionary mapping format to success status
        """
        if formats is None:
            formats = self.supported_formats
        
        results = {}
        base_path = Path(base_path)
        
        for fmt in formats:
            if fmt.startswith('.'):
                ext = fmt
            else:
                ext = f'.{fmt}'
            
            output_path = base_path.with_suffix(ext)
            results[ext] = self.export(pcd, output_path)
        
        return results