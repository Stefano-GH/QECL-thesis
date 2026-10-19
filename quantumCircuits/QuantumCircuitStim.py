########################################
# LIBRARIES
########################################
import logging
import numpy as np
import os
import stim 
from quantumCircuits.QuantumCircuitBase import QuantumCircuitBase

# Log conf
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Images directory
IMG_PATH = os.path.sep.join([os.getcwd(), 'output', 'images', 'stim'])


########################################
# CLASS DEFINITION
########################################
class QuantumCircuitStim(QuantumCircuitBase):


    def __init__(self, num_qubits, num_clbits):
        super().__init__(num_qubits, num_clbits)
        self._class = 'Stim'
        self.circuit = stim.Circuit()



    def append_gate(self, gate_name, qubits):
        self.circuit.append(gate_name, qubits)



    def instantiate_YK_protocol(self, input_state='zero', theta=0, phi=0):
        if input_state == 'arbitrary':
            raise ValueError(f'[{self._class}] Input state *{input_state}* cannot be implemented with Stim! Use the Qiskit-based class.')

        super().instantiate_YK_protocol(input_state, theta, phi)



    def append_noise(self, noise_name, qubits, p):
        error_p = 1 - p

        if noise_name == 'X':
            for q in qubits:
                self.circuit.append('X_ERROR', [q], error_p)

        elif noise_name == 'Z':
            for q in qubits:
                self.circuit.append('Z_ERROR', [q], error_p)

        else:
            raise NotImplementedError(f'[{self._class}] Noise type {noise_name} not implemented.')



    def append_kraus_noise(self, kraus_matrices, qubits):
        raise NotImplementedError(f'[{self._class}] General matrix Kraus channel cannot be simulated in Stim. Use the Qiskit-based class!')



    def calculate_fidelity(self, target_qubit_idx=0, sample_size=1000):
        sim_circuit = self.circuit.copy()

        # Reverse the gates according to the input state
        if self.input_state == 'zero':
            pass
        elif self.input_state == 'plus':
            sim_circuit.append('H', [target_qubit_idx])

        # Append the measurement
        sim_circuit.append('M', [target_qubit_idx])

        # Execute the simulation
        sampler = sim_circuit.compile_sampler()
        samples = sampler.sample(shots=sample_size)

        target_measurements = samples[:, -1]
        success_count = np.sum(target_measurements == False)
        fidelity = success_count / sample_size
        return fidelity



    def save_circuit_diagram(self, filename:str, verbose:bool=False):
        # Complete the filename with the right extension
        filename = filename + '.svg'

        # Create the directory if not exist
        os.makedirs(IMG_PATH, exist_ok=True)
        file = os.path.sep.join([IMG_PATH, filename])

        # Generate the diagram and save it
        diagram = str( self.circuit.diagram('timeline-svg') )
        # TODO: test value 'timeline-3d', 'interactive'

        mode = 'wb' if isinstance(diagram, bytes) else 'w'
        with open(file, mode) as f:
            f.write(diagram)

        if verbose:
            logger.info(f'[{self._class}] Diagram of the circuit *{self.name}* saved in {file}')
    