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


class QuantumCoinFlipper:
    """
    Quantum coin flipper using a real quantum device or simulator.

    Creates and executes a quantum circuit with Hadamard gates on multiple qubits
    to generate truly random coin flip results.
    """

    def __init__(self, num_coins=5, use_simulator=None):
        """
        Initialize the quantum coin flipper.

        :param num_coins: Number of coins (qubits) to flip
        :type num_coins: int
        :param use_simulator: Whether to use simulator instead of real device.
                             If None, reads from SIM_BOOL environment variable
        :type use_simulator: bool or None
        """
        load_dotenv()

        self.num_coins = num_coins
        self.num_shots = 1

        # Determine if using simulator from env if not specified
        if use_simulator is None:
            sim_bool_env = os.getenv("SIM_BOOL", "False")
            # Convert string to boolean
            self.use_simulator = sim_bool_env.lower() in ("true", "1", "yes")
        else:
            self.use_simulator = use_simulator

        # Load environment variables
        self.host = os.getenv("HOST")
        self.user = os.getenv("USER")
        self.access_token = os.getenv("ACCESS_TOKEN")

        # Initialize devices
        self.client = None
        self.dev_real = None
        self.dev_sim = None
        self.circuit_func = None
        self.circuit_fig = None

    def initialize_device(self):
        """
        Initialize the quantum device (real or simulator).

        This should be called during app initialization to set up the quantum backend.

        :return: Status message
        :rtype: str
        """
        try:
            if not self.use_simulator:
                # Initialize real device
                self.client = CalculQuebecClient(
                    host=self.host,
                    user=self.user,
                    access_token=self.access_token,
                    project_name="default",
                )

                self.dev_real = qml.device(
                    "monarq.backup",
                    client=self.client,
                    wires=self.num_coins,
                )

                # Create quantum circuit for real device
                @qml.set_shots(self.num_shots)
                @qml.qnode(self.dev_real)
                def circuit():
                    for i in range(self.num_coins):
                        qml.Hadamard(wires=i)
                    return qml.counts()

                self.circuit_func = circuit
            else:
                # Initialize simulator
                self.dev_sim = qml.device("default.qubit", wires=self.num_coins)

                # Create quantum circuit for simulator
                @qml.set_shots(self.num_shots)
                @qml.qnode(self.dev_sim)
                def circuit_sim():
                    for i in range(self.num_coins):
                        qml.Hadamard(wires=i)
                    return qml.counts()

                self.circuit_func = circuit_sim

            return "Device loaded successfully"
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

        :return: String of binary results (e.g., "01101")
        :rtype: str
        """
        if self.circuit_func is None:
            raise RuntimeError(
                "Device not initialized. Call initialize_device() first."
            )

        # Add delay for simulator to mimic real device
        if self.use_simulator:
            time.sleep(7)  # Simulate network delay

        result_states_list = list(self.circuit_func())
        return str(result_states_list[0])

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
