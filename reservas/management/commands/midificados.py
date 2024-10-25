from django.core.management.base import BaseCommand
import os
import time

class Command(BaseCommand):
    help = 'Find and print files modified in the last given number of days in the entire project'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7, help='Number of days to look back')

    def handle(self, *args, **kwargs):
        days = kwargs['days']
        project_path = '/home/tvacation/thatvacation'  # Directorio del proyecto completo
        self.stdout.write(f"Scanning for files modified in the last {days} days in project: {project_path}")
        self.get_modified_files(project_path, days)

    def get_modified_files(self, path, days):
        current_time = time.time()
        cutoff = current_time - (days * 86400)

        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_stat = os.stat(file_path)
                    if file_stat.st_mtime > cutoff:
                        self.stdout.write(f"{file_path} modified at {time.ctime(file_stat.st_mtime)}")
                except FileNotFoundError:
                    # Handle the case where a file might be deleted during the scan
                    continue
