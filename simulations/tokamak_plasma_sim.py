#!/usr/bin/env python3

"""
Tokamak Plasma Simulation

This script simulates plasma behavior in a tokamak fusion reactor, modeling
magnetic confinement, plasma stability, and fusion reactions.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy.integrate import solve_ivp
import pandas as pd

# Physical constants
BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
PROTON_MASS = 1.67262192e-27  # kg
DEUTERIUM_MASS = 2.0 * PROTON_MASS  # kg
TRITIUM_MASS = 3.0 * PROTON_MASS  # kg
ELEMENTARY_CHARGE = 1.602176634e-19  # C

class TokamakPlasmaSimulation:
    """Class for simulating plasma in a tokamak fusion reactor."""
    
    def __init__(self, major_radius=6.2, minor_radius=2.0, magnetic_field=5.3):
        """Initialize tokamak parameters.
        
        Args:
            major_radius: Major radius of the tokamak (m)
            minor_radius: Minor radius of the tokamak (m)
            magnetic_field: Toroidal magnetic field strength at major radius (T)
        """
        self.major_radius = major_radius  # R in meters
        self.minor_radius = minor_radius  # a in meters
        self.magnetic_field = magnetic_field  # B in Tesla
        self.plasma_config = None
        self.simulation_results = None
        
    def configure_plasma(self, temperature=15e6, density=1e20, pressure=None):
        """Configure plasma parameters.
        
        Args:
            temperature: Plasma temperature (K)
            density: Plasma particle density (m⁻³)
            pressure: Optional plasma pressure (Pa). If None, calculated from T and n.
        """
        self.plasma_config = {
            'temperature': temperature,
            'density': density,
        }
        
        # Calculate pressure if not provided
        if pressure is None:
            # p = nkT for ideal plasma
            pressure = density * BOLTZMANN_CONSTANT * temperature
        
        self.plasma_config['pressure'] = pressure
        
        # Calculate plasma beta (ratio of plasma pressure to magnetic pressure)
        magnetic_pressure = (self.magnetic_field ** 2) / (2 * 4 * np.pi * 1e-7)
        plasma_beta = pressure / magnetic_pressure
        self.plasma_config['beta'] = plasma_beta
        
        # Calculate basic stability parameters
        self.plasma_config['safety_factor'] = self.calculate_safety_factor()
        
        print(f"Plasma configured with T = {temperature/1e6:.2f} million K, "
              f"n = {density/1e20:.2f}×10²⁰ m⁻³, β = {plasma_beta:.4f}")
        
    def calculate_safety_factor(self, radius_ratio=0.5):
        """Calculate the safety factor q at specified radius ratio.
        
        Args:
            radius_ratio: Ratio of local minor radius to total minor radius (0-1)
            
        Returns:
            Safety factor q
        """
        # Simplified model assuming cylindrical approximation
        local_radius = radius_ratio * self.minor_radius
        q = (self.magnetic_field * self.major_radius) / \
            (local_radius * self.calculate_poloidal_field(radius_ratio))
        return q
    
    def calculate_poloidal_field(self, radius_ratio=0.5):
        """Calculate the poloidal magnetic field at specified radius ratio.
        
        Args:
            radius_ratio: Ratio of local minor radius to total minor radius (0-1)
            
        Returns:
            Poloidal field strength (T)
        """
        # This is a simplified model, actual calculation is more complex
        # Assuming a typical current profile j(r) ~ (1 - (r/a)²)^0.8
        if self.plasma_config is None:
            raise ValueError("Plasma not configured. Call configure_plasma first.")
            
        # Estimated plasma current based on typical tokamak parameters
        total_current = 15e6  # 15 MA, typical for large tokamak
        current_density_profile = (1 - (radius_ratio ** 2)) ** 0.8
        
        # Calculate poloidal field at this radius
        local_radius = radius_ratio * self.minor_radius
        poloidal_field = (4e-7 * np.pi * total_current * radius_ratio) / (2 * np.pi * local_radius)
        return poloidal_field
    
    def simulate_plasma_evolution(self, duration=1.0, time_steps=1000):
        """Simulate time evolution of plasma parameters.
        
        Args:
            duration: Simulation duration (s)
            time_steps: Number of time steps
            
        Returns:
            Dictionary of simulation results
        """
        if self.plasma_config is None:
            raise ValueError("Plasma not configured. Call configure_plasma first.")
            
        # Time points
        times = np.linspace(0, duration, time_steps)
        
        # Initial conditions [temperature, density, beta]
        y0 = [
            self.plasma_config['temperature'],
            self.plasma_config['density'],
            self.plasma_config['beta']
        ]
        
        # Solve ODE system
        result = solve_ivp(
            self._plasma_evolution_model,
            [0, duration],
            y0,
            t_eval=times,
            method='RK45'
        )
        
        # Store results
        self.simulation_results = {
            'times': result.t,
            'temperature': result.y[0],
            'density': result.y[1],
            'beta': result.y[2],
            'fusion_power': self._calculate_fusion_power(result.y[0], result.y[1])
        }
        
        return self.simulation_results
    
    def _plasma_evolution_model(self, t, y):
        """ODE model for plasma evolution.
        
        Args:
            t: Time
            y: State vector [temperature, density, beta]
            
        Returns:
            Derivatives [dT/dt, dn/dt, dbeta/dt]
        """
        temperature, density, beta = y
        
        # Simplified fusion heating
        fusion_power = self._calculate_fusion_power(temperature, density)
        alpha_heating = 0.2 * fusion_power  # 20% of fusion power goes to alpha heating
        
        # Energy loss due to confinement time and radiation
        energy_confinement_time = 3.0  # seconds, typical for large tokamak
        bremsstrahlung_loss = 5.5e-37 * density**2 * np.sqrt(temperature)
        
        # Rate of change of temperature
        dT_dt = (alpha_heating - bremsstrahlung_loss) / \
                (3 * density * BOLTZMANN_CONSTANT) - temperature / energy_confinement_time
        
        # Rate of change of density (simplified with fueling and loss)
        dn_dt = 1e19 - density / (2 * energy_confinement_time)  # Constant fueling rate
        
        # Rate of change of beta (follows from changes in T and n)
        magnetic_pressure = (self.magnetic_field ** 2) / (2 * 4 * np.pi * 1e-7)
        dbeta_dt = (BOLTZMANN_CONSTANT * (density * dT_dt + temperature * dn_dt)) / magnetic_pressure
        
        return [dT_dt, dn_dt, dbeta_dt]
    
    def _calculate_fusion_power(self, temperature, density):
        """Calculate fusion power density for D-T reaction.
        
        Args:
            temperature: Plasma temperature (K)
            density: Plasma density (m⁻³)
            
        Returns:
            Fusion power density (W/m³)
        """
        # Convert temperature to keV for cross-section calculation
        temperature_keV = temperature * BOLTZMANN_CONSTANT / ELEMENTARY_CHARGE / 1000
        
        # Simplified D-T fusion reactivity <σv> in m³/s
        # Using parametric fit valid for T between 1-100 keV
        C1 = 1.17e-24
        C2 = 1.56e-2
        C3 = 1.03
        C4 = -0.06
        
        x = temperature_keV / (1 - temperature_keV * (C2 + temperature_keV * (C3 + temperature_keV * C4)))
        reactivity = C1 * x * np.exp(-19.94 / np.sqrt(temperature_keV))
        
        # Assuming 50-50 D-T mix
        nd = density / 2
        nt = density / 2
        
        # Fusion energy per reaction (17.6 MeV)
        energy_per_reaction = 17.6e6 * ELEMENTARY_CHARGE
        
        # Power density
        power_density = nd * nt * reactivity * energy_per_reaction
        
        return power_density
    
    def plot_simulation_results(self):
        """Plot the simulation results."""
        if self.simulation_results is None:
            raise ValueError("No simulation results. Call simulate_plasma_evolution first.")
            
        times = self.simulation_results['times']
        
        # Create a figure with subplots
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        
        # Temperature plot
        axs[0, 0].plot(times, self.simulation_results['temperature'] / 1e6, 'r-')
        axs[0, 0].set_xlabel('Time (s)')
        axs[0, 0].set_ylabel('Temperature (million K)')
        axs[0, 0].set_title('Plasma Temperature')
        axs[0, 0].grid(alpha=0.3)
        
        # Density plot
        axs[0, 1].plot(times, self.simulation_results['density'] / 1e20, 'b-')
        axs[0, 1].set_xlabel('Time (s)')
        axs[0, 1].set_ylabel('Density (10²⁰ m⁻³)')
        axs[0, 1].set_title('Plasma Density')
        axs[0, 1].grid(alpha=0.3)
        
        # Beta plot
        axs[1, 0].plot(times, self.simulation_results['beta'], 'g-')
        axs[1, 0].set_xlabel('Time (s)')
        axs[1, 0].set_ylabel('Beta')
        axs[1, 0].set_title('Plasma Beta')
        axs[1, 0].grid(alpha=0.3)
        
        # Fusion power plot
        axs[1, 1].plot(times, self.simulation_results['fusion_power'] / 1e6, 'm-')
        axs[1, 1].set_xlabel('Time (s)')
        axs[1, 1].set_ylabel('Fusion Power (MW/m³)')
        axs[1, 1].set_title('Fusion Power Density')
        axs[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    def animate_plasma_cross_section(self, frames=100, interval=50):
        """Create an animation of plasma cross-section with perturbations.
        
        Args:
            frames: Number of frames in animation
            interval: Interval between frames (ms)
        """
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(-1.5 * self.minor_radius, 1.5 * self.minor_radius)
        ax.set_ylim(-1.5 * self.minor_radius, 1.5 * self.minor_radius)
        ax.set_aspect('equal')
        ax.grid(alpha=0.3)
        
        # Create initial circular plasma boundary
        theta = np.linspace(0, 2 * np.pi, 100)
        x = self.minor_radius * np.cos(theta)
        y = self.minor_radius * np.sin(theta)
        line, = ax.plot(x, y, 'r-', linewidth=2)
        
        # Text for time display
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
        
        # Animation update function
        def update(frame):
            # Add time-dependent perturbations to plasma shape
            time = frame / frames
            perturbation = 0.1 * np.sin(4 * theta - 5 * time) * np.exp(-time)
            
            # Update plasma boundary
            x = self.minor_radius * (1 + perturbation) * np.cos(theta)
            y = self.minor_radius * (1 + perturbation) * np.sin(theta)
            line.set_data(x, y)
            
            # Update time display
            time_text.set_text(f'Time: {time:.2f} s')
            
            return line, time_text
        
        # Create animation
        anim = animation.FuncAnimation(fig, update, frames=frames, interval=interval, blit=True)
        plt.title(f'Tokamak Plasma Cross-Section (R={self.major_radius}m, a={self.minor_radius}m)')
        plt.xlabel('X (m)')
        plt.ylabel('Y (m)')
        
        # Display animation
        plt.close()  # Prevent duplicate display
        return anim

# Example usage
if __name__ == "__main__":
    # This is a demonstration of the tokamak simulation
    print("Tokamak Plasma Simulation")
    print("This script simulates plasma behavior in a tokamak fusion reactor.")
    
    try:
        # Create tokamak simulation with ITER-like parameters
        sim = TokamakPlasmaSimulation(
            major_radius=6.2,  # meters
            minor_radius=2.0,  # meters
            magnetic_field=5.3  # Tesla
        )
        
        # Configure plasma
        sim.configure_plasma(
            temperature=15e6,  # 15 million K
            density=1e20      # 10²⁰ particles per m³
        )
        
        # Run simulation
        print("\nRunning plasma evolution simulation...")
        results = sim.simulate_plasma_evolution(duration=5.0, time_steps=200)
        
        # Plot results
        print("Plotting results...")
        sim.plot_simulation_results()
        
        # Create animation
        # Note: In non-interactive environments, this animation might not display
        print("Creating plasma cross-section animation...")
        anim = sim.animate_plasma_cross_section(frames=50, interval=100)
        plt.show()
        
    except Exception as e:
        print(f"Error in demonstration: {e}")
