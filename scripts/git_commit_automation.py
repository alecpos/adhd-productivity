#!/usr/bin/env python3
"""
Script to automate Git commits for the ADHD Calendar Backend project.

This script helps maintain accurate development timelines when uploading the project
to GitHub by creating commits based on file modification dates.
"""

import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import logging
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FileTimestamp:
    """Data class to store file timestamp information."""
    path: str
    mtime: float
    ctime: float
    size: int

def get_file_timestamps(file_path: str) -> Optional[FileTimestamp]:
    """Get modification and creation timestamps for a file."""
    try:
        stat = os.stat(file_path)
        return FileTimestamp(
            path=file_path,
            mtime=stat.st_mtime,
            ctime=stat.st_ctime,
            size=stat.st_size
        )
    except OSError as e:
        logger.error(f"Error getting timestamps for {file_path}: {e}")
        return None

def get_git_tracked_files() -> List[str]:
    """Get list of files that Git would track (not ignored)."""
    try:
        # First, get all files that Git would track
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True,
            text=True,
            check=True
        )
        tracked_files = result.stdout.splitlines()
        
        # Then get untracked files that aren't ignored
        result = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            capture_output=True,
            text=True,
            check=True
        )
        untracked_files = result.stdout.splitlines()
        
        # Filter out certain file types and directories we don't want to track
        excluded_patterns = [
            '__pycache__',
            '.pyc',
            '.env',
            'venv/',
            '.DS_Store',
            '.idea/',
            '.vscode/',
            'logs/',
            'trained_models/',
            'data/raw/',
            'data/processed/'
        ]
        
        def should_include(file: str) -> bool:
            return not any(pattern in file for pattern in excluded_patterns)
        
        return [f for f in (tracked_files + untracked_files) if should_include(f)]
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting Git tracked files: {e}")
        return []

def group_files_by_date(files: List[FileTimestamp]) -> Dict[str, List[FileTimestamp]]:
    """Group files by their modification date."""
    date_groups = defaultdict(list)
    for file in files:
        date = datetime.fromtimestamp(file.mtime).strftime('%Y-%m-%d')
        date_groups[date].append(file)
    return dict(date_groups)

def create_commit_for_date(
    date: str,
    files: List[FileTimestamp],
    commit_message: Optional[str] = None
) -> bool:
    """Create a Git commit for files modified on a specific date."""
    try:
        # Set the commit date
        commit_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d 12:00:00')
        env = os.environ.copy()
        env['GIT_AUTHOR_DATE'] = commit_date
        env['GIT_COMMITTER_DATE'] = commit_date

        # Add files to staging
        for file in files:
            try:
                subprocess.run(['git', 'add', file.path], check=True)
            except subprocess.CalledProcessError as e:
                logger.warning(f"Skipping {file.path}: {e}")
                continue

        # Create commit with a more descriptive message for the ADHD Calendar project
        if not commit_message:
            # Count files by type/directory for a more informative commit message
            dirs = defaultdict(int)
            for file in files:
                top_dir = Path(file.path).parts[0] if Path(file.path).parts else 'root'
                dirs[top_dir] += 1
            
            changes = [f"{count} files in {dir_}" for dir_, count in dirs.items()]
            changes_str = ", ".join(changes)
            commit_message = f"Updates from {date}: {changes_str}"

        subprocess.run(
            ['git', 'commit', '-m', commit_message],
            env=env,
            check=True
        )
        logger.info(f"Created commit for {date} with {len(files)} files")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating commit for {date}: {e}")
        return False

def initialize_git_repo() -> bool:
    """Initialize Git repository if not already initialized."""
    if not os.path.exists('.git'):
        try:
            subprocess.run(['git', 'init'], check=True)
            logger.info("Initialized Git repository")
            
            # Create a default .gitignore file for Python/ML project
            gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
.env
logs/
trained_models/
data/raw/
data/processed/
*.log
"""
            with open('.gitignore', 'w') as f:
                f.write(gitignore_content.strip())
            logger.info("Created .gitignore file")
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error initializing Git repository: {e}")
            return False
    return True

def setup_remote_repo(remote_url: str) -> bool:
    """Set up remote repository."""
    try:
        # Check if remote already exists
        result = subprocess.run(
            ['git', 'remote', '-v'],
            capture_output=True,
            text=True,
            check=True
        )
        if remote_url not in result.stdout:
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
            logger.info(f"Added remote repository: {remote_url}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting up remote repository: {e}")
        return False

def main():
    """Main function to handle Git commit automation."""
    parser = argparse.ArgumentParser(
        description='Automate Git commits for ADHD Calendar Backend with timestamp preservation'
    )
    parser.add_argument('--remote-url', help='GitHub repository URL')
    parser.add_argument('--branch', default='main', help='Branch name (default: main)')
    parser.add_argument(
        '--commit-message',
        help='Custom commit message template (use {date} for date placeholder)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be committed without actually committing'
    )
    args = parser.parse_args()

    # Initialize Git repository
    if not initialize_git_repo():
        return

    # Set up remote repository if URL provided
    if args.remote_url and not setup_remote_repo(args.remote_url):
        return

    # Get list of files that Git would track
    tracked_files = get_git_tracked_files()
    if not tracked_files:
        logger.warning("No files found to commit. Make sure you have files that aren't ignored by .gitignore")
        return

    # Get timestamps for tracked files
    files = []
    for file_path in tracked_files:
        timestamp = get_file_timestamps(file_path)
        if timestamp:
            files.append(timestamp)

    if not files:
        logger.warning("No files found with valid timestamps")
        return

    # Group files by date
    date_groups = group_files_by_date(files)

    # Create commits for each date
    success = True
    for date, date_files in sorted(date_groups.items()):
        if args.dry_run:
            logger.info(f"Would commit {len(date_files)} files from {date}")
            continue

        commit_message = args.commit_message.format(date=date) if args.commit_message else None
        if not create_commit_for_date(date, date_files, commit_message):
            success = False
            break

    if success and not args.dry_run:
        logger.info("Successfully created all commits")
        if args.remote_url:
            try:
                subprocess.run(['git', 'push', '-u', 'origin', args.branch], check=True)
                logger.info(f"Successfully pushed to {args.remote_url}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error pushing to remote repository: {e}")
    elif args.dry_run:
        logger.info("Dry run completed - no commits were made")

if __name__ == '__main__':
    main() 