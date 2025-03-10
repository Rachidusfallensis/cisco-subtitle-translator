"""File management and cleanup module."""
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self, upload_dir: str, output_dir: str, max_age_hours: int = 24):
        self.upload_dir = upload_dir
        self.output_dir = output_dir
        self.max_age_hours = max_age_hours
        
        # Ensure directories exist
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

    def cleanup_old_files(self) -> Tuple[int, List[str]]:
        """Clean up files older than max_age_hours."""
        cutoff = datetime.now() - timedelta(hours=self.max_age_hours)
        cleaned_files = []
        error_files = []

        for directory in [self.upload_dir, self.output_dir]:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.getctime(file_path) < cutoff.timestamp():
                        os.remove(file_path)
                        cleaned_files.append(filename)
                        logger.info(f"Cleaned up old file: {filename}")
                except Exception as e:
                    error_files.append(filename)
                    logger.error(f"Error cleaning up {filename}: {e}")

        return len(cleaned_files), error_files

    def get_file_info(self, filename: str) -> dict:
        """Get information about a file."""
        file_path = os.path.join(self.upload_dir, filename)
        if not os.path.exists(file_path):
            file_path = os.path.join(self.output_dir, filename)
            if not os.path.exists(file_path):
                return {"error": "File not found"}

        stats = os.stat(file_path)
        return {
            "name": filename,
            "size": stats.st_size,
            "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "age_hours": (datetime.now() - datetime.fromtimestamp(stats.st_ctime)).total_seconds() / 3600
        }

    def is_file_expired(self, filename: str) -> bool:
        """Check if a file has expired."""
        file_info = self.get_file_info(filename)
        if "error" in file_info:
            return True
        return file_info["age_hours"] > self.max_age_hours

    def get_storage_stats(self) -> dict:
        """Get storage statistics."""
        upload_size = sum(os.path.getsize(os.path.join(self.upload_dir, f)) 
                         for f in os.listdir(self.upload_dir))
        output_size = sum(os.path.getsize(os.path.join(self.output_dir, f)) 
                         for f in os.listdir(self.output_dir))
        
        return {
            "upload_dir_size": upload_size,
            "output_dir_size": output_size,
            "total_size": upload_size + output_size,
            "upload_file_count": len(os.listdir(self.upload_dir)),
            "output_file_count": len(os.listdir(self.output_dir))
        } 