"""
Generate unified project_file_access.json manifest
Combines documentation, source code, and configuration
WITH CACHE BUSTING for fresh GitHub content

UAE Legal Agent - AI-powered legal analysis system for UAE law
"""
import os
import json
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_NAME = "uae-legal-agent"
BASE_URL = "https://raw.githubusercontent.com/rauschiccsk/uae-legal-agent/main"
OUTPUT_FILE = "docs/project_file_access.json"

# Categories to scan - FIXED
CATEGORIES = {
    "documentation": {
        "description": "Project documentation and guides",
        "directories": ["docs"],
        "extensions": [".md"],
        "recursive": True,
        "exclude_dirs": []
    },
    "python_sources": {
        "description": "Python source code modules",
        "directories": ["utils", "scripts"],  # FIXED: Added utils
        "extensions": [".py"],
        "recursive": True,
        "exclude_dirs": ["__pycache__", ".pytest_cache"]
    },
    "root_modules": {
        "description": "Root-level Python modules",
        "directories": ["."],
        "extensions": [".py"],
        "recursive": False,
        "exclude_dirs": [],
        "include_patterns": ["config", "main"]  # Only config.py and main.py
    },
    "tests": {
        "description": "Test suite and fixtures",
        "directories": ["tests"],
        "extensions": [".py"],
        "recursive": True,
        "exclude_dirs": ["__pycache__"]
    },
    "configuration": {
        "description": "Configuration files and templates",
        "directories": [".", "config"],
        "extensions": [".txt", ".yaml", ".yml", ".example", ".ini"],
        "recursive": False,
        "exclude_dirs": [],
        "include_patterns": ["requirements", ".env", "pytest"]
    },
    "data_structure": {
        "description": "Data directories structure (UAE laws, cases)",
        "directories": ["data"],
        "extensions": [".md", ".json", ".txt"],
        "recursive": True,
        "exclude_dirs": ["embeddings", "__pycache__", "chroma_db"]
    },
    "templates": {
        "description": "Project templates and standards",
        "directories": ["docs/templates"],
        "extensions": [".yaml", ".yml", ".md", ".txt"],
        "recursive": True,
        "exclude_dirs": []
    },
}


def should_skip(path):
    """Check if path should be skipped"""
    skip_patterns = [
        "__pycache__",
        ".git",
        ".pytest_cache",
        "venv",
        "venv32",
        ".venv",
        "node_modules",
        ".idea",
        ".vscode",
        "*.pyc",
        ".DS_Store",
        "logs",
        ".env",  # Never include actual .env!
        "*.log",
        "*.db",
        "dev_chat_history.db"
    ]

    path_str = str(path)
    for pattern in skip_patterns:
        if pattern in path_str:
            return True
    return False


def matches_include_pattern(file_name, patterns):
    """Check if file name matches any include pattern"""
    if not patterns:
        return True

    for pattern in patterns:
        if pattern in file_name.lower():
            return True
    return False


def scan_category(category_name, config, base_path, version_param):
    """Scan files for a specific category"""
    files = []

    for directory in config["directories"]:
        dir_path = base_path / directory if directory != "." else base_path

        if not dir_path.exists():
            print(f"   ⚠️  Directory not found: {dir_path}")
            continue

        # Scan directory
        if config["recursive"]:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and not should_skip(file_path):
                # Check if in excluded directory
                if any(excl in str(file_path) for excl in config.get("exclude_dirs", [])):
                    continue

                # Check extension
                if file_path.suffix in config["extensions"]:
                    # Check include patterns if specified
                    if "include_patterns" in config:
                        if not matches_include_pattern(file_path.name, config["include_patterns"]):
                            continue

                    relative_path = file_path.relative_to(base_path)
                    clean_path = str(relative_path).replace(os.sep, '/')

                    files.append({
                        "path": clean_path,
                        "raw_url": f"{BASE_URL}/{clean_path}?v={version_param}",
                        "size": file_path.stat().st_size,
                        "extension": file_path.suffix,
                        "name": file_path.name,
                        "category": category_name
                    })

    return files


def print_usage_urls(version_param):
    """Print ready-to-use URLs for next Claude chat"""
    print("\n" + "=" * 70)
    print("📋 COPY THESE URLs FOR NEXT CLAUDE CHAT")
    print("=" * 70)
    print("\n🔗 Paste both URLs at the start of new conversation:\n")
    print(f"{BASE_URL}/docs/INIT_CONTEXT.md")
    print(f"{BASE_URL}/docs/project_file_access.json?v={version_param}")
    print("\n" + "=" * 70)
    print("💡 TIP: Cache parameter (?v=...) ensures fresh content from GitHub")
    print("=" * 70)


