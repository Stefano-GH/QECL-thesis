########################################
# LIBRARIES
########################################
from abc import ABC, abstractmethod
import logging
import numpy as np

# Log conf
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


########################################
# CLASS DEFINITION
########################################
class QuantumCircuitBase(ABC):


    def __init__(self, num_qubits=10, num_clbits=6):
        self.num_qubits = num_qubits
        self.num_clbits = num_clbits

        self.input_state = ''
        self.name = ''
        self._class = ''



    @abstractmethod
    def append_gate(self, gate_name, qubits, params=None):
        '''
        Abstract method for adding a new gate to the circuit. Each backend has to develop its own implementarion
        '''
        pass



    def instantiate_YK_protocol(self, input_state='zero', theta=0.0, phi=0.0):
        '''
        Instatiation of the simple protocol:
        - q0: input state A (secret)
        - q1, q2: Bepp pair for clone S1, S2
        '''

        # Save internal attributes
        self.input_state = input_state
        self.name = f'Task 1 protocol with {input_state} input state'

        # Preparation of the input state q0
        if input_state == 'zero':
            pass
        elif input_state == 'plus':
            self.append_gate('H', [0])
        elif input_state == 'arbitrary':
            self.append_gate('RY', [0], params=theta)
            self.append_gate('RZ', [0], params=phi)
        else:
            raise ValueError(f'[{self._class}] State {input_state} not supported!')

        # Generating the Bell pair
        self.append_gate('H', [1])
        self.append_gate('CNOT', [1, 2])

        # Generate the entanglement between q0 and q1 through phase kickback
        self.append_gate('CZ', [1, 0])



    def append_distribution_teledata(self, verbose=False):
        '''
        Distribute clones S1 (q1), S2 (q2) to remote nodes L1, L2 through teledata
        It uses additional Bell pairs
        '''

        # Distribute S1 (q1)
        self.append_gate('H', [3])
        self.append_gate('CNOT', [3, 4])

        self.append_gate('CNOT', [1, 3])
        self.append_gate('H', [1])

        self.append_gate('M', [1, 3])
        self.append_gate('CX', [3, 4])
        self.append_gate('CZ', [1, 4])

        # Distribute S2 (q2)
        self.append_gate('H', [5])
        self.append_gate('CNOT', [5, 6])

        self.append_gate('CNOT', [2, 5])
        self.append_gate('H', [2])

        self.append_gate('M', [2, 5])
        self.append_gate('CX', [5, 6])
        self.append_gate('CZ', [2, 6])

        if verbose:
            logger.info(f'[{self._class}] Distribution teledata applied on S1 and S2')



    def append_noise_channel(self, qubits, p=0.99, error_type='bit_flip', verbose=False):
        '''
        Add a noise channel to specific qubits
        '''
        if error_type == 'bit_flip':
            self.append_noise('X', qubits, p)
        elif error_type == 'phase_flip':
            self.append_noise('Z', qubits, p)

        if verbose:
            logger.info(f'[{self._class}] Noise channel {error_type}, probability={p} applied on qubits {qubits}')



    @abstractmethod
    def append_noise(self, noise_name, qubits, p):
        '''
        Abstract method for adding backend-specific noise instructions
        '''
        pass



    def append_kraus_noise_channel(self, kraus_matrices, qubits, verbose=False):
        '''
        Add a general noise channel defined by a list of Kraus matrices on specific qubits
        '''
        self.append_kraus_noise(kraus_matrices, qubits)

        if verbose:
            operations_no = len(kraus_matrices)
            flattened_matrices = [np.array(k).flatten().tolist() for k in kraus_matrices]
            logger.info(
                f'[{self._class}] Kraus matrix noise channel applied on qubits {qubits}'
                f'Number of operations = {operations_no}'
                f'Flattened matrices = {flattened_matrices}'
            )



    @abstractmethod
    def append_kraus_noise(self, kraus_matrices, qubits):
        '''
        Abstract methos for adding backend-specific Kraus noise instructions
        '''
        pass



    def redemption(self, strategy='teledata', target_clone='S1', verbose=False):
        '''
        Redemption method to support different strategies (e.g.: teledata or telegate)
        '''
        if strategy == 'teledata':
            self.redemption_teledata(target_clone=target_clone, verbose=verbose)
        elif strategy == 'telegate':
            self.redemption_telegate(target_clone=target_clone, verbose=verbose)
        else:
            raise ValueError(f'[{self._class}] Redemption strategy *{strategy}* not implemented!')



    def redemption_teledata(self, target_clone='S1', verbose=False):
        '''
        Return the choosen clone to the location L0
        '''
        clone_qubit = 4 if target_clone == 'S1' else 6

        # Add a new Bell pair
        self.append_gate('H', [7])
        self.append_gate('CNOT', [7, 8])

        # Quantum teleportation by consuming the Bell pair
        self.append_gate('CNOT', [clone_qubit, 7])
        self.append_gate('H', [clone_qubit])
        self.append_gate('M', [clone_qubit, 7])
        self.append_gate('CX', [7, 8])
        self.append_gate('CZ', [7, 8])

        # Pair the key q0 with choosen clone
        self.append_gate('CZ', [8, 0])

        if verbose:
            logger.info(f'[{self._class}] Redemption by TELEDATA configured for path by using {target_clone}')



    @abstractmethod
    def calculate_fidelity(self, target_qubit_idx=0, sample_size=1000):
        '''
        Abstract method to backend-specific calculate fidelity via comparing the results of measuring q0 with expected theoretical state.
        '''
        pass



    @abstractmethod
    def save_circuit_diagram(self, filename:str):
        pass