# -*- coding: utf-8 -*-
"""
Created on Mon May 29 15:44:42 2017

@author: Michael Nauge 
"""

#lib pour la sauvegarde de configurations d'un lancement a l'autre
import configparser

#lib pour la creation d'interface graphique
from tkinter import *

#lib pour le scraping omeka
from omekaXML2CSV import *



class UiOmeskrap(Frame):
    
    #la configuration (c'est un dictionnary contenant url et dirOut  )
    config = None
    
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        
        self.config = configparser.ConfigParser()
        self.readConfig()
        
        self.parent = parent
        self.initUI()


    def readConfig(self):

        r = self.config.read('config.ini')
        #si le fichier de config n'existe pas
        #on le cree avec des valeurs par defaut
        if len(r) ==0 :
            self.config['DEFAULT'] = {'url': 'https://guarnido.nakalona.fr/items/browse?','dirOut': './DirOut/'} 
            self.writeConfig()
        #sinon on fait test la remonter les données qu'il contient
        else:
            try:
                self.config['DEFAULT']['url']
                self.config['DEFAULT']['dirOut']
            except :
                print('catch except in config.ini !')
                #si il manque une key (car manipulation manuelle du fichier ini...) ça va generer une exception donc on l'intercept et on remet proprement des valeurs par defaut
                self.config['DEFAULT'] = {'urlCur': 'https://guarnido.nakalona.fr/items/browse?','dirOut': './DirOut/'}  
                #et on reaffecte
                #puis reecrit
                self.writeConfig()
        
    
    def writeConfig(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        
    def initUI(self):
      
        self.parent.title("omeskrap")
        self.pack(fill=BOTH, expand=True)
                
        #-----------------------------------------------------------------
        #------- Config Input Frame ---------------------------------------------
        frameConfig = LabelFrame(self, text="Configuration",font=("Font",14))
        frameConfig.pack(fill=X, expand=True,  padx=5, pady=5)
        frameConfig.grid(row=0,column=0, ipadx=5,ipady=5, padx=5,pady=5)
        
        
        #---- URL -----------------------------
        #le width d'un entry, c'est le nombre de caracter pas la taille en pixel
        #mais ça ne limite pas le nombre de caracteres saisissable
        lblUrl = Label(frameConfig, text="Url cible", font=("Font",14)).grid(row=0,column=0)
        
        inputUrl = Entry(frameConfig,width=50,font=("Font",14))
        inputUrl.grid(row=0,column=1,ipadx=5,ipady=5)
        inputUrl.insert(0,self.config['DEFAULT']['url'])

        #-----------------------------------------------------------------

        #---- Dir Out ------------------------
        lblDirOut= Label(frameConfig, text="Dossier de sortie", font=("Font",14)).grid(row=1,column=0)       
        
        inputDirOut = Entry(frameConfig,width=50,font=("Font",14))
        inputDirOut.grid(row=1,column=1,ipadx=5,ipady=5)
        inputDirOut.insert(0,self.config['DEFAULT']['dirOut'])
        #-----------------------------------------------------------------
        
        #---- Btn Run ------------------------
        def btnRunCallback():
            
                #on fait une petite vérification sur la saisies utilisateur
                dirOut = inputDirOut.get()
                if not(dirOut[-1]=='/'):
                    dirOut = dirOut+'/'
                    
                #on sauvegarde la saisi utilisateur
                self.config['DEFAULT']['url'] = inputUrl.get()
                self.config['DEFAULT']['dirOut'] = dirOut
                self.writeConfig()
                    
                    
                try:
                    res = runScraping(self.config['DEFAULT']['url'], self.config['DEFAULT']['dirOut'])
                    if res == 0 :
                        print('La collecte de données a été réalisée avec succès. Vous pouvez travailler :) ')
                    else:
                        print('Des erreurs on été rencontrées essayez vérifiez votre url et relancez')
                        print("l'url doit etre de la forme :   http://www.lorem.com/items/browse?")
                except :
                        print('Des erreurs on été rencontrées essayez vérifiez votre url et relancez')
                        print("l'url doit etre de la forme :   http://www.lorem.com/items/browse?")
                
                
        btnRun = Button(self,text="Collecter", font=("Font",15), command=btnRunCallback)
        btnRun.grid(row=1,column=1, ipadx=5,ipady=5, padx=5,pady=5)
        #-----------------------------------------------------------------
        
        
              

def main():
  
    root = Tk()
    #root.geometry("850x300+300+300")
    app = UiOmeskrap(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  