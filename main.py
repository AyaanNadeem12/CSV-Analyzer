# ======================= CSV ANALYZER =======================
# A Python desktop application to analyze, clean, and visualize CSV files.
# Built with Tkinter for GUI, pandas for data processing, and matplotlib for charts.
# Features include NaN handling, column stats, and exportable insights.
# Author: Ayaan Nadeem | License: MIT

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tabulate import tabulate
import io
import os

# Global dataframe to store loaded CSV
df = None

# === Load CSV File ===
def load_csv():
    """
    Opens a file dialog to load a CSV and stores it in the global df.
    Displays a message with rows and columns on successful load
    """
    global df
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    try:
        df = pd.read_csv(file_path)
        messagebox.showinfo(" File Loaded", f"File loaded: {file_path}\nRows: {df.shape[0]}, Columns: {df.shape[1]}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

# === Basic Analysis ===
def run_basic_analysis():
    """
    Displays dataset info and descriptive statistics in a formatted way using tabulate.
    """
    if df is None:
        messagebox.showwarning("Warning", "Please load a CSV file first.")
        return
    try:
        output_box.config(state=tk.NORMAL)
        output_box.delete(1.0, tk.END)

        # === 1. DATASET INFO ===
        output_box.insert(tk.END, "=== DATASET INFO ===\n\n")

        # Capture df.info() output
        buffer = io.StringIO()
        df.info(buf=buffer, verbose=True)
        info_str = buffer.getvalue()
        info_lines = info_str.split('\n')

        # insert header lines
        output_box.insert(tk.END, "\n".join(info_lines[:3]) + "\n\n")

        # Format column-wise info
        col_data = []
        for line in info_lines[4:-2]:
            if line.strip():
                parts = line.split()
                col_data.append([
                    parts[0],  # Column number
                    parts[1],  # Column name
                    " ".join(parts[2:4]),  # Non-null count
                    parts[-1]  # Dtype
                ])

        output_box.insert(tk.END, tabulate(
            col_data,
            headers=["#", "Column", "Non-Null", "Dtype"],
            tablefmt="grid"
        ))
        output_box.insert(tk.END, "\n\n" + info_lines[-2] + "\n\n")  # Memory usage

        # === 2. DESCRIPTIVE STATISTICS ===
        output_box.insert(tk.END, "=== DESCRIPTIVE STATISTICS ===\n\n")
        desc_stats = df.describe(include='all')

        # Format numeric columns
        formatted_desc = desc_stats.copy()
        for col in desc_stats.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                formatted_desc[col] = desc_stats[col].apply(
                    lambda x: f"{x:.2f}" if not pd.isna(x) else "NaN"
                )

        output_box.insert(tk.END, tabulate(
            formatted_desc,
            headers="keys",
            tablefmt="grid",
            stralign="center",
            numalign="center"
        ))

        output_box.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Analysis Error", f"An error occurred:\n{str(e)}")

# === NaN Summary ===
def show_nan_summary():
    """
    Displays NaN (missing values) count and percentage for each column.
    """
    if df is None:
        messagebox.showwarning("Warning", "Please load a CSV file first.")
        return
    try:
        output_box.config(state=tk.NORMAL)
        output_box.delete(1.0, tk.END)

        # Compute NaN counts
        nan_counts = df.isnull().sum()
        nan_df = pd.DataFrame({
            "Column": nan_counts.index,
            "NaN Count": nan_counts.values,
            "Percentage (%)": (nan_counts / len(df) * 100).round(2)  # Add percentage
        })

        output_box.insert(tk.END, "=== NaN SUMMARY ===\n\n")
        output_box.insert(tk.END, tabulate(
            nan_df,
            headers="keys",
            tablefmt="grid",
            showindex=False,
            stralign="center",
            numalign="center"
        ))

        if nan_counts.sum() == 0:
            output_box.insert(tk.END, "\n\n No missing values found!")

        output_box.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Error", f"Error generating NaN summary:\n{str(e)}")

# === Data Visualizer ===
def open_plot_window():
    """
    Opens a new window to select a column and chart type to visualize using matplotlib.
    """
    if df is None:
        messagebox.showwarning("Warning", "Please load a CSV file first.")
        return

    def plot():
        col = column_cb.get()
        chart_type = chart_cb.get()

        if not col:
            messagebox.showwarning("Select Column", "Please select a column.")
            return

        try:
            fig, ax = plt.subplots(figsize=(8, 6))

            # Chart logic
            if chart_type == "Bar Chart":
                df[col].value_counts().plot(kind='bar', ax=ax)
            elif chart_type == "Pie Chart":
                df[col].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
            elif chart_type == "Histogram":
                df[col].plot(kind='hist', ax=ax, bins=10, color='skyblue', edgecolor='black')

            ax.set_title(f"{chart_type} of {col}")
            plt.tight_layout()

            plot_canvas_win = tk.Toplevel(plot_win)
            plot_canvas_win.title(f"{chart_type} of {col}")
            plot_canvas_win.geometry("800x600")

            # Set window icon
            try:
                plot_canvas_win.iconbitmap(os.path.join("assets", "visualize.ico"))
            except:
                pass

            # Show chart in new window
            canvas = FigureCanvasTkAgg(fig, master=plot_canvas_win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Plot Error", f"Failed to create chart:\n{str(e)}")

    # Create plot window
    plot_win = tk.Toplevel(root)
    plot_win.title(" Data Visualizer")
    plot_win.configure(bg="#2d2d2d")
    plot_win.geometry("600x400")

    # Set window icon
    try:
        plot_win.iconbitmap(os.path.join("assets", "visualize.ico"))
    except:
        pass

    ttk.Label(plot_win, text="Select Column:", font=("Segoe UI", 10)).pack(pady=5)
    column_cb = ttk.Combobox(plot_win, values=list(df.columns), font=("Segoe UI", 10))
    column_cb.pack(pady=5)

    ttk.Label(plot_win, text="Select Chart Type:", font=("Segoe UI", 10)).pack(pady=5)
    chart_cb = ttk.Combobox(plot_win, values=["Bar Chart", "Pie Chart", "Histogram"], font=("Segoe UI", 10))
    chart_cb.pack(pady=5)

    ttk.Button(plot_win, text="Generate Chart", command=plot).pack(pady=10)

# === Export Results ===
def export_results():
    """
    Exports the current output box content to a text or CSV file.
    """
    if df is None:
        messagebox.showwarning("Warning", "No data to export!")
        return
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv")]
        )
        if not file_path:
            return

        with open(file_path, "w") as f:
            f.write(output_box.get("1.0", tk.END))
        messagebox.showinfo("Success", f"Exported to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Export failed:\n{str(e)}")

# === Column Stats ===
def show_column_stats():
    """
    Shows detailed statistics for a user-selected column
    """
    if df is None:
        messagebox.showwarning("Warning", "Load a CSV first!")
        return

    # Create custom dialog window
    stats_win = tk.Toplevel(root)
    stats_win.title("Column Stats")
    stats_win.configure(bg="#2d2d2d")
    stats_win.geometry("400x550")

    # Set window icon
    try:
        stats_win.iconbitmap(os.path.join("assets", "col_stats.ico"))
    except:
        pass

    # Label and Combobox for column selection
    ttk.Label(stats_win, text="Select Column:").pack(pady=10)
    col_cb = ttk.Combobox(stats_win, values=list(df.columns))
    col_cb.pack(pady=5)

    # Frame for results
    result_frame = tk.Frame(stats_win, bg="#2d2d2d")
    result_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    # Text widget for displaying stats
    stats_text = tk.Text(result_frame, wrap=tk.WORD, font=("Consolas", 10),
                         bg="#3d3d3d", fg="#3fb9bf", state=tk.DISABLED)
    stats_text.pack(fill=tk.BOTH, expand=True)

    def show_stats():
        col = col_cb.get()
        if not col or col not in df.columns:
            return

        # Generate stats
        stats = {
            "Mean": df[col].mean() if pd.api.types.is_numeric_dtype(df[col]) else "N/A",
            "Unique Values": df[col].nunique(),
            "Top Value": df[col].mode().iloc[0] if len(df[col].mode()) > 0 else "N/A",
            "NaN Count": df[col].isnull().sum(),
            "Data Type": str(df[col].dtype)
        }

        # Display in text widget
        stats_text.config(state=tk.NORMAL)
        stats_text.delete(1.0, tk.END)
        stats_text.insert(tk.END, f"=== COLUMN STATS: {col} ===\n\n")
        stats_text.insert(tk.END, tabulate(
            [(k, v) for k, v in stats.items()],
            headers=["Statistic", "Value"],
            tablefmt="grid"
        ))
        stats_text.config(state=tk.DISABLED)

    ttk.Button(stats_win, text="Show Stats", command=show_stats).pack(pady=10)

# === Data Cleaning ===
def clean_data():
    """
    Provides options to clean data
    """
    global df

    if df is None:
        messagebox.showwarning("Warning", "Load a CSV first!")
        return

    # Create custom dialog window
    clean_win = tk.Toplevel(root)
    clean_win.title("Data Cleaning")
    clean_win.configure(bg="#2d2d2d")
    clean_win.geometry("400x200")


    # Set window icon
    try:
        clean_win.iconbitmap(os.path.join("assets", "clean.ico"))
    except:
        pass

    # Frame for options
    option_frame = tk.Frame(clean_win, bg="#2d2d2d")
    option_frame.pack(pady=20)

    # Style the radio buttons
    style.configure("TRadiobutton",
                    background="#2d2d2d",
                    foreground="#00ffff",
                    font=("Segoe UI", 10))

    choice = tk.IntVar()

    # Radio buttons
    ttk.Radiobutton(option_frame, text="1. Drop NaN Rows", variable=choice, value=1).pack(anchor='w', pady=5)
    ttk.Radiobutton(option_frame, text="2. Drop NaN Columns", variable=choice, value=2).pack(anchor='w', pady=5)
    ttk.Radiobutton(option_frame, text="3. Fill NaN with 0", variable=choice, value=3).pack(anchor='w', pady=5)

    def execute_cleaning():
        try:
            if choice.get() == 1:
                df.dropna(axis=0, inplace=True)
                messagebox.showinfo("Success", "NaN rows dropped!")
            elif choice.get() == 2:
                df.dropna(axis=1, inplace=True)
                messagebox.showinfo("Success", "NaN columns dropped!")
            elif choice.get() == 3:
                df.fillna(0, inplace=True)
                messagebox.showinfo("Success", "NaN values filled with 0!")
            clean_win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Cleaning failed:\n{str(e)}")

    # Button frame
    button_frame = tk.Frame(clean_win, bg="#2d2d2d")
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Execute", command=execute_cleaning).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Cancel", command=clean_win.destroy).pack(side=tk.LEFT, padx=10)