def generate_manifest():
    """Generate unified project file access manifest"""
    print("=" * 70)
    print("🛠️  UAE Legal Agent - Project File Access Manifest Generator")
    print("=" * 70)

    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent if script_dir.name == "scripts" else script_dir

    # Generate version parameter for cache busting
    now = datetime.now()
    version_param = now.strftime("%Y%m%d-%H%M%S")

    print(f"\n📁 Project root: {project_root}")
    print(f"🔄 Cache version: {version_param}")

    # Collect all files by category
    all_files = []
    category_stats = {}

    for category_name, category_config in CATEGORIES.items():
        print(f"\n📂 Scanning: {category_name}")
        print(f"   Description: {category_config['description']}")
        print(f"   Directories: {', '.join(category_config['directories'])}")
        print(f"   Extensions: {', '.join(category_config['extensions'])}")

        files = scan_category(category_name, category_config, project_root, version_param)
        all_files.extend(files)
        category_stats[category_name] = len(files)

        print(f"   ✅ Found: {len(files)} files")

    # Sort files by path
    all_files.sort(key=lambda x: x["path"])

    # Create quick access section - FIXED URLs
    quick_access = {
        "context_files": [
            {
                "name": "INIT_CONTEXT.md",
                "description": "Complete project context - load this first",
                "url": f"{BASE_URL}/docs/INIT_CONTEXT.md?v={version_param}"
            },
            {
                "name": "SYSTEM_PROMPT.md",
                "description": "Claude instructions and workflow rules",
                "url": f"{BASE_URL}/docs/SYSTEM_PROMPT.md?v={version_param}"
            },
            {
                "name": "MASTER_CONTEXT.md",
                "description": "Quick reference guide",
                "url": f"{BASE_URL}/docs/MASTER_CONTEXT.md?v={version_param}"
            }
        ],
        "core_modules": [
            {
                "name": "config.py",
                "description": "Project configuration (root)",
                "url": f"{BASE_URL}/config.py?v={version_param}"
            },
            {
                "name": "main.py",
                "description": "CLI entry point (root)",
                "url": f"{BASE_URL}/main.py?v={version_param}"
            },
            {
                "name": "utils/claude_client.py",
                "description": "Claude API wrapper",
                "url": f"{BASE_URL}/utils/claude_client.py?v={version_param}"
            },
            {
                "name": "utils/vector_store.py",
                "description": "Vector database interface",
                "url": f"{BASE_URL}/utils/vector_store.py?v={version_param}"
            }
        ]
    }

    # Create manifest
    manifest = {
        "project_name": PROJECT_NAME,
        "description": "AI-powered legal analysis system for UAE law - Unified file access manifest",
        "repository": "https://github.com/rauschiccsk/uae-legal-agent",
        "generated_at": now.isoformat(),
        "cache_version": version_param,
        "base_url": BASE_URL,
        "quick_access": quick_access,
        "categories": list(CATEGORIES.keys()),
        "category_descriptions": {
            name: config["description"]
            for name, config in CATEGORIES.items()
        },
        "statistics": {
            "total_files": len(all_files),
            "by_category": category_stats,
            "generated_by": "generate_project_access.py"
        },
        "files": all_files,
        "usage_instructions": {
            "step_1": "Load INIT_CONTEXT.md first for complete project overview",
            "step_2": "Load this manifest for access to all project files",
            "step_3": "Access individual files using raw_url with cache version",
            "note": "Always regenerate manifest after pushing changes to get fresh cache version"
        }
    }

    # Write manifest
    output_path = project_root / OUTPUT_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("✅ MANIFEST GENERATED SUCCESSFULLY")
    print("=" * 70)
    print(f"\n📄 Output: {output_path}")
    print(f"📊 Total files: {len(all_files)}")
    print(f"🔄 Cache version: {version_param}")
    print(f"\n📈 Files by category:")
    for category, count in category_stats.items():
        print(f"   • {category}: {count} files")

    # Print ready-to-use URLs
    print_usage_urls(version_param)

    print("\n⚠️  NEXT STEPS:")
    print("   1. Commit updated manifest: git add docs/project_file_access.json")
    print("   2. Push to GitHub: git push")
    print("   3. Use URLs above in next Claude chat (they include fresh cache version)")

    return manifest


if __name__ == "__main__":
    try:
        manifest = generate_manifest()
        print("\n✅ Done! Ready to commit and push.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()