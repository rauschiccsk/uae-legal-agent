"""
Generate project_file_access.json manifest for GitHub file access.
This script scans the project directory and creates a structured manifest
with direct GitHub URLs for easy file access.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# GitHub repository configuration
GITHUB_REPO = "yourusername/uae-legal-agent"  # Update with actual repo
BRANCH = "main"
BASE_URL = f"https://github.com/{GITHUB_REPO}/blob/{BRANCH}"

# Categories to scan
CATEGORIES = {
    "root_modules": {
        "description": "Root-level Python modules",
        "directories": ["."],
        "extensions": [".py"],
        "recursive": False,
        "include_patterns": ["config", "main"]
    },
    "python_sources": {
        "description": "Python source files",
        "directories": ["utils", "scripts"],
        "extensions": [".py"],
        "recursive": True
    },
    "tests": {
        "description": "Test files",
        "directories": ["tests"],
        "extensions": [".py"],
        "recursive": True
    },
    "documentation": {
        "description": "Documentation files",
        "directories": ["docs"],
        "extensions": [".md", ".txt", ".rst"],
        "recursive": True
    },
    "templates": {
        "description": "Template files",
        "directories": ["docs/templates"],
        "extensions": [".yaml", ".yml", ".md"],
        "recursive": True
    },
    "configuration": {
        "description": "Configuration files",
        "directories": ["."],
        "extensions": [".yaml", ".yml", ".json", ".toml", ".ini"],
        "recursive": False
    }
}


def scan_directory(base_path: Path, category_config: Dict) -> List[Dict[str, str]]:
    """Scan directory for files matching category configuration."""
    files = []
    
    for directory in category_config["directories"]:
        dir_path = base_path / directory
        if not dir_path.exists():
            continue
            
        extensions = tuple(category_config["extensions"])
        recursive = category_config.get("recursive", True)
        include_patterns = category_config.get("include_patterns", [])
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
            
        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and file_path.suffix in extensions:
                # Check include patterns if specified
                if include_patterns:
                    if not any(pattern in file_path.stem for pattern in include_patterns):
                        continue
                
                rel_path = file_path.relative_to(base_path)
                files.append({
                    "name": file_path.name,
                    "path": str(rel_path).replace("\\", "/"),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat()
                })
    
    return sorted(files, key=lambda x: x["path"])


def generate_manifest(project_root: Path) -> Dict[str, Any]:
    """Generate complete project manifest."""
    version_param = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    manifest = {
        "generated": datetime.now().isoformat(),
        "project": "uae-legal-agent",
        "repository": GITHUB_REPO,
        "branch": BRANCH,
        "cache_version": version_param,
        "categories": {},
        "quick_access": {
            "core_modules": [
                {
                    "name": "config.py",
                    "description": "Configuration management",
                    "url": f"{BASE_URL}/config.py?v={version_param}"
                },
                {
                    "name": "utils/claude_client.py",
                    "description": "Claude API client",
                    "url": f"{BASE_URL}/utils/claude_client.py?v={version_param}"
                },
                {
                    "name": "utils/vector_db.py",
                    "description": "Vector database management",
                    "url": f"{BASE_URL}/utils/vector_db.py?v={version_param}"
                },
                {
                    "name": "utils/pdf_processor.py",
                    "description": "PDF processing utilities",
                    "url": f"{BASE_URL}/utils/pdf_processor.py?v={version_param}"
                }
            ],
            "key_documentation": [
                {
                    "name": "MASTER_CONTEXT.md",
                    "description": "Complete project context",
                    "url": f"{BASE_URL}/docs/MASTER_CONTEXT.md?v={version_param}"
                },
                {
                    "name": "README.md",
                    "description": "Project overview",
                    "url": f"{BASE_URL}/README.md?v={version_param}"
                }
            ]
        },
        "statistics": {}
    }
    
    # Scan each category
    total_files = 0
    for category_name, category_config in CATEGORIES.items():
        files = scan_directory(project_root, category_config)
        
        manifest["categories"][category_name] = {
            "description": category_config["description"],
            "count": len(files),
            "files": [
                {
                    **file_info,
                    "url": f"{BASE_URL}/{file_info['path']}?v={version_param}"
                }
                for file_info in files
            ]
        }
        
        total_files += len(files)
    
    # Add statistics
    manifest["statistics"] = {
        "total_files": total_files,
        "total_categories": len(CATEGORIES),
        "files_by_category": {
            cat: manifest["categories"][cat]["count"]
            for cat in manifest["categories"]
        }
    }
    
    return manifest


def main():
    """Main entry point."""
    project_root = Path(__file__).parent
    output_file = project_root / "project_file_access.json"
    
    print("Generating project file access manifest...")
    print(f"Project root: {project_root}")
    print(f"Output file: {output_file}")
    print()
    
    manifest = generate_manifest(project_root)
    
    # Write manifest
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print("✓ Manifest generated successfully!")
    print(f"  Total files: {manifest['statistics']['total_files']}")
    print(f"  Categories: {manifest['statistics']['total_categories']}")
    print()
    print("Files by category:")
    for cat, count in manifest['statistics']['files_by_category'].items():
        print(f"  {cat}: {count}")
    print()
    print(f"Cache version: {manifest['cache_version']}")


if __name__ == "__main__":
    main()