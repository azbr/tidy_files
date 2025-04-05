#!/usr/bin/env python3
import os
import sys
import stat
import time
import json
from datetime import datetime
from pathlib import Path


def get_file_stats(file_path):
    """Get detailed stats for a file or directory."""
    try:
        stats = os.stat(file_path)
        return {
            'path': str(file_path),
            'name': os.path.basename(file_path),
            'size': stats.st_size,
            'created_time': stats.st_ctime,
            'created_date': datetime.fromtimestamp(stats.st_ctime).isoformat(),
            'modified_time': stats.st_mtime,
            'modified_date': datetime.fromtimestamp(stats.st_mtime).isoformat(),
            'access_time': stats.st_atime,
            'access_date': datetime.fromtimestamp(stats.st_atime).isoformat(),
            'is_dir': os.path.isdir(file_path),
            'is_file': os.path.isfile(file_path),
            'is_symlink': os.path.islink(file_path),
            'permissions': oct(stats.st_mode & 0o777),
        }
    except Exception as e:
        return {
            'path': str(file_path),
            'name': os.path.basename(file_path),
            'error': str(e)
        }


def scan_directory(root_dir):
    """Recursively scan a directory and collect file/directory information."""
    file_system = {
        'root': str(root_dir),
        'scan_time': datetime.now().isoformat(),
        'items': {}
    }
    
    # Walk through all directories and files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Get relative path from root
        rel_path = os.path.relpath(dirpath, root_dir)
        if rel_path == '.':
            rel_path = ''
        
        # Create path in our nested dictionary
        current_dict = file_system['items']
        if rel_path:
            parts = rel_path.split(os.sep)
            for part in parts:
                if part not in current_dict:
                    current_dict[part] = {'__stats__': get_file_stats(os.path.join(root_dir, *parts[:parts.index(part)+1])), '__contents__': {}}
                current_dict = current_dict[part]['__contents__']
        
        # Add directory stats
        if not rel_path:
            file_system['items']['__stats__'] = get_file_stats(root_dir)
            file_system['items']['__contents__'] = {}
            current_dict = file_system['items']['__contents__']
        
        # Add files
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            current_dict[filename] = get_file_stats(file_path)
    
    return file_system


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <root_directory>")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    if not os.path.isdir(root_dir):
        print(f"Error: {root_dir} is not a valid directory")
        sys.exit(1)
    
    print(f"Scanning directory: {root_dir}")
    start_time = time.time()
    
    file_system = scan_directory(root_dir)
    
    end_time = time.time()
    print(f"Scan completed in {end_time - start_time:.2f} seconds")
    
    # Output to JSON file
    output_file = f"filesystem_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(file_system, f, indent=2)
    
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()
