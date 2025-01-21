

import networkx as nx
from concurrent.futures import ThreadPoolExecutor
import time

def get_user_input():
    """
    Erfasst Benutzereingaben zur Definition von Prozessen, Abhängigkeiten, Dauer und Parallelitätsgrenzen.
    
    Rückgabe:
        processes (dict): Ein Dictionary mit Prozessdefinitionen.
        max_concurrent (int): Maximale Anzahl paralleler Prozesse.
    """
    processes = {}
    print("Definiere die Prozesse und deren Eigenschaften:")
    
    num_processes = int(input("Anzahl der Prozesse: "))
    
    for _ in range(num_processes):
        name = input("Name des Prozesses: ")
        duration = int(input(f"Dauer des Prozesses '{name}' in Sekunden: "))
        dependencies = input(f"Abhängigkeiten von '{name}' (Komma-getrennt, leer lassen für keine): ").split(",")
        dependencies = [dep.strip() for dep in dependencies if dep.strip()]
        processes[name] = {"duration": duration, "dependencies": dependencies}
    
    max_concurrent = int(input("Maximale Anzahl paralleler Prozesse: "))
    return processes, max_concurrent

def create_dependency_graph(processes):
    """
    Erstellt einen gerichteten Graphen (DAG) basierend auf den Prozessabhängigkeiten.
    
    Parameter:
        processes (dict): Ein Dictionary, das die Prozesse und ihre Abhängigkeiten beschreibt.
    
    Rückgabe:
        graph (nx.DiGraph): Ein NetworkX gerichteter Graph, der die Abhängigkeiten darstellt.
    """
    graph = nx.DiGraph()
    for process, details in processes.items():
        graph.add_node(process)
        for dependency in details["dependencies"]:
            graph.add_edge(dependency, process)
    return graph

def execute_process(process, duration):
    """
    Simuliert die Ausführung eines Prozesses.
    
    Parameter:
        process (str): Der Name des Prozesses.
        duration (int): Die Dauer des Prozesses in Sekunden.
    """
    print(f"Starte Prozess: {process}")
    time.sleep(duration)
    print(f"Prozess abgeschlossen: {process}")

def main():
    """
    Hauptfunktion zur Verwaltung und Optimierung der Prozessabläufe.
    """
    # Erfassung der Benutzereingaben
    processes, max_concurrent = get_user_input()
    
    # Erstellung des Abhängigkeitsgraphen
    graph = create_dependency_graph(processes)
    
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Der Abhängigkeitsgraph enthält Zyklen! Bitte prüfen Sie die Eingabedaten.")
    
    # Topologische Sortierung für die Ausführungsreihenfolge
    execution_order = list(nx.topological_sort(graph))
    print(f"\nAusführungsreihenfolge: {execution_order}\n")
    
    # Initialisierung der parallelen Ausführung
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        futures = {}
        completed = set()
        results = []  # Speichert Ergebnisse der Ausführung
        
        while execution_order:
            # Bestimme Prozesse, die ausgeführt werden können
            ready_to_run = [
                process for process in execution_order
                if all(dep in completed for dep in graph.predecessors(process))
            ]
            
            # Starte ausführbare Prozesse unter Beachtung der Parallelitätsgrenze
            for process in ready_to_run:
                if len(futures) < max_concurrent:
                    execution_order.remove(process)
                    futures[process] = executor.submit(
                        execute_process, process, processes[process]["duration"]
                    )
            
            # Überwache Threads und markiere abgeschlossene Prozesse
            for process, future in list(futures.items()):
                if future.done():
                    completed.add(process)
                    results.append(f"Prozess {process} abgeschlossen.")
                    del futures[process]
        
        # Warten auf Abschluss aller laufenden Prozesse
        executor.shutdown(wait=True)
    
    # Ergebnisübersicht anzeigen
    print("\nErgebnisse der Prozessausführung:")
    for result in results:
        print(result)

if __name__ == "__main__":
    main()
