import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk,scrolledtext
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import random, os, csv

# Global variables
save_directory = ""
race_data = {'men': [], 'women': []}
current_heat_index = 0  # To track the current heat
current_entry_window = None  # Store the current entry window
results_table_window = None  # Store the results table window
m_results_dfs = {}  # Dictionary to hold DataFrames for each heat
round_2_m_results_dfs = {}  # Initialize an empty dict for storing heat results
m_round_3_results_df = pd.DataFrame()
heat_bibs = []  # Store bibs for the current heat



# Load Excel file
def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if not file_path:
        return None
    if file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)
    else:
        messagebox.showerror("Error", "Unsupported file type.")
        return None

# Sort racers into heats
def sort_racers(df, num_groups, swim_col, run_col, bib_col, team_col):
    swim_times = df[swim_col].values
    run_times = df[run_col].values
    first_names = df['Participant name: First name'].values
    last_names = df['Participant name: Last name'].values
    bib_numbers = df[bib_col].values  # Load bib numbers
    teams = df[team_col].values  # Load teams
    
    # Create full names with bib numbers
    full_names = [f"{first} {last}" for first, last in zip(first_names, last_names)]
    
    # Objective function for optimization
    def objective(x):
        groups = np.array_split(np.argsort(x), num_groups)
        swim_averages = [np.mean(swim_times[group]) for group in groups]
        run_averages = [np.mean(run_times[group]) for group in groups]
        return np.var(swim_averages) + np.var(run_averages)

    x0 = np.random.rand(len(full_names))
    bounds = [(0, 1) for _ in full_names]

    result = minimize(objective, x0, bounds=bounds, method='L-BFGS-B')
    
    groups = np.array_split(np.argsort(result.x), num_groups)

    return groups, full_names, swim_times, run_times, bib_numbers, teams


# Combined function to load racers and automatically save heat assignments
def load_and_sort_racers_and_save_heats():
    df = load_file()
    if df is None:
        return
    
    # Clean up the gender column
    df['Gender'] = df['Gender'].str.strip().str.capitalize()

    # Separate males and females
    males_df = df[df['Gender'] == 'Male'].copy()
    females_df = df[df['Gender'] == 'Female'].copy()

    # Sorting the male participants into 3 groups
    male_groups, male_names, male_swim_times, male_run_times, male_bibs, male_teams = sort_racers(males_df, 3, 'Short answer', 'Copy of 5k time', 'Chip number', 'Dropdown menu')
    race_data['men'] = (male_groups, male_names, male_swim_times, male_run_times, male_bibs, male_teams)

    # Sorting the female participants into 2 groups
    female_groups, female_names, female_swim_times, female_run_times, female_bibs, female_teams = sort_racers(females_df, 2, 'Short answer', 'Copy of 5k time', 'Chip number', 'Dropdown menu')
    race_data['women'] = (female_groups, female_names, female_swim_times, female_run_times, female_bibs, female_teams)

    # Combine and display full details in the text file
    combined_display_heat_details(male_groups, male_names, male_swim_times, male_run_times, male_bibs, female_groups, female_names, female_swim_times, female_run_times, female_bibs)

    # Save without swim times
    combined_display_heat_details_without_times(male_groups, male_names, male_bibs, male_teams, female_groups, female_names, female_bibs, female_teams)

def display_heat_details(groups, full_names, swim_times, run_times, bib_numbers, gender):
    output = f"\n{gender.capitalize()} Wave Groups:\n"
    
    for i, group in enumerate(groups):
        output += f"\nGroup {i + 1}:\n"
        swim_avg = np.mean(swim_times[group])
        run_avg = np.mean(run_times[group])
        output += f"  Swim Average: {swim_avg:.3g}\n"
        output += f"  Run Average: {run_avg:.3g}\n"
        
        # Print header
        output += f"{'Bib Number':<20} {'Name':<30} {'Swim Time':<10} {'Run Time':<10}\n"
        output += "-" * 70 + "\n"
        
        for j in group:
            output += f"{bib_numbers[j]:<20} {full_names[j]:<30} {swim_times[j]:<10.3g} {run_times[j]:<10.3g}\n"

    return output

def display_heat_details_without_times(groups, full_names, bib_numbers, teams, gender):
    output = f"\n{gender.capitalize()} Round 1 Heats:\n"
    
    for i, group in enumerate(groups):
        output += f"\nHeat {i + 1}:\n"
        
        # Print header
        output += f"{'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n"
        output += "-" * 70 + "\n"
        
        for j in group:
            output += f"{bib_numbers[j]:<10} | {full_names[j]:<30} | {teams[j]:<20}\n"

    return output

def combined_display_heat_details(men_groups, male_names, male_swim_times, male_run_times, male_bibs, women_groups, female_names, female_swim_times, female_run_times, female_bibs):
    output = ""

    # Add men's groups
    output += display_heat_details(men_groups, male_names, male_swim_times, male_run_times, male_bibs, 'men')

    # Add women's groups
    output += display_heat_details(women_groups, female_names, female_swim_times, female_run_times, female_bibs, 'women')

    global save_directory
    
    # Ask user for a directory to save the file if not already set
    if not save_directory:
        save_directory = filedialog.askdirectory(title="Select Folder to Save Results")
    
    # Construct the file path for saving
    file_name = "Round1Director.txt"  # Adjust the filename as needed
    file_path = f"{save_directory}/{file_name}"

    # Save the output to the specified path
    with open(file_path, 'w') as f:
        f.write(output)
    
    messagebox.showinfo("Success", f"Data exported to {file_path}")

def combined_display_heat_details_without_times(men_groups, male_names, male_bibs, male_teams, women_groups, female_names, female_bibs, female_teams):
    output = ""

    # Add men's groups without times
    output += "\nMen Round 1 Heats:\n"
    for i, group in enumerate(men_groups):
        output += f"\nHeat {i + 1}:\n"
        output += f"{'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n"
        output += "-" * 70 + "\n"
        for j in group:
            output += f"{male_bibs[j]:<10} | {male_names[j]:<30} | {male_teams[j]:<20}\n"

    # Add women's groups without times
    output += "\nWomen Round 1 Heats:\n"
    for i, group in enumerate(women_groups):
        output += f"\nHeat {i + 1}:\n"
        output += f"{'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n"
        output += "-" * 70 + "\n"
        for j in group:
            output += f"{female_bibs[j]:<10} | {female_names[j]:<30} | {female_teams[j]:<20}\n"

    global save_directory
    
    # Ask user for a directory to save the file if not already set
    if not save_directory:
        save_directory = filedialog.askdirectory(title="Select Folder to Save Results")
    
    # Construct the file paths for saving
    text_file_name = "Round1Printout.txt"
    csv_file_name = "Round1Printout.csv"
    text_file_path = f"{save_directory}/{text_file_name}"
    csv_file_path = f"{save_directory}/{csv_file_name}"

    # Save the output to the text file
    with open(text_file_path, 'w') as f:
        f.write(output)
    
    # Prepare data for CSV export
    combined_data = []
    
    # Men's data: loop through each heat (group) and store all bibs, names, and teams
    for i, group in enumerate(men_groups):
        for j in group:
            combined_data.append(['Men', i + 1, male_names[j], male_bibs[j], male_teams[j]])
    
    # Women's data: loop through each heat (group) and store all bibs, names, and teams
    for i, group in enumerate(women_groups):
        for j in group:
            combined_data.append(['Women', i + 1, female_names[j], female_bibs[j], female_teams[j]])

    # Save the output to the CSV file
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Gender', 'Heat', 'Name', 'Bib', 'Team'])
        # Write the combined data
        writer.writerows(combined_data)

    messagebox.showinfo("Success", f"Data exported to {text_file_path} and {csv_file_path}")
       
        
#Round 1

def show_results_entry_window():
    global current_heat_index, current_entry_window, results_table_window, heat_bibs
    print(current_heat_index)
    
    # Check if there is a previous entry window and destroy it
    if 'current_entry_window' in globals() and current_entry_window is not None:
        current_entry_window.destroy()  # Close the previous entry window if it exists

    # Check if there are no more heats left
    if current_heat_index >= len(race_data['men'][0]):
        messagebox.showinfo("Notice", "All heats have been processed.")
        save_all_heats()
        create_round_2_heats()
        show_round_2_entry_window()
        return

    # Get the current heat indices and bib numbers
    heat_indices = race_data['men'][0][current_heat_index]
    print(heat_indices)
    heat_bibs = race_data['men'][4][heat_indices]
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
        global current_heat_index, heat_bibs, m_results_dfs

        bib_number = bib_entry.get().strip()
        if bib_number:
            heat_bibs_str = list(map(str, heat_bibs))

            if bib_number in heat_bibs_str:
                idx = heat_bibs_str.index(bib_number)

                full_name = race_data['men'][1][heat_indices[idx]]
                team = race_data['men'][5][heat_indices[idx]]
                bib = heat_bibs[idx]

                results_listbox.insert(tk.END, f"{bib} - {full_name} - {team}")

                # Check if the DataFrame for the current heat exists; if not, create it
                if current_heat_index not in m_results_dfs:
                    m_results_dfs[current_heat_index] = pd.DataFrame(columns=["Finish Order", "Bib Number", "Full Name", "Team"])

                m_results_dfs[current_heat_index].loc[len(m_results_dfs[current_heat_index])] = [len(m_results_dfs[current_heat_index]) + 1, bib, full_name, team]
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
    if current_heat_index in m_results_dfs:
        for index, row in m_results_dfs[current_heat_index].iterrows():
            tree.insert("", tk.END, values=(index + 1, row["Bib Number"], row["Full Name"], row["Team"]))

    # Add buttons for saving and continuing to the next heat
    edit_entry_button = tk.Button(results_table_window, text="Edit Selected", command=lambda: edit_entry(tree))
    edit_entry_button.pack(pady=10)

    next_heat_button = tk.Button(results_table_window, text="Next Heat", command=lambda: (save_results(tree), results_table_window.destroy(), show_results_entry_window()))
    next_heat_button.pack(pady=10)

    
def edit_entry(tree):
    global m_results_dfs, current_heat_index  # Declare globals

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select an entry to edit.")
        return

    # Get selected row data
    item = tree.item(selected_item)
    finish_order, bib_number, full_name, team = item['values']

    # Check if the DataFrame for the current heat exists
    if current_heat_index not in m_results_dfs:
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
            results_df = m_results_dfs[current_heat_index]
            
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

        # Optionally, update the original m_results_dfs with the new DataFrame
        m_results_dfs[current_heat_index] = results_df

        edit_window.destroy()  # Close the edit window

    # Button to save changes
    save_button = tk.Button(edit_window, text="Save Changes", command=save_changes)
    save_button.pack(pady=10)


def save_results(tree):
    global save_directory, current_heat_index
    # Construct the file path for saving
    file_name = f"Heat_{current_heat_index+1}_Results.txt"  # Adjust the filename for each heat
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
    global save_directory, m_results_dfs    
    # Construct the file path for saving
    file_name = "All_Heats_Results.txt"  # Adjust the filename as needed
    file_path = f"{save_directory}/{file_name}"

    with open(file_path, 'w') as f:
        for heat_index in sorted(m_results_dfs.keys()):
            f.write(f"Round 1 Heat {heat_index + 1} Results:\n")
            f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
            f.write(f"{'-' * 70}\n")
            
            # Write each row from the DataFrame with proper formatting
            for idx, row in m_results_dfs[heat_index].iterrows():
                f.write(f"{idx + 1:<10} | {row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")
            f.write("\n")  # Add some spacing between heats

    messagebox.showinfo("Success", f"All heat results compiled and saved to {file_path}")
    
def create_round_2_heats():
    global save_directory, m_results_dfs, current_heat_index, round_2_heats  # Add round_2_heats to globals
    file_name = "Round2Heats.txt"  # Adjust the filename as needed
    file_path = f"{save_directory}/{file_name}"

    # Create a new DataFrame to hold the Round 2 heats
    round_2_df = pd.DataFrame()

    # Initialize a list to store heat assignments for Round 2
    heat_numbers = []

    # Loop over each heat in Round 1 (m_results_dfs contains the DataFrames for each heat)
    for heat_index, (heat_name, heat_df) in enumerate(m_results_dfs.items()):
        # Sort the participants by their finishing order
        heat_df = heat_df.sort_index()

        # Calculate the number of participants in this heat
        num_participants = len(heat_df)
        two_thirds_index = (num_participants * 2) // 3  # Index for the top 66% cutoff

        # Assign top 2/3 participants to appropriate Round 2 heats
        top_two_thirds = heat_df.iloc[:two_thirds_index]
        bottom_one_third = heat_df.iloc[two_thirds_index:]

        # Populate Round 2 heats based on the heat index
        if heat_index == 0:  # Round 1 Heat 1 → Round 2 Heat 1
            round_2_df = pd.concat([round_2_df, top_two_thirds])
            heat_numbers.extend(["1"] * len(top_two_thirds))
            # Assign the bottom 1/3 to Heat 3
            round_2_df = pd.concat([round_2_df, bottom_one_third])
            heat_numbers.extend(["3"] * len(bottom_one_third))

        elif heat_index == 1:  # Round 1 Heat 2 → Split between Round 2 Heat 1 and Heat 2
            num_top_two_thirds = len(top_two_thirds)
            half_top_two_thirds = num_top_two_thirds // 2

            # Assign first half of top two-thirds to Heat 1
            round_2_df = pd.concat([round_2_df, top_two_thirds.iloc[:half_top_two_thirds]])
            heat_numbers.extend(["1"] * half_top_two_thirds)

            # Assign second half of top two-thirds to Heat 2
            round_2_df = pd.concat([round_2_df, top_two_thirds.iloc[half_top_two_thirds:]])
            heat_numbers.extend(["2"] * (num_top_two_thirds - half_top_two_thirds))

            # Assign the bottom one-third participants to Heat 3
            round_2_df = pd.concat([round_2_df, bottom_one_third])
            heat_numbers.extend(["3"] * len(bottom_one_third))

        elif heat_index == 2:  # Round 1 Heat 3 → Round 2 Heat 2
            round_2_df = pd.concat([round_2_df, top_two_thirds])
            heat_numbers.extend(["2"] * len(top_two_thirds))

            # Assign the bottom one-third participants to Heat 3
            round_2_df = pd.concat([round_2_df, bottom_one_third])
            heat_numbers.extend(["3"] * len(bottom_one_third))

    # Assign heat numbers to the DataFrame
    round_2_df['Heat'] = heat_numbers

    # Randomly select finishers with position #7 from m_results_dfs
        # Randomly select finishers with position #7 from m_results_dfs
    finishers_with_7 = []

    # Collect all finishers with rank 7 from each heat in m_results_dfs
    for heat_index, (heat_name, heat_df) in enumerate(m_results_dfs.items()):
        rank_7_participants = heat_df[heat_df['Finish Order'] == 7]  # Adjusted to use the correct column name

        if not rank_7_participants.empty:
            finishers_with_7.append(rank_7_participants)
            # Remove the rank 7 participants from their original heat
            m_results_dfs[heat_name] = heat_df[heat_df['Finish Order'] != 7]

    # Combine all the rank 7 finishers into a single DataFrame
    if len(finishers_with_7) >= 3:
        all_rank_7_participants = pd.concat(finishers_with_7)

        # Randomly select 2 out of the 3 or more rank 7 athletes
        selected_finishers = all_rank_7_participants.sample(n=2)

        # Remove the selected rank 7 finishers from Heat 3 if they are there
        heat_3_finishers = round_2_df[round_2_df['Heat'] == "3"]
        selected_ids = selected_finishers['Bib Number'].tolist()

        # Remove those from Heat 3 who are being reassigned to Heat 1 or 2
        round_2_df = round_2_df[~((round_2_df['Heat'] == "3") & (round_2_df['Bib Number'].isin(selected_ids)))]

        # Assign the selected finishers to Heat 1 and Heat 2
        for i, (_, selected_finisher) in enumerate(selected_finishers.iterrows()):
            round_2_df = pd.concat([round_2_df, pd.DataFrame([selected_finisher])], ignore_index=True)
            round_2_df.iloc[-1, round_2_df.columns.get_loc('Heat')] = f'{i + 1}'

    # Save the heats to a file
    with open(file_path, 'w') as f:
        for heat_index in sorted(round_2_df['Heat'].unique()):
            f.write(f"Round 2 {heat_index}\n")
            f.write(f"{'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
            f.write(f"{'-' * 70}\n")

            # Filter by current heat
            heat_participants = round_2_df[round_2_df['Heat'] == heat_index]

            for idx, row in heat_participants.iterrows():
                f.write(f"{row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")
            f.write("\n")  # Add some spacing between heats

    messagebox.showinfo("Success", f"Round 2 heats have been compiled and saved to {file_path}")

    current_heat_index = 0
    round_2_heats = round_2_df  # Assign the populated DataFrame to round_2_heats
    return round_2_df



# Round 2
def show_round_2_entry_window():
    global current_heat_index, current_entry_window, results_table_window, round_2_heats, heat_bibs_2

    # Check if there is a previous entry window and destroy it
    if 'current_entry_window' in globals() and current_entry_window is not None:
        current_entry_window.destroy()  # Close the previous entry window if it exists

    # Check if there are no more heats left
    if current_heat_index >= len(round_2_heats['Heat'].unique()):
        messagebox.showinfo("Notice", "All Round 2 heats have been processed.")
        save_all_heats2()  # Save all heats
        create_round_3_heat()
        show_round_3_entry_window()
        return

    # Get the DataFrame for the current heat
    current_heat_df = round_2_heats[round_2_heats['Heat'] == str(current_heat_index + 1)]
    
    # Get the corresponding Bib Numbers for the current heat
    heat_bibs_2 = current_heat_df['Bib Number'].tolist()

    # Debugging prints
    print(f"Current heat index: {current_heat_index}")
    print(f"Heat Bibs 2: {heat_bibs_2}")

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

    # Dictionary to store data for editing
    edit_dict = {"selected_index": None}

    def add_entry(event=None):
        try:
            global current_heat_index, round_2_m_results_dfs

            bib_number = bib_entry.get().strip()
            if bib_number:
                heat_bibs_str = list(map(str, heat_bibs_2))  # Convert all round 2 bibs to string

                if bib_number in heat_bibs_str:
                    idx = heat_bibs_str.index(bib_number)

                    # Get full name and team from round 2 heat data
                    full_name = current_heat_df.iloc[idx]['Full Name']
                    team = current_heat_df.iloc[idx]['Team']
                    bib = heat_bibs_2[idx]

                    if edit_dict["selected_index"] is not None:
                        # Editing an existing entry
                        results_listbox.delete(edit_dict["selected_index"])
                        results_listbox.insert(edit_dict["selected_index"], f"{bib} - {full_name} - {team}")
                        
                        round_2_m_results_dfs[current_heat_index].iloc[edit_dict["selected_index"]] = [edit_dict["selected_index"] + 1, bib, full_name, team]
                        edit_dict["selected_index"] = None
                        bib_entry.delete(0, tk.END)
                        bib_entry.config(state=tk.NORMAL)
                    else:
                        # Adding a new entry
                        results_listbox.insert(tk.END, f"{bib} - {full_name} - {team}")

                        # Check if the DataFrame for the current heat exists; if not, create it
                        if current_heat_index not in round_2_m_results_dfs:
                            round_2_m_results_dfs[current_heat_index] = pd.DataFrame(columns=["Finish Order", "Bib Number", "Full Name", "Team"])

                        round_2_m_results_dfs[current_heat_index].loc[len(round_2_m_results_dfs[current_heat_index])] = [len(round_2_m_results_dfs[current_heat_index]) + 1, bib, full_name, team]
                        bib_entry.delete(0, tk.END)

                    # If all entries for the current heat are entered, disable the entry field
                    if len(results_listbox.get(0, tk.END)) == len(heat_bibs_2):
                        bib_entry.config(state=tk.DISABLED)
                        show_results_table2()  # Show results table for the current heat
                        print("All entries entered for this heat. Moving to next heat...")
                else:
                    messagebox.showwarning("Warning", "Bib number not found in this heat.")
        except Exception as e:
            print(f"Error occurred: {e}")  # Print the error for debugging

    def edit_entry(event=None):
        try:
            # Get the selected item from the listbox
            selected_index = results_listbox.curselection()
            if selected_index:
                selected_index = selected_index[0]
                selected_item = results_listbox.get(selected_index)

                # Parse the bib number from the selected item
                bib_number = selected_item.split(" - ")[0]
                bib_entry.delete(0, tk.END)
                bib_entry.insert(0, bib_number)

                # Set the selected index for editing
                edit_dict["selected_index"] = selected_index
                bib_entry.config(state=tk.NORMAL)
                bib_entry.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit entry: {str(e)}")

    # Bind the return key to trigger add_entry
    bib_entry.bind("<Return>", add_entry)
    
    # Bind double-click event to trigger edit_entry
    results_listbox.bind("<Double-Button-1>", edit_entry)

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
    if current_heat_index in round_2_m_results_dfs:
        for index, row in round_2_m_results_dfs[current_heat_index].iterrows():
            tree.insert("", tk.END, values=(index + 1, row["Bib Number"], row["Full Name"], row["Team"]))

    # Add buttons for saving and continuing to the next heat
    edit_entry_button = tk.Button(results_table_window, text="Edit Selected", command=lambda: edit_entry2(tree))
    edit_entry_button.pack(pady=10)
    
    next_heat_button = tk.Button(results_table_window, text="Next Heat", command=lambda: (save_results2(tree), results_table_window.destroy(), show_round_2_entry_window()))
    next_heat_button.pack(pady=10)
    
def edit_entry2(tree):
    global round_2_m_results_dfs, current_heat_index

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select an entry to edit.")
        return

    # Get selected row data
    item = tree.item(selected_item)
    finish_order, bib_number, full_name, team = item['values']

    # Check if the DataFrame for the current heat exists in Round 2 results
    if current_heat_index not in round_2_m_results_dfs:
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
            results_df = round_2_m_results_dfs[current_heat_index]

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
        round_2_m_results_dfs[current_heat_index] = results_df

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
    global save_directory, round_2_m_results_dfs
    file_name = "Round_2_All_Results.txt"
    file_path = f"{save_directory}/{file_name}"

    with open(file_path, 'w') as f:
        f.write("Round 2 All Heats Results:\n")
        for heat_index, df in round_2_m_results_dfs.items():
            f.write(f"\nResults for Heat {heat_index + 1}:\n")
            f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
            f.write(f"{'-' * 70}\n")
            for i, row in df.iterrows():
                f.write(f"{i + 1:<10} | {row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")
    messagebox.showinfo("Success", f"All Round 2 results saved to {file_path}")
    
def create_round_3_heat():
    global save_directory, round_2_heats, round_3_df  # Include round_3_df in the global statement

    # Create a new DataFrame to hold the Round 3 participants
    round_3_df = pd.DataFrame()

    # Filter participants from Heat 1 and Heat 2 in Round 2
    heat_1_participants = round_2_heats[round_2_heats['Heat'] == "1"]
    heat_2_participants = round_2_heats[round_2_heats['Heat'] == "2"]

    # Calculate the number of top 50% participants from each heat
    top_50_heat_1 = heat_1_participants.iloc[:len(heat_1_participants) // 2]
    top_50_heat_2 = heat_2_participants.iloc[:len(heat_2_participants) // 2]

    # Combine the top 50% from both heats into Round 3
    round_3_df = pd.concat([top_50_heat_1, top_50_heat_2], ignore_index=True)

    # Assign all participants to Heat 1 for Round 3
    round_3_df['Heat'] = "1"

    # Save the Round 3 heat data to a file
    file_name = "Round3Heat.txt"
    file_path = f"{save_directory}/{file_name}"

    with open(file_path, 'w') as f:
        f.write("Round 3 Heat 1:\n")
        f.write(f"{'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
        f.write(f"{'-' * 70}\n")

        # Write the participants to the file
        for idx, row in round_3_df.iterrows():
            f.write(f"{row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")
    
    messagebox.showinfo("Success", f"Round 3 heat has been compiled and saved to {file_path}")

    return round_3_df

#Round 3
def show_round_3_entry_window():
    global round_3_df, current_round_3_entry_window, m_round_3_results_df, heat_bibs_3

    # Check if there is an existing entry window and destroy it
    if 'current_round_3_entry_window' in globals() and current_round_3_entry_window is not None:
        current_round_3_entry_window.destroy()

    # Create a new entry window for Round 3
    current_round_3_entry_window = tk.Toplevel()
    current_round_3_entry_window.title("Round 3 Heat 1 Results Entry")

    # Set the size of the window
    window_width = 400
    window_height = 400
    screen_width = current_round_3_entry_window.winfo_screenwidth()
    screen_height = current_round_3_entry_window.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    current_round_3_entry_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Get Bib Numbers for the heat
    heat_bibs_3 = round_3_df['Bib Number'].tolist()

    # Add label and entry for Bib Number input
    tk.Label(current_round_3_entry_window, text="Enter Bib Number:").grid(row=0, column=0, padx=10, pady=10)
    bib_entry = tk.Entry(current_round_3_entry_window)
    bib_entry.grid(row=0, column=1, padx=10, pady=10)
    bib_entry.focus_set()

    # Add a Listbox to display the results
    results_listbox = tk.Listbox(current_round_3_entry_window)
    results_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # Configure grid layout for resizing
    current_round_3_entry_window.grid_rowconfigure(1, weight=1)
    current_round_3_entry_window.grid_columnconfigure(0, weight=1)
    current_round_3_entry_window.grid_columnconfigure(1, weight=1)

    # Dictionary to store selected entry for editing
    edit_dict = {"selected_index": None}

    def add_entry(event=None):
        try:
            global m_round_3_results_df

            bib_number = bib_entry.get().strip()
            if bib_number:
                heat_bibs_str = list(map(str, heat_bibs_3))  # Convert all bibs to strings

                if bib_number in heat_bibs_str:
                    idx = heat_bibs_str.index(bib_number)

                    # Get full name and team from round_3_df
                    full_name = round_3_df.iloc[idx]['Full Name']
                    team = round_3_df.iloc[idx]['Team']
                    bib = heat_bibs_3[idx]

                    if edit_dict["selected_index"] is not None:
                        # Editing an existing entry
                        results_listbox.delete(edit_dict["selected_index"])
                        results_listbox.insert(edit_dict["selected_index"], f"{bib} - {full_name} - {team}")
                        
                        m_round_3_results_df.iloc[edit_dict["selected_index"]] = [edit_dict["selected_index"] + 1, bib, full_name, team]
                        edit_dict["selected_index"] = None
                        bib_entry.delete(0, tk.END)
                        bib_entry.config(state=tk.NORMAL)
                    else:
                        # Adding a new entry
                        results_listbox.insert(tk.END, f"{bib} - {full_name} - {team}")

                        if m_round_3_results_df.empty:
                            m_round_3_results_df = pd.DataFrame(columns=["Finish Order", "Bib Number", "Full Name", "Team"])

                        m_round_3_results_df.loc[len(m_round_3_results_df)] = [len(m_round_3_results_df) + 1, bib, full_name, team]
                        bib_entry.delete(0, tk.END)

                    # Disable entry field when all bibs are entered
                    if len(results_listbox.get(0, tk.END)) == len(heat_bibs_3):
                        bib_entry.config(state=tk.DISABLED)
                        show_results_table3()  # Show results table for Round 3
                        save_results3(results_listbox)
                        combine_all_rounds_results()
                else:
                    messagebox.showwarning("Warning", "Bib number not found in this heat.")
        except Exception as e:
            print(f"Error occurred: {e}")



    def edit_entry(event=None):
        try:
            selected_index = results_listbox.curselection()
            if selected_index:
                selected_index = selected_index[0]
                selected_item = results_listbox.get(selected_index)

                bib_number = selected_item.split(" - ")[0]
                bib_entry.delete(0, tk.END)
                bib_entry.insert(0, bib_number)

                edit_dict["selected_index"] = selected_index
                bib_entry.config(state=tk.NORMAL)
                bib_entry.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit entry: {str(e)}")

    # Bind return key to add entry
    bib_entry.bind("<Return>", add_entry)

    # Bind double-click event to edit entry
    results_listbox.bind("<Double-Button-1>", edit_entry)

def show_results_table3():
    global m_round_3_results_df

    # Create a new window to display the results table
    results_table_window = tk.Toplevel()
    results_table_window.title("Results Table for Round 3 Heat 1")
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

    # Populate the treeview with data from the results DataFrame
    for index, row in m_round_3_results_df.iterrows():
        tree.insert("", tk.END, values=(index + 1, row["Bib Number"], row["Full Name"], row["Team"]))

    # Add buttons for saving, editing, and continuing
    edit_entry_button = tk.Button(results_table_window, text="Edit Selected", command=lambda: edit_entry3(tree))
    edit_entry_button.pack(pady=10)

    # Add a Save button that will close the windows when clicked
    save_results_button = tk.Button(results_table_window, text="Save Results", command=lambda: save_results3(tree, results_table_window))
    save_results_button.pack(pady=10)
    
def edit_entry3(tree):
    global m_round_3_results_df

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select an entry to edit.")
        return

    # Get selected row data
    item = tree.item(selected_item)
    finish_order, bib_number, full_name, team = item['values']

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
        global m_round_3_results_df  # Declare m_round_3_results_df as global

        # Get the new finish order from the entry
        new_finish_order = finish_order_entry.get()

        # Validate the new finish order
        try:
            new_finish_order_index = int(new_finish_order) - 1  # Convert to zero-based index

            # Check if the new index is valid
            if new_finish_order_index < 0 or new_finish_order_index >= len(m_round_3_results_df):
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

        # Update the results DataFrame with the new order
        m_round_3_results_df = pd.DataFrame(new_order, columns=["Finish Order", "Bib Number", "Full Name", "Team"])
        m_round_3_results_df["Finish Order"] = range(1, len(m_round_3_results_df) + 1)  # Update the Finish Order column

        # Update the Treeview
        tree.delete(*tree.get_children())  # Clear the Treeview
        for idx, row in m_round_3_results_df.iterrows():
            tree.insert("", tk.END, values=(row["Finish Order"], row["Bib Number"], row["Full Name"], row["Team"]))

        edit_window.destroy()  # Close the edit window

    # Button to save changes
    save_button = tk.Button(edit_window, text="Save Changes", command=save_changes)
    save_button.pack(pady=10)

def save_results3(tree, window):
    global save_directory, m_round_3_results_df, current_round_3_entry_window

    # Define file path to save results
    file_name = "Round_3_Heat_1_Results.txt"
    file_path = f"{save_directory}/{file_name}"

    with open(file_path, 'w') as f:
        f.write("Round 3 Heat 1 Results:\n")
        f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
        f.write(f"{'-' * 70}\n")
        
        # Write each result from the treeview
        for i, row_id in enumerate(tree.get_children(), start=1):
            row = tree.item(row_id)["values"]
            f.write(f"{i:<10} | {row[1]:<10} | {row[2]:<30} | {row[3]:<20}\n")
    
    messagebox.showinfo("Success", f"Round 3 Heat 1 results saved to {file_path}")

    # Close the Round 3 entry window and results table window after saving
    if current_round_3_entry_window is not None:
        current_round_3_entry_window.destroy()  # Close the Round 3 entry window
    window.destroy()  # Close the Results Table window

    combine_all_rounds_results()
        
        
def combine_all_rounds_results():
    global save_directory, m_results_dfs, round_2_m_results_dfs, m_round_3_results_df

    # File path to save the combined results
    file_name = "All_Rounds_Results.txt"
    file_path = f"{save_directory}/{file_name}"

    with open(file_path, 'w') as f:
        # Writing Round 1 results
        f.write("Round 1 Results:\n")
        for heat_index, df in m_results_dfs.items():
            f.write(f"\nRound 1 Heat {heat_index + 1}:\n")
            f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
            f.write(f"{'-' * 70}\n")
            for i, row in df.iterrows():
                f.write(f"{i + 1:<10} | {row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")
        
        # Writing Round 2 results
        f.write("\n\n\nRound 2 Results:\n")
        for heat_index, df in round_2_m_results_dfs.items():
            f.write(f"\nRound 2 Heat {heat_index + 1}:\n")
            f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
            f.write(f"{'-' * 70}\n")
            for i, row in df.iterrows():
                f.write(f"{i + 1:<10} | {row['Bib Number']:<10} | {row['Full Name']:<30} | {row['Team']:<20}\n")
        
        # Writing Round 3 results
        f.write("\n\n\nRound 3 Results:\n")
        f.write(f"{'Rank':<10} | {'Bib Number':<10} | {'Name':<30} | {'Team':<20}\n")
        f.write(f"{'-' * 70}\n")
        for i, row in m_round_3_results_df.iterrows():
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
        load_button = tk.Button(button_frame, text="Load Racers", command=load_and_sort_racers_and_save_heats)
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
