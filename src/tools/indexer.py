import os
from src.core.memory import KnowledgeBase
from src.tools.files import FileReader

class DiskIndexer:
    SUPPORTED_EXTENSIONS = {
        '.txt', '.md', '.markdown', 
        '.py', '.js', '.html', '.css', '.json', '.xml', '.yml', '.yaml', 
        '.c', '.cpp', '.h', '.hpp', '.rs', '.java', '.go', '.sh',
        '.pdf'
    }

    @staticmethod
    def index_directory(path, recursive=True):
        """
        Walks a directory and indexes supported files into the KnowledgeBase.
        Returns a summary string.
        """
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."

        files_indexed = 0
        errors = 0
        path = os.path.abspath(path)

        if os.path.isfile(path):
            # Index single file
            if DiskIndexer._index_file(path):
                return f"Successfully indexed file: {path}"
            return f"Failed or unsupported file: {path}"

        # Directory walk
        for root, dirs, files in os.walk(path):
            if '.git' in dirs:
                dirs.remove('.git') # Skip git directories
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            if 'node_modules' in dirs:
                dirs.remove('node_modules')
            
            for file in files:
                file_path = os.path.join(root, file)
                if DiskIndexer._index_file(file_path):
                    files_indexed += 1
                else:
                    # specialized logging could go here
                    pass
            
            if not recursive:
                break
        
        return f"Indexing complete. Processed {files_indexed} files in '{path}'."

    @staticmethod
    def index_structure(path):
        """
        Recursively scans a directory and indexes only file paths and names.
        Skips hidden files and heavy directories like .git or node_modules.
        """
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."

        path = os.path.abspath(path)
        items_indexed = 0
        
        # We'll group filenames by directory to reduce the number of embedding calls
        for root, dirs, files in os.walk(path):
            # Skip hidden and heavy dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            if not files:
                continue
                
            # Filter out hidden files
            visible_files = [f for f in files if not f.startswith('.')]
            if not visible_files:
                continue
                
            # Create a summary of the directory contents
            structure_summary = f"FILE_STRUCTURE in directory '{root}':\n"
            structure_summary += "\n".join([f"- {f}" for f in visible_files])
            
            KnowledgeBase.auto_index(structure_summary)
            items_indexed += len(visible_files)
            
        return f"Structure indexing complete. Indexed {items_indexed} file names in '{path}'."

    @staticmethod
    def _index_file(file_path):
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in DiskIndexer.SUPPORTED_EXTENSIONS:
            return False
        
        try:
            # FileReader handles PDF and Text
            content = FileReader.read_file(file_path, max_lines=5000) # Increased limit for indexing
            if content.startswith("Read failed"):
                return False
            
            # Remove the "File (...):" header added by FileReader for pure indexing if possible,
            # or keep it as metadata. Keeping it helps context.
            
            KnowledgeBase.auto_index(content)
            return True
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")
            return False
