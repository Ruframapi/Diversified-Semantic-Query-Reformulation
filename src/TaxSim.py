# -*- coding: utf-8 -*-

import MySQLdb as mdb
import ConfigParser


class TaxSim:
    # Nodo raiz
    root = "Main topic classifications"
    noroot = ["Categories by type","Categories by parameter","Wikipedia categories","Categories by topic"]
    #Categoria A
    ci = ""
    
    #Categoria B
    cj = ""
    
    #LCS
    c_lca = ""

    #MYSQL
    host=''
    db=''
    user=''
    passwd=''
    
    #
    nodesIlevel = []
    nodesJlevel = []
    totalchain = []
    common = []
    dlca_root = 0
    dci_lca = 0
    dcj_lca = 0
    hss = 0
    
    #Busqueda por nivel
    sqlcate = "SELECT cate FROM Wikicate WHERE 1=0 %s "    

    
    def __init__(self, categoriaA = "", categoriaB=""):
        """ Constructor """
        self.ci = categoriaA;
        self.cj = categoriaB;
        config = ConfigParser.ConfigParser()
        config.read('config.cfg')
        self.host=config.get('MySQL', 'host')  
        self.db=config.get('MySQL', 'db') 
        self.user=config.get('MySQL', 'user')  
        self.passwd=config.get('MySQL', 'passwd')         
        if self.cj == self.ci:
            raise ValueError
        self.con = mdb.connect(self.host,self.user,self.passwd,self.db, charset='utf8')
        self.cursor = self.con.cursor()  
        
    def comunancestro(self):
        self.nodesIlevel = []
        self.nodesJlevel = []
        self.totalchain = []
        self.nodesIlevel.append([self.ci])
        self.nodesJlevel.append([self.cj])
        self.totalchain.append(self.ci)
        self.totalchain.append(self.cj)
        for i in range(1,10):#Control del nivel de profundidad que es alcanzadp
            

            whereIn = ""
            #print self.nodesIlevel[i-1]
            for node in self.nodesIlevel[i-1]:
                whereIn = whereIn + " or subcate='" + node + "'"
            
            whereJn = ""
            for node in self.nodesJlevel[i-1]:
                whereJn = whereJn + " or subcate='" + node + "'"        
                
            sqli = self.sqlcate % (whereIn)
            sqlj = self.sqlcate % (whereJn)
            
            self.cursor.execute(sqli)
            results = self.cursor.fetchall()
            signivel = []
            for row in results:
                if row[0] not in self.noroot:
                    signivel.append(row[0])
            
            signivel = list(set(signivel))
            self.nodesIlevel.append(signivel)
            
            self.cursor.execute(sqlj)
            results = self.cursor.fetchall()
            signivel = []
            for row in results:
                if row[0] not in self.noroot:
                    signivel.append(row[0])
            
            signivel = list(set(signivel))
            self.nodesJlevel.append(signivel)
            
            #Lista de un solo nivel y sin duplicados
            flatnodesIlevel = list(set([item for sublist in self.nodesIlevel for item in sublist]))
            flatnodesJlevel = list(set([item for sublist in self.nodesJlevel for item in sublist]))

            self.totalchain = flatnodesJlevel + flatnodesIlevel
            
            #Evaluar si existe intersección es equivalente a revisar si existen duplicados en la lista
            self.common = [x for n, x in enumerate(self.totalchain) if x in self.totalchain[:n]]
            if len(self.common) >0:
                break;

    def distancias(self):
        #distancia del LCA al root
        nodeslevel = []
        nodeslevel.append(self.common)
        
        if self.root not in self.common:
            for level in range(0,11):
                where = ""
                for node in nodeslevel[level]:
                    where = where + " or subcate='" + node + "'"
                
                sql = self.sqlcate % (where)
                
                self.cursor.execute(sql)
                results = self.cursor.fetchall()
                signivel = []
                for row in results:
                    if row[0] not in self.noroot:
                        signivel.append(row[0])
    
                nodeslevel.append(signivel)
                if self.root in signivel:
                    self.dlca_root = level + 1
                    #print ".-.-.-.-.-.-.-.-.-.-.-.H-"
                    #print nodeslevel
                    break
        else:
            self.dlca_root = 0
        #distancia del ci al LCA
        self.dci_lca = len(self.nodesIlevel)-1
        #distancia del cj al LCA
        self.dcj_lca = len(self.nodesJlevel)-1
    
    def HSsimilarity(self):
        self.hss = float((self.dlca_root)) / float((self.dlca_root + self.dci_lca + self.dcj_lca))
    
    def run(self):
        self.comunancestro()
        #print self.common
        #print ".-.-.-.-.-.-.-.-.-.-.-.-"
        #print self.nodesIlevel
        #print ".-.-.-.-.-.-.-.-.-.-.-.-"
        #print self.nodesJlevel
        self.distancias()
        #print ".-.-.-.-.-.-.-.-.-.-.-.-"
        #print self.dlca_root
        #print ".-.-.-.-.-.-.-.-.-.-.-.-"
        #print self.dci_lca
        #print ".-.-.-.-.-.-.-.-.-.-.-.-"
        #print self.dcj_lca

        self.HSsimilarity()
        return self.hss;
        
       
#txsim = TaxSim("Vehicles by type", "Literary genres")
#txsim = TaxSim("Automotive industry", "Vehicles by type")

#print txsim.run()
