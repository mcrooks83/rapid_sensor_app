from tkinter import BOTH
from tkinter import filedialog as fd
from tkinter.ttk import  Treeview

class Table3(Treeview):
    def __init__(self, parent):
        super().__init__(parent, column=("Measurement", "Mean", "Median", "Max", "Min", "Range", "Q#", "Q1", "IQR", "STD", "MAD"), show='headings',)
        self.parent = parent
        #Measurement", "Mean", "Median", "Max", "Min", "Range", "Q3", "Q1", "IQR", "STD", "MAD"
        # Define column headings
        self.heading("#1", text="Measurement")
        self.heading("#2", text="Mean")
        self.heading("#3", text="Median")
        self.heading("#4", text="Max")
        self.heading("#5", text="Min")
        self.heading("#6", text="Range")
        self.heading("#7", text="Q3")
        self.heading("#8", text="Q1")
        self.heading("#9", text="IQR")
        self.heading("#10", text="STD")
        self.heading("#11", text="MAD")

        # Pack the Treeview widget
        self.pack(fill=BOTH, expand=True)
        self.center_treeview_columns()

        # Bind an event to update column widths when the window is resized
        self.parent.bind("<Configure>", self.update_column_widths)

    def center_treeview_columns(self):
    # Get the column IDs
        columns = self["columns"]
        # Center-align the text in each column
        for col in columns:
            self.column(col, anchor="center")

    def clear_table(self):
        item_count = self.get_children()
        # Delete all items from the treeview
        for item in item_count:
            self.delete(item)
    def insert_data(self, data):
        for item in data:
            self.insert("", "end", values=item)

    def update_column_widths(self, event):
        # Calculate column widths based on the frame width
        frame_width = self.parent.winfo_width()
        column_width = frame_width // 11  # Divide equally among 9 columns

        # Set the column widths
        for col in ("#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8", "#9", "#10", "#11"):
            self.column(col, width=column_width)