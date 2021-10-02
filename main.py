# coding=utf-8
# This is a sample Python script.

# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import csv
import json
import tkinter as tk

# Function to convert a CSV to JSON
# Takes the file paths as arguments
def run_app():
    window = tk.Tk()
    greeting = tk.Label(text="MAG Cartography Metadata", # Set the text color to white
    background="#34A2FE")  # Set the background color to black)
    greeting.pack()
    button = tk.Button(
        text="Upload",
        width=25,
        height=5,
        bg="grey",
        fg="black",
    )
    button.pack()
    window.mainloop()

# Driver Code

# Decide the two file paths according to your
# computer system


# Call the make_json function

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    run_app()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
