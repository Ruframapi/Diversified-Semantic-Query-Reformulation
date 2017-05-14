# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON
import itertools

class KeyWordMap:
    """ Clase KeyWordMap"""
        
    # Nivel de profundidad de conexiones entre recursos
    nivel_profundidad = 1
    
    #Numero de resultados en la busqueda Libre
    limit_BL = 10 
    
    #Numero de resultados en la busqueda Conexion
    limit_BC = 50    
    
    # Key words
    key_words = [];   
    
    #Consultas
    ConsultasLibres = [];
    ResultConsultaLibre = [];
    CombiConsultaLibre = [];
    ConsultasConexion = [];
    ResultConsultasConexion = [];
    
    #ArchivoSalida
    FileName = "Filename";
    
    #BusquedaLibre
    busLibre = "PREFIX :     <http://dbpedia.org/resource/> \
                PREFIX dbp:  <http://dbpedia.org/property/> \
                PREFIX dbo:  <http://dbpedia.org/ontology/> \
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
                SELECT DISTINCT ?s  FROM <http://dbpedia.org>   WHERE { \
                ?s rdfs:label ?label. \
                FILTER(STRSTARTS(STR(?s), 'http://dbpedia.org/resource/')) \
                FILTER(!CONTAINS(STR(?s), 'Category')) \
                FILTER (regex(?label,'%s','i')) \
                } \
                LIMIT %s \
                ";
    #BusquedaConexion


    busConex1 = "PREFIX :     <http://dbpedia.org/resource/> \
                 SELECT DISTINCT ?p1  FROM <http://dbpedia.org> WHERE  { \
                 %s ?p1 %s  . \
                 FILTER(!CONTAINS(STR(?p1), 'wikiPageDisambiguates')) \
                 } \
                 LIMIT %s \
                ";
                
    busConex2 = "PREFIX :     <http://dbpedia.org/resource/> \
                 SELECT DISTINCT ?p1 ?o1 ?p2 FROM <http://dbpedia.org> WHERE { \
                 %s ?p1 ?o1 . \
                 %s ?p2 ?o1 . \
                 FILTER(!CONTAINS(STR(?p1), 'wikiPageDisambiguates')) \
                 FILTER(!CONTAINS(STR(?p2), 'wikiPageDisambiguates')) \
                 FILTER(STRSTARTS(STR(?o1), 'http://dbpedia.org/resource/')) \
                 } \
                 LIMIT %s \
                ";
                
                
    busConex3_1 = "PREFIX :     <http://dbpedia.org/resource/> \
                   SELECT DISTINCT ?p1 ?o1 ?p2 ?o2 ?p3 FROM <http://dbpedia.org> WHERE { \
                   %s ?p1 ?o1 . \
                   %s ?p2 ?o2 . \
                   ?o1 ?p3 ?o2 . \
                   FILTER(!CONTAINS(STR(?p1), 'wikiPageDisambiguates')) \
                   FILTER(!CONTAINS(STR(?p2), 'wikiPageDisambiguates')) \
                   FILTER(!CONTAINS(STR(?p3), 'wikiPageDisambiguates')) \
                   FILTER(STRSTARTS(STR(?o1), 'http://dbpedia.org/resource/')) \
                   FILTER(STRSTARTS(STR(?o2), 'http://dbpedia.org/resource/')) \
                   } \
                   LIMIT %s \
                   ";

    busConex3_2 = "PREFIX :     <http://dbpedia.org/resource/> \
                   SELECT DISTINCT ?p1 ?o1 ?p2 ?o2 ?p3 FROM <http://dbpedia.org> WHERE { \
                   %s ?p1 ?o1 . \
                   %s ?p2 ?o2 . \
                   ?o2 ?p3 ?o1 . \
                   FILTER(!CONTAINS(STR(?p1), 'wikiPageDisambiguates')) \
                   FILTER(!CONTAINS(STR(?p2), 'wikiPageDisambiguates')) \
                   FILTER(!CONTAINS(STR(?p3), 'wikiPageDisambiguates')) \
                   FILTER(STRSTARTS(STR(?o1), 'http://dbpedia.org/resource/')) \
                   FILTER(STRSTARTS(STR(?o2), 'http://dbpedia.org/resource/')) \
                   } \
                   LIMIT %s \
                   ";
    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------
    
    def __init__(self, nivelProfundidad =1, words = [], limitBL = 10, filename = "Filename"):
        """ Constructor """
        self.nivel_profundidad = nivelProfundidad
        self.key_words = words;
        self.limit_BL = limitBL;
        self.limit_BC = limitBL*5;
        self.FileName = filename;
                
    def generarConsultasLibres(self):
        """Por cada palabra una busqueda libre"""  
        
        for idw,word in enumerate(self.key_words):
            consultasparql = self.busLibre % (word,self.limit_BL)
            self.ConsultasLibres.append(consultasparql)
            
                       
        return self.ConsultasLibres
    
    def aplicarConsultasLibres(self):
        """Se ejecuta cada consulta libre"""
        
        for consultaCL in self.ConsultasLibres:
            print(consultaCL)
            resultoCL=self.consulta(consultaCL)
            for resul in resultoCL['results']['bindings']:
                uri = resul['s']['value']
                uri=uri.replace('http://dbpedia.org/resource/','')
                self.ResultConsultaLibre.append(uri)
    
    def generarCombinaciones(self):
        """Combina cada recurso como una pareja"""
        combi = [list(x) for x in itertools.combinations(self.ResultConsultaLibre, 2)]
        self.CombiConsultaLibre=combi
        #print(self.CombiConsultaLibre)
        
    def limpiaRecursos(self, recursoDirty):
        """Limpia de () las consultas SPARQL"""
        recursoClean = recursoDirty
        limpio = True
        if ("(" in recursoClean) or (")" in recursoClean) or ("." in recursoClean):
            limpio = False
            out = "<http://dbpedia.org/resource/" + recursoClean + ">"
            recursoClean = out
  
        if (limpio):
            return ":"+recursoClean
        else:
            return recursoClean
        
    def generarConsultasConexion(self):
        """Genera consultas de conexion entre dos recursos"""
        for parRecursos in self.CombiConsultaLibre:
            parRecursosL0=self.limpiaRecursos(parRecursos[0])
            parRecursosL1=self.limpiaRecursos(parRecursos[1])
            
            if self.nivel_profundidad>=1:
                consultasparql = self.busConex1 % (parRecursosL0,parRecursosL1,self.limit_BC)
                print consultasparql;
                resultoCC=self.consulta(consultasparql)
                for resul in resultoCC['results']['bindings']:
                    triple = parRecursos[0]+"-|"+parRecursos[1]+"-|"+resul['p1']['value']
                    self.ResultConsultasConexion.append(triple)                
            
            if self.nivel_profundidad>=2:
                consultasparql = self.busConex2 % (parRecursosL0,parRecursosL1,self.limit_BC)
                resultoCC=self.consulta(consultasparql)
                for resul in resultoCC['results']['bindings']:
                    o1=resul['o1']['value']
                    o1=o1.replace('http://dbpedia.org/resource/','')
                    triple1 = parRecursos[0]+"-|"+o1+"*-|"+resul['p1']['value']
                    triple2 = parRecursos[1]+"-|"+o1+"*-|"+resul['p2']['value']
                    self.ResultConsultasConexion.append(triple1)  
                    self.ResultConsultasConexion.append(triple2)  
                    
            if self.nivel_profundidad>=3:
                consultasparql = self.busConex3_1 % (parRecursosL0,parRecursosL1,self.limit_BC)
                resultoCC=self.consulta(consultasparql)
                for resul in resultoCC['results']['bindings']:
                    o1=resul['o1']['value']
                    o1=o1.replace('http://dbpedia.org/resource/','')
                    o2=resul['o2']['value']
                    o2=o1.replace('http://dbpedia.org/resource/','')
                    triple1 = parRecursos[0]+"-|"+o1+"*-|"+resul['p1']['value']
                    triple2 = parRecursos[1]+"-|"+o2+"*-|"+resul['p2']['value']
                    triple3 = o1+"*-|"+o2+"*-|"+resul['p3']['value']                    
                    self.ResultConsultasConexion.append(triple1)  
                    self.ResultConsultasConexion.append(triple2)  
                    self.ResultConsultasConexion.append(triple3) 

                consultasparql = self.busConex3_2 % (parRecursosL0,parRecursosL1,self.limit_BC)
                resultoCC=self.consulta(consultasparql)
                for resul in resultoCC['results']['bindings']:
                    o1=resul['o1']['value']
                    o1=o1.replace('http://dbpedia.org/resource/','')
                    o2=resul['o2']['value']
                    o2=o1.replace('http://dbpedia.org/resource/','')
                    triple1 = parRecursos[0]+"-|"+o1+"*-|"+resul['p1']['value']
                    triple2 = parRecursos[1]+"-|"+o2+"*-|"+resul['p2']['value']
                    triple3 = o2+"*-|"+o1+"*-|"+resul['p3']['value']                    
                    self.ResultConsultasConexion.append(triple1)  
                    self.ResultConsultasConexion.append(triple2)  
                    self.ResultConsultasConexion.append(triple3)
                    
    def archivoSalida(self):
        fo=open(filename,"w")
        s="\n"
        imprimir=s.join(self.ResultConsultasConexion)
        fo.write(imprimir.encode('utf-8'))
        fo.close()
        
    def consulta(self, sqlQuery):
        """Ejecuta query"""  
        sparql = SPARQLWrapper("http://localhost:8890/sparql")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(sqlQuery)
        results = sparql.query()
        results = results.convert()
        return results

    def ejecutarproceso(self):
        """Ejecuta de forma sequencial el proceso de consultas a DBpedia y genera un archivo output"""
        self.generarConsultasLibres()
        self.aplicarConsultasLibres()
        self.generarCombinaciones()
        self.generarConsultasConexion()
        self.archivoSalida()


#mywords=["Machine","Learning"]
#mynivelProfundidad = 2
#mylimitBL = 2
#filename = "CA003"
#dbpe = KeyWordMap(mynivelProfundidad, mywords, mylimitBL,filename)
#dbpe.ejecutarproceso()
#print(dbpe.ResultConsultasConexion)