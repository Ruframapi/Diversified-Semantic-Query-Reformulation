# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON
import itertools
import ConfigParser
import json

class QKG:
    """ Clase KeyWordMap Mapea palabras recuperadas a recursos.
        Similar al servicio de Spotlight    
    """
    
    virtuosoEndpoint = ""
    
    #Input SET
    S= []    

    #Expanded SET
    S_expand= []    
    
    # f: S set size control parameter
    f = 20
    
    #Maximun path lenght
    l_maxpath = 2 
    
    #QKG Archivo Salida
    FileName = "Filename";
    
    #BusquedaLibre
    busDisambiguates = "PREFIX :     <http://dbpedia.org/resource/> \
                        PREFIX dbp:  <http://dbpedia.org/property/> \
                        PREFIX dbo:  <http://dbpedia.org/ontology/> \
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
                            SELECT DISTINCT ?p  FROM <http://dbpedia.org>   WHERE {  \
                            %s dbo:wikiPageDisambiguates ?p.  \
                            FILTER(STRSTARTS(STR(?p), 'http://dbpedia.org/resource/')) \
                            FILTER(!CONTAINS(STR(?p), 'Category')) \
                            } \
                        ";
    #BusquedaConexion

    busSeeAlso = "PREFIX :     <http://dbpedia.org/resource/> \
                     PREFIX dbp:  <http://dbpedia.org/property/> \
                     PREFIX dbo:  <http://dbpedia.org/ontology/> \
                     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
                     SELECT DISTINCT ?p  FROM <http://dbpedia.org>   WHERE { \
                     %s rdfs:seeAlso ?p. \
                    FILTER(STRSTARTS(STR(?p), 'http://dbpedia.org/resource/')) \
                    FILTER(!CONTAINS(STR(?p), 'Category')) \
                    } \
                    ";

    #Busqueda Info jerarquica del Nodo
    busWikiCate = "PREFIX :     <http://dbpedia.org/resource/>  \
                  PREFIX dbp:  <http://dbpedia.org/property/>  \
                  PREFIX dbo:  <http://dbpedia.org/ontology/>  \
                  PREFIX dct:  <http://purl.org/dc/terms/>  \
                  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  \
                  SELECT DISTINCT ?p  FROM <http://dbpedia.org>   WHERE { \
                  %s dct:subject ?p. \
                  FILTER(CONTAINS(STR(?p), 'Category')) \
                  } \
                    ";          
    
    #Busqueda Info Lista Recursos Vecinos
    busWikiCate = "PREFIX :     <http://dbpedia.org/resource/>  \
                  PREFIX dbp:  <http://dbpedia.org/property/>  \
                  PREFIX dbo:  <http://dbpedia.org/ontology/>  \
                  PREFIX dct:  <http://purl.org/dc/terms/>  \
                  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  \
                  SELECT DISTINCT ?p  FROM <http://dbpedia.org>   WHERE { \
                  %s dct:subject ?p. \
                  FILTER(CONTAINS(STR(?p), 'Category')) \
                  } \
                    ";   
                    
    busNeighborhood =" PREFIX :     <http://dbpedia.org/resource/>  \
                    PREFIX dbp:  <http://dbpedia.org/property/>  \
                    PREFIX dbo:  <http://dbpedia.org/ontology/>  \
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  \
                    SELECT DISTINCT ?r1  FROM <http://dbpedia.org>   WHERE { \
                    %s ?p1 ?r1.  \
                    FILTER(!CONTAINS(STR(?r1), 'Category'))  \
                    FILTER(!CONTAINS(STR(?r1), 'File')) \
                    FILTER(STRSTARTS(STR(?r1), 'http://dbpedia.org/resource/')) \
                    FILTER(STRSTARTS(STR(?p1), 'http://dbpedia.org/ontology/')) \
                    } \
                    LIMIT 3 "; #Remover el limite cuando se trabaje contra el Big Server

    busLabels ="PREFIX :     <http://dbpedia.org/resource/>  \
                PREFIX dbp:  <http://dbpedia.org/property/>  \
                PREFIX dbo:  <http://dbpedia.org/ontology/>  \
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
                PREFIX foaf: <http://xmlns.com/foaf/0.1/> \
                SELECT DISTINCT ?r1 ?r2 FROM <http://dbpedia.org>   WHERE {  \
                %s rdfs:label ?r1. \
                OPTIONAL { \
                %s foaf:name  ?r2 \
                } \
                FILTER (LANG(?r1) = 'en') \
                } ";
                    
                    
    ConsultasSetExpandedDis = []
    ConsultasSetExpandedSeeA = []
    PathGuadarGrafo = "Grafos/"; 
    NodesInfo = {}
    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------
    
    def __init__(self, resourceSet = [], f_val = 20, l_maxpath_val = 2, filename = "Filename"):
        """ Constructor """
        self.S = resourceSet
        self.f = f_val;
        self.l_maxpath_val = l_maxpath_val;
        self.FileName = filename;
        config = ConfigParser.ConfigParser()
        config.read('config.cfg')
        self.virtuosoEndpoint=config.get('Virtuoso','endpoint')
        self.PathGuadarGrafo=config.get('Grafos','path')
                
    def generarExpandedSet(self):
        """Construye el expanded SET"""  
        
        for idw,resource in enumerate(self.S):
            consultasparqlDis = self.busDisambiguates % (self.limpiaRecursos(resource))
            consultasparqlSeeA = self.busSeeAlso % (self.limpiaRecursos(resource))
            self.ConsultasSetExpandedDis.append(consultasparqlDis)
            self.ConsultasSetExpandedSeeA.append(consultasparqlSeeA)
    
    def aplicarConsultaSetExpanded(self):
        """Se ejecuta cada consulta"""
        
        for consultaCL in self.ConsultasSetExpandedDis:
            #print(consultaCL)
            resultoCL=self.consulta(consultaCL)
            for resul in resultoCL['results']['bindings']:
                uri = resul['p']['value']
                uri=uri.replace('http://dbpedia.org/resource/','')
                self.S_expand.append((uri,'D'))

        for consultaCL in self.ConsultasSetExpandedSeeA:
            #print(consultaCL)
            resultoCL=self.consulta(consultaCL)
            for resul in resultoCL['results']['bindings']:
                uri = resul['p']['value']
                uri=uri.replace('http://dbpedia.org/resource/','')
                self.S_expand.append((uri,'SA'))
                
    def generarNodeInfo(self):
        """Obtiene la información de cada Nodo en S_expand"""
        nodosgraph = self.S +self.S_expand
        for tuplanodo in nodosgraph:
            nodeinfo={}
            #NHSW
            nodeWikiCat = []
            consultasparqlWikiCate = self.busWikiCate % (self.limpiaRecursos(tuplanodo[0]))
            #print consultasparqlWikiCate
            resultoWikiCat=self.consulta(consultasparqlWikiCate)
            for resul in resultoWikiCat['results']['bindings']:
                uri = resul['p']['value']
                uri=uri.replace('http://dbpedia.org/resource/Category:','')
                nodeWikiCat.append(uri)
            nodeinfo['NHSW'] = nodeWikiCat
            #LNR
            nodeLNR = []
            listofRecurNodes = [tuplanodo[0]]
            for i in range(l_maxpath_val):
                #print str(i) + "----------------"
                levelnodes = []
                for recurNode in listofRecurNodes:
                    consultasparqlLNR = self.busNeighborhood % (self.limpiaRecursos(recurNode))
                    #print consultasparqlLNR
                    resultLNR=self.consulta(consultasparqlLNR)
                    for result in resultLNR['results']['bindings']:                        
                        uri = result['r1']['value']
                        uri=uri.replace('http://dbpedia.org/resource/','')
                        if uri not in self.S:
                            levelnodes.append(uri)
                            nodeLNR.append((uri,i))
                listofRecurNodes = levelnodes
            nodeinfo['LNR'] = nodeLNR
            #NL
            nodeLabels = []
            consultasparqlLabels = self.busLabels % (self.limpiaRecursos(tuplanodo[0]),self.limpiaRecursos(tuplanodo[0]))
            resultLabel=self.consulta(consultasparqlLabels)     
            #print resultLabel
            for resul in resultLabel['results']['bindings']:
                if 'r1' in resul.keys(): 
                    nodeLabels.append(resul['r1']['value'])
                if 'r2' in resul.keys(): 
                    nodeLabels.append(resul['r2']['value'])
            print nodeLabels
            nodeinfo['NL'] = nodeLabels               
            self.NodesInfo[tuplanodo[0]]=nodeinfo
                               
    def limpiaRecursos(self, recursoDirty):
        """Limpia de () las consultas SPARQL"""
        recursoClean = recursoDirty
        limpio = True
        if ("(" in recursoClean) or (")" in recursoClean) or ("." in recursoClean) or ("," in recursoClean) or ("&" in recursoClean):
            limpio = False
            out = "<http://dbpedia.org/resource/" + recursoClean + ">"
            recursoClean = out
  
        if (limpio):
            return ":"+recursoClean
        else:
            return recursoClean
        
                    
    def archivoSalida(self):
        name=self.PathGuadarGrafo+self.FileName
        fo=open(name+"_Nodes","w")
        json.dump(self.NodesInfo,fo)
        fo.close()
        fo=open(name+"_S","w")
        json.dump(self.S,fo)
        fo.close()
        fo=open(name+"_S_expand","w")
        json.dump(self.S_expand,fo)
        fo.close()         
        
    def consulta(self, sqlQuery):
        """Ejecuta query"""  
        sparql = SPARQLWrapper(self.virtuosoEndpoint)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(sqlQuery)
        results = sparql.query()
        results = results.convert()
        return results

    def run(self):
        """Ejecuta de forma sequencial el proceso de consultas a DBpedia y genera un archivo output"""
        #self.generarConsultasLibres()
        self.generarExpandedSet()
        self.aplicarConsultaSetExpanded()
        self.generarNodeInfo()
        self.archivoSalida()


#myresources=["Car","Auto"]
#f_val=20
#l_maxpath_val = 2
#filename = "QUERY0012"
#queryGraph = QKG(myresources, f_val, l_maxpath_val,filename)
#queryGraph.run()