# === GUI Setup ===
root = tk.Tk()
root.title(" CSV Analyzer")
root.geometry("900x600")
root.configure(bg="#2d2d2d")

# Set app icon
try:
    root.iconbitmap(os.path.join("assets", "icon.ico"))
except:
    pass  # ignore if missing

# Load button icons
try:
    load_img = tk.PhotoImage(file=os.path.join("assets", "folder.png"))
    analysis_img = tk.PhotoImage(file=os.path.join("assets", "analysis.png"))
    nan_img = tk.PhotoImage(file=os.path.join("assets", "NAN.png"))
    plot_img = tk.PhotoImage(file=os.path.join("assets", "visualize.png"))
    exit_img = tk.PhotoImage(file=os.path.join("assets", "exit.png"))
    export_img = tk.PhotoImage(file=os.path.join("assets", "export.png"))
    stats_img = tk.PhotoImage(file=os.path.join("assets", "col_stats.png"))
    clean_img = tk.PhotoImage(file=os.path.join("assets", "clean.png"))
except:
    load_img = analysis_img = nan_img = plot_img = exit_img = export_img = stats_img = clean_img = None

# === Styling UI ===
style = ttk.Style()
style.theme_use("clam")

style.configure("TButton",
                font=("Segoe UI", 11),
                padding=6,
                background="#3fb9bf",
                foreground="white")
style.map("TButton",
          background=[("active", "#2c7e82")])

style.configure("TLabel", font=("Segoe UI", 11), foreground="#00ffff", background="#2d2d2d")
style.configure("TCombobox", font=("Segoe UI", 10), fieldbackground="#3d3d3d", foreground="#00ffff")

# === Left Sidebar (Buttons) ===
button_frame = tk.Frame(root, bg="#3d3d3d", bd=2, relief=tk.GROOVE)
button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

ttk.Button(
    button_frame,
    text=" Load CSV",
    image=load_img,
    compound=tk.LEFT,
    command=load_csv
).pack(pady=6, fill='x')

ttk.Button(
    button_frame,
    text=" Run Analysis",
    image=analysis_img,
    compound=tk.LEFT,
    command=run_basic_analysis
).pack(pady=6, fill='x')

ttk.Button(
    button_frame,
    text=" NaN Summary",
    image=nan_img,
    compound=tk.LEFT,
    command=show_nan_summary
).pack(pady=6, fill='x')

ttk.Button(
    button_frame,
    text=" Column Stats",
    image=stats_img,
    compound=tk.LEFT,
    command=show_column_stats
).pack(pady=6, fill='x')

ttk.Button(
    button_frame,
    text=" Clean Data",
    image=clean_img,
    compound=tk.LEFT,
    command=clean_data
).pack(pady=6, fill='x')

ttk.Button(
    button_frame,
    text=" Export Results",
    image=export_img,
    compound=tk.LEFT,
    command=export_results
).pack(pady=6, fill='x')

ttk.Button(
    button_frame,
    text=" Visualize Data",
    image=plot_img,
    compound=tk.LEFT,
    command=open_plot_window
).pack(pady=6, fill='x')

ttk.Button(
    button_frame,
    text=" Exit",
    image=exit_img,
    compound=tk.LEFT,
    command=root.quit
).pack(pady=20, fill='x')

# === Right Side (Output Viewer) ===
output_frame = tk.Frame(root, bg="#2d2d2d")
output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

output_box = tk.Text(output_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#3d3d3d", fg="#3fb9bf")
output_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
output_box.config(state=tk.DISABLED)

scrollbar = ttk.Scrollbar(output_frame, command=output_box.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_box.config(yscrollcommand=scrollbar.set)

# === Start the App ===
root.mainloop()