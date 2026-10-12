########################################
# LIBRARIES
########################################
import logging
import os

from QuantumCircuit import QuantumCircuit


# Log conf
'''logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
'''


# Images directory
IMG_PATH = os.path.sep.join([os.getcwd(), 'output', 'images'])


########################################
# RUN THE PROJECT
########################################
if __name__ == '__main__':

    # Task 1
    qc = QuantumCircuit()
    qc.instantiate_task1_protocol(input_state='generical')
    # qc.Pauli_depolarization(depolarization_probability=0.05)
    qc.add_distribution_teledata()
    qc.redemption_teledata(target_clone='S2')
    qc.save_circuit_diagram('Y&K teledata circuit diagram.svg')

    # Execute the circuit
    # qc.execute_circuit(sample_size=1000)
    qc.calculate_fidelty(sample_size=1000)