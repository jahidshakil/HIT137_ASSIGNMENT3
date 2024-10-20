# Q1
# Task: Create a Tkinter application
# Name: Charles O Duku
# Date: 18 October 2024

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from abc import ABC, abstractmethod

# Base class demonstrating abstraction (enforcing method to be implemented by child classes)
class Converter(ABC):
    @abstractmethod
    def convert(self, value):
        pass

# Inheriting the Converter class and implementing conversion
class TemperatureConverter(Converter):
    def fahrenheit_to_celsius(self, f):
        return (f - 32) * 5 / 9
    
    def convert(self, value):
        # Encapsulated conversion logic
        return self.fahrenheit_to_celsius(value)

# UI Frame for the converter
class ConverterFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.converter = TemperatureConverter()  # Object of TemperatureConverter class

        # field options
        options = {'padx': 5, 'pady': 5}

        # temperature label
        self.__temperature_label = ttk.Label(self, text='Fahrenheit')  # Encapsulating UI labels as private
        self.__temperature_label.grid(column=0, row=0, sticky=tk.W, **options)

        # temperature entry
        self.__temperature = tk.StringVar()
        self.__temperature_entry = ttk.Entry(self, textvariable=self.__temperature)
        self.__temperature_entry.grid(column=1, row=0, **options)
        self.__temperature_entry.focus()

        # convert button
        self.__convert_button = ttk.Button(self, text='Convert', command=self.convert)
        self.__convert_button.grid(column=2, row=0, sticky=tk.W, **options)

        # result label
        self.__result_label = ttk.Label(self)
        self.__result_label.grid(row=1, columnspan=3, **options)

        # add padding to the frame and show it
        self.grid(padx=10, pady=10, sticky=tk.NSEW)

    def convert(self):
        try:
            # Encapsulation: using getter to access entry value
            f = float(self.__get_temperature_value())
            c = self.converter.convert(f)
            result = f'{f} Fahrenheit = {c:.2f} Celsius'
            self.__result_label.config(text=result)
        except ValueError as error:
            showerror(title='Error', message="Please enter a valid number.")

    # Getter and setter methods to encapsulate access to temperature value
    def __get_temperature_value(self):
        return self.__temperature.get()

    def __set_temperature_value(self, value):
        self.__temperature.set(value)

# App class that inherits from Tk (demonstrating inheritance)
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Temperature Converter')
        self.geometry('300x70')
        self.resizable(False, False)

        # Initialize the converter frame
        ConverterFrame(self)

if __name__ == "__main__":
    app = App()
    app.mainloop()

# # How it works: Explainations
# The ConverterFrame needs a container, therefore, its __init__() method has the container argument.
# Inside the __init__() method of the ConverterCFrame class, call the __init__() method of its superclass.
# Assign the widgets to the self object so that you can reference them in other methods of the ConverterFrame class.
# Assign the command option of the convert button to the self.convert method.
# Third, define an App class that inherits from the tk.Tk class:
