from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

class ExistingFileStorage(FileSystemStorage):
    """
    Custom storage class that doesn't copy files but just points to existing ones.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize with the project's MEDIA_ROOT
        """
        super().__init__(*args, **kwargs)
        self.location = settings.MEDIA_ROOT
    
    def _save(self, name, content):
        """
        Don't save the file - just return the name as is.
        This avoids copying files that already exist in the media directory.
        """
        return name
    
    def get_available_name(self, name, max_length=None):
        """
        Return the name as is without checking for collisions.
        """
        return name
        
    def path(self, name):
        """
        Return the absolute path to the file.
        If the path is already absolute, return it as is.
        """
        if os.path.isabs(name):
            return name
        return super().path(name)
