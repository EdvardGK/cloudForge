import time
import functools
from typing import Dict, Any, Callable
from tqdm import tqdm

# Global usage tracking
_usage_stats: Dict[str, Dict[str, Any]] = {}

def track_usage(operation_name: str):
    """
    Decorator to track usage statistics for CloudForge operations.
    
    Args:
        operation_name: Unique identifier for the operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                # Record usage statistics
                if operation_name not in _usage_stats:
                    _usage_stats[operation_name] = {
                        'call_count': 0,
                        'total_time': 0.0,
                        'avg_time': 0.0,
                        'success_count': 0,
                        'error_count': 0,
                        'last_called': None,
                        'errors': []
                    }
                
                stats = _usage_stats[operation_name]
                stats['call_count'] += 1
                stats['total_time'] += duration
                stats['avg_time'] = stats['total_time'] / stats['call_count']
                stats['last_called'] = time.time()
                
                if success:
                    stats['success_count'] += 1
                else:
                    stats['error_count'] += 1
                    stats['errors'].append({
                        'error': error,
                        'timestamp': time.time(),
                        'args': str(args)[:100],  # Truncate long args
                        'kwargs': str(kwargs)[:100]
                    })
                    # Keep only last 10 errors
                    if len(stats['errors']) > 10:
                        stats['errors'] = stats['errors'][-10:]
            
            return result
        return wrapper
    return decorator

class ProgressTracker:
    """
    Enhanced progress tracking with context management and nested progress bars.
    """
    
    def __init__(self, description: str = "Processing", total: int = 100):
        self.description = description
        self.total = total
        self.current = 0
        self.start_time = None
        self.pbar = None
        self.context_stack = []
    
    def __enter__(self):
        self.start_time = time.time()
        self.pbar = tqdm(
            total=self.total,
            desc=self.description,
            unit=" points" if "point" in self.description.lower() else " items",
            ncols=80
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pbar:
            self.pbar.close()
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        if exc_type is None:
            print(f"✓ {self.description} completed in {elapsed:.2f}s")
        else:
            print(f"✗ {self.description} failed after {elapsed:.2f}s")
    
    def update(self, amount: int = 1, description: str = None):
        """Update progress by specified amount."""
        if self.pbar:
            self.pbar.update(amount)
            if description:
                self.pbar.set_description(description)
        self.current += amount
    
    def set_progress(self, current: int, description: str = None):
        """Set absolute progress value."""
        if self.pbar:
            delta = current - self.current
            self.pbar.update(delta)
            if description:
                self.pbar.set_description(description)
        self.current = current
    
    def push_context(self, description: str, total: int = 100):
        """Push a new progress context (for nested operations)."""
        self.context_stack.append({
            'description': self.description,
            'total': self.total,
            'current': self.current,
            'pbar': self.pbar
        })
        
        # Create new progress bar for nested operation
        self.description = description
        self.total = total
        self.current = 0
        if self.pbar:
            self.pbar.close()
        self.pbar = tqdm(
            total=total,
            desc=description,
            unit=" items",
            ncols=80,
            leave=False
        )
    
    def pop_context(self):
        """Return to previous progress context."""
        if not self.context_stack:
            return
        
        # Close current nested progress bar
        if self.pbar:
            self.pbar.close()
        
        # Restore previous context
        context = self.context_stack.pop()
        self.description = context['description']
        self.total = context['total']
        self.current = context['current']
        self.pbar = context['pbar']

def get_usage_stats() -> Dict[str, Dict[str, Any]]:
    """Get all recorded usage statistics."""
    return _usage_stats.copy()

def print_usage_report():
    """Print a formatted report of all usage statistics."""
    if not _usage_stats:
        print("No usage statistics recorded yet.")
        return
    
    print("\n🔍 CloudForge Usage Statistics")
    print("=" * 50)
    
    for operation, stats in _usage_stats.items():
        success_rate = (stats['success_count'] / stats['call_count']) * 100
        
        print(f"\n📊 {operation}")
        print(f"   Calls: {stats['call_count']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Avg Time: {stats['avg_time']:.3f}s")
        print(f"   Total Time: {stats['total_time']:.3f}s")
        
        if stats['error_count'] > 0:
            print(f"   Recent Errors: {len(stats['errors'])}")
            for error in stats['errors'][-3:]:  # Show last 3 errors
                print(f"     - {error['error'][:60]}...")

def reset_usage_stats():
    """Clear all usage statistics."""
    global _usage_stats
    _usage_stats.clear()

# Convenience functions for common operations
def create_progress_bar(description: str, total: int) -> ProgressTracker:
    """Create a new progress tracker."""
    return ProgressTracker(description, total)

def track_point_cloud_operation(operation_name: str, point_count: int):
    """Create progress tracker specifically for point cloud operations."""
    return ProgressTracker(f"{operation_name} ({point_count:,} points)", point_count)