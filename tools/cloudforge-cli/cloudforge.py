#!/usr/bin/env python3
"""
CloudForge CLI - Scan-to-BIM Point Cloud Processing Toolkit
Main command-line interface for point cloud processing operations.
"""

import click
from pathlib import Path
import sys
import os

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.core.io.multi_format_loader import PointCloudLoader
from components.core.io.export_manager import PointCloudExporter
from components.core.config.config_manager import ConfigManager
from components.core.utils.progress_tracker import (
    ProgressTracker, print_usage_report, reset_usage_stats
)

@click.group()
@click.version_option(version='0.1.0', prog_name='CloudForge')
@click.option('--config-dir', type=click.Path(), help='Configuration directory path')
@click.pass_context
def cli(ctx, config_dir):
    """
    CloudForge - Scan-to-BIM Point Cloud Processing Toolkit
    
    Process, clean, and extract BIM elements from point clouds.
    """
    ctx.ensure_object(dict)
    
    # Initialize global configuration manager
    if config_dir:
        config_dir = Path(config_dir)
    else:
        config_dir = project_root / "config"
    
    ctx.obj['config_manager'] = ConfigManager(config_dir)
    ctx.obj['loader'] = PointCloudLoader()
    ctx.obj['exporter'] = PointCloudExporter()

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--preset', default='leica_rtc360', help='Scanner preset to use')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', 'output_format', default='ply', help='Output format (ply, pcd, pts, xyz)')
@click.option('--skip-cleaning', is_flag=True, help='Skip cleaning operations')
@click.option('--skip-thinning', is_flag=True, help='Skip thinning operations')
@click.pass_context
def process(ctx, input_file, preset, output, output_format, skip_cleaning, skip_thinning):
    """
    Process a point cloud file with cleaning and thinning operations.
    
    INPUT_FILE: Path to the input point cloud file
    """
    config_manager = ctx.obj['config_manager']
    loader = ctx.obj['loader']
    exporter = ctx.obj['exporter']
    
    input_path = Path(input_file)
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_processed.{output_format}"
    
    try:
        # Load configuration
        click.echo(f"Loading preset: {preset}")
        config = config_manager.load_preset(preset)
        
        # Load point cloud
        click.echo(f"Loading point cloud: {input_path}")
        with ProgressTracker("Loading point cloud") as progress:
            pcd = loader.load(input_path)
            progress.update(100)
        
        load_info = loader.get_load_info()
        click.echo(f"Loaded {load_info['points']:,} points from {load_info['format']} file")
        
        if load_info.get('has_colors'):
            click.echo("✓ Point cloud includes color information")
        if load_info.get('has_intensity'):
            click.echo("✓ Point cloud includes intensity information")
        
        # Processing pipeline
        if not skip_cleaning:
            click.echo("Cleaning point cloud...")
            # TODO: Implement cleaning operations
            click.echo("⚠ Cleaning operations not yet implemented")
        
        if not skip_thinning:
            click.echo("Thinning point cloud...")
            # TODO: Implement thinning operations  
            click.echo("⚠ Thinning operations not yet implemented")
        
        # Export result
        click.echo(f"Exporting to: {output_path}")
        with ProgressTracker("Exporting point cloud") as progress:
            success = exporter.export(pcd, output_path)
            progress.update(100)
        
        if success:
            export_stats = exporter.get_export_stats()
            click.echo(f"✓ Export completed: {export_stats['points_exported']:,} points")
            click.echo(f"  File size: {export_stats['file_size_mb']:.1f} MB")
        else:
            click.echo("✗ Export failed")
            return 1
            
    except Exception as e:
        click.echo(f"✗ Processing failed: {e}", err=True)
        return 1

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--elements', default='walls,floors', help='BIM elements to extract (comma-separated)')
@click.option('--format', 'output_format', default='ifc', help='Output format (ifc, json)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def extract_bim(ctx, input_file, elements, output_format, output):
    """
    Extract BIM elements from a point cloud.
    
    INPUT_FILE: Path to the input point cloud file
    """
    click.echo("⚠ BIM extraction not yet implemented")
    click.echo(f"Would extract: {elements} from {input_file}")
    # TODO: Implement BIM extraction

@cli.command()
@click.argument('scan1', type=click.Path(exists=True))
@click.argument('scan2', type=click.Path(exists=True))
@click.option('--report', type=click.Path(), help='Output HTML report path')
@click.option('--threshold', default=0.05, help='Alignment threshold in meters')
@click.pass_context
def validate(ctx, scan1, scan2, report, threshold):
    """
    Validate alignment between two point cloud scans.
    
    SCAN1: Path to the first scan
    SCAN2: Path to the second scan
    """
    click.echo("⚠ Alignment validation not yet implemented")
    click.echo(f"Would validate alignment between {scan1} and {scan2}")
    # TODO: Implement alignment validation

@cli.command()
@click.pass_context
def list_presets(ctx):
    """List all available scanner presets."""
    config_manager = ctx.obj['config_manager']
    presets = config_manager.list_presets()
    
    if not presets:
        click.echo("No presets found.")
        return
    
    click.echo("Available scanner presets:")
    for preset in sorted(presets):
        try:
            config = config_manager.load_preset(preset)
            scanner_name = config.scanner.name
            noise = config.scanner.typical_noise * 1000  # Convert to mm
            click.echo(f"  {preset:20} - {scanner_name} ({noise:.1f}mm noise)")
        except Exception as e:
            click.echo(f"  {preset:20} - ⚠ Invalid preset: {e}")

@cli.command()
@click.option('--name', required=True, help='Name for the new preset')
@click.option('--scanner', required=True, help='Scanner model name')
@click.option('--noise', type=float, required=True, help='Typical noise in millimeters')
@click.option('--based-on', default='default', help='Template to base preset on')
@click.pass_context
def create_preset(ctx, name, scanner, noise, based_on):
    """Create a new scanner preset."""
    config_manager = ctx.obj['config_manager']
    
    try:
        noise_meters = noise / 1000.0  # Convert mm to meters
        config = config_manager.create_preset_from_template(
            name, scanner, noise_meters, based_on
        )
        click.echo(f"✓ Created preset '{name}' for {scanner}")
        click.echo(f"  Noise level: {noise}mm")
        click.echo(f"  Voxel size: {config.thinning.voxel_size*1000:.1f}mm")
    except Exception as e:
        click.echo(f"✗ Failed to create preset: {e}", err=True)
        return 1

@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
def validate_config(ctx, config_file):
    """Validate a configuration file."""
    config_manager = ctx.obj['config_manager']
    
    if config_manager.validate_config_file(Path(config_file)):
        click.echo(f"✓ Configuration file {config_file} is valid")
    else:
        click.echo(f"✗ Configuration file {config_file} is invalid", err=True)
        return 1

@cli.command()
def stats():
    """Show usage statistics."""
    print_usage_report()

@cli.command()
def reset_stats():
    """Reset usage statistics."""
    reset_usage_stats()
    click.echo("✓ Usage statistics reset")

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def info(input_file):
    """Get information about a point cloud file."""
    loader = PointCloudLoader()
    
    try:
        click.echo(f"Analyzing: {input_file}")
        pcd = loader.load(Path(input_file))
        info = loader.get_load_info()
        
        click.echo(f"\n📊 Point Cloud Information:")
        click.echo(f"  Format: {info['format']}")
        click.echo(f"  Points: {info['points']:,}")
        
        if info.get('has_colors'):
            click.echo(f"  Colors: ✓")
        if info.get('has_normals'):
            click.echo(f"  Normals: ✓")
        if info.get('has_intensity'):
            click.echo(f"  Intensity: ✓")
        
        # Basic statistics
        import numpy as np
        points = np.asarray(pcd.points)
        bounds = {
            'min': points.min(axis=0),
            'max': points.max(axis=0),
            'size': points.max(axis=0) - points.min(axis=0)
        }
        
        click.echo(f"\n📐 Bounding Box:")
        click.echo(f"  X: {bounds['min'][0]:.3f} to {bounds['max'][0]:.3f} ({bounds['size'][0]:.3f}m)")
        click.echo(f"  Y: {bounds['min'][1]:.3f} to {bounds['max'][1]:.3f} ({bounds['size'][1]:.3f}m)")
        click.echo(f"  Z: {bounds['min'][2]:.3f} to {bounds['max'][2]:.3f} ({bounds['size'][2]:.3f}m)")
        
    except Exception as e:
        click.echo(f"✗ Failed to analyze file: {e}", err=True)
        return 1

if __name__ == '__main__':
    cli()