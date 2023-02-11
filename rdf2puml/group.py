

def create_unique_id(o):
    s = str(o).split('#')[-1]
    return s.replace("/","_").replace("-","_").replace(":","_")


class Group:

    def __init__(self,id,name):
        self.name = name
        self.id = id
        self.nodes = []
        self.groups = {}


    def append(self,group,node):

        if(len(group) == 0):
            self.nodes.append(node)
            return

        head, *tail = group

        if head not in self.groups:
            self.groups[head] = Group(head,head)
        self.groups[head].append(tail,node)


    def to_puml_package(self):


        puml = []

        if self.name != None:
            puml.append(f'rectangle "'+self.name+'" as '+self.id+' <<subsystem>> {')
            #puml.append(f'package "'+self.name+'" as '+self.id+' {')
           

        puml.extend(self.nodes)
        for gn in self.groups:
            puml.extend(self.groups[gn].to_puml_package())

        if self.name != None:
            puml.append("}")
        return puml

