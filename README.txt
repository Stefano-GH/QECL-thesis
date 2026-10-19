##############################
# ----- Virtual environment
# Windows
Create venv: python -m venv <name_of_virtual_environment (typically env)>
Run venv: env/Scripts/activate
Deactivate venv: deactivate

# MAC / Linux
Create venv: python3 -m venv <name_of_virtual_environment (typically env)>
Run venv: env/bin/activate
Deactivate venv: deactivate



# ----- Packages inside venv
See all the packages: pip list
Install new package: pip install <package_name>



# ----- Save venv for remote repository
Export dependencies on an external file: pip freeze --all > requirements.txt



# ----- Import dependencies on a venv
pip install -r requirements.txt



##############################
# ----- Implementazione del circuito a template
Disponendo di due importanti librerie (Stim e Qiskit), si è scelto di lavorare con entrambe per consentire all'utilizzatore del codice di compiere una scelta in base alle diverse situazioni che si possono presentare.

STIM:
Si tratta di un simulatore a stabilizzatori basato sul teorema di Gottesman-Knill. Sfrutta una rappresentazione algebrica degli stati quantistici che scala come un polinomio. Qunidi si possono lanciare migliaia di shot in pochi secondi. Tuttavia, siamo vincolati a lavorare con le porte di tipo Clifford.

QISKIT:
La libreria è in grado di simulare l'intero spazio di Hilbert, permettendo la gestione di parametri continui (theta e phi, ad esempio, nella costruzione di uno stato quantistico arbitrario), estrarre direttamente la matrice di densità e isolare singoli qubit. Tuttavia, l'uso della memoria cresce in modo esponenziale con il numero di qubite e si rischia di non reggere il carico se si lancia un numero elevato di shots.

L'implementazione a template costruisce una classe astratta di base che implementa tutte le funzioni necessarie per i circuiti. Poi, vengono sviluppate due ulteriori classi figlie che ereditano dalla classe astratta i metodi e li rendono compatibili con la specifica libreria.