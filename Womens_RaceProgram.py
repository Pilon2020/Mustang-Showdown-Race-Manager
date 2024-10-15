import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk,scrolledtext
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import random
import os

# Global variables
race_data = {'men': [], 'women': []}
save_directory = ""
results_dfs = {}  # Dictionary to hold DataFrames for each heat
round_2_heats = pd.DataFrame(columns=["Heat", "Bib Number", "Full Name", "Team"])# Initialize the DataFramesave_directory = ""
round_2_results_dfs = {}
current_heat_index = 0  # To track the current heat
current_entry_window = None  # Store the current entry window
results_table_window = None  # Store the results table window
heat_bibs = []  # Store bibs for the current heat


# Load CSV file
def load_csv_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return None
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    else:
        messagebox.showerror("Error", "Unsupported file type.")
        return None

# Load heats from the CSV file and populate the DataFrame for round 2
def load_heats_from_csv():
    df = load_csv_file()
    if df is None:
        return
    
    # Check if necessary columns exist in the CSV
    required_columns = ['Gender', 'Heat', 'Name', 'Bib', 'Team']
    if not all(col in df.columns for col in required_columns):
        messagebox.showerror("Error", "CSV file is missing required columns.")
        return
    
    # Separate data by gender (men and women) and create DataFrames
    men_heats = df[df['Gender'] == 'Men'].copy()
    women_heats = df[df['Gender'] == 'Women'].copy()
    
    # Store the data in a dictionary for easy access
    race_data['men'] = men_heats
    race_data['women'] = women_heats
    
    # Update round_2_heats DataFrame with the data from CSV (for easy access in later rounds)
    global round_2_heats
    round_2_heats = df[['Heat', 'Bib', 'Name', 'Team']].copy()

    # Show success message
    messagebox.showinfo("Success", "Heats loaded from CSV file successfully.")

# Function to display heats from the loaded CSV file
def display_loaded_heats():
    output = ""
    
    # Display Men's heats
    output += "\nMen's Round 1 Heats:\n"
    men_heats = race_data['men']
    for heat in men_heats['Heat'].unique():
        output += f"\nHeat {heat}:\n"
        heat_group = men_heats[men_heats['Heat'] == heat]
        for index, row in heat_group.iterrows():
            output += f"{row['Bib']:<10} | {row['Name']:<30} | {row['Team']:<20}\n"
    
    # Display Women's heats
    output += "\nWomen's Round 1 Heats:\n"
    women_heats = race_data['women']
    for heat in women_heats['Heat'].unique():
        output += f"\nHeat {heat}:\n"
        heat_group = women_heats[women_heats['Heat'] == heat]
        for index, row in heat_group.iterrows():
            output += f"{row['Bib']:<10} | {row['Name']:<30} | {row['Team']:<20}\n"
    
    # Display the result in a message box or scrolled text widget
    print(output)
    messagebox.showinfo("Heats", output)


#Round 1

