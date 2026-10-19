########################################
# LIBRARIES
########################################
import logging
import matplotlib.pyplot as plt
import os
import qiskit
from qiskit.quantum_info import DensityMatrix, partial_trace, state_fidelity, Statevector, Kraus
from qiskit_aer import AerSimulator
from qiskit_aer.noise import pauli_error

from quantumCircuits.QuantumCircuitBase import QuantumCircuitBase

# Log conf
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Images directory
IMG_PATH = os.path.sep.join([os.getcwd(), 'output', 'images', 'qiskit'])


########################################
# CLASS DEFINITION
########################################
class QuantumCircuitQiskit(QuantumCircuitBase):


    def __init__(self, num_qubits=10, num_clbits=6):
        super().__init__(num_qubits, num_clbits)
        self._class = 'Qiskit'
        self.circuit = qiskit.QuantumCircuit(self.num_qubits, self.num_clbits)
        self.initial_state_vector = None
        
        # Initialize the counter to make automatic the management of the classical bits for measurements
        self.clbits_counter = 0

        # Gate mapping from parent class
        self.gate_mapping = {
            'H':    lambda qubits, params: self.circuit.h(qubits[0]),
            'X':    lambda qubits, params: self.circuit.x(qubits[0]),
            'Z':    lambda qubits, params: self.circuit.z(qubits[0]),
            'CX':   lambda qubits, params: self.circuit.cx(qubits[0], qubits[1]),
            'CZ':   lambda qubits, params: self.circuit.cz(qubits[0], qubits[1]),
            'CNOT': lambda qubits, params: self.circuit.cx(qubits[0], qubits[1]),
            'RY':   lambda qubits, params: self.circuit.ry(params, qubits[0]),
            'RZ':   lambda qubits, params: self.circuit.rz(params, qubits[0]),
            'M':    lambda qubits, params: self._handle_measurement(qubits)
        }



    def append_gate(self, gate_name, qubits, params=None):
        if gate_name in self.gate_mapping:
            self.gate_mapping[gate_name](qubits, params)
        else:
            raise NotImplementedError(f"[{self._class}] Gate {gate_name} not implemented")



    def instantiate_YK_protocol(self, input_state='zero', theta=0, phi=0):
        super().instantiate_YK_protocol(input_state, theta, phi)

        if input_state == 'zero':
            self.initial_state_vector = Statevector.from_label('0')
        elif input_state == 'plus':
            self.initial_state_vector = Statevector.from_label('+')
        elif input_state == 'arbitrary':
            state = Statevector.from_label('0')
            temp_qc = qiskit.QuantumCircuit(1)
            temp_qc.ry(theta, 0)
            temp_qc.rz(phi, 0)
            self.initial_state_vector = state.evolve(temp_qc)
        else:
            raise ValueError(f'[{self._class}] State {input_state} not supported!')



    def _handle_measurement(self, qubits):
        '''
        Support method for measure quantum bits
        '''
        for qubit_idx in qubits:
            if self.clbits_counter >= self.num_clbits:
                raise ValueError(f'[{self._class}] Exceeded the number of classical bits ({self.num_clbits}) allocated in Qiskit!')

            # Measure the qubit by using a classical bit. Increase then the counter for the next measure
            self.circuit.measure(qubit_idx, self.clbits_counter)
            self.clbits_counter += 1



    def append_noise(self, noise_name, qubits, p):
        identity_p = p
        error_p = 1 - p
        
        if noise_name in ['X', 'Z']:
            # Create the error channel for single qubits
            error_channel = pauli_error([('I', identity_p), (noise_name, error_p)])
            for q in qubits:
                self.circuit.append(error_channel, [q])

        else:
            raise NotImplementedError(f'[{self._class}] Noise type {noise_name} not implemented.')



    def append_kraus_noise(self, kraus_matrices, qubits):
        kraus_channel = Kraus(kraus_matrices)
        for q in qubits:
            self.circuit.append(kraus_channel, [q])



    def calculate_fidelity(self, target_qubit_idx=0, sample_size=1000):
        # Check the existence of the initial state variable
        if self.initial_state_vector is None:
            raise ValueError('You have to instantiate a circuit protocol first!')

        # Copy the circuit for the simulation and take the density matrix
        sim_circuit = self.circuit.copy()
        sim_circuit.save_density_matrix()

        # Prepare the simulation
        simulator = AerSimulator(method='density_matrix')
        result = simulator.run(sim_circuit).result()

        # Save the output's density matrix
        rho_global_result = result.data()['density_matrix']
        rho_global = DensityMatrix(rho_global_result)

        # Compute partial trace to isolate target qubit
        qubits_traced_out = [q for q in range(self.num_qubits) if q != target_qubit_idx]
        rho_target = partial_trace(rho_global, qubits_traced_out)

        fidelity = state_fidelity(self.initial_state_vector, rho_target)
        return fidelity



    def save_circuit_diagram(self, filename:str, verbose:bool=False):
        # Complete the filename with the right extension
        filename = filename + '.png'

        # Create the directory if not exist
        os.makedirs(IMG_PATH, exist_ok=True)
        file = os.path.sep.join([IMG_PATH, filename])

        diagram = self.circuit.draw(output='mpl')
        diagram.savefig(file, bbox_inches='tight')
        plt.close(diagram)

        if verbose:
            logger.info(f'[{self._class}] Diagram of the circuit *{self.name}* saved in {file}')