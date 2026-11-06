
class FileSelection:

    def __init__(self, files, directories):
        self.file_paths = {
            file["path"] for file in files
        }

        self.directories = set(directories)
        self.selected = set(self.file_paths)

    def toggle(self, path):
        if path in self.file_paths:
            if path in self.selected:
                self.selected.remove(path)
            else:
                self.selected.add(path)

            return

        if path in self.directories:
            descendants = {
                file_path
                for file_path in self.file_paths
                if file_path.startswith(path + "/")
            }

            if descendants and descendants.issubset(self.selected):
                self.selected.difference_update(descendants)
            else:
                self.selected.update(descendants)

    def select_all(self):
        self.selected = set(self.file_paths)

    def deselect_all(self):
        self.selected.clear()

    def get_state(self, path):
        if path in self.file_paths:
            return "checked" if path in self.selected else "unchecked"

        descendants = {
            file_path
            for file_path in self.file_paths
            if file_path.startswith(path + "/")
        }

        if not descendants:
            return "unchecked"

        selected_count = len(descendants.intersection(self.selected))

        if selected_count == len(descendants):
            return "checked"

        if selected_count == 0:
            return "unchecked"

        return "partial"

    def get_selected_files(self):
        return sorted(self.selected)
