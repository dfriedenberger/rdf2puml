from .group import Group
from .constants import DIRECTION, POSITION

def create_unique_id(o):
    s = str(o).split('#')[-1]
    return s.replace("/", "_").replace("-", "_").replace(":", "_").replace("[", "_").replace("]", "_").replace(" ", "_").replace("(", "_").replace(")", "_")


class PumlModel:

    def __init__(self, title, layout="LAYOUT_TOP_DOWN"):
        self.puml = []
        self.nodes = Group(None, None)
        self.components = Group(None, None)
        self.states = Group(None, None)
        self.relations = []
        self.component_uses = []
        self.transitions = []
        self.datastructs = []
        self.note_index = 0
        self.notes = []

        self.puml.append("@startuml")
        self.puml.append("!include c4/C4.puml")
        self.puml.append("!include nano/nanoservices.puml")
        self.puml.append(f"title {title}")
        self.puml.append(layout)

        self.cache = set()

    def create_node(self, node, node_name, node_type, group):
        node_id = create_unique_id(node)
        if node_id in self.cache:  # already created
            return

        # T = "Unknown"
        # if type in ["Process","Message","Interface","Service"]:
        # TODO check if Type exists, if not use default
        T = node_type

        puml_obj = f'{T}({node_id}, "{node_name}","{node_type}")'

        self.nodes.append(group, puml_obj)
        self.cache.add(node_id)

    def create_relation(self, node1, node2, name=" "):
        id1 = create_unique_id(node1)
        id2 = create_unique_id(node2)
        puml_rel = f'Rel_D({id1}, {id2},"{name}")'
        self.relations.append(puml_rel)

    def create_relation_directed(self, node1, node2, name=" ", direction=DIRECTION.NONE):
        id1 = create_unique_id(node1)
        id2 = create_unique_id(node2)
        puml_rel = f'{id1} -{direction}-> {id2}: "{name}"'
        self.relations.append(puml_rel)

    def create_relation_undirected(self, node1, node2, name=" "):
        id1 = create_unique_id(node1)
        id2 = create_unique_id(node2)
        puml_rel = f'{id1} -- {id2}: "{name}"'
        self.relations.append(puml_rel)

    # state machines
    def create_state(self, state, group):
        puml_obj = f"state {state}"
        self.states.append(group, puml_obj)

    def create_junction_state(self, state, group):
        puml_obj = f"state {state} <<choice>>"
        self.states.append(group, puml_obj)

    def create_initial_state(self, state, group):
        puml_obj = f"state {state} <<start>>"
        self.states.append(group, puml_obj)

    def create_final_state(self, state, group):
        puml_obj = f"state {state} <<end>>"
        self.states.append(group, puml_obj)

    def create_transition(self, source_state, target_state, description):
        puml = f"{source_state} --> {target_state} : {description}"
        self.transitions.append(puml)

    def create_package(self, package, package_name):  # TODO Workaround
        package_id = create_unique_id(package)
        self.components.groups[package_id] = Group(package_id, package_name)
        return package_id

    def create_component(self, component, name, package, descriptions):
        pattern = "Component"
        package_id = create_unique_id(package)
        component_id = create_unique_id(component)

        component_obj = f'\tcomponent {component_id} <<{pattern}>> [{name}\n'

        # Add Multiline description
        if len(descriptions) > 0:
            component_obj += "\t\t\n"
            component_obj += "\t\t---\n"
        for description in descriptions:
            component_obj += f'\t\t* {description}\n'
   
        component_obj += '\t]'
        self.components.append([package_id], component_obj)

    def create_component_use(self, component, used_component):
        component_id = create_unique_id(component)
        used_id = create_unique_id(used_component)
        puml_use = f'[{component_id}] --> [{used_id}] : use'
        self.component_uses.append(puml_use)

    # data structs
    def create_datastruct(self,datastruct, name, properties):

        datastruct_id = create_unique_id(datastruct)
        datastruct_puml = f'map "{name}" as {datastruct_id} {{\n'
        for (property_type, property_name, property_datastruct) in properties:
            if property_type == "basic":
                datastruct_puml += f'\t{property_name} => {property_datastruct.split("#")[-1]}\n'
            elif property_type == "array":
                datastruct_puml += f'\t{property_name}[] *-> {create_unique_id(property_datastruct)}\n'
            else:
                raise ValueError(f"{property_type} not implemented")
        datastruct_puml += "}\n"
        self.datastructs.append(datastruct_puml)

    # notes
    def create_note(self, obj, note, position=POSITION.NONE):

        obj_id = create_unique_id(obj)

        if position:
            puml = f'note {position} of {obj_id}: "{note}\n'
        else:
            self.note_index += 1
            puml = f'note "{note}" as N{self.note_index}\n'
            puml += f'{obj_id} .. N{self.note_index}\n'

        self.notes.append(puml)

    def finish(self):

        self.puml.extend(self.nodes.to_puml_package())
        self.puml.extend(self.components.to_puml_package())
        self.puml.extend(self.states.to_puml_package())
        self.puml.extend(self.datastructs)

        self.puml.extend(self.relations)
        self.puml.extend(self.component_uses)
        self.puml.extend(self.transitions)

        self.puml.extend(self.notes)

        self.puml.append("@enduml")
        return self.puml

    def serialize(self, filename):
        with open(filename, "w", encoding="UTF-8") as f:
            f.write('\n'.join(self.puml))
