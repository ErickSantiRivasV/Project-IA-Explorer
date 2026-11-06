
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import PurePosixPath
from core.scanner import scan_project
from core.selection import FileSelection
from core.analyzer import analyze_project
from core.content_reader import read_selected_content
from core.context_builder import build_project_context
from core.exporter import create_export_package


class ProjectAIExporter:

    def __init__(self, root):
        self.root = root
        self.root.title("Project AI Exporter")
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)

        self.project_data = None
        self.selection = None
        self.node_paths = {}
        self.node_labels = {}

        self.create_interface()

    def create_interface(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        title = ttk.Label(
            main_frame,
            text="Project AI Exporter",
            font=("Arial", 20, "bold")
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            main_frame,
            text="Analiza y prepara proyectos de programación."
        )
        subtitle.pack(anchor="w", pady=(2, 15))

        selection_frame = ttk.LabelFrame(
            main_frame,
            text="Seleccionar proyecto",
            padding=10
        )
        selection_frame.pack(fill="x", pady=(0, 15))

        self.path_label = ttk.Label(
            selection_frame,
            text="Ninguna carpeta seleccionada",
            anchor="w"
        )
        self.path_label.pack(side="left", fill="x", expand=True)

        select_button = ttk.Button(
            selection_frame,
            text="Seleccionar carpeta",
            command=self.select_project
        )
        select_button.pack(side="right", padx=(10, 0))

        info_frame = ttk.LabelFrame(
            main_frame,
            text="Información del proyecto",
            padding=10
        )
        info_frame.pack(fill="x", pady=(0, 15))

        self.info_label = ttk.Label(
            info_frame,
            text="Selecciona una carpeta para comenzar.",
            justify="left"
        )
        self.info_label.pack(side="left", fill="x", expand=True)

        self.analysis_button = ttk.Button(
            info_frame,
            text="Análisis detallado",
            command=self.show_analysis,
            state="disabled"
        )
        self.analysis_button.pack(side="right", padx=(8, 0))

        self.content_button = ttk.Button(
            info_frame,
            text="Ver contenido",
            command=self.show_contents,
            state="disabled"
        )
        self.content_button.pack(side="right", padx=(8, 0))

        self.context_button = ttk.Button(
            info_frame,
            text="Generar contexto",
            command=self.generate_context,
            state="disabled"
        )
        self.context_button.pack(side="right", padx=(8, 0))

        self.excluded_button = ttk.Button(
            info_frame,
            text="Ver omitidos",
            command=self.show_excluded,
            state="disabled"
        )
        self.excluded_button.pack(side="right")

        files_frame = ttk.LabelFrame(
            main_frame,
            text="Explorador de archivos",
            padding=10
        )
        files_frame.pack(fill="both", expand=True)

        controls_frame = ttk.Frame(files_frame)
        controls_frame.pack(fill="x", pady=(0, 10))

        self.select_all_button = ttk.Button(
            controls_frame,
            text="Seleccionar todo",
            command=self.select_all_files,
            state="disabled"
        )
        self.select_all_button.pack(side="left")

        self.deselect_all_button = ttk.Button(
            controls_frame,
            text="Desmarcar todo",
            command=self.deselect_all_files,
            state="disabled"
        )
        self.deselect_all_button.pack(side="left", padx=(8, 0))

        self.selection_label = ttk.Label(
            controls_frame,
            text="0 archivos seleccionados"
        )
        self.selection_label.pack(side="right")

        columns = ("category", "extension", "size")

        self.file_tree = ttk.Treeview(
            files_frame,
            columns=columns,
            show="tree headings",
            selectmode="browse"
        )

        self.file_tree.heading("#0", text="Archivo o carpeta")
        self.file_tree.heading("category", text="Categoría")
        self.file_tree.heading("extension", text="Extensión")
        self.file_tree.heading("size", text="Tamaño")

        self.file_tree.column("#0", width=450, minwidth=250)
        self.file_tree.column("category", width=180, anchor="center")
        self.file_tree.column("extension", width=100, anchor="center")
        self.file_tree.column("size", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(
            files_frame,
            orient="vertical",
            command=self.file_tree.yview
        )

        self.file_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.file_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.file_tree.bind(
            "<Button-1>",
            self.handle_tree_click
        )

        self.status_label = ttk.Label(
            main_frame,
            text="Esperando selección de proyecto."
        )
        self.status_label.pack(anchor="w", pady=(12, 0))

    def select_project(self):
        selected_path = filedialog.askdirectory(
            title="Seleccionar carpeta del proyecto"
        )

        if not selected_path:
            return

        try:
            self.status_label.config(text="Analizando proyecto...")
            self.root.update_idletasks()

            data = scan_project(selected_path)
            self.project_data = data

            self.selection = FileSelection(
                data["files"],
                data["directories"]
            )

            self.display_project(data)

        except (ValueError, OSError) as error:
            messagebox.showerror(
                "Error al analizar",
                str(error)
            )

            self.status_label.config(
                text="No se pudo analizar el proyecto."
            )

    def display_project(self, data):
        self.path_label.config(
            text=data["project_path"]
        )

        category_text = " | ".join(
            f"{category}: {quantity}"
            for category, quantity in data["categories"].items()
        )

        self.info_label.config(
            text=(
                f"Proyecto: {data['project_name']} | "
                f"Archivos: {data['total_files']} | "
                f"Carpetas: {data['total_directories']} | "
                f"Omitidos: {data['total_excluded']} | "
                f"Tamaño: {self.format_size(data['total_size'])}\n"
                f"Categorías: {category_text or 'Ninguna'}"
            )
        )

        self.file_tree.delete(*self.file_tree.get_children())

        self.node_paths.clear()
        self.node_labels.clear()

        directory_ids = {}

        ordered_directories = sorted(
            data["directories"],
            key=lambda path: (path.count("/"), path.lower())
        )

        for directory in ordered_directories:
            parent_path = PurePosixPath(directory).parent.as_posix()

            if parent_path == ".":
                parent_id = ""
            else:
                parent_id = directory_ids.get(
                    parent_path,
                    ""
                )

            directory_id = f"D:{directory}"
            directory_name = PurePosixPath(directory).name

            self.file_tree.insert(
                parent_id,
                "end",
                iid=directory_id,
                text=f"☑ {directory_name}",
                values=("Carpeta", "", "")
            )

            directory_ids[directory] = directory_id
            self.node_paths[directory_id] = directory
            self.node_labels[directory_id] = directory_name

        for file in data["files"]:
            file_path = file["path"]
            parent_path = PurePosixPath(file_path).parent.as_posix()

            if parent_path == ".":
                parent_id = ""
            else:
                parent_id = directory_ids.get(
                    parent_path,
                    ""
                )

            file_id = f"F:{file_path}"
            file_name = file["name"]

            self.file_tree.insert(
                parent_id,
                "end",
                iid=file_id,
                text=f"☑ {file_name}",
                values=(
                    file["category"],
                    file["extension"] or "Sin extensión",
                    self.format_size(file["size"])
                )
            )

            self.node_paths[file_id] = file_path
            self.node_labels[file_id] = file_name

        self.excluded_button.config(
            state="normal" if data["excluded"] else "disabled"
        )
        self.analysis_button.config(state="normal")
        self.content_button.config(state="normal")
        self.context_button.config(state="normal")

        self.select_all_button.config(state="normal")
        self.deselect_all_button.config(state="normal")

        self.update_selection_display()

        self.status_label.config(
            text=(
                f"Análisis completado. "
                f"{data['total_excluded']} elementos omitidos. "
                f"{len(data['errors'])} errores de lectura."
            )
        )

        if data["errors"]:
            messagebox.showwarning(
                "Advertencia",
                f"Se encontraron {len(data['errors'])} errores. "
                "Algunos archivos o carpetas podrían no haberse leído."
            )

    def handle_tree_click(self, event):
        item_id = self.file_tree.identify_row(event.y)

        if not item_id:
            return

        element = self.file_tree.identify_element(
            event.x,
            event.y
        )

        if element.endswith("indicator"):
            return

        path = self.node_paths.get(item_id)

        if path is None or self.selection is None:
            return

        self.selection.toggle(path)
        self.update_selection_display()

        return "break"

    def update_selection_display(self):
        if not self.selection:
            return

        for item_id, path in self.node_paths.items():
            state = self.selection.get_state(path)

            symbols = {
                "checked": "☑",
                "unchecked": "☐",
                "partial": "◩"
            }

            symbol = symbols[state]
            label = self.node_labels[item_id]

            self.file_tree.item(
                item_id,
                text=f"{symbol} {label}"
            )

        selected_count = len(
            self.selection.get_selected_files()
        )

        total_count = len(
            self.selection.file_paths
        )

        self.selection_label.config(
            text=(
                f"{selected_count} de "
                f"{total_count} archivos seleccionados"
            )
        )

    def select_all_files(self):
        if not self.selection:
            return

        self.selection.select_all()
        self.update_selection_display()

    def deselect_all_files(self):
        if not self.selection:
            return

        self.selection.deselect_all()
        self.update_selection_display()

    def get_selected_files(self):
        if not self.selection:
            return []

        return self.selection.get_selected_files()


    def show_analysis(self):
        if not self.project_data or not self.selection:
            return

        selected_paths = self.get_selected_files()

        if not selected_paths:
            messagebox.showinfo(
                "Sin archivos seleccionados",
                "Selecciona al menos un archivo para analizar el proyecto."
            )
            return

        try:
            analysis = analyze_project(
                self.project_data,
                selected_paths
            )
        except Exception as error:
            messagebox.showerror(
                "Error de análisis",
                f"No se pudo completar el análisis:\n{error}"
            )
            return

        window = tk.Toplevel(self.root)
        window.title("Análisis del proyecto")
        window.geometry("950x650")
        window.minsize(700, 450)

        notebook = ttk.Notebook(window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        def add_text_tab(title, content):
            frame = ttk.Frame(notebook, padding=8)
            notebook.add(frame, text=title)

            text_frame = ttk.Frame(frame)
            text_frame.pack(fill="both", expand=True)

            text_widget = tk.Text(
                text_frame,
                wrap="none",
                font=("Consolas", 10),
                padx=10,
                pady=10
            )

            vertical = ttk.Scrollbar(
                text_frame,
                orient="vertical",
                command=text_widget.yview
            )

            horizontal = ttk.Scrollbar(
                frame,
                orient="horizontal",
                command=text_widget.xview
            )

            text_widget.configure(
                yscrollcommand=vertical.set,
                xscrollcommand=horizontal.set
            )

            text_widget.pack(side="left", fill="both", expand=True)
            vertical.pack(side="right", fill="y")
            horizontal.pack(fill="x")

            text_widget.insert("1.0", content)
            text_widget.config(state="disabled")

        inventory_lines = [
            f"Archivos seleccionados: {analysis['total_files']}",
            f"Carpetas representadas: {analysis['total_directories']}",
            f"Tamaño total: {self.format_size(analysis['total_size'])}",
            "",
            "ARCHIVOS POR EXTENSIÓN",
            "----------------------"
        ]

        for extension, quantity in analysis["extensions"]:
            inventory_lines.append(f"{extension:<24} {quantity}")

        inventory_lines.extend([
            "",
            "ARCHIVOS POR CATEGORÍA",
            "----------------------"
        ])

        for category, quantity in analysis["categories"]:
            inventory_lines.append(f"{category:<24} {quantity}")

        add_text_tab("Inventario", "\n".join(inventory_lines))
        add_text_tab("Estructura", analysis["structure"])

        technology_labels = {
            "languages": "LENGUAJES",
            "frameworks": "FRAMEWORKS",
            "databases": "BASES DE DATOS",
            "tools": "HERRAMIENTAS"
        }
        technology_lines = []

        for group, label in technology_labels.items():
            technology_lines.extend([label, "-" * len(label)])
            technology_lines.extend(
                f"• {item}" for item in analysis["technology_groups"][group]
            )
            if not analysis["technology_groups"][group]:
                technology_lines.append("No se detectaron elementos.")
            technology_lines.append("")

        add_text_tab("Tecnologías", "\n".join(technology_lines).strip())

        dependency_lines = []

        if analysis["manifests"]:
            dependency_lines.append("ARCHIVOS DE DEPENDENCIAS DETECTADOS")
            dependency_lines.append("----------------------------------")
            dependency_lines.extend(analysis["manifests"])
            dependency_lines.append("")

        dependency_lines.append("DEPENDENCIAS DECLARADAS")
        dependency_lines.append("-----------------------")

        if analysis["dependencies"]:
            for dependency in analysis["dependencies"]:
                version = dependency["version"] or "Versión no especificada"
                dependency_lines.append(
                    f"{dependency['name']} | {version} | {dependency['source']}"
                )
        else:
            dependency_lines.append(
                "No se encontraron dependencias reconocibles."
            )

        add_text_tab("Dependencias", "\n".join(dependency_lines))

        important_lines = [
            "POSIBLES PUNTOS DE ENTRADA",
            "--------------------------"
        ]

        important_lines.extend(
            analysis["entry_points"] or ["No se detectaron puntos de entrada conocidos."]
        )

        important_lines.extend([
            "",
            "ARCHIVOS IMPORTANTES",
            "--------------------"
        ])

        other_important = [path for path in analysis["important_files"] if path not in set(analysis["entry_points"])]
        important_lines.extend(
            other_important or ["No se detectaron otros archivos importantes conocidos."]
        )

        add_text_tab("Archivos importantes", "\n".join(important_lines))

    def show_contents(self):
        if not self.project_data or not self.selection:
            return

        selected_paths = self.get_selected_files()

        if not selected_paths:
            messagebox.showinfo(
                "Sin archivos seleccionados",
                "Selecciona al menos un archivo para extraer su contenido."
            )
            return

        try:
            result = read_selected_content(
                self.project_data,
                selected_paths
            )
        except Exception as error:
            messagebox.showerror(
                "Error de lectura",
                f"No se pudo extraer el contenido:\n{error}"
            )
            return

        window = tk.Toplevel(self.root)
        window.title("Contenido de los archivos")
        window.geometry("1050x680")
        window.minsize(750, 450)

        summary = ttk.Label(
            window,
            text=(
                f"Leídos: {result['read_files']} | "
                f"Omitidos: {result['omitted_files']} | "
                f"Limitados: {result['limited_files']} | "
                f"Errores: {result['error_files']} | "
                f"Líneas: {result['total_lines']} | "
                f"Caracteres: {result['total_characters']}"
            ),
            padding=10
        )
        summary.pack(fill="x")

        body = ttk.Panedwindow(window, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left = ttk.Frame(body, padding=5)
        right = ttk.Frame(body, padding=5)
        body.add(left, weight=1)
        body.add(right, weight=3)

        file_list = tk.Listbox(left, font=("Arial", 10), width=38)
        list_scroll = ttk.Scrollbar(left, orient="vertical", command=file_list.yview)
        file_list.configure(yscrollcommand=list_scroll.set)
        file_list.pack(side="left", fill="both", expand=True)
        list_scroll.pack(side="right", fill="y")

        content_text = tk.Text(
            right,
            wrap="none",
            font=("Consolas", 10),
            padx=10,
            pady=10
        )
        vertical = ttk.Scrollbar(right, orient="vertical", command=content_text.yview)
        horizontal = ttk.Scrollbar(right, orient="horizontal", command=content_text.xview)
        content_text.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        content_text.pack(side="left", fill="both", expand=True)
        vertical.pack(side="right", fill="y")
        horizontal.pack(side="bottom", fill="x")

        documents = result["documents"]
        for document in documents:
            status_labels = {
                "ok": "Leído",
                "omitted": "Omitido",
                "limited": "Límite",
                "error": "Error"
            }
            file_list.insert(
                "end",
                f"[{status_labels[document['status']]}] {document['path']}"
            )

        def display_document(event=None):
            selection = file_list.curselection()
            if not selection:
                return

            document = documents[selection[0]]
            content_text.config(state="normal")
            content_text.delete("1.0", "end")

            if document["status"] == "ok":
                header = (
                    f"Ruta: {document['path']}\n"
                    f"Codificación: {document['encoding']} | "
                    f"Líneas: {document['lines']} | "
                    f"Caracteres: {document['characters']}\n"
                    f"{'-' * 72}\n\n"
                )
                content_text.insert("1.0", header + document["content"])
            else:
                content_text.insert(
                    "1.0",
                    f"Ruta: {document['path']}\n\n{document['message']}"
                )

            content_text.config(state="disabled")

        file_list.bind("<<ListboxSelect>>", display_document)
        if documents:
            file_list.selection_set(0)
            display_document()


    def generate_context(self):
        if not self.project_data or not self.selection:
            return

        selected_paths = self.get_selected_files()
        if not selected_paths:
            messagebox.showinfo(
                "Sin archivos seleccionados",
                "Selecciona al menos un archivo para generar el contexto."
            )
            return

        try:
            self.status_label.config(text="Generando contexto del proyecto...")
            self.root.update_idletasks()
            analysis = analyze_project(self.project_data, selected_paths)
            content_result = read_selected_content(self.project_data, selected_paths)
            context_text = build_project_context(
                self.project_data,
                analysis,
                content_result
            )
        except Exception as error:
            messagebox.showerror(
                "Error al generar contexto",
                f"No se pudo generar el contexto:\n{error}"
            )
            self.status_label.config(text="No se pudo generar el contexto.")
            return

        window = tk.Toplevel(self.root)
        window.title("Contexto completo del proyecto")
        window.geometry("1050x700")
        window.minsize(750, 450)

        summary = ttk.Label(
            window,
            text=(
                f"Archivos seleccionados: {analysis['total_files']} | "
                f"Contenido incluido: {content_result['read_files']} | "
                f"Omitidos: {content_result['omitted_files']} | "
                f"Limitados: {content_result['limited_files']} | "
                f"Errores: {content_result['error_files']} | "
                f"Caracteres generados: {len(context_text):,}"
            ),
            padding=10
        )
        summary.pack(fill="x")

        text_frame = ttk.Frame(window, padding=(10, 0, 10, 10))
        text_frame.pack(fill="both", expand=True)

        context_widget = tk.Text(
            text_frame,
            wrap="none",
            font=("Consolas", 10),
            padx=10,
            pady=10
        )
        vertical = ttk.Scrollbar(text_frame, orient="vertical", command=context_widget.yview)
        horizontal = ttk.Scrollbar(window, orient="horizontal", command=context_widget.xview)
        context_widget.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )
        context_widget.pack(side="left", fill="both", expand=True)
        vertical.pack(side="right", fill="y")
        horizontal.pack(fill="x", padx=10)
        context_widget.insert("1.0", context_text)

        buttons = ttk.Frame(window, padding=10)
        buttons.pack(fill="x")

        def copy_context():
            self.root.clipboard_clear()
            self.root.clipboard_append(context_text)
            self.root.update()
            messagebox.showinfo(
                "Contexto copiado",
                "El contexto completo se copió al portapapeles."
            )

        def save_context():
            destination = filedialog.asksaveasfilename(
                title="Guardar contexto del proyecto",
                defaultextension=".md",
                initialfile=f"{self.project_data['project_name']}_contexto.md",
                filetypes=[("Documento Markdown", "*.md"), ("Archivo de texto", "*.txt")]
            )
            if not destination:
                return
            try:
                with open(destination, "w", encoding="utf-8") as output:
                    output.write(context_text)
                messagebox.showinfo(
                    "Contexto guardado",
                    f"El contexto se guardó correctamente en:\n{destination}"
                )
            except OSError as error:
                messagebox.showerror("Error al guardar", str(error))

        include_originals = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            buttons,
            text="Incluir archivos originales seleccionados",
            variable=include_originals
        ).pack(side="left", padx=(0, 12))

        def export_zip():
            destination = filedialog.asksaveasfilename(
                title="Exportar paquete del proyecto",
                defaultextension=".zip",
                initialfile=f"{self.project_data['project_name']}_contexto.zip",
                filetypes=[("Paquete ZIP", "*.zip")]
            )
            if not destination:
                return

            try:
                result = create_export_package(
                    self.project_data,
                    selected_paths,
                    context_text,
                    destination,
                    include_originals.get()
                )
                messagebox.showinfo(
                    "Paquete exportado",
                    "El paquete se creó correctamente.\n\n"
                    f"Archivos originales incluidos: {len(result['included_files'])}\n"
                    f"Ubicación: {result['destination']}"
                )
                self.status_label.config(text="Paquete ZIP exportado correctamente.")
            except (OSError, ValueError) as error:
                messagebox.showerror("Error al exportar", str(error))

        ttk.Button(buttons, text="Copiar contexto", command=copy_context).pack(side="left")
        ttk.Button(buttons, text="Guardar como .md", command=save_context).pack(side="left", padx=8)
        ttk.Button(buttons, text="Exportar ZIP", command=export_zip).pack(side="left")
        ttk.Button(buttons, text="Cerrar", command=window.destroy).pack(side="right")
        context_widget.config(state="disabled")
        self.status_label.config(text="Contexto del proyecto generado correctamente.")

    def show_excluded(self):
        if not self.project_data or not self.project_data["excluded"]:
            return

        window = tk.Toplevel(self.root)
        window.title("Elementos omitidos")
        window.geometry("850x400")
        window.minsize(600, 300)

        frame = ttk.Frame(window, padding=10)
        frame.pack(fill="both", expand=True)

        columns = ("type", "path", "reason")

        table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        table.heading("type", text="Tipo")
        table.heading("path", text="Ruta")
        table.heading("reason", text="Motivo")

        table.column("type", width=90, anchor="center")
        table.column("path", width=350)
        table.column("reason", width=350)

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=table.yview
        )

        table.configure(
            yscrollcommand=scrollbar.set
        )

        table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for item in self.project_data["excluded"]:
            table.insert(
                "",
                "end",
                values=(
                    item["type"],
                    item["path"],
                    item["reason"]
                )
            )

    @staticmethod
    def format_size(size):
        units = ["B", "KB", "MB", "GB", "TB"]

        for unit in units:
            if size < 1024 or unit == "TB":
                return f"{size:.2f} {unit}"
            size /= 1024


if __name__ == "__main__":
    window = tk.Tk()
    app = ProjectAIExporter(window)
    window.mainloop()
