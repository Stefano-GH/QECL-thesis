########################################
# LIBRARIES
########################################
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import stim


# Log conf
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Images directory
IMG_PATH = os.path.sep.join([os.getcwd(), 'output', 'images'])


########################################
# CLASS DEFINITION
########################################
class QuantumCircuit:



    def __init__(self):
        self.circuit = stim.Circuit()
        self.name = ''



    def add_distribution_teledata(self):
        '''
        Distribute clones S1 (q1), S2 (q2) to remote nodes L1, L2 through teledata
        It uses additional Bell pairs
        '''

        # Distribute S1 (q1)
        self.circuit.append('H', [3])
        self.circuit.append('CNOT', [3, 4])

        self.circuit.append('CNOT', [1, 3])
        self.circuit.append('H', [1])

        self.circuit.append('M', [1, 3])
        self.circuit.append('CX', [3, 4])
        self.circuit.append('CZ', [1, 4])

        # Distribute S2 (q2)
        self.circuit.append('H', [5])
        self.circuit.append('CNOT', [5, 6])

        self.circuit.append('CNOT', [2, 5])
        self.circuit.append('H', [2])

        self.circuit.append('M', [2, 5])
        self.circuit.append('CX', [5, 6])
        self.circuit.append('CZ', [2, 6])

        logger.info('Distribution teledata applied on S1 and S2')



    def calculate_fidelty(self, sample_size=1000):
        '''
        Calculate fidelty via comparing the results of measuring q0 with expected theoretical state
        '''

        # Unpreparation tasks according to the state
        if self.input_state == 'plus':
            self.circuit.append('H', [0])
        elif self.input_state == 'generical':
            self.circuit.append('S_DAG', [0])
            self.circuit.append('H', [0])

        # Measure the qubit q0
        self.circuit.append('M', [0])

        # Execute the simulation
        sampler = self.circuit.compile_sampler()
        samples = sampler.sample(shots=sample_size)

        # Save the outcome and count the number of zeros (False)
        final_measurements = samples[:, -1]
        success_count = np.sum(final_measurements == False)

        fidelty = success_count / sample_size
        logger.info(f"Fidelty = [{fidelty:.4f}]")
        return fidelty



    def execute_circuit(self, sample_size:int):
        # Run the simulation
        sampler = self.circuit.compile_sampler()
        samples = sampler.sample(shots=sample_size)

        # False = 0 and True = 1
        one_count = np.sum(samples, axis=0)
        zero_count = sample_size - one_count

        qubits_number = samples.shape[1]
        qubits_indexes = [f"Qubit {i}" for i in range(qubits_number)]

        # Plot the outcome
        x = np.arange(qubits_number)
        width = 0.35

        fig,ax = plt.subplots(figsize=(8, 5))
        rects1 = ax.bar(x - width/2, zero_count, width, label="0 (False)", color="skyblue")
        rects2 = ax.bar(x + width/2, one_count, width, label="1 (True)", color="salmon")

        ax.set_xlabel('Qubits')
        ax.set_ylabel('Count')
        ax.set_title(f'Outcome distribution')
        ax.set_xticks(x)
        ax.set_xticklabels(qubits_indexes)
        ax.legend()

        plt.tight_layout()
    
        plot_path = os.path.join(IMG_PATH, "outcome_circuit_execution.png")
        plt.savefig(plot_path)
        logger.info(f"Circuit executed successfully with {sample_size} shots! Output shape: {samples.shape}. Plot saved in {plot_path}")
        plt.close()



    def instantiate_task1_protocol(self, input_state='zero', theta=0.0, phi =0.0):
        '''
        Implementation of Proof of Concept protocol with 2 clones.
        Instantiation of three qubits:
        - q0:     input state A
        - q1, q2: Bell pair for clone S1, S2

        INPUTS:
        :input_state: ('zero', 'plus', 'generical')
        :theta:
        '''
        self.name = f'Proof of Concept protocol with input state {input_state}'
        self.input_state = input_state
        self.theta = theta
        self.phi = phi

        # Input state q0
        if input_state == 'zero':
            pass
        elif input_state == 'plus':
            self.circuit.append('H', [0])
        elif input_state == 'generical':
            self.circuit.append('H', [0])
            self.circuit.append('S', [0])
        else:
            raise ValueError(f"State {input_state} does not supported")
    
        # Bell state q1, q2 --> 1/√2 (|00> + |11>)
        self.circuit.append('H', [1])
        self.circuit.append('CNOT', [1, 2])
    
        # Distribute the secret between input q0 and clone q1 through phase kickback
        self.circuit.append('CZ', [1, 0])
    
        logger.info(f"Circuit with name *{self.name}* has been created")



    def redemption_teledata(self, target_clone='S1'):
        '''
        Strategy A: teledata redemption
        Come back the chosen clone to L0
        '''
        clone_qubit = 4 if target_clone == 'S1' else 6

        # Add Bell pair for the clone to come back
        self.circuit.append('H', [7])
        self.circuit.append('CNOT', [7, 8])

        # Teleport the clone t
        self.circuit.append('CNOT', [clone_qubit, 7])
        self.circuit.append('H', [clone_qubit])
        self.circuit.append('M', [clone_qubit, 7])
        self.circuit.append('CX', [7, 8])
        self.circuit.append('CZ', [7, 8])

        if target_clone == 'S2':
            self.circuit.append('CZ', [8, 0])

        self.circuit.append('M', [0])
        logger.info(f"Redemption by teledata configured for path by using {target_clone}")



    def redemption_telegate(self, target_clone='S1'):
        '''
        Strategy B: telegate redemption
        Keep the clone on its location and use non-local CZ through entanglement
        '''
        clone_qubit = 4 if target_clone == 'S1' else 6

        # Simulate remote CZ by using a Bell pair
        self.circuit.append('H', [7])
        self.circuit.append('CNOT', [7, 8])

        # Non-local interaction
        self.circuit.append('CZ', [clone_qubit, 7])
        self.circuit.append('M', [7])
        self.circuit.append('CZ', [8, clone_qubit])

        self.circuit.append('M', [0])
        logger.info(f"Redemption by telegate configured for path by using {target_clone}")


    
    def save_circuit_diagram(self, filename:str):
        # Create the directory if not exist
        os.makedirs(IMG_PATH, exist_ok=True)

        # Generate the diagram and save it
        diagram = str( self.circuit.diagram('timeline-svg') )
        mode = 'wb' if isinstance(diagram, bytes) else 'w'
        file = os.path.sep.join([IMG_PATH, filename])
        with open(file, mode) as f:
            f.write(diagram)

        logger.info(f"Diagram of the circuit *{self.name}* saved in {file}")
