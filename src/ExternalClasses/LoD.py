
#******************************************************************************
#                                  LoD.py
#******************************************************************************
import hou #@UnresolvedImport

buildingEngineNames = ["Comp", "Subdiv", "Repeat", "Insert", "Extrude", "CreateBase", "Roof", "Trans", "Filter"]

class obtenirNodes:
    def __init__(self):
        self.nodesObtinguts = []
        
class obtenirNodesArrels(obtenirNodes):
    def obtenir(self):
        for m in hou.selectedNodes()[0].parent().children():
            if m.inputs() == () and m.outputs() != ():
                if m not in self.nodesObtinguts:
                    self.nodesObtinguts.append(m)
        return self.nodesObtinguts
    
class obtenirNodesFulles(obtenirNodes):
    def obtenir(self):
        for m in hou.selectedNodes()[0].parent().children():
            if m.outputs() == () and m.inputs() != ():
                if m not in self.nodesObtinguts:
                    self.nodesObtinguts.append(m)
        return self.nodesObtinguts
    
class obtenirNodesIndependents(obtenirNodes):
    def obtenir(self):
        for m in hou.selectedNodes()[0].parent().children():
            if m.inputs() == () and m.outputs() == ():
                if m not in self.nodesObtinguts:
                    self.nodesObtinguts.append(m)
        return self.nodesObtinguts
    

class selectorConnexions:
    pass
        
class connexioAscendent(selectorConnexions):
    def connected(self, node):
        return node.inputs()
    
class connexioDescendent(selectorConnexions):
    def connected(self, node):
        return node.outputs()
        
        
class LoD:
    def __init__(self):
        self.nodesVisiatats = []
        self.parent = hou.selectedNodes()[0].parent()
        self.merge = ""

    def visitarNode(self, node, selectorConnexions):
        if node.path() not in self.nodesVisiatats:
            self.nodesVisiatats.append(node.path())
            self.tractar(node)
            for n in selectorConnexions.connected(node):
                self.visitarNode(n, selectorConnexions)
                
    def recorrer(self, selectorConnexions, llistnodes):
        node = self.ferRecorregut(selectorConnexions, llistnodes)
        return node
        self.finish()
        
    def finish(self):
        pass

class LoD_max(LoD):
    
    def tractar(self, node):
        if node.type().name() in buildingEngineNames:
            counter = 1
            if node.type().name() == 'Comp':
                counter = node.parm('components').eval()
            elif node.type().name() == 'Subdiv':
                counter = node.parm('Divisions').eval()
            elif node.type().name() == 'Filter':
                counter = 2
            self.outputs = []
            for n in node.outputs():
                filter = n.parm('filter').evalAsString()
                for f in filter.split(' '):
                    self.outputs.append(f)
            for s in range(counter):
                if node.parm('product' + str(s)).evalAsString() not in self.outputs:
                    # Afegim al merge
                    numobj = self.merge.parm('numobj').eval() + 1
                    self.merge.parm('numobj').set(numobj)
                    self.merge.parm('objpath' + str(numobj)).set(node.path())
                    self.merge.parm('group' + str(numobj)).set(node.parm('product' + str(s)))

    def ferRecorregut(self, selectorConnexions, llistnodes):
        self.merge = self.parent.createNode('object_merge')
        self.merge.parm('numobj').set(0)
        for n in llistnodes:
            self.visitarNode(n, selectorConnexions)
        return self.merge

class ImprimirProductsNoUtilitzats(LoD):                
    def tractar(self, node):
        if node.type().name() in buildingEngineNames:
            counter = 1
            if node.type().name() == 'Comp':
                counter = node.parm('components').eval()
            elif node.type().name() == 'Subdiv':
                counter = node.parm('Divisions').eval()
            elif node.type().name() == 'Filter':
                counter = 2
            self.outputs = []
            for n in node.outputs():
                filter = n.parm('filter').evalAsString()
                for f in filter.split(' '):
                    self.outputs.append(f)
        else:
            print " ~", node.type().name(), " not in buildingEngineNames"

    def ferRecorregut(self, selectorConnexions, llistnodes):
        for n in llistnodes:
            self.visitarNode(n, selectorConnexions)

class LoD_user(LoD):
    def __init__(self):
        self.nodesVisiatats = []
        self.parent = hou.selectedNodes()[0].parent()
        self.merge = ""
        self.afegir = []
        self.excloure = []

    def tractar(self, node):
        if node.type().name() in buildingEngineNames:
            filter = node.parm('filter').evalAsString()
            for n in node.inputs():
                counter = 1
                if n.type().name() == 'Comp':
                    counter = n.parm('components').eval()
                elif n.type().name() == 'Subdiv':
                    counter = n.parm('Divisions').eval()
                elif n.type().name() == 'Filter':
                    counter = 2
                for s in range(counter):
                    nProd = n.path() + ":" + n.parm('product' + str(s)).evalAsString()
                    if n.parm('product' + str(s)).evalAsString() not in filter.split(' '):
                        if nProd not in self.afegir:
                            self.afegir.append(nProd)
                    else:
                        self.excloure.append(nProd)
        else:
            print " ~", node.type().name(), " not in buildingEngineNames"
    
    def ferRecorregut(self, selectorConnexions, llistnodes):
        self.merge = self.parent.createNode('object_merge')
        self.merge.parm('numobj').set(0)
        for n in llistnodes:
            if n.type().name() in buildingEngineNames:
                nProd = n.path() + ":" + n.parm('product' + str(0)).evalAsString()
                if nProd not in self.afegir:
                    self.afegir.append(nProd)
            
            self.visitarNode(n, selectorConnexions)

    def finish(self):
        for n in self.afegir:
            if n not in self.excloure:
                numobj = self.merge.parm('numobj').eval() + 1
                self.merge.parm('numobj').set(numobj)
                self.merge.parm('objpath' + str(numobj)).set(n.split(':')[0])
                self.merge.parm('group' + str(numobj)).set(n.split(':')[1])
