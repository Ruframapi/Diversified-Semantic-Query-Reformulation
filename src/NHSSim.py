# -*- coding: utf-8 -*-

import MySQLdb as mdb
import ast
import ConfigParser

class NHSSim:

    #MYSQL
    host=''
    db=''
    user=''
    passwd=''
    

    #
    r_i = ""
    r_j = ""
    nhs = 0
    beta = 0.5
    #Busqueda por nivel
    sqllnr = "SELECT lnr FROM graphNodes WHERE resource='%s' "    

    
    def __init__(self, resourceA = "", resourceB=""):
        """ Constructor """
        self.r_i = resourceA;
        self.r_j = resourceB;
        config = ConfigParser.ConfigParser()
        config.read('config.cfg')
        self.host=config.get('MySQL', 'host')  
        self.db=config.get('MySQL', 'db') 
        self.user=config.get('MySQL', 'user')  
        self.passwd=config.get('MySQL', 'passwd')  
        self.con = mdb.connect(self.host,self.user,self.passwd,self.db, charset='utf8')
        self.cursor = self.con.cursor()  
        
    def sumatorias(self):
        slnr_i = ""
        slnr_j = ""

        sqllnr_i = self.sqllnr % (self.r_i)
        self.cursor.execute(sqllnr_i)
        results = self.cursor.fetchall()
        for row in results:
            slnr_i = row[0]                

        sqllnr_j = self.sqllnr % (self.r_j)
        self.cursor.execute(sqllnr_j)
        results = self.cursor.fetchall()
        for row in results:
            slnr_j = row[0]
        
        
        #Transformarlos en diccionarios
        if slnr_i == "" or slnr_j=="":
            self.nhs = 0.0
        else:
            lnr_i = ast.literal_eval(slnr_i)   
            lnr_j = ast.literal_eval(slnr_j)
        
            #Mshared
            keys_i = set(lnr_i.keys())
            keys_j = set(lnr_j.keys())
            intersection = keys_i & keys_j
        

            #print intersection
            for mshare in intersection:
                self.nhs = self.nhs + pow(self.beta,float(lnr_i[mshare]+lnr_j[mshare]))  
        
        
    def run(self):
        self.sumatorias()
        return self.nhs

        
       
#nhs = NHSSim("Colombia", "Cali")
#print nhs.run()