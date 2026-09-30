import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class GradeCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Grade Calculator")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Set style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), background="#f0f0f0", foreground="#2c3e50")
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        
        self.students = []
        self.data_file = "grades_data.json"
        self.load_data()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="📚 Student Grade Calculator", style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Add Student", padding=15)
        input_frame.pack(fill="x", padx=0, pady=(0, 20))
        
        # Student name
        ttk.Label(input_frame, text="Student Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Scores
        ttk.Label(input_frame, text="Scores (comma separated):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.scores_entry = ttk.Entry(input_frame, width=30)
        self.scores_entry.grid(row=1, column=1, padx=5, pady=5)
        self.scores_entry.insert(0, "90, 85, 88")
        
        # Add button
        add_btn = ttk.Button(input_frame, text="Add Student", command=self.add_student)
        add_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Results Section
        results_frame = ttk.LabelFrame(main_frame, text="Student Grades", padding=15)
        results_frame.pack(fill="both", expand=True, padx=0, pady=(0, 20))
        
        # Create treeview
        self.tree = ttk.Treeview(results_frame, columns=("Name", "Average", "Grade", "Status"), height=15)
        self.tree.column("#0", width=0, stretch="no")
        self.tree.column("Name", anchor="w", width=200)
        self.tree.column("Average", anchor="center", width=120)
        self.tree.column("Grade", anchor="center", width=80)
        self.tree.column("Status", anchor="w", width=180)
        
        self.tree.heading("#0", text="")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Average", text="Average Score")
        self.tree.heading("Grade", text="Letter Grade")
        self.tree.heading("Status", text="Performance")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", padx=0)
        
        delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_student)
        delete_btn.pack(side="left", padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="Clear All", command=self.clear_all)
        clear_btn.pack(side="left", padx=5)
        
        summary_btn = ttk.Button(btn_frame, text="Show Summary", command=self.show_summary)
        summary_btn.pack(side="left", padx=5)
        
        export_btn = ttk.Button(btn_frame, text="Export Data", command=self.export_data_to_file)
        export_btn.pack(side="left", padx=5)
        
        self.refresh_tree()
    
    def add_student(self):
        name = self.name_entry.get().strip()
        scores_str = self.scores_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a student name")
            return
        
        try:
            scores = [float(s.strip()) for s in scores_str.split(",")]
            if not scores or any(s < 0 or s > 100 for s in scores):
                raise ValueError("Scores must be between 0 and 100")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid scores (0-100, comma separated)")
            return
        
        # Check for duplicate
        if any(s["name"].lower() == name.lower() for s in self.students):
            messagebox.showerror("Error", f"{name} already exists")
            return
        
        avg = sum(scores) / len(scores)
        grade = self.get_letter_grade(avg)
        
        self.students.append({
            "name": name,
            "scores": scores,
            "average": avg,
            "grade": grade
        })
        
        self.save_data()
        self.refresh_tree()
        self.name_entry.delete(0, "end")
        self.scores_entry.delete(0, "end")
        self.scores_entry.insert(0, "90, 85, 88")
        messagebox.showinfo("Success", f"{name} added successfully!")
    
    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student to delete")
            return
        
        for item in selected:
            index = self.tree.index(item)
            self.students.pop(index)
        
        self.save_data()
        self.refresh_tree()
        messagebox.showinfo("Success", "Student(s) deleted")
    
    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all student data?"):
            self.students = []
            self.save_data()
            self.refresh_tree()
    
    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for student in self.students:
            status = self.get_status(student["average"])
            self.tree.insert("", "end", values=(
                student["name"],
                f"{student['average']:.2f}",
                student["grade"],
                status
            ))
    
    def get_letter_grade(self, average):
        if average >= 90:
            return "A"
        elif average >= 80:
            return "B"
        elif average >= 70:
            return "C"
        elif average >= 60:
            return "D"
        else:
            return "F"
    
    def get_status(self, average):
        if average >= 90:
            return "✓ Excellent"
        elif average >= 80:
            return "✓ Good"
        elif average >= 70:
            return "~ Satisfactory"
        elif average >= 60:
            return "⚠ Needs Improvement"
        else:
            return "✗ Failing"
    
    def show_summary(self):
        if not self.students:
            messagebox.showinfo("Summary", "No students added yet")
            return
        
        averages = [s["average"] for s in self.students]
        class_avg = sum(averages) / len(averages)
        highest = max(averages)
        lowest = min(averages)
        
        summary_text = f"""
CLASS SUMMARY
─────────────────────
Total Students: {len(self.students)}
Class Average: {class_avg:.2f}
Highest Score: {highest:.2f}
Lowest Score: {lowest:.2f}

GRADE DISTRIBUTION
─────────────────────
A (90-100): {len([s for s in self.students if s['average'] >= 90])}
B (80-89): {len([s for s in self.students if 80 <= s['average'] < 90])}
C (70-79): {len([s for s in self.students if 70 <= s['average'] < 80])}
D (60-69): {len([s for s in self.students if 60 <= s['average'] < 70])}
F (<60): {len([s for s in self.students if s['average'] < 60])}
        """
        
        messagebox.showinfo("Class Summary", summary_text)
    
    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.students, f, indent=2)
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    self.students = json.load(f)
            except:
                self.students = []
    
    def export_data_to_file(self):
        if not self.students:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"grades_export_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("STUDENT GRADES REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for student in self.students:
                f.write(f"Student: {student['name']}\n")
                f.write(f"Scores: {', '.join(map(str, student['scores']))}\n")
                f.write(f"Average: {student['average']:.2f}\n")
                f.write(f"Grade: {student['grade']}\n")
                f.write("-" * 60 + "\n")
            
            averages = [s["average"] for s in self.students]
            f.write("\nCLASS SUMMARY\n")
            f.write(f"Total Students: {len(self.students)}\n")
            f.write(f"Class Average: {sum(averages) / len(averages):.2f}\n")
            f.write(f"Highest: {max(averages):.2f}\n")
            f.write(f"Lowest: {min(averages):.2f}\n")
        
        messagebox.showinfo("Success", f"Data exported to {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GradeCalculatorApp(root)
    root.mainloop()
