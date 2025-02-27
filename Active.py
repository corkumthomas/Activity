#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import json
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, date, timedelta
import numpy as np


class WorkoutTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Workout Tracker")
        self.root.geometry("900x900")
        
        # Challenge parameters
        self.challenge_start = datetime(2025, 2, 1).date()
        self.challenge_end = datetime(2026, 2, 1).date()
        self.elevation_goal = 100000  # meters
        
        # Data storage
        self.workouts = []
        self.activities = ["Bike", "Run", "Hike", "Ski Tour"]
        self.filename = "workout_history.json"
        
        # Load existing data
        self.load_data()
        
        # Configure styles
        self.setup_styles()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill='both')
        
        # Create tabs - Stats first
        self.stats_frame = ttk.Frame(self.notebook)
        self.input_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.stats_frame, text="Statistics")
        self.notebook.add(self.input_frame, text="Add Workout")
        self.notebook.add(self.history_frame, text="History")
        
        self.setup_stats_tab()
        self.setup_input_tab()
        self.setup_history_tab()

    def setup_styles(self):
        style = ttk.Style()
        
        # Configure progress bar
        style.configure("Challenge.Horizontal.TProgressbar",
                       background='#4CAF50',
                       troughcolor='#f0f0f0')
        
        # Configure headers
        style.configure("Header.TLabel",
                       font=('TkDefaultFont', 10, 'bold'))
        
        # Configure frames
        style.configure("Card.TFrame",
                       background='#ffffff')




    def setup_stats_tab(self):
        # Create main container for stats
        stats_container = ttk.Frame(self.stats_frame)
        stats_container.pack(fill='both', expand=True)
        
        # Upper section for challenge and overall stats
        upper_section = ttk.Frame(stats_container)
        upper_section.pack(fill='both', expand=True, pady=(0, 10))
        
        # Challenge frame
        challenge_frame = ttk.LabelFrame(upper_section, text="Elevation Challenge Progress", padding=10)
        challenge_frame.pack(fill='x', padx=10, pady=5)
        
        # Overall frame
        overall_frame = ttk.LabelFrame(upper_section, text="Overall Statistics", padding=10)
        overall_frame.pack(fill='x', padx=10, pady=5)
        
        # Activities frame
        activities_frame = ttk.LabelFrame(upper_section, text="Activity Breakdown", padding=10)
        activities_frame.pack(fill='x', padx=10, pady=5)
        
        # Lower section for graph
        graph_frame = ttk.LabelFrame(stats_container, text="Elevation Progress", padding=10)
        graph_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Setup graph controls and container
        self.setup_graph_controls(graph_frame)
        
        # Create initial graph
        self.create_graph(graph_frame)
        
        # Challenge Progress Section
        challenge_stats = self.calculate_challenge_stats()
        
        # Progress bar frame
        progress_frame = ttk.Frame(challenge_frame)
        progress_frame.pack(fill='x', pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame,
                                          style="Challenge.Horizontal.TProgressbar",
                                          length=300,
                                          mode='determinate')
        self.progress_bar.pack(side='left', padx=(0, 10))
        self.progress_bar['value'] = min(100, challenge_stats['progress_percentage'])
        
        # Progress percentage label
        progress_label = ttk.Label(progress_frame,
                                 text=f"{challenge_stats['progress_percentage']:.1f}%",
                                 style="Header.TLabel")
        progress_label.pack(side='left')
        
        # Challenge stats grid
        stats_grid = ttk.Frame(challenge_frame)
        stats_grid.pack(fill='x')
        
        # Left column
        ttk.Label(stats_grid, text="Current Progress:",
                 style="Header.TLabel").grid(row=0, column=0, sticky='w', padx=5)
        ttk.Label(stats_grid,
                 text=f"{challenge_stats['challenge_elevation']:,.0f}m / {self.elevation_goal:,}m"
                 ).grid(row=0, column=1, sticky='w', padx=5)
        
        ttk.Label(stats_grid, text="Remaining:",
                 style="Header.TLabel").grid(row=1, column=0, sticky='w', padx=5)
        ttk.Label(stats_grid,
                 text=f"{challenge_stats['remaining_elevation']:,.0f}m"
                 ).grid(row=1, column=1, sticky='w', padx=5)
        
        # Right column
        ttk.Label(stats_grid, text="Days Remaining:",
                 style="Header.TLabel").grid(row=0, column=2, sticky='w', padx=5)
        ttk.Label(stats_grid,
                 text=f"{challenge_stats['days_remaining']} days"
                 ).grid(row=0, column=3, sticky='w', padx=5)
        
        ttk.Label(stats_grid, text="Required Daily:",
                 style="Header.TLabel").grid(row=1, column=2, sticky='w', padx=5)
        ttk.Label(stats_grid,
                 text=f"{challenge_stats['required_daily_avg']:.1f}m"
                 ).grid(row=1, column=3, sticky='w', padx=5)
        
        # Bottom row - Yearly average target
        yearly_target = self.elevation_goal / 365
        ttk.Label(stats_grid, text="Yearly Daily Target:",
                 style="Header.TLabel").grid(row=2, column=0, sticky='w', padx=5)
        ttk.Label(stats_grid,
                 text=f"{yearly_target:.1f}m per day"
                 ).grid(row=2, column=1, columnspan=3, sticky='w', padx=5)
        
        # Overall Stats Section
        total_distance = sum(w['distance'] for w in self.workouts)
        total_elevation = sum(w['elevation'] for w in self.workouts)
        
        overall_grid = ttk.Frame(overall_frame)
        overall_grid.pack(fill='x')
        
        ttk.Label(overall_grid, text="Total Distance:",
                 style="Header.TLabel").grid(row=0, column=0, sticky='w', padx=5)
        ttk.Label(overall_grid,
                 text=f"{total_distance:,.1f} km"
                 ).grid(row=0, column=1, sticky='w', padx=5)
        
        ttk.Label(overall_grid, text="Total Elevation:",
                 style="Header.TLabel").grid(row=1, column=0, sticky='w', padx=5)
        ttk.Label(overall_grid,
                 text=f"{total_elevation:,.0f} m"
                 ).grid(row=1, column=1, sticky='w', padx=5)
        
        # Activity Breakdown Section
        columns = ("Activity", "Count", "Distance", "Elevation")
        self.activity_tree = ttk.Treeview(activities_frame, columns=columns,
                                        show="headings", height=6)
        
        # Set column headings and widths
        column_widths = {
            "Activity": 150,
            "Count": 100,
            "Distance": 150,
            "Elevation": 150
        }
        
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=column_widths[col])
        
        self.activity_tree.pack(fill='both', expand=True)
        
        # Add activity data
        for activity in self.activities:
            activity_workouts = [w for w in self.workouts if w['activity'] == activity]
            count = len(activity_workouts)
            distance = sum(w['distance'] for w in activity_workouts)
            elevation = sum(w['elevation'] for w in activity_workouts)
            
            self.activity_tree.insert("", "end", values=(
                activity,
                count,
                f"{distance:,.1f} km",
                f"{elevation:,.0f} m"
            ))

    def setup_input_tab(self):
        input_frame = ttk.Frame(self.input_frame, padding=20)
        input_frame.pack(expand=True)
        
        # Activity selection
        ttk.Label(input_frame, text="Activity:", style="Header.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.activity_var = tk.StringVar()
        activity_combo = ttk.Combobox(input_frame, textvariable=self.activity_var, values=self.activities, width=30)
        activity_combo.grid(row=0, column=1, padx=5, pady=5)
        activity_combo.set(self.activities[0])
        
        # Date input
        ttk.Label(input_frame, text="Date:", style="Header.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.date_var = tk.StringVar()
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(input_frame, textvariable=self.date_var, width=32).grid(row=1, column=1, padx=5, pady=5)
        
        # Distance input
        ttk.Label(input_frame, text="Distance (km):", style="Header.TLabel").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.distance_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.distance_var, width=32).grid(row=2, column=1, padx=5, pady=5)
        
        # Elevation input
        ttk.Label(input_frame, text="Elevation Gain (m):", style="Header.TLabel").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.elevation_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.elevation_var, width=32).grid(row=3, column=1, padx=5, pady=5)
        
        # Save button
        save_button = ttk.Button(input_frame, text="Save Workout", command=self.save_workout, padding=10)
        save_button.grid(row=4, column=0, columnspan=2, pady=20)

    def setup_history_tab(self):
        # Create treeview for workout history
        columns = ("Date", "Activity", "Distance", "Elevation")
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns, show="headings")
        
        # Set column headings and widths
        column_widths = {
            "Date": 150,
            "Activity": 150,
            "Distance": 150,
            "Elevation": 150
        }
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=column_widths[col])
        
        # Pack the treeview with scrollbar
        self.history_tree.pack(pady=10, padx=10, expand=True, fill='both')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Delete button
        delete_button = ttk.Button(self.history_frame, text="Delete Selected", command=self.delete_workout, padding=10)
        delete_button.pack(pady=10)
        
        # Load existing workouts into history
        self.update_history()

    def calculate_challenge_stats(self):
        today = date.today()
        
        # Calculate elevation gain during challenge period
        challenge_elevation = sum(w['elevation'] for w in self.workouts 
                                if self.challenge_start <= datetime.strptime(w['date'], "%Y-%m-%d").date() <= self.challenge_end)
        
        # Calculate remaining elevation needed
        remaining_elevation = max(0, self.elevation_goal - challenge_elevation)
        
        # Calculate days elapsed and remaining in challenge
        if today < self.challenge_start:
            days_elapsed = 0
            days_remaining = (self.challenge_end - self.challenge_start).days
        elif today > self.challenge_end:
            days_elapsed = (self.challenge_end - self.challenge_start).days
            days_remaining = 0
        else:
            days_elapsed = (today - self.challenge_start).days
            days_remaining = (self.challenge_end - today).days
        
        # Calculate progress percentage
        progress_percentage = (challenge_elevation / self.elevation_goal) * 100
        
        # Calculate required daily average for remaining days
        required_daily_avg = remaining_elevation / max(1, days_remaining) if days_remaining > 0 else 0
        
        # Calculate current daily average
        current_daily_avg = challenge_elevation / max(1, days_elapsed) if days_elapsed > 0 else 0
        
        return {
            'challenge_elevation': challenge_elevation,
            'remaining_elevation': remaining_elevation,
            'progress_percentage': progress_percentage,
            'required_daily_avg': required_daily_avg,
            'current_daily_avg': current_daily_avg,
            'days_remaining': days_remaining
        }
    
# Add this method to calculate daily data
    def calculate_daily_data(self, days=14):
        """Calculate daily elevation data for the specified number of recent days"""
        if not self.workouts:
            return {'dates': [], 'totals': []}
        
        # Convert workout data to DataFrame
        df = pd.DataFrame(self.workouts)
        df['date'] = pd.to_datetime(df['date'])
        
        # Set the date range for the last N days
        end_date = max(df['date'])
        start_date = end_date - timedelta(days=days-1)  # Show last N days
        
        # Create a date range for all days in the period
        date_range = pd.date_range(start=start_date, end=end_date)
        
        # Create daily bins for the elevation data
        df = df[df['date'] >= start_date]
        daily_totals = df.resample('D', on='date')['elevation'].sum().reindex(date_range).fillna(0)
        
        # Format date labels
        date_labels = [d.strftime('%b %d') for d in daily_totals.index]
        
        return {
            'dates': date_labels,
            'totals': daily_totals.values
        }

        # Add this method to create the daily graphs
        def create_daily_graphs(self, parent_frame):
            """Create daily elevation graphs for the last 14 days"""
            # Clear existing graphs
            for widget in parent_frame.winfo_children():
                widget.destroy()
            
            # Create a container for both graphs
            graphs_container = ttk.Frame(parent_frame)
            graphs_container.pack(fill='both', expand=True)
            
            # Create top frame for cumulative graph
            cumulative_frame = ttk.LabelFrame(graphs_container, text="Cumulative Elevation (Last 14 Days)", padding=10)
            cumulative_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            # Create bottom frame for daily graph
            daily_frame = ttk.LabelFrame(graphs_container, text="Daily Elevation (Last 14 Days)", padding=10)
            daily_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            # Get the daily data
            data = self.calculate_daily_data(days=14)
            
            if not data['dates']:  # If no data, return empty graphs
                for frame in [cumulative_frame, daily_frame]:
                    fig = Figure(figsize=(8, 2.5), dpi=100)
                    canvas = FigureCanvasTkAgg(fig, master=frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill='both', expand=True)
                return
            
            # Create cumulative graph
            fig_cumulative = Figure(figsize=(8, 2.5), dpi=100)
            ax_cumulative = fig_cumulative.add_subplot(111)
            
            # Calculate cumulative values
            cumulative = np.cumsum(data['totals'])
            
            # Plot actual cumulative data
            ax_cumulative.plot(range(len(data['dates'])), cumulative, 
                            marker='o', color='#4CAF50', linewidth=2, markersize=6, label='Actual')
            
            # Calculate and plot goal trend line
            challenge_stats = self.calculate_challenge_stats()
            remaining_days = challenge_stats['days_remaining']
            remaining_elevation = challenge_stats['remaining_elevation']
            
            if remaining_days > 0:
                daily_goal = remaining_elevation / remaining_days
                # For the 14-day window, calculate what the goal trend should be
                start_elevation = cumulative[0] if len(cumulative) > 0 else 0
                goal_line = start_elevation + np.arange(1, len(data['dates']) + 1) * daily_goal
                
                # Plot goal trend line
                ax_cumulative.plot(range(len(data['dates'])), goal_line, '--', 
                                color='#FF9800', linewidth=2, label='Goal Trend')
                
                # Add label for final goal value
                if len(goal_line) > 0:
                    final_goal = goal_line[-1]
                    ax_cumulative.text(len(data['dates']) - 1, final_goal + (max(cumulative) * 0.02),
                                    f'Goal: {int(final_goal):,}m', ha='center', va='bottom', color='#FF9800')
            
            # Add value labels for actual data
            for i, value in enumerate(cumulative):
                if i % 2 == 0:  # Add labels to every other point to avoid overcrowding
                    label_y = value + (max(cumulative) * 0.02) if len(cumulative) > 0 else value
                    ax_cumulative.text(i, label_y, f'{int(value):,}m', ha='center', va='bottom', fontsize=8)
            
            # Customize cumulative graph
            ax_cumulative.set_xticks(range(len(data['dates'])))
            ax_cumulative.set_xticklabels(data['dates'], rotation=45, ha='right', fontsize=8)
            ax_cumulative.set_ylabel('Elevation Gain (m)')
            ax_cumulative.grid(True, linestyle='--', alpha=0.7)
            ax_cumulative.legend()
            
            # Add some padding to the top of the graph for labels
            ax_cumulative.margins(y=0.1)
            
            # Adjust layout
            fig_cumulative.tight_layout()
            
            # Create canvas and add to frame
            canvas_cumulative = FigureCanvasTkAgg(fig_cumulative, master=cumulative_frame)
            canvas_cumulative.draw()
            canvas_cumulative.get_tk_widget().pack(fill='both', expand=True)
            
            # Create daily graph
            fig_daily = Figure(figsize=(8, 2.5), dpi=100)
            ax_daily = fig_daily.add_subplot(111)
            
            # Create bar chart for daily data
            bars = ax_daily.bar(range(len(data['dates'])), data['totals'], color='#4CAF50', alpha=0.8)
            
            # Add horizontal line for average daily needed
            if remaining_days > 0:
                avg_line = ax_daily.axhline(y=daily_goal, color='#FF9800', linestyle='--', linewidth=2, 
                                            label=f'Goal: {daily_goal:.0f}m/day')
                ax_daily.legend()
            
            # Add value labels
            for i, bar in enumerate(bars):
                height = bar.get_height()
                if height > 0:  # Only add labels to bars with values
                    ax_daily.text(bar.get_x() + bar.get_width()/2., height + (max(data['totals']) * 0.02),
                                f'{int(height):,}m', ha='center', va='bottom', fontsize=8)
            
            # Customize daily graph
            ax_daily.set_xticks(range(len(data['dates'])))
            ax_daily.set_xticklabels(data['dates'], rotation=45, ha='right', fontsize=8)
            ax_daily.set_ylabel('Elevation Gain (m)')
            ax_daily.grid(True, linestyle='--', alpha=0.7)
            
            # Add some padding to the top of the graph for labels
            ax_daily.margins(y=0.1)
            
            # Adjust layout
            fig_daily.tight_layout()
            
            # Create canvas and add to frame
            canvas_daily = FigureCanvasTkAgg(fig_daily, master=daily_frame)
            canvas_daily.draw()
            canvas_daily.get_tk_widget().pack(fill='both', expand=True)

    def create_weekly_graph(self, parent_frame):
        # Create figure and axis
        fig = Figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Calculate weekly totals
        weekly_data = self.calculate_weekly_totals()
        
        if not weekly_data['weeks']:  # If no data, return empty graph
            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            return
        
        # Create line graph
        line = ax.plot(range(len(weekly_data['weeks'])), 
                      weekly_data['totals'],
                      marker='o',  # Add markers at data points
                      color='#4CAF50',
                      linewidth=2,
                      markersize=6)
        
        # Customize graph
        ax.set_xticks(range(len(weekly_data['weeks'])))
        ax.set_xticklabels(weekly_data['weeks'], rotation=45, ha='right')
        ax.set_ylabel('Elevation Gain (m)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add value labels above points
        for i, value in enumerate(weekly_data['totals']):
            # Add small offset above each point
            label_y = value + (max(weekly_data['totals']) * 0.02)  # 2% of max value as offset
            ax.text(i, label_y, f'{int(value):,}m',
                    ha='center', va='bottom')
        
        # Add some padding to the top of the graph for labels
        ax.margins(y=0.2)
        
        # Adjust layout
        fig.tight_layout()
        
        # Create canvas and add to frame
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def setup_graph_controls(self, parent_frame):
        # Create control frame
        controls_frame = ttk.Frame(parent_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Create graph type selector
        ttk.Label(controls_frame, text="Graph Type:", style="Header.TLabel").pack(side='left', padx=5)
        self.graph_type = tk.StringVar(value="Daily Elevation")
        graph_combo = ttk.Combobox(controls_frame, 
                                textvariable=self.graph_type,
                                values=["Daily Elevation", "Daily Cumulative", "Weekly Elevation", "Weekly Cumulative", "Monthly Elevation", "Monthly Cumulative"],
                                state="readonly",
                                width=20)
        graph_combo.pack(side='left', padx=5)
        graph_combo.bind('<<ComboboxSelected>>', lambda e: self.update_graph())
        
        # Create frame for graph
        self.graph_container = ttk.Frame(parent_frame)
        self.graph_container.pack(fill='both', expand=True)

    # Modify the create_graph method to show total cumulative elevation for daily view

    def create_graph(self, parent_frame):
        # Clear existing graph
        for widget in self.graph_container.winfo_children():
            widget.destroy()
        
        # Create figure and axis
        fig = Figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        graph_type = self.graph_type.get()
        
        if "Daily" in graph_type:
            data = self.calculate_daily_data(days=14)  # Get data for the last 14 days
            x_labels = data['dates']
        elif "Weekly" in graph_type:
            data = self.calculate_weekly_data()
            x_labels = data['weeks']
        else:  # Monthly
            data = self.calculate_monthly_data()
            x_labels = data['months']
        
        if not x_labels:  # If no data, return empty graph
            canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            return
        
        if "Cumulative" in graph_type:
            if "Daily" in graph_type:
                # For daily cumulative, we want to show the total progress, not just within the window
                challenge_stats = self.calculate_challenge_stats()
                total_so_far = challenge_stats['challenge_elevation']
                
                # Calculate how much of that total came from the last 14 days
                recent_elevation = sum(data['totals'])
                
                # Start value is total minus what was gained in this window
                start_value = max(0, total_so_far - recent_elevation)
                
                # Create cumulative array starting from the overall progress
                daily_cumulative = start_value + np.cumsum(data['totals'])
                
                # Plot actual cumulative data
                line = ax.plot(range(len(x_labels)), 
                              daily_cumulative,
                              marker='o',
                              color='#4CAF50',
                              linewidth=2,
                              markersize=6,
                              label='Actual')
                
                # Calculate and plot goal trend line
                remaining_days = challenge_stats['days_remaining']
                remaining_elevation = challenge_stats['remaining_elevation']
                
                if remaining_days > 0:
                    daily_goal = remaining_elevation / remaining_days
                    current_progress = daily_cumulative[0] if len(daily_cumulative) > 0 else 0
                    goal_line = current_progress + np.arange(1, len(x_labels) + 1) * daily_goal
                    
                    # Plot goal trend line
                    ax.plot(range(len(x_labels)),
                           goal_line,
                           '--',
                           color='#FF9800',
                           linewidth=2,
                           label='Goal Trend')
                    
                    # Add final goal value label
                    if len(goal_line) > 0:
                        final_goal = goal_line[-1]
                        ax.text(len(x_labels) - 1, final_goal + (max(daily_cumulative) * 0.02),
                               f'Goal: {int(final_goal):,}m',
                               ha='center', va='bottom',
                               color='#FF9800')
                
                # Add value labels for actual data
                for i, value in enumerate(daily_cumulative):
                    if i % 2 == 0:  # Add labels to every other point to avoid overcrowding
                        label_y = value + (max(daily_cumulative) * 0.02)
                        ax.text(i, label_y, f'{int(value):,}m',
                               ha='center', va='bottom', fontsize=8)
            else:
                # Regular cumulative for weekly/monthly
                cumulative = np.cumsum(data['totals'])
                line = ax.plot(range(len(x_labels)), 
                              cumulative,
                              marker='o',
                              color='#4CAF50',
                              linewidth=2,
                              markersize=6,
                              label='Actual')
                
                # Calculate and plot goal trend line
                challenge_stats = self.calculate_challenge_stats()
                remaining_elevation = challenge_stats['remaining_elevation']
                
                if "Weekly" in graph_type:
                    total_weeks = (self.challenge_end - self.challenge_start).days / 7
                    weekly_goal = self.elevation_goal / total_weeks
                    goal_line = np.arange(1, len(x_labels) + 1) * weekly_goal
                else:
                    total_months = (self.challenge_end - self.challenge_start).days / 30.44  # Average month length
                    monthly_goal = self.elevation_goal / total_months
                    goal_line = np.arange(1, len(x_labels) + 1) * monthly_goal
                
                # Plot goal trend line
                ax.plot(range(len(x_labels)),
                       goal_line,
                       '--',
                       color='#FF9800',
                       linewidth=2,
                       label='Goal Trend')
                
                # Add value labels for actual data
                for i, value in enumerate(cumulative):
                    label_y = value + (max(cumulative) * 0.02)
                    ax.text(i, label_y, f'{int(value):,}m',
                           ha='center', va='bottom', fontsize=9)
                
                # Add label for final goal value only
                if len(goal_line) > 0:
                    final_goal = goal_line[-1]
                    ax.text(len(x_labels) - 1, final_goal + (max(cumulative) * 0.02),
                           f'Goal: {int(final_goal):,}m',
                           ha='center', va='bottom',
                           color='#FF9800')
            
            ax.legend()
            
        else:
            # For non-cumulative views
            if "Daily" in graph_type:
                # Use bar chart for daily elevation
                bars = ax.bar(range(len(x_labels)), data['totals'], color='#4CAF50', alpha=0.8)
                
                # Add horizontal line for daily goal if applicable
                challenge_stats = self.calculate_challenge_stats()
                if challenge_stats['days_remaining'] > 0:
                    daily_goal = challenge_stats['required_daily_avg']
                    ax.axhline(y=daily_goal, color='#FF9800', linestyle='--', linewidth=2, 
                             label=f'Goal: {daily_goal:.0f}m/day')
                    ax.legend()
                
                # Add value labels to bars
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    if height > 0:  # Only add labels to bars with values
                        ax.text(bar.get_x() + bar.get_width()/2., height + (max(data['totals']) * 0.02),
                              f'{int(height):,}m', ha='center', va='bottom', fontsize=8)
            else:
                # Use line chart for weekly and monthly
                line = ax.plot(range(len(x_labels)), 
                              data['totals'],
                              marker='o',
                              color='#4CAF50',
                              linewidth=2,
                              markersize=6)
                
                # Add value labels
                for i, value in enumerate(data['totals']):
                    label_y = value + (max(data['totals']) * 0.02)
                    ax.text(i, label_y, f'{int(value):,}m',
                            ha='center', va='bottom')
        
        # Customize graph
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8 if "Daily" in graph_type else 9)
        ax.set_ylabel('Elevation Gain (m)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add some padding to the top of the graph for labels
        ax.margins(y=0.2)
        
        # Adjust layout
        fig.tight_layout()
        
        # Create canvas and add to frame
        canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def calculate_weekly_data(self):
        if not self.workouts:
            return {'weeks': [], 'totals': []}
        
        # Convert workout data to DataFrame
        df = pd.DataFrame(self.workouts)
        df['date'] = pd.to_datetime(df['date'])
        
        # Set the date range
        end_date = max(df['date'])
        start_date = end_date - timedelta(weeks=11)  # Show last 12 weeks
        
        # Create weekly bins
        df = df[df['date'] >= start_date]
        weekly_totals = df.resample('W-MON', on='date')['elevation'].sum()
        
        # Format week labels
        week_labels = [d.strftime('%b %d') for d in weekly_totals.index]
        
        return {
            'weeks': week_labels,
            'totals': weekly_totals.values
        }


    def calculate_monthly_data(self):
        if not self.workouts:
            return {'months': [], 'totals': []}
        
        df = pd.DataFrame(self.workouts)
        df['date'] = pd.to_datetime(df['date'])
        
        # Set the date range
        end_date = max(df['date'])
        start_date = end_date - pd.DateOffset(months=11)  # Show last 12 months
        
        # Create monthly bins using 'ME' (Month End) instead of deprecated 'M'
        df = df[df['date'] >= start_date]
        monthly_totals = df.resample('ME', on='date')['elevation'].sum()
        
        # Format month labels
        month_labels = [d.strftime('%b %Y') for d in monthly_totals.index]
        
        return {
            'months': month_labels,
            'totals': monthly_totals.values
        }

    def update_graph(self):
        self.create_graph(self.stats_frame)


    def update_stats(self):
        # Clear and recreate stats tab
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        self.setup_stats_tab()

    def save_workout(self):
        try:
            # Validate inputs
            date = datetime.strptime(self.date_var.get(), "%Y-%m-%d").strftime("%Y-%m-%d")
            distance = float(self.distance_var.get())
            elevation = float(self.elevation_var.get())
            activity = self.activity_var.get()
            
            if not activity or activity not in self.activities:
                raise ValueError("Please select a valid activity")
            
            # Create workout entry
            workout = {
                "date": date,
                "activity": activity,
                "distance": distance,
                "elevation": elevation
            }
            
            # Add to workouts list
            self.workouts.append(workout)
            self.save_data()
            self.update_history()
            self.update_stats()
            
            # Clear inputs
            self.distance_var.set("")
            self.elevation_var.set("")
            
            messagebox.showinfo("Success", "Workout saved successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_workout(self):
        selected_item = self.history_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a workout to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this workout?"):
            item = self.history_tree.item(selected_item[0])
            date = item['values'][0]
            activity = item['values'][1]
            
            # Find and remove the workout
            self.workouts = [w for w in self.workouts if not (w['date'] == date and w['activity'] == activity)]
            self.save_data()
            self.update_history()
            self.update_stats()

    def update_history(self):
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Sort workouts by date (newest first)
        sorted_workouts = sorted(self.workouts, key=lambda x: x['date'], reverse=True)
        
        # Add workouts to treeview
        for workout in sorted_workouts:
            self.history_tree.insert("", "end", values=(
                workout['date'],
                workout['activity'],
                f"{workout['distance']:.1f} km",
                f"{workout['elevation']:.0f} m"
            ))

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.workouts = json.load(f)
            except json.JSONDecodeError:
                self.workouts = []
                messagebox.showwarning("Warning", "Could not load workout history. Starting fresh.")
        else:
            self.workouts = []

    def save_data(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.workouts, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save workout data: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkoutTracker(root)
    root.mainloop()



            
