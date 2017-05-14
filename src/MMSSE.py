# -*- coding: utf-8 -*-

import MySQLdb as mdb
import ConfigParser
from NHSSim import NHSSim
from TaxSim import TaxSim
import json

class MMSSE:
    # Identificador de Grafo
    graphID = 0

    #Conjunto de Recursos Seleccionados
    SelectSet = []
    
    #S set
    S = []
    #S expand
    S_expand = []
    
    #Alpha
    lamda = 0.5
    
    #MYSQL
    host=''
    db=''
    user=''
    passwd=''
    
    #Busqueda del grafo
    sqlgrafo = "SELECT S,S_expand FROM qkgraph WHERE id='%s' " 
    #Busqueda de nodos
    sqlnodo = "SELECT id,nhsw FROM graphNodes WHERE resource='%s' " 
    #Actualización del grafo
    update_qkg = "UPDATE qkgraph SET Select='%s' WHERE id='%s'" ;

    
    def __init__(self, graphident = 0, lam= 0.5):
        """ Constructor """
        self.graphID = graphident;
        self.lamda = lam;
        config = ConfigParser.ConfigParser()
        config.read('config.cfg')
        self.host=config.get('MySQL', 'host')  
        self.db=config.get('MySQL', 'db') 
        self.user=config.get('MySQL', 'user')  
        self.passwd=config.get('MySQL', 'passwd')
        self.con = mdb.connect(self.host,self.user,self.passwd,self.db, charset='utf8')
        self.cursor = self.con.cursor()  
        
    def capturarGrafo(self):
        sql1 = self.sqlgrafo % (str(self.graphID))
        self.cursor.execute(sql1)
        results = self.cursor.fetchall()
        for row in results:
            self.S = json.loads(row[0])
            self.S_expand = json.loads(row[1])
        #print self.S_expand

    def directSimilarity(self,r_i,r_j):
        
        nodoi_nhsw = ""
        nodoj_nhsw = ""
        
        #Informacion del nodo 1
        sql2 = self.sqlnodo % (str(r_i))
        self.cursor.execute(sql2)
        results = self.cursor.fetchall()
        for row in results:
            nodoi_nhsw = row[1]
        #Informacion del nodo 2
        sql3 = self.sqlnodo % (str(r_j))
        self.cursor.execute(sql3)
        results = self.cursor.fetchall()
        for row in results:
            nodoj_nhsw = row[1]
        #HS
        if (nodoi_nhsw == "" or nodoj_nhsw == ""):
            hs = 0.0
        else:
            hs = 0.0
            nodoi_nhsw = nodoi_nhsw.replace("_"," ").split("-")
            nodoj_nhsw = nodoj_nhsw.replace("_"," ").split("-")
            #print nodoj_nhsw
            for cat_nodoi in nodoi_nhsw:
                for cat_nodoj in nodoj_nhsw:
                    taxclass = TaxSim(cat_nodoj,cat_nodoi)
                    hstemp=taxclass.run()
                    if hstemp>hs:
                        hs=hstemp

        #NHS
        nhsclass = NHSSim(r_i,r_j)  
        #print r_i
        #print r_j
        nhs = nhsclass.run()
        #Total Sim
        return (nhs + hs)
                        

    def jointSimilarity(self,r_i):
        sumatoria = 0.0
        for node in self.S:
            sumatoria = sumatoria + self.directSimilarity(r_i,node)
        return (float(sumatoria / len(self.S)))
        
    def mmsseVal(self,r_i,C_r):
        #C_r conjunto de los ya seleccionados
        maxsim = 0.0
        for nodeS in C_r:
            temsim = self.directSimilarity(nodeS,r_i)
            if temsim > maxsim:
                maxsim = temsim
        jsim = self.jointSimilarity(r_i)
        return (float(self.lamda*jsim)-float((1-self.lamda)*maxsim))
        
            
        
    def runExample(self):
        #SOLO PARA PRUEBAS SOBRE EL GRAFO Q0012
        print self.mmsseVal(self.S_expand[5],[self.S_expand[9],self.S_expand[10]])
        return True;
        
       
mmss = MMSSE(1,0.5)
mmss.capturarGrafo()
print mmss.runExample()


