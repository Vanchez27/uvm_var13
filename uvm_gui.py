import tkinter as tk
from tkinter import ttk, messagebox
import os
from assembler_stage1 import Assembler
from interpreter import VirtualMachine

class UVMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("УВМ - GUI (Этап 6)")
        self.root.geometry("900x600")

        # Верхняя панель (Настройки)
        control_frame = tk.Frame(root, pady=10)
        control_frame.pack(fill=tk.X, padx=10)

        tk.Label(control_frame, text="Диапазон памяти (Start-End):").pack(side=tk.LEFT)

        self.entry_start = tk.Entry(control_frame, width=8)
        self.entry_start.insert(0, "490")
        self.entry_start.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="-").pack(side=tk.LEFT)

        self.entry_end = tk.Entry(control_frame, width=8)
        self.entry_end.insert(0, "610")
        self.entry_end.pack(side=tk.LEFT, padx=5)

        self.btn_run = tk.Button(control_frame, text="Скомпилировать и Запустить",
                                 command=self.run_process, bg="#e1e1e1", relief=tk.RAISED)
        self.btn_run.pack(side=tk.LEFT, padx=20)

        # Основная область
        paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Слева: Редактор
        left_frame = tk.Frame(paned)
        tk.Label(left_frame, text="Редактор кода (.asm)").pack(anchor=tk.W)

        self.text_editor = tk.Text(left_frame, width=50, font=("Consolas", 11), undo=True)
        default_code = (
            "PUSH 12345\nPUSH 0\nSTORE 500\n"
            "PUSH 0\nPOPCNT 500\n"
            "PUSH 0\nSTORE 600"
        )
        self.text_editor.insert("1.0", default_code)

        scroll_txt = tk.Scrollbar(left_frame, command=self.text_editor.yview)
        self.text_editor.config(yscrollcommand=scroll_txt.set)

        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_txt.pack(side=tk.RIGHT, fill=tk.Y)

        paned.add(left_frame)

        # Справа: Таблица памяти
        right_frame = tk.Frame(paned)
        tk.Label(right_frame, text="Просмотр памяти").pack(anchor=tk.W)

        cols = ("addr", "val")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings")
        self.tree.heading("addr", text="Адрес")
        self.tree.heading("val", text="Значение")
        self.tree.column("addr", width=100, anchor=tk.CENTER)
        self.tree.column("val", width=150, anchor=tk.CENTER)

        scroll_tree = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_tree.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_tree.pack(side=tk.RIGHT, fill=tk.Y)

        paned.add(right_frame)

        # Статус бар
        self.status_bar = tk.Label(root, text="Готов к работе", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def run_process(self):
        # Временные файлы
        temp_asm = "gui_temp.asm"
        temp_bin = "gui_temp.bin"

        try:
            # Сохранение текста из редактора во временный файл
            code_text = self.text_editor.get("1.0", tk.END)
            with open(temp_asm, "w", encoding="utf-8") as f:
                f.write(code_text)

            assembler = Assembler()
            commands = assembler.parse_file(temp_asm)

            binary_data = bytearray()
            for cmd in commands:
                machine_code = assembler.assemble_command(cmd)
                binary_data.extend(machine_code)

            with open(temp_bin, "wb") as f:
                f.write(binary_data)

            vm = VirtualMachine(memory_size=2048)
            vm.load_program(temp_bin)
            vm.run()

            self.update_memory_view(vm)
            self.status_bar.config(text=f"Успешно выполнено. Размер программы: {len(binary_data)} байт.", fg="green")

        except Exception as e:
            messagebox.showerror("Ошибка выполнения", str(e))
            self.status_bar.config(text=f"Ошибка: {e}", fg="red")

        finally:
            if os.path.exists(temp_asm): os.remove(temp_asm)
            if os.path.exists(temp_bin): os.remove(temp_bin)

    def update_memory_view(self, vm):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            start = int(self.entry_start.get())
            end = int(self.entry_end.get())
        except ValueError:
            messagebox.showwarning("Ввод", "Некорректный диапазон адресов")
            return

        for addr in range(start, end + 1):
            if addr < len(vm.memory):
                val = vm.memory[addr]
                self.tree.insert("", tk.END, values=(addr, val))


if __name__ == "__main__":
    root = tk.Tk()
    app = UVMApp(root)
    root.mainloop()