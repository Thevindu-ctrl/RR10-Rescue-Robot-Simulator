import os
from graphviz import Digraph

# FORCE PATH 
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'

def create_uml_class_diagram():
    uml = Digraph('UML_Class', format='png')
    uml.attr(nodesep='0.5', ranksep='0.8')
    uml.attr('node', shape='record', style='filled', color='lightyellow')

    # Robot Base Class
    uml.node('Robot', '{Robot|+ x: double\l+ y: double\l+ state: int\l|+ updatePos()\l+ getState()}')

    # Sensor Base & Derived Classes
    uml.node('Sensor', '{Sensor|# range: double\l# accuracy: double\l|+ virtual read(): double}')
    uml.node('Lidar', '{Lidar (Derived)|+ laserCount: int\l|+ read(): double}')
    uml.node('Ultrasonic', '{Ultrasonic (Derived)|+ triggerPin: int\l|+ read(): double}')

    # Actuator Class
    uml.node('Actuator', '{Actuator|+ motorSpeed: int\l|+ setSpeed(int)}')

    # Controller Class
    uml.node('Controller', '{Controller|+ mode: string\l|+ process(Sensor, Actuator)}')

    # Define Relationships (Inheritance and Composition)
    uml.edge('Lidar', 'Sensor', arrowhead='empty') # Inheritance
    uml.edge('Ultrasonic', 'Sensor', arrowhead='empty') # Inheritance
    uml.edge('Robot', 'Sensor', label='contains', arrowhead='diamond') # Composition
    uml.edge('Robot', 'Actuator', label='contains', arrowhead='diamond')
    uml.edge('Controller', 'Robot', label='manages')

    uml.render(filename='uml_class_diagram', directory='./', cleanup=True, format='png')

def create_architecture_diag():
    arch = Digraph('Architecture', format='png')
    arch.attr(rankdir='LR')
    arch.node('CPP', 'C++ Engine\n(Logic/Threads)', shape='box', style='filled', color='lightblue')
    arch.node('LOGS', 'CSV Logs\n(Data Bridge)', shape='note')
    arch.node('PY', 'Python Visualizer\n(Pygame GUI)', shape='box', style='filled', color='lightgreen')
    arch.edge('CPP', 'LOGS', label='Writes')
    arch.edge('LOGS', 'PY', label='Parses')
    arch.render(filename='architecture_diagram', directory='./', cleanup=True, format='png')

if __name__ == "__main__":
    try:
        create_uml_class_diagram()
        create_architecture_diag()
        print("Success! Generated 'uml_class_diagram.png' and 'architecture_diagram.png'")
    except Exception as e:
        print(f"Error: {e}. Check if Graphviz is installed and path is correct.")