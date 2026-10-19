########################################
# LIBRARIES
########################################
import logging
import numpy as np
import os

from quantumCircuits.QuantumCircuitQiskit import QuantumCircuitQiskit
from quantumCircuits.QuantumCircuitStim import QuantumCircuitStim


# Log conf
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Images directory
IMG_PATH = os.path.sep.join([os.getcwd(), 'output', 'images'])


# Class mapping
BE_CLASSES = {
    'qiskit': QuantumCircuitQiskit,
    'stim':   QuantumCircuitStim
}

INPUT_STATE_LIST = ['zero', 'plus', 'arbitrary']
TARGET_CLONES = ['S1', 'S2']
SAMPLE_SIZE = 1000
NUM_QUBITS = 9
NUM_CLBITS = 6
NOISE_PROB = 0
NOISE_TYPE = 'none'


########################################
# MAIN FUNCTION
########################################
def run_YK_protocol(be_name='qiskit', input_state='zero', target_clone='S1', redemption_strategy='teledata', noise_type='none'):

    # Check the input class
    if be_name not in BE_CLASSES:
        raise ValueError(f'Backend {be_name} not supported. Choose between : {list(BE_CLASSES.keys())}')

    # Intantiate the current class
    ChoosenClass = BE_CLASSES[be_name]
    qc = ChoosenClass(NUM_QUBITS, NUM_CLBITS)

    # Instantiate the protocol
    qc.instantiate_YK_protocol(input_state=input_state)

    # Distribute clones through teledata
    qc.append_distribution_teledata()

    # Add noise channel (Kraus operators)
    if noise_type == 'none':
        pass
    elif noise_type == 'bit_flip':
        qc.append_noise_channel(qubits=[0, 1, 2], p=NOISE_PROB, error_type=NOISE_TYPE, verbose=True)
    elif noise_type == 'phase_flip':
        qc.append_noise_channel(qubits=[0, 1, 2], p=NOISE_PROB, error_type=NOISE_TYPE, verbose=True)
    elif noise_type == 'kraus':
        identity_p = np.sqrt(NOISE_PROB)
        error_p = np.sqrt(1 - NOISE_PROB)

        K0 = error_p * np.array([[1, 0], [0, 1]], dtype=complex)
        K1 = identity_p * np.array([[0, 1], [1, 0]], dtype=complex)
        kraus_matrices = [K0, K1]

        try:
            qc.append_kraus_noise_channel(kraus_matrices=kraus_matrices, qubits=[0, 1, 2])
        except Exception as e:
            logger.warning(e)
    else:
        raise ValueError(f'Unknown noise type: {NOISE_TYPE}')

    # Redemption of the choosen clone
    try:
        qc.redemption(strategy=redemption_strategy, target_clone=target_clone)
    except Exception as e:
        logger.error(f'Skipped due to missing implementation: {e}')
        return None

    # Save the circuit diagram
    qc.save_circuit_diagram(filename=f'{be_name}_{input_state}_{target_clone}')

    # Compute the fidelity
    F = qc.calculate_fidelity(target_qubit_idx=0, sample_size=SAMPLE_SIZE)
    logger.info(f'Input state = [{input_state}] | target_clone = [{target_clone}] | Fidelity = [{F:.3f}]')


########################################
# RUN THE PROJECT
########################################
if __name__ == '__main__':

    # Print all the parameters
    logger.info(f'Noise type for the current run: {NOISE_TYPE}')
    logger.info(f'Noise probability for the current run: {NOISE_PROB}')

    for be_name in list(BE_CLASSES.keys()):
        logger.info('========================================')
        logger.info(f'Running YK protocol with {be_name.upper()}')
        logger.info('========================================')

        for input_state in INPUT_STATE_LIST:
            for target_clone in TARGET_CLONES:
                try:
                    run_YK_protocol(be_name=be_name, input_state=input_state, target_clone=target_clone)
                except Exception as e:
                    logger.warning(e)
                    continue