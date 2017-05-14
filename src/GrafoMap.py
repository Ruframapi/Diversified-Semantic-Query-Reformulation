# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 10:38:25 2016

@author: proyecto
"""

import networkx as nx
import json


class GrafoMap:
    
    G = nx.DiGraph()

    alpha=0.85 #Parametro del Pagerank    
    
    FileName = "Filename";
    
    FileOutput = "FileOut";
    
    PathGuadarGrafo = "Grafos/"; 
    
    labelNodeDictionary = {}

    jsonDictionary = {}
    
    numNodes = 0

    def __init__(self, filename = "Filename", fileoutput = "FileOut"):
        """ Constructor """
        self.FileName = filename
        self.FileOutput = fileoutput;

        
    def dreagrafo(self):
        """ Metodo Principal para la Construccion del grafo"""
        rdfc = open (self.FileName,'r')
        lines = rdfc.readlines()
        for line in lines:
            conex=line.split("-|")
            if len(conex)>0:
                self.addnodeG(conex[0])
                self.addnodeG(conex[1])
                self.addedgeG(conex[0],conex[1],conex[2])
        
    def addedgeG(self,nodeIni,nodeFin,edgeProperty):
        
        if nodeIni.endswith("*"):
            nodeIni=nodeIni[:-1]
        if nodeFin.endswith("*"):
            nodeFin=nodeFin[:-1]
        
        nodeINIid = self.labelNodeDictionary[nodeIni]
        nodeFINid = self.labelNodeDictionary[nodeFin]
        
        edgeProperty=edgeProperty.replace('http://www.w3.org/2000/01/rdf-schema#','rdfs:')
        edgeProperty=edgeProperty.replace('http://dbpedia.org/ontology/','dbo:')
        edgeProperty=edgeProperty.replace('http://purl.org/dc/terms/','dct:')        
        edgeProperty=edgeProperty.replace("\n","")
        indice = [i for i,v in enumerate(self.G.edges()) if (v[0]==nodeINIid and v[1]==nodeFINid)]
        if (len(indice)>0): #Si ya existe esta conexion
            self.G[nodeINIid][nodeFINid]['weight']+=1
            self.G[nodeINIid][nodeFINid]['conexpro']= edgeProperty+"-"+self.G[nodeINIid][nodeFINid]['conexpro']
        else:
            self.G.add_edge(nodeINIid,nodeFINid,weight=1,conexpro=edgeProperty)
        
    def addnodeG(self,node):
        """Verifica la existencia del nodo y si es es de un path o de la busqueda libre"""
        if node.endswith("*"):
            path=True
            node=node[:-1]
        else:
            path=False
        

        if node not in self.labelNodeDictionary.keys():
            self.numNodes+=1
            self.labelNodeDictionary[node] = self.numNodes
            if path:
                #self.idNodeDictionary[self.numNodes] = node
                self.G.add_node(self.numNodes,label=node,camino="True")
            else:
                self.G.add_node(self.numNodes,label=node,camino="False")
    
    def pageRankG(self):
        """Calculo del pagerank y se agrega como atributo a los nodos"""
        pr=nx.pagerank(self.G,self.alpha)
        for node,prval in pr.iteritems():
            self.G.node[node]['pagerank'] = float("{0:.4f}".format(prval))

    def guardagrafo(self):
        """Guarda el grafo en gexf y json"""
        name=self.PathGuadarGrafo+self.FileOutput+".gexf"
        namej=self.PathGuadarGrafo+self.FileOutput+".json"
        nx.write_gexf(self.G,name)
        nodes = []
        edges = []
        colordict = {}
        colordict["True"] = "rgb(220,246,215)"
        colordict["False"] = "rgb(18,126,233)" 
        for node,attr in self.G.nodes(data = True): 
            nodes.append({"label":attr['label'],"id":node,"value":attr['pagerank'],"color":colordict[attr['camino']],"attributes":{"pagerank":attr['pagerank'],"camino":attr['camino'] }})

        for edge in self.G.edges(data = True):
            edges.append({"source": edge[0],"target":edge[1],"value":edge[2]['weight'],"attributes":{"weight":edge[2]['weight'],"conexpro":edge[2]['conexpro']}})
            
        self.jsonDictionary["nodes"]=nodes
        self.jsonDictionary["edges"]=edges
        fo=open(namej,"w")
        json.dump(self.jsonDictionary,fo)
        
        #print self.jsonDictionary
        

    def ejecutarproceso(self):
        """Ejecuta de forma sequencial el proceso de generacion del grafo y construye un archivo output"""
        self.dreagrafo()
        self.pageRankG()
        self.guardagrafo()

            
#dbpe = GrafoMap("CA003", "CA003Out")
#dbpe.ejecutarproceso()
#print dbpe.G.nodes(data=True)