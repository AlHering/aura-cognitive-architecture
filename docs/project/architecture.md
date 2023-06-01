# Project Architecture
The project can be understood as a workbench for developing and testing more complex AI-leveraging architectures, with special focus on the topic Cognitive Architecture and the role of dynamic interfaces. This defines the base line for the necessary components.

# Modular Fronend
A modular frontend is crucial to the project beeing a "workbench". It will allow to abstract away most of the basic administrative work around developing and testing different solutions, concepting and visualizing (cognitive) architectures and understanding the data-flow, data-lineage and evaluating data pipelines and the used components.

## Docker as base
With Docker (and other containerization-solutions) as the foundation of modern DevOps work and allowing for environment-agnostic and highly scalable solutions with optimized CI/CD-pipelines, it will be used as base for this project.
The idea is to abstract away a large portion of backend functionality inside containers to keep the focus on developing the interfaces. 
With a well planned and implemented interface, different solutions can be containerized (if not already available as containers) and evaluated against each other.