def show_results_entry_window():
    global current_heat_index, current_entry_window, results_table_window, heat_bibs
    print(current_heat_index)
    
    # Check if there is a previous entry window and destroy it
    if 'current_entry_window' in globals() and current_entry_window is not None:
        current_entry_window.destroy()  # Close the previous entry window if it exists

    # Check if there are no more heats left
    if current_heat_index >= len(race_data['women'][0]):
        messagebox.showinfo("Notice", "All heats have been processed.")
        create_round_2_heats()
        save_all_heats()
        show_round_2_entry_window()
        return

    # Get the current heat indices and bib numbers
    heat_indices = race_data['women'][0][current_heat_index]
    print(heat_indices)
    heat_bibs = race_data['women'][4][heat_indices]
    print(heat_bibs)

    # Create a new entry window
    current_entry_window = tk.Toplevel()
    current_entry_window.title(f"Round 1 Heat {current_heat_index + 1} Results Entry")
    
    # Set the size of the window
    window_width = 400
    window_height = 400
    
    # Get the screen width and height
    screen_width = current_entry_window.winfo_screenwidth()
    screen_height = current_entry_window.winfo_screenheight()
    
    # Calculate x and y coordinates for the window to be centered
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    
    # Set the geometry of the window
    current_entry_window.geometry(f"{window_width}x{window_height}+{x}+{y}")


    tk.Label(current_entry_window, text="Enter Bib Number:").grid(row=0, column=0, padx=10, pady=10)
    bib_entry = tk.Entry(current_entry_window)
    bib_entry.grid(row=0, column=1, padx=10, pady=10)

    current_entry_window.grid_rowconfigure(1, weight=1)
    current_entry_window.grid_columnconfigure(0, weight=1)
    current_entry_window.grid_columnconfigure(1, weight=1)

    results_listbox = tk.Listbox(current_entry_window)
    results_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def add_entry(event=None):
        global current_heat_index, heat_bibs, w_results_dfs

        bib_number = bib_entry.get().strip()
        if bib_number:
            heat_bibs_str = list(map(str, heat_bibs))

            if bib_number in heat_bibs_str:
                idx = heat_bibs_str.index(bib_number)

                full_name = race_data['women'][1][heat_indices[idx]]
                team = race_data['women'][5][heat_indices[idx]]
                bib = heat_bibs[idx]

                results_listbox.insert(tk.END, f"{bib} - {full_name} - {team}")

                # Check if the DataFrame for the current heat exists; if not, create it
                if current_heat_index not in w_results_dfs:
                    w_results_dfs[current_heat_index] = pd.DataFrame(columns=["Finish Order", "Bib Number", "Full Name", "Team"])

                w_results_dfs[current_heat_index].loc[len(w_results_dfs[current_heat_index])] = [len(w_results_dfs[current_heat_index]) + 1, bib, full_name, team]
                bib_entry.delete(0, tk.END)

                # If all entries for the current heat are entered, disable the entry field
                if len(results_listbox.get(0, tk.END)) == len(heat_bibs):
                    bib_entry.config(state=tk.DISABLED)
                    show_results_table()  # Show results table for the current heat
                    print("All entries entered for this heat. Moving to next heat...")
            else:
                messagebox.showwarning("Warning", "Bib number not found in this heat.")

    bib_entry.bind("<Return>", add_entry)


def show_results_table():
    global results_table_window, current_heat_index

    # Create a new results table window for each heat
    results_table_window = tk.Toplevel()
    results_table_window.title(f"Results Table for Heat {current_heat_index + 1}")
    results_table_window.geometry("600x400")

    tree = ttk.Treeview(results_table_window, columns=("Finish Order", "Bib Number", "Name", "Team"), show="headings")
    tree.heading("Finish Order", text="Finish Order")
    tree.heading("Bib Number", text="Bib Number")
    tree.heading("Name", text="Name")
    tree.heading("Team", text="Team")

    tree.column("Finish Order", width=20)
    tree.column("Bib Number", width=100)
    tree.column("Name", width=200)
    tree.column("Team", width=200)

    tree.pack(fill=tk.BOTH, expand=True)

    # Populate the treeview with data from the results DataFrame for the current heat
    if current_heat_index in w_results_dfs:
        for index, row in w_results_dfs[current_heat_index].iterrows():
            tree.insert("", tk.END, values=(index + 1, row["Bib Number"], row["Full Name"], row["Team"]))

    # Add buttons for saving and continuing to the next heat
    edit_entry_button = tk.Button(results_table_window, text="Edit Selected", command=lambda: edit_entry(tree))
    edit_entry_button.pack(pady=10)

    next_heat_button = tk.Button(results_table_window, text="Next Heat", command=lambda: (save_results(tree), results_table_window.destroy(), show_results_entry_window()))
    next_heat_button.pack(pady=10)

    
def edit_entry(tree):
    global w_results_dfs, current_heat_index  # Declare globals

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select an entry to edit.")
        return

    # Get selected row data
    item = tree.item(selected_item)
    finish_order, bib_number, full_name, team = item['values']

    # Check if the DataFrame for the current heat exists
    if current_heat_index not in w_results_dfs:
        messagebox.showwarning("Warning", "No results found for the current heat.")
        return  # Exit if no results found

    # Create a new window for editing
    edit_window = tk.Toplevel()
    edit_window.title("Edit Entry")
    edit_window.geometry("300x400")

    tk.Label(edit_window, text="Finish Order:").pack(pady=5)
    finish_order_entry = tk.Entry(edit_window)
    finish_order_entry.insert(0, finish_order)
    finish_order_entry.pack(pady=5)

    # Display Bib Number, Name, and Team as labels
    tk.Label(edit_window, text=f"Bib Number: {bib_number}").pack(pady=5)
    tk.Label(edit_window, text=f"Name: {full_name}").pack(pady=5)
    tk.Label(edit_window, text=f"Team: {team}").pack(pady=5)

    def save_changes():
        # Get the new finish order from the entry
        new_finish_order = finish_order_entry.get()

        # Validate the new finish order
        try:
            new_finish_order_index = int(new_finish_order) - 1  # Convert to zero-based index

            # Get the DataFrame for the current heat
            results_df = w_results_dfs[current_heat_index]
            
            # Check if the new index is valid
            if new_finish_order_index < 0 or new_finish_order_index >= len(results_df):
                messagebox.showwarning("Warning", "Invalid finish order.")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Finish order must be a number.")
            return

        # Find the current index of the selected item
        current_items = [tree.item(child)['values'] for child in tree.get_children()]
        selected_index = next((i for i, child in enumerate(tree.get_children()) if child == selected_item[0]), None)

        if selected_index is None:
            messagebox.showwarning("Warning", "No entry selected.")
            return

        # Move the selected item to the new position
        item_to_move = current_items[selected_index]  # The selected item

        # Adjust the order
        new_order = [current_items[i] for i in range(len(current_items)) if i != selected_index]
        new_order.insert(new_finish_order_index, item_to_move)

        # Update results_df with the new order
        results_df = pd.DataFrame(new_order, columns=["Finish Order", "Bib Number", "Full Name", "Team"])
        results_df["Finish Order"] = range(1, len(results_df) + 1)  # Update Finish Order column

        # Update Treeview
        tree.delete(*tree.get_children())  # Clear the Treeview
        for idx, row in results_df.iterrows():
            tree.insert("", tk.END, values=(row["Finish Order"], row["Bib Number"], row["Full Name"], row["Team"]))

        # Optionally, update the original w_results_dfs with the new DataFrame
        w_results_dfs[current_heat_index] = results_df

        edit_window.destroy()  # Close the edit window

    # Button to save changes
    save_button = tk.Button(edit_window, text="Save Changes", command=save_changes)
    save_button.pack(pady=10)


def save_results(tree):
    global save_directory, current_heat_index
    # Construct the file path for saving
    file_name = f"Heat_{current_heat_index+1}_ResultsW.txt"  # Adjust the filename for each heat
    file_path = f"{save_directory}/{file_name}"

    # Save the results from the treeview to the specified path in the desired format
    with open(file_path, 'w') as f:
        f.write(f"Round 1 Heat {current_heat_index} Results:\n")
        # Write the header with proper spacing
        f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
        f.write(f"{'-' * 70}\n")  # Divider line
        
        # Write each row from the treeview with proper formatting
        for i, row_id in enumerate(tree.get_children(), start=1):
            row = tree.item(row_id)["values"]
            f.write(f"{i:<10} | {row[1]:<10} | {row[2]:<30} | {row[3]:<20}\n")
    
    messagebox.showinfo("Success", f"Results saved to {file_path}")
    current_heat_index += 1  # Move to the next heat

def save_all_heats():
    global save_directory, w_results_dfs    
    # Construct the file path for saving
    file_name = "All_Heats_Results.txt"  # Adjust the filename as needed
    file_path = f"{save_directory}/{file_name}"

    with open(file_path, 'w') as f:
        for heat_index in sorted(w_results_dfs.keys()):
            f.write(f"Round 1 Heat {heat_index + 1} Results:\n")
            f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
            f.write(f"{'-' * 70}\n")
            
            # Write each row from the DataFrame with proper formatting
            for idx, row in w_results_dfs[heat_index].iterrows():
                f.write(f"{idx + 1:<10} | {row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")
            f.write("\n")  # Add some spacing between heats

    messagebox.showinfo("Success", f"All heat results compiled and saved to {file_path}")
    
    
def create_round_2_heats():
    global save_directory, w_results_dfs, round_2_heats  # Use w_results_dfs (Round 1 results)

    # Create new DataFrame to hold Round 2 participants
    round_2_df = pd.DataFrame()

    # Process each heat from Round 1
    for heat_index in sorted(w_results_dfs.keys()):
        heat_df = w_results_dfs[heat_index]

        # Calculate the number of participants for each heat
        total_participants = len(heat_df)
        half_point = total_participants // 2

        # Split participants as evenly as possible into bottom 50% (Heat 1) and top 50% (Heat 2)
        if total_participants % 2 == 0:
            bottom_half = heat_df.iloc[half_point:]  # Bottom half
            top_half = heat_df.iloc[:half_point]  # Top half
        else:
            # If odd number of participants, give the larger half to Heat 1
            bottom_half = heat_df.iloc[half_point + 1:]  # Bottom half
            top_half = heat_df.iloc[:half_point + 1]  # Top half

        # Assign bottom half to Heat 1 and top half to Heat 2
        bottom_half.loc[:, 'Heat'] = "1"
        top_half.loc[:, 'Heat'] = "2"

        # Add participants to the Round 2 DataFrame
        round_2_df = pd.concat([round_2_df, bottom_half, top_half], ignore_index=True)

    # Save the heats to a file
    file_name = "W_Round2_Heats.txt"
    file_path = f"{save_directory}/{file_name}"

    with open(file_path, 'w') as f:
        for heat_index in sorted(round_2_df['Heat'].unique()):
            f.write(f"Round 2 Heat {heat_index}\n")
            f.write(f"{'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
            f.write(f"{'-' * 70}\n")

            # Filter by current heat
            heat_participants = round_2_df[round_2_df['Heat'] == heat_index]

            for idx, row in heat_participants.iterrows():
                f.write(f"{row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")
            f.write("\n")  # Add some spacing between heats

    messagebox.showinfo("Success", f"Round 2 heats have been compiled and saved to {file_path}")

    # Reset and assign round_2_heats to the populated DataFrame
    global current_heat_index
    current_heat_index = 0
    round_2_heats = round_2_df  # Assign the populated DataFrame to round_2_heats

    return round_2_df


# Round 2
def show_round_2_entry_window():
    global current_heat_index, current_entry_window, results_table_window, round_2_heats, heat_bibs_2

    # Check if there is a previous entry window and destroy it
    if current_entry_window is not None:
        current_entry_window.destroy()  # Close the previous entry window if it exists

    # Check if there are no more heats left
    if current_heat_index >= len(round_2_heats['Heat'].unique()):
        messagebox.showinfo("Notice", "All Round 2 heats have been processed.")
        save_all_heats2()  # Save all heats
        return

    # Get the DataFrame for the current heat
    current_heat_df = round_2_heats[round_2_heats['Heat'] == str(current_heat_index + 1)]
    
    # Get the corresponding Bib Numbers for the current heat
    heat_bibs_2 = current_heat_df['Bib Number'].tolist()

    # Create a new entry window
    current_entry_window = tk.Toplevel()
    current_entry_window.title(f"Round 2 Heat {current_heat_index + 1} Results Entry")

    # Set the size of the window
    window_width = 400
    window_height = 400
    screen_width = current_entry_window.winfo_screenwidth()
    screen_height = current_entry_window.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    current_entry_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Add label and entry for Bib Number input
    tk.Label(current_entry_window, text="Enter Bib Number:").grid(row=0, column=0, padx=10, pady=10)
    bib_entry = tk.Entry(current_entry_window)
    bib_entry.grid(row=0, column=1, padx=10, pady=10)

    # Set focus on the Bib Number entry
    bib_entry.focus_set()

    # Configure grid layout for resizing
    current_entry_window.grid_rowconfigure(1, weight=1)
    current_entry_window.grid_columnconfigure(0, weight=1)
    current_entry_window.grid_columnconfigure(1, weight=1)

    # Add a Listbox to display the results
    results_listbox = tk.Listbox(current_entry_window)
    results_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def add_entry(event=None):
        global current_heat_index, round_2_w_results_dfs

        bib_number = bib_entry.get().strip()
        if bib_number:
            heat_bibs_str = list(map(str, heat_bibs_2))  # Convert all round 2 bibs to string

            if bib_number in heat_bibs_str:
                idx = heat_bibs_str.index(bib_number)

                # Get full name and team from round 2 heat data
                full_name = current_heat_df.iloc[idx]['Full Name']
                team = current_heat_df.iloc[idx]['Team']
                bib = heat_bibs_2[idx]

                # Adding a new entry
                results_listbox.insert(tk.END, f"{bib} - {full_name} - {team}")

                # Check if the DataFrame for the current heat exists; if not, create it
                if current_heat_index not in round_2_w_results_dfs:
                    round_2_w_results_dfs[current_heat_index] = pd.DataFrame(columns=["Finish Order", "Bib Number", "Full Name", "Team"])

                round_2_w_results_dfs[current_heat_index].loc[len(round_2_w_results_dfs[current_heat_index])] = [len(round_2_w_results_dfs[current_heat_index]) + 1, bib, full_name, team]
                bib_entry.delete(0, tk.END)

                # If all entries for the current heat are entered, disable the entry field
                if len(results_listbox.get(0, tk.END)) == len(heat_bibs_2):
                    bib_entry.config(state=tk.DISABLED)
                    show_results_table2()  # Show results table for the current heat
                    print("All entries entered for this heat. Moving to next heat...")
            else:
                messagebox.showwarning("Warning", "Bib number not found in this heat.")

    # Bind the return key to trigger add_entry
    bib_entry.bind("<Return>", add_entry)
    
def show_results_table2():
    global results_table_window, current_heat_index

    # Create a new results table window for each heat
    results_table_window = tk.Toplevel()
    results_table_window.title(f"Results Table for Heat {current_heat_index + 1}")
    results_table_window.geometry("600x400")

    tree = ttk.Treeview(results_table_window, columns=("Finish Order", "Bib Number", "Name", "Team"), show="headings")
    tree.heading("Finish Order", text="Finish Order")
    tree.heading("Bib Number", text="Bib Number")
    tree.heading("Name", text="Name")
    tree.heading("Team", text="Team")

    tree.column("Finish Order", width=20)
    tree.column("Bib Number", width=100)
    tree.column("Name", width=200)
    tree.column("Team", width=200)

    tree.pack(fill=tk.BOTH, expand=True)

    # Populate the treeview with data from the results DataFrame for the current heat
    if current_heat_index in round_2_w_results_dfs:
        for index, row in round_2_w_results_dfs[current_heat_index].iterrows():
            tree.insert("", tk.END, values=(index + 1, row["Bib Number"], row["Full Name"], row["Team"]))

    # Add buttons for saving and continuing to the next heat
    edit_entry_button = tk.Button(results_table_window, text="Edit Selected", command=lambda: edit_entry2(tree))
    edit_entry_button.pack(pady=10)
    
    next_heat_button = tk.Button(results_table_window, text="Next Heat", command=lambda: (save_results2(tree), results_table_window.destroy(), show_round_2_entry_window()))
    next_heat_button.pack(pady=10)
    
def edit_entry2(tree):
    global round_2_w_results_dfs, current_heat_index

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select an entry to edit.")
        return

    # Get selected row data
    item = tree.item(selected_item)
    finish_order, bib_number, full_name, team = item['values']

    # Check if the DataFrame for the current heat exists in Round 2 results
    if current_heat_index not in round_2_w_results_dfs:
        messagebox.showwarning("Warning", "No results found for the current heat.")
        return  # Exit if no results found

    # Create a new window for editing
    edit_window = tk.Toplevel()
    edit_window.title("Edit Entry")
    edit_window.geometry("300x400")

    # Input field for the finish order
    tk.Label(edit_window, text="Finish Order:").pack(pady=5)
    finish_order_entry = tk.Entry(edit_window)
    finish_order_entry.insert(0, finish_order)
    finish_order_entry.pack(pady=5)

    # Display Bib Number, Name, and Team as labels (non-editable)
    tk.Label(edit_window, text=f"Bib Number: {bib_number}").pack(pady=5)
    tk.Label(edit_window, text=f"Name: {full_name}").pack(pady=5)
    tk.Label(edit_window, text=f"Team: {team}").pack(pady=5)

    def save_changes():
        # Get the new finish order from the entry
        new_finish_order = finish_order_entry.get()

        # Validate the new finish order
        try:
            new_finish_order_index = int(new_finish_order) - 1  # Convert to zero-based index

            # Get the DataFrame for the current heat in Round 2
            results_df = round_2_w_results_dfs[current_heat_index]

            # Check if the new index is valid
            if new_finish_order_index < 0 or new_finish_order_index >= len(results_df):
                messagebox.showwarning("Warning", "Invalid finish order.")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Finish order must be a number.")
            return

        # Find the current index of the selected item
        current_items = [tree.item(child)['values'] for child in tree.get_children()]
        selected_index = next((i for i, child in enumerate(tree.get_children()) if child == selected_item[0]), None)

        if selected_index is None:
            messagebox.showwarning("Warning", "No entry selected.")
            return

        # Move the selected item to the new position
        item_to_move = current_items[selected_index]  # The selected item

        # Adjust the order by removing the item from its current position and inserting it at the new position
        new_order = [current_items[i] for i in range(len(current_items)) if i != selected_index]
        new_order.insert(new_finish_order_index, item_to_move)

        # Update the Round 2 DataFrame with the new order
        results_df = pd.DataFrame(new_order, columns=["Finish Order", "Bib Number", "Full Name", "Team"])
        results_df["Finish Order"] = range(1, len(results_df) + 1)  # Update the Finish Order column

        # Update the Treeview
        tree.delete(*tree.get_children())  # Clear the Treeview
        for idx, row in results_df.iterrows():
            tree.insert("", tk.END, values=(row["Finish Order"], row["Bib Number"], row["Full Name"], row["Team"]))

        # Save the updated DataFrame back to the Round 2 results
        round_2_w_results_dfs[current_heat_index] = results_df

        # Close the edit window
        edit_window.destroy()

    # Button to save changes
    save_button = tk.Button(edit_window, text="Save Changes", command=save_changes)
    save_button.pack(pady=10)


def save_results2(tree):
    global save_directory, current_heat_index
    # Construct the file path for saving
    file_name = f"Round_2_Heat_{current_heat_index + 1}_Results.txt"
    file_path = f"{save_directory}/{file_name}"

    # Save the results from the treeview to the specified path in the desired format
    with open(file_path, 'w') as f:
        f.write(f"Round 2 Heat {current_heat_index + 1} Results:\n")
        # Write the header with proper spacing
        f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
        f.write(f"{'-' * 70}\n")  # Divider line
        
        # Write each row from the treeview with proper formatting
        for i, row_id in enumerate(tree.get_children(), start=1):
            row = tree.item(row_id)["values"]
            f.write(f"{i:<10} | {row[1]:<10} | {row[2]:<30} | {row[3]:<20}\n")
    
    messagebox.showinfo("Success", f"Results saved to {file_path}")
    current_heat_index += 1  # Move to the next heat

def save_all_heats2():
    global save_directory, round_2_w_results_dfs

    if not round_2_w_results_dfs:  # Check if the dictionary is empty
        messagebox.showerror("Error", "No results to save for Round 2.")
        return

    file_name = "Round_2_All_Results.txt"
    file_path = f"{save_directory}/{file_name}"

    with open(file_path, 'w') as f:
        f.write("Round 2 All Heats Results:\n")
        for heat_index, df in round_2_w_results_dfs.items():
            f.write(f"\nResults for Heat {heat_index + 1}:\n")
            f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
            f.write(f"{'-' * 70}\n")
            for i, row in df.iterrows():
                f.write(f"{i + 1:<10} | {row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")

    messagebox.showinfo("Success", f"All Round 2 results saved to {file_path}")
    combine_all_rounds_results()

def combine_all_rounds_results():
    global save_directory, w_results_dfs, round_2_w_results_dfs, round_3_results_df

    # File path to save the combined results
    file_name = "All_Rounds_Results.txt"
    file_path = f"{save_directory}/{file_name}"

    with open(file_path, 'w') as f:
        # Writing Round 1 results
        f.write("Round 1 Results:\n")
        for heat_index, df in w_results_dfs.items():
            f.write(f"\nRound 1 Heat {heat_index + 1}:\n")
            f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
            f.write(f"{'-' * 70}\n")
            for i, row in df.iterrows():
                f.write(f"{i + 1:<10} | {row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")
        
        # Writing Round 2 results
        f.write("\n\n\nRound 2 Results:\n")
        for heat_index, df in round_2_w_results_dfs.items():
            f.write(f"\nRound 2 Heat {heat_index + 1}:\n")
            f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
            f.write(f"{'-' * 70}\n")
            for i, row in df.iterrows():
                f.write(f"{i + 1:<10} | {row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")
        
    messagebox.showinfo("Success", f"All rounds' results combined and saved to {file_path}")


    
# App Home Page

class MustangShowdownManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mustang Showdown Manager")

        # Set the window size to 400x400
        window_width = 400
        window_height = 400

        # Center the window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Frame for buttons
        button_frame = tk.Frame(self)
        button_frame.pack(expand=True)  # Center the frame in the window

        # Buttons for loading racers and results
        load_button = tk.Button(button_frame, text="Load Racers", command=load_csv_file)
        load_button.pack(pady=10)  # Add some vertical padding

        load_results_button = tk.Button(button_frame, text="Results Entry", command=show_results_entry_window)
        load_results_button.pack(pady=10)  # Add some vertical padding

        # Configure the frame to center the buttons
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)

        # Set minimum size for the window
        self.minsize(window_width, window_height)


# Example usage
if __name__ == "__main__":
    app = MustangShowdownManager()
    app.mainloop()
