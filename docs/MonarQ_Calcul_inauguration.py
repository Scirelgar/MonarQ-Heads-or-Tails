import pennylane as qml
from pennylane_calculquebec.API.client import CalculQuebecClient
import numpy as np
import random
import time
import os
from dotenv import load_dotenv


load_dotenv()

HOST_ENV = os.getenv("HOST")
USER_ENV = os.getenv("USER")
ACCESS_TOKEN_ENV = os.getenv("ACCESS_TOKEN")
sim = os.getenv("SIM_BOOL")

num_wires = 5
num_shots = 1

client = CalculQuebecClient(
    host=HOST_ENV,
    user=USER_ENV,
    access_token=ACCESS_TOKEN_ENV,
    project_id="default",
)

# Define the device
print("Chargement de l'appareil...")
dev_sf = qml.device(
    "monarq.backup",
    client=client,
    wires=num_wires,
)

dev_sim = qml.device("default.qubit", wires=num_wires)

print("Création du circuit...")


@qml.set_shots(num_shots)
@qml.qnode(dev_sf)
def circuit():
    for i in range(num_wires):
        qml.Hadamard(wires=i)
    return qml.counts()


@qml.set_shots(num_shots)
@qml.qnode(dev_sim)
def circuit_sim():
    for i in range(num_wires):
        qml.Hadamard(wires=i)
    return qml.counts()


# Draw the circuit
time.sleep(1)
fig, ax = qml.draw_mpl(circuit)()
fig.show()


def execute_circuit():
    if sim:
        result_states_list = list(circuit_sim())
        return str(result_states_list[0])
        # return (np.random.choice(2, num_wires, p=[0.51, 0.49])).astype(str)

    result_states_list = list(circuit())
    return str(result_states_list[0])


print("Circuit en cours d'exécution...")
time.sleep(7) if sim else 0
result_str = execute_circuit()
print(f"Résultat du calcul: {result_str}")

result_dict = {}
counter = dict(face=0, pile=0)

for i in range(num_wires):
    if result_str[i] == "1":
        result_dict[f"Qubit {i + 1}"] = "PILE"
        counter["pile"] += 1
    else:
        result_dict[f"Qubit {i + 1}"] = "FACE"
        counter["face"] += 1

for key, value in result_dict.items():
    print(f"{key} : {value}")

for key, value in counter.items():
    print(f"{value} qubits sont tombés sur {key}")
