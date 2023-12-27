from typing import List
from obse.sparql_queries import SparQLWrapper
from obse.namespace import MBA
from rdflib import Graph, RDFS

from .pumlmodel import PumlModel


def get_name(wrapper, instance):
    names = wrapper.get_object_properties(instance, RDFS.label)
    return "/".join(names)


def get_type(wrapper, instance):
    return wrapper.get_type(instance).split("#")[1]


def get_id(instance):
    return str(instance).split("#")[1].replace("-", "")


def rdf2puml(graph : Graph) -> PumlModel:

    puml = PumlModel("Model")
    wrapper = SparQLWrapper(graph)

    for instance in wrapper.get_instances():
        instance_name = get_name(wrapper, instance)
        instance_type = get_type(wrapper, instance)

        puml.create_node(instance, instance_name, instance_type, [])

    for (n1, n2) in wrapper.get_references():
        puml.create_relation(n1, n2)

    puml.finish()
    return puml


def statemachines2puml(graph: Graph) -> List[PumlModel]:
    puml_models = {}
    wrapper = SparQLWrapper(graph)

    for state_machine in wrapper.get_instances_of_type(MBA.StateMachine):
        state_machine_name = get_name(wrapper, state_machine)
        state_machine_states = set()

        puml = PumlModel(state_machine_name)
        for state in wrapper.get_out_references(state_machine, MBA.has):
            state_machine_states.add(state)
            state_name = get_name(wrapper, state)
            state_type = wrapper.get_type(state)

            if state_type == MBA.FinalState:
                puml.create_final_state(state_name, [])
            elif state_type == MBA.InitialState:
                puml.create_initial_state(state_name, [])
            elif state_type == MBA.Junction:
                puml.create_junction_state(state_name, [])
            elif state_type == MBA.State:  # default
                puml.create_state(state_name, [])
            else:
                raise ValueError(f"Unknown type {state_type} for {state_name}")

        for transition in wrapper.get_instances_of_type(MBA.Transition): 
            transition_name = get_name(wrapper, transition)
            source_state = wrapper.get_out_references(transition, MBA.source)[0]
            target_state = wrapper.get_out_references(transition, MBA.target)[0]
            guards = wrapper.get_object_properties(transition, MBA.guard)
            guard = " and ".join(guards)

            # Check if states belongs to statemachine
            if source_state in state_machine_states or target_state in state_machine_states:
                source_state_name = get_name(wrapper, source_state)
                target_state_name = get_name(wrapper, target_state)

                puml.create_transition(source_state_name, target_state_name, f"[{guard}] / {transition_name}")
            
        puml.finish()
        puml_models[state_machine_name] = puml

    return puml_models


def packages2puml(graph: Graph) -> PumlModel:
    puml = PumlModel("Components")
    wrapper = SparQLWrapper(graph)

    for package in wrapper.get_instances_of_type(MBA.Subsystem):
        package_name = get_name(wrapper, package)
        puml.create_package(package, package_name)

        for interface in wrapper.get_out_references(package, MBA.has):
            if wrapper.get_type(interface) != MBA.Interface:
                continue
            puml.create_relation(package, interface)

        for component in wrapper.get_out_references(package, MBA.contains):
            component_name = get_name(wrapper, component)
            pattern = wrapper.get_single_object_property(component, MBA.pattern)
            puml.create_component(component, component_name, package, pattern)

            for interface in wrapper.get_out_references(component, MBA.has):
                if wrapper.get_type(interface) != MBA.Interface:
                    continue
                puml.create_relation(component, interface)

            # use
            for used_component in wrapper.get_out_references(component, MBA.use):
                puml.create_component_use(component, used_component)

    for interface in wrapper.get_instances_of_type(MBA.Interface):
        interface_name = get_name(wrapper, interface)
        interface_type = get_type(wrapper, interface)
        puml.create_node(interface, interface_name, interface_type,[])

    puml.finish()
    return puml
