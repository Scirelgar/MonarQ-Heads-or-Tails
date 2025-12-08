"""
Quantum backend module for MonarQ Heads or Tails.

This module handles the quantum circuit creation, execution, and result processing
using PennyLane and the CalculQuebec quantum computing platform.
"""

import pennylane as qml
from pennylane_calculquebec.API.client import CalculQuebecClient
import os
import time
from dotenv import load_dotenv
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for embedding in pygame
import matplotlib.pyplot as plt

import logging

logger = logging.getLogger(__name__)


class QuantumCoinFlipper:
    """
    Quantum coin flipper using a real quantum device or simulator.

    Creates and executes a quantum circuit with Hadamard gates on multiple qubits
    to generate truly random coin flip results.
    """

    def __init__(self, device_name=None):
        """
        Initialize the quantum coin flipper.

        :param device_name: Name of the quantum device to use.
                           If None, defaults to "default.qubit" (simulator)
        :type device_name: str or None
        """
        load_dotenv()

        # Set device name and corresponding coin count
        if device_name is None:
            self.current_device_name = "default.qubit"  # Default to simulator
            self.num_coins = 6  # Default coin count for simulator
            self.circuit_qubits = 6  # Default circuit size
            self.num_executions = 1  # Default number of executions
        else:
            self.current_device_name = device_name
            # Set default parameters (will be updated by change_device if needed)
            self.num_coins = 6
            self.circuit_qubits = 6
            self.num_executions = 1

        self.num_shots = 1

        # Load environment variables for real devices
        self.host = os.getenv("HOST")
        self.user = os.getenv("USER")
        self.access_token = os.getenv("ACCESS_TOKEN")

        # Initialize device components
        self.client = None
        self.device = None
        self.circuit_func = None
        self.circuit_fig = None

    def initialize_device(self):
        """
        Initialize the quantum device.

        This should be called during app initialization to set up the quantum backend.

        :return: Status message
        :rtype: str
        """
        try:
            if self.current_device_name == "default.qubit":
                # Initialize simulator device using circuit_qubits
                circuit_qubits = getattr(self, "circuit_qubits", self.num_coins)
                self.device = qml.device("default.qubit", wires=circuit_qubits)
            else:
                # Initialize real quantum device using circuit_qubits
                circuit_qubits = getattr(self, "circuit_qubits", self.num_coins)
                self.client = CalculQuebecClient(
                    host=self.host,
                    user=self.user,
                    access_token=self.access_token,
                    project_name="default",
                )

                self.device = qml.device(
                    self.current_device_name,
                    client=self.client,
                    wires=circuit_qubits,
                )

            # Create quantum circuit using circuit_qubits
            @qml.set_shots(self.num_shots)
            @qml.qnode(self.device)
            def circuit():
                for i in range(circuit_qubits):
                    qml.Hadamard(wires=i)
                return qml.counts()

            self.circuit_func = circuit

            if self.current_device_name == "monarq.default":
                return f"Device MonarQ is not supported at this time."

            return f"Device {self.current_device_name} initialized successfully."
        except Exception as e:
            return f"Error loading device: {str(e)}"

    def generate_circuit_figure(self):
        """
        Generate the matplotlib figure of the quantum circuit.

        :return: Matplotlib figure object
        :rtype: matplotlib.figure.Figure
        """
        if self.circuit_func is None:
            raise RuntimeError(
                "Device not initialized. Call initialize_device() first."
            )

        # Close any existing figures
        if self.circuit_fig is not None:
            plt.close(self.circuit_fig)

        # Generate circuit diagram
        fig, ax = qml.draw_mpl(self.circuit_func)()
        self.circuit_fig = fig

        return fig

    def execute_circuit(self):
        """
        Execute the quantum circuit and return results.

        For devices requiring multiple executions (like MonarQ-Backup with 24 coins),
        this will execute the circuit multiple times and concatenate the results.

        :return: String of binary results (e.g., "01101")
        :rtype: str
        """
        if self.circuit_func is None:
            raise RuntimeError(
                "Device not initialized. Call initialize_device() first."
            )

        # Add delay for simulator to mimic real device
        if self.current_device_name == "default.qubit":
            time.sleep(7)  # Simulate network delay

        # Get execution parameters (default to 1 if not set)
        num_executions = getattr(self, "num_executions", 1)

        # Collect results from multiple executions
        all_results = []

        for execution in range(num_executions):
            # Execute the circuit
            result_states_list = list(self.circuit_func())
            execution_result = str(result_states_list[0])
            all_results.append(execution_result)

            # Add small delay between executions for real devices
            if self.current_device_name != "default.qubit" and num_executions > 1:
                time.sleep(1)  # Brief pause between executions

        # Concatenate all results
        final_result = "".join(all_results)

        # Ensure we return exactly num_coins bits (trim or pad if necessary)
        if len(final_result) > self.num_coins:
            final_result = final_result[: self.num_coins]
        elif len(final_result) < self.num_coins:
            # This shouldn't happen with proper configuration, but just in case
            final_result = final_result.ljust(self.num_coins, "0")

        return final_result

    def parse_results(self, result_str):
        """
        Parse quantum circuit results into coin flip outcomes.

        :param result_str: Binary string result from quantum circuit
        :type result_str: str
        :return: List of coin results, "H" for Heads (0), "T" for Tails (1)
        :rtype: list
        """
        results = []
        for i in range(self.num_coins):
            if result_str[i] == "1":
                results.append("T")  # Tails
            else:
                results.append("H")  # Heads

        return results

    def get_statistics(self, result_str):
        """
        Get statistics from the quantum results.

        :param result_str: Binary string result from quantum circuit
        :type result_str: str
        :return: Dictionary with heads and tails counts
        :rtype: dict
        """
        stats = {"heads": 0, "tails": 0}

        for i in range(self.num_coins):
            if result_str[i] == "1":
                stats["tails"] += 1
            else:
                stats["heads"] += 1

        return stats

    def change_device(self, device_name):
        """
        Change the quantum device and reinitialize.

        :param device_name: Name of the device ("MonarQ", "MonarQ-Backup", "Yukon", "Simulation")
        :type device_name: str
        :return: Status message
        :rtype: str
        """
        # Map device names to their technical identifiers
        device_config = {
            "MonarQ": "monarq.default",
            "MonarQ-Backup": "monarq.backup",
            "Yukon": "monarq.backup",
            "Simulation": "default.qubit",
        }

        if device_name not in device_config:
            return f"Unknown device: {device_name}"

        # Update device name and set device-specific configuration
        self.current_device_name = device_config[device_name]
        self.device_type = device_name  # Store the logical device type

        # Set device-specific number of coins and execution parameters
        if device_name == "MonarQ":
            self.num_coins = 24
            self.circuit_qubits = 24
            self.num_executions = 1
        elif device_name == "MonarQ-Backup":
            self.num_coins = 24
            self.circuit_qubits = 6  # Use 6-qubit circuits
            self.num_executions = 4  # Execute 4 times to get 24 coins
        elif device_name == "Yukon":
            self.num_coins = 6
            self.circuit_qubits = 6  # Use 6-qubit circuit
            self.num_executions = 1  # Execute once
        elif device_name == "Simulation":
            # For simulation, keep current num_coins or use default
            if not hasattr(self, "num_coins") or self.num_coins is None:
                self.num_coins = 6  # Default for simulation
            self.circuit_qubits = self.num_coins  # Use all qubits in one circuit
            self.num_executions = 1
        # Clean up existing device components
        self.client = None
        self.device = None
        self.circuit_func = None

        # Close existing circuit figure
        if self.circuit_fig is not None:
            plt.close(self.circuit_fig)
            self.circuit_fig = None

        # Reinitialize with new device
        return self.initialize_device()
