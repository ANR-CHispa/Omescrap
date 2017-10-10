#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python 3 

#author : Nauge Michael 
#description : script contenant plusieurs outils de traitement de fichier CSV


import urllib.request

import csv
import sys

import re

import os

import time





def saveWebImagesFromCSV(readerCSV, ext, pathOut): 
    """Cette fonction parcours toutes les lignes du fichier CSV (ouvert par open puis reader) passé en parametre.
    pour chaque ressource de type image 
    une requete get est effecuée afin de recuperer cette ressource distante 
    puis elle est sauvegardé localement dans le dossier specifié
    
    :param readerCSV: un fichier CSV deja ouvert
    :type readerCSV: readerfile. 
    
    :param ext: permet le filtrage des images suivant leur extension (jpg)
    :type ext: str.   
    

    :returns: la list des images qui n'ont pas pu etre sauvegardées
    :raises: urllib.URLError
    """
    
    
    listUrlImgs = []
    
    for i, row in enumerate(readerCSV):
        if not(i == 0):
            #print(row)
            for column in row:
                #print(column)
                
                #il n'est pas possible d'avoir une virgule dans une url
                #si il y en a c'est surement quil y a plusieurs url dans la meme column
                for v in column.split(','):
                    for m in re.findall("(http:.*/(.*\.(jpg|png|gif)))", v): 
                        #print(m[0])
                        listUrlImgs.append(m[0]) 
                    
    
    listRes = saveWebImagesFromListUrl(listUrlImgs,pathOut)
    print ('nb images non recuperees :', len(listRes))
    
    return listRes
    

def saveWebImagesFromListUrl(listUrl, pathOut):
    """
    :returns: la list des images qui n'ont pas pu etre sauvegardées
    :raises: urllib.URLError
    """
    
    #on fait une copie de la liste 
    #que l'on va progressivement supprimmer
    #pour savoir quelles images n'ont pas été sauvegardé
    listRes = listUrl[:]
    
    print('nb image a recupere ',len(listUrl))
    
    for urlImage in listUrl:
        
        listRes.pop(0)
        
        filenameImg = urlImage.split('/')[-1]
        
        pathFileOut = pathOut+filenameImg
        
        #pour ne pas aller recuperer plusieur fois la meme image on test si elle existe deja en local
        if not(os.path.isfile(pathFileOut)):
            #attention, si le nom du fichier distant est le meme mais que lurl avant ete differente
            #ce nest pas bien geree.... L image ne sera pas recupere...
        
            print(filenameImg)
            try:
                urllib.request.urlretrieve(urlImage, pathFileOut)
            except:
                print('probleme de connexion...ou de sauvegarde de fichier...')
                        
    return listRes
   
 
    
def test_saveWebImagesFromCSV():
    """
    fonction de test de la fonction saveWebImagesFromCSV
    """
    fileCSVIn = "./../../Guarnido/03-metadatas/extractionDepuisSiteExistant/dirOutCSVGuarnido/merge/Guarnido_part1-12.csv"
    
    ext = "jpg"
    pathOut = "./../../Guarnido/02-numerisation/compress-Jpg/"
    
    f = open(fileCSVIn, encoding='utf-8')
    readerCSV = csv.reader(f) 
    #on le fait en boucle car sur certains site on est bloqué si on fai  trop de requetes rapidement
    
    
    encore = True
    
    while encore:
        try:
            listRes = saveWebImagesFromCSV(readerCSV, ext, pathOut)
            if len(listRes)==0:
                encore = False
            
            
        except:
            time.sleep(20)

    #listUrlImgs = ["http://eman-archives.org/hispanique/files/original/fa3e642ae9495c446ba43bcd70f0dd28.jpg","http://eman-archives.org/hispanique/files/original/a1af650734f9c224ce0400df71f24e3a.jpg"]
    #saveWebImagesFromListUrl(listUrlImgs,pathOut)
    
    
    
def remappForOmekaImportCSV(pathFileCSV_Source, pathFileCSV_Mapp, pathFileCSV_Out):
    """
    fonction permettant de realiser une conversion des colonnes en utilisant un fichier de mapping.
    Ex: Disposant d'un tableur contenant les colonnes nommees : "etat document", "nombre de page", "date de publication"
    et que je souhaite un tableur de sortie avec les colonne : "Dublin Core:Date", "Dublin Core:Description"
    je creer un tableur de mapping de la forme "etat document":"Dublin Core:Description";"nombre de page":"Dublin Core:Description";"date de publication":"Dublin Core:Date"
    
    
    :returns: None
    :raises: IOerror (si probleme de d'ouverture de fichier) 
   
    """


    separator = "|"
    #on commence par lire le fichier de mapping
    #normalement il y a deux lignes
    #la ligne 0 contenant les champs source
    #la ligne 1 contenant les champs destination
    dicoMapp = {}
    with open(pathFileCSV_Mapp,encoding='utf-8') as csvfileMapp:
        readerMapp = csv.DictReader(csvfileMapp, delimiter=';')
        #on peut obtenir un dico par ligne
        countLine = 1
        for dicMappCur in readerMapp:
            #print("le mapping des champs : ",dicMappCur)
            countLine+=1
            
            if countLine==2:
                dicoMapp = dicMappCur
            
        if not(countLine==2):
            print("error [FileCSV_Mapp] : nb ligne presente : ",str(countLine)," attendu :2" )
     
    """
    #dans le cas present il sera plus interressant que les clefs soit la value et inversement
    #mais pour le tableur c'était plus logique pour humain dans lautre sens....
    inv_dicoMapp = {v: k for k, v in dicoMapp.items()}       
    """
    
    #on peut maintenant lire le CSV source pour le convertir
    #et ouvrir le CSV out pour sauvegarder la conversion
    with open(pathFileCSV_Source, encoding='utf-8') as csvfileSource:
        readerSource = csv.DictReader(csvfileSource, delimiter=';')
        
        
        #on ouvre le fichier Out
        with open(pathFileCSV_Out, 'w', encoding='utf-8',newline="\n") as csvfileOut:
                        
            
            listChampDistinctTriees= []
            listChampDistinct = set(dicoMapp.values())
            listChampDistinctTriees = sorted(listChampDistinct)
                
            #on peut obtenir un dico par ligne
            countLine = 0
            for dicSourceCur in readerSource:
                countLine+=1
                
                #cas particulier pour la premiere ligne
                if countLine==1:           
                #on va commencer par verifier que tous les champs de ce fichier d'entree
                #sont present dans le dictionnaire de mapping
                #(quil ne manque pas une clef ce qui poserai probleme pdt la conversion...)
                #dans le dico de Mapping
                                                
                    if not(dicSourceCur.keys()==dicoMapp.keys()):
                        raise ValueError("error [FileCSV Source] : probleme de champs present dans pathFileCSV_Source et inexistants dans FileCSV_Mapp")
                        
                    else:
                        
                        #on a egalite de champs donc on peut faire la copie
                        csvfileOut = csv.writer(csvfileOut, delimiter=';')
                        
                        #ecriture de la premiere dans le fichier CSV de sortie
                        csvfileOut.writerow(listChampDistinctTriees)
                            
                #maintenant nous traitons toutes les lignes de la meme facon
                
                rowOut = []
                #pour chaque champs de sortie 
                #on va regarder dans le dico de mapping  puis chercher dans le dicSourceCur
                
                for champCur in listChampDistinctTriees:
                    champOutCur = ""
                    for keyOut in dicoMapp:
                        if dicoMapp[keyOut] == champCur:
                            champOutCur+= dicSourceCur[keyOut]+separator
                            
                    rowOut.append(champOutCur)
                            
                csvfileOut.writerow(rowOut)
                    
         


def test_remappForOmekaImportCSV():
    """
    fonction de test de remappCSV
    """
    pathFileCSV_Source = "./remapp/Guarnido-All.csv"
    pathFileCSV_Mapp = "./remapp/mappingOmeka.csv"
    pathFileCSV_Out ="./remapp/Guarnido-remapped.csv"
    
    remappForOmekaImportCSV(pathFileCSV_Source, pathFileCSV_Mapp,pathFileCSV_Out)
    
    
    

def orientedOmekaCsv2LineByFileCsv(pathFileCSV_Source, pathFileCSV_Out, fileColumnName, additionalColumnName, columnUsedForCollection ) :
    """
    fonction permettant de transformer un CSV de données orienté omeka (plusieurs fichiers pour un meme item)
    vers un csv orienté nakala une ligne par fichier
    plus précisement dans omeka il y a 3 types: des collections, des items, et des images
    nativement une collection ne peut pas avoir de collection fille mais peut contenir plusieurs items et images
    tandis un item peut contenir une ou plusieurs images.....
    
    Dans nakala il n'est question que de data et de collection.
    Chaque image est une data, il n'est pas question d'item,
    pour relier plusieurs images entre elle sur le principe de l'item
    il faut utiliser les collections.
    par contre dans nakala une collection peut contenir plusieurs collections!
    
    Dans nakala une méta donnée doit être liée à une data
    si la data n'existe pas la métadata non plus...
    CE traitement fait également disparaitre les lignes sans fichiers de data ...
    
    :param pathFileCSV_Source: un fichier CSV deja ouvert
    :type pathFileCSV_Source: readerfile. 
    
    :param ext: permet le filtrage des images suivant leur extension (jpg)
    :type ext: str.   
    

    :returns: none
    :raises: urllib.URLError
    """
    
    #on ouvre le fichier d'entree
    #et le fichier de sortie
    
    with open(pathFileCSV_Source, encoding='utf-8') as csvfileSource:
        readerSource = csv.DictReader(csvfileSource, delimiter=';')
        #on vient de lire tout le fichier est il est stoqué dans un dico
        #on peut traiter chaque ligne du dico
        
            
     
        countItemWithImage = 0
        countItemWithNoneStr = 0
        countItemWithNone = 0
        countImages = 0
        countMotherCollection = 0
        #on ouvre le fichier Out
        with open(pathFileCSV_Out, 'w', encoding='utf-8',newline="\n") as csvfileOut:
            csvfileOut = csv.writer(csvfileOut, delimiter=';')

            
            #on parcourir toute les lignes du fichier d'entree
            #pour la reecrire une ou plusieur fois dans le fichier de sortie
            #on ecrira plusieurs fois la ligne si en entrée il a plusieurs images dans la column file
            
            countLine = 0
            for dicSourceCur in readerSource:
                
                listChampDistinctTriees= []
                listChampDistinct = set(dicSourceCur.keys())
                listChampDistinctTriees = sorted(listChampDistinct)
            
                countLine+=1
                
                #cas particulier pour la premiere ligne
                # va reecrire les noms de column du fichier dentree plus le nom de la comun additionnel
                if countLine==1:
                    

                    rowOut = list(listChampDistinctTriees)
                    rowOut.append(additionalColumnName)
                    rowOut.append('linkedInCollection')
                    
                    csvfileOut.writerow(rowOut)
                    #on creer un dico de sortie avec une column de plus qu'en entree!
                 
                #pour chaque ligne de contenu:
                #on analyse la column File
                #print(dicSourceCur[fileColumnName])
                input_line = dicSourceCur[fileColumnName]
                
                #quand il n'y a pas de fichier pour le moment on ne les recreer pas...
                #car on ne sais pas comment les gerer dans nakala...
                if input_line=='none' :
                    countItemWithNoneStr+=1
                    #print('ya du none en str')
                
                elif input_line==None:
                    countItemWithNone+=1
                    #print('ya du none en vide')
                    
                else:
                    countItemWithImage+=1
                    listFile = [s.strip() for s in input_line[1:-1].split(',')]
                    countImages+=len(listFile)
                    #print(listFile)
                    
                    if len(listFile)==0:
                        countItemWithNone+=1
                    else:
                        countMotherCollection+=1
                        #on va creer une une ligne dans le fichier de sortie par fichier trouve
                        countPart = 0
                        for file in listFile:
                            
                            countPart+=1
                            rowOut = []
                            for columName in listChampDistinctTriees:
                                
                                
                                if not(columName==fileColumnName):
                                    rowOut.append(dicSourceCur[columName])
                                    #il ne faut pas traiter la column file comme les autres du coup...
                                
                            rowOut.append([file.replace("'",'')])
                            rowOut.append(countPart)
                            if len(listFile)>1:
                                nameCollection = dicSourceCur[columnUsedForCollection]
                                nameCollection = nameCollection.replace("[",'')
                                nameCollection = nameCollection.replace("]",'')
                                nameCollection = nameCollection.replace("'",'')
                                rowOut.append(['collection '+nameCollection])
                            else:
                                rowOut.append('')
                            
                            
                            csvfileOut.writerow(rowOut)
                        
                    
                    
                    
        print('countItemWithImage',countItemWithImage)
        print('countItemWithNoneStr',countItemWithNoneStr)
        print('countItemWithNone',countItemWithNone)      
        print('total items',str(countItemWithImage+countItemWithNoneStr+countItemWithNone))
        print('nbImagevue',countImages)
        print('nbMotherCollection',countMotherCollection)
                    
                   
                
            
    
def test_orientedOmekaCsv2LineByFileCsv():
    """
    fonction de test de remappCSV
    """
    pathFileCSV_Source = "./../../Guarnido/03-metadatas/extractionDepuisSiteExistant/dirOutCSVGuarnido/merge/Guarnido_part1-12.csv"
    pathFileCSV_Out ="./../../Guarnido/03-metadatas/extractionDepuisSiteExistant/dirOutCSVGuarnido/merge/Guarnido_part1-12_lineByFile.csv"
    
    fileColumnName = "file"
    additionalColumnName = "numeroDeFolio"
    columnUsedForCollection = "Title"
    
    
    orientedOmekaCsv2LineByFileCsv(pathFileCSV_Source, pathFileCSV_Out, fileColumnName, additionalColumnName, columnUsedForCollection)    
    
    
def renameFileFromCSV_pjtGuarnido(pathFileCSV_Source, pathFileCSV_Out, fileColumnName, listColumnNameForNewName):
    """
    fonction permettant de renommer des fichiers en utilisant une ou plusieurs column pour définir le nouveau nom de fichier.
    ex: dans le cadre du projet Guarnido les images ont un nom non porteur de sens car généré par omeka
    nous souhaitons redonner un sens aux noms des images
    pour cela nous renommons les fichiers en utilisant la column "source"
    
    les fichiers ayant changés de nom il est interressant de disposer d'un nouveau tableur csv
    contenant les nouveaux noms !
    
    :param pathFileCSV_Source: le chemin vers le fichier CSV contenant des métadonnées et une column contenant des fichiers a renommer
    :type pathFileCSV_Source: str.   
    
    :param pathFileCSV_Out: le chemin vers le fichier CSV de sortie ayant le même contenant que le FileCSV_Source mais dont les noms des fichiers sont mis a jours
    :type pathFileCSV_Out: str.   
    
        
    :param fileColumnName: le nom de la column contenant les fichiers à renommer
    :type fileColumnName: str.  
    
    :param listColumnNameForNewName: la liste des comun a utiliser pour creer un nouveau nom fichier ayant du sens.
    :type listColumnNameForNewName::str
    
    :returns: None
    :raises: IOerror (si probleme d'acces aux fichiers) 
    """
    
    #on ouvre le fichier d'entree
    #et le fichier de sortie
    
    with open(pathFileCSV_Source, encoding='utf-8') as csvfileSource:
        readerSource = csv.DictReader(csvfileSource, delimiter=';')
        #on vient de lire tout le fichier est il est stoqué dans un dico
        #on peut traiter chaque ligne du dico
        
        #on ouvre le fichier Out
        with open(pathFileCSV_Out, 'w', encoding='utf-8',newline="\n") as csvfileOut:
            csvfileOut = csv.writer(csvfileOut, delimiter=';')
            
            #on parcourir toute les lignes du fichier d'entree
            #pour la reecrire une ou plusieur fois dans le fichier de sortie
            #on ecrira plusieurs fois la ligne si en entrée il a plusieurs images dans la column file
            
            countLine = 0
            for dicSourceCur in readerSource:
                
                listChampDistinctTriees= []
                listChampDistinct = set(dicSourceCur.keys())
                listChampDistinctTriees = sorted(listChampDistinct)
            
                countLine+=1
                
                #cas particulier pour la premiere ligne
                # va reecrire les noms de column du fichier dentree plus le nom de la comun additionnel
                if countLine==1:
                    rowOut = list(listChampDistinctTriees)                  
                    csvfileOut.writerow(rowOut)



                rowOut = []
                for columName in listChampDistinctTriees:
                    
                    if columName==fileColumnName:
                        #il ne faut pas traiter la column file comme les autres du coup...
                        pathFileCur = dicSourceCur[columName]
                        pathFileCur = pathFileCur.replace("']",'')
                        pathFileCur = pathFileCur.replace("['",'')
                        #extraire uniquement le nom de fichier
                        head, tail = os.path.split(pathFileCur) 
                        unused, extensionFile = tail.split('.')
                        extensionFile = extensionFile
                        newFileName = head+'/'
                        #on parcour toutes les column necessaire à la creation du nouveau nom de fichier
                        countPart = 0
                        for columnForNewName in listColumnNameForNewName:
                            #on pourrait utiliser une expression reguliere pour eviter le double replace des caracteres crochets
                            newname = str(dicSourceCur[columnForNewName])
                            
                            newname = newname.replace("[",'')
                            newname = newname.replace("]",'')
                            newname = newname.replace("'",'')
                            
                            if countPart==0:
                                newFileName += newname
                            else:
                                newFileName += '_'
                                newFileName += newname
                                
                            countPart+= 1 
                            
                        newFileName+='.'+extensionFile
                        #là on a le bon nouveau pathfilename!!
                        #un petit coup de rename
                        try:
                            os.rename(pathFileCur, newFileName)
                        except:
                            print('pas pu renommer', pathFileCur)
                        
                        rowOut.append([newFileName])
                    else:
                        rowOut.append(dicSourceCur[columName])
                                                    
                
                csvfileOut.writerow(rowOut)
    
def test_renameFileFromCSV():
    pathFileCSV_Source = "./../../Guarnido/03-metadatas/extractionDepuisSiteExistant/dirOutCSVGuarnido/merge/Guarnido_part1-12_lf_localPath.csv"
    pathFileCSV_Out = "./../../Guarnido/03-metadatas/extractionDepuisSiteExistant/dirOutCSVGuarnido/merge/Guarnido_part1-12_lf_lp_renamed.csv"
    fileColumnName = "file"
    newNameColumnName = ["Source","numeroDeFolio"]
    
    renameFileFromCSV_pjtGuarnido(pathFileCSV_Source, pathFileCSV_Out, fileColumnName, newNameColumnName)
    
    
def changeColumnFileWithLocalPath(pathFileCSV_Source, pathFileCSV_Out, fileColumnName, localPath):
    """
    fonction permettant de changer le contenu d'une column contenant une url vers un fichier distant
    en specifiant un chemin vers un fichier local.
    C'est aussi l'occasion de vérifier la présence en local de ce fichier et de lever une exception si le fihier n'existe pas.
    
    :param pathFileCSV_Source: le chemin vers le fichier CSV contenant des métadonnées et une column contenant des chemins fichiers a modifier
    :type pathFileCSV_Source: str.   
    
    :param pathFileCSV_Out: le chemin vers le fichier CSV de sortie ayant le même contenant que le FileCSV_Source mais dont les chemins des fichiers sont mis a jours
    :type pathFileCSV_Out: str.   
    
        
    
    :param localPath: le chemin vers les fichier locaux
    :type localPath::str
    
    :returns: None
    :raises: IOerror (si probleme d'acces aux fichiers) 
    """  
    #on ouvre le fichier d'entree
    #et le fichier de sortie
    
    with open(pathFileCSV_Source, encoding='utf-8') as csvfileSource:
        readerSource = csv.DictReader(csvfileSource, delimiter=';')
        #on vient de lire tout le fichier est il est stoqué dans un dico
        #on peut traiter chaque ligne du dico
        
        #on ouvre le fichier Out
        with open(pathFileCSV_Out, 'w', encoding='utf-8',newline="\n") as csvfileOut:
            csvfileOut = csv.writer(csvfileOut, delimiter=';')
            
            #on parcourir toute les lignes du fichier d'entree
            #pour la reecrire une ou plusieur fois dans le fichier de sortie
            #on ecrira plusieurs fois la ligne si en entrée il a plusieurs images dans la column file
            
            countLine = 0
            for dicSourceCur in readerSource:
                
                
                listChampDistinctTriees= []
                listChampDistinct = set(dicSourceCur.keys())
                listChampDistinctTriees = sorted(listChampDistinct)
            
                countLine+=1
                
                #cas particulier pour la premiere ligne
                # va reecrire les noms de column du fichier dentree plus le nom de la comun additionnel
                if countLine==1:
                    rowOut = list(listChampDistinctTriees)                  
                    csvfileOut.writerow(rowOut)
                
                
                rowOut = []
                for columName in listChampDistinctTriees:
                    
                    if columName==fileColumnName:
                        #il ne faut pas traiter la column file comme les autres du coup..
                        
                        input_line = dicSourceCur[columName]
                        listpathFileCur = [s.strip() for s in input_line[1:-1].split(',')]
                        #normalement un seul fichier!
                        for pathFileCur in listpathFileCur:
                            
                            #extraire uniquement le chemin vers le fichier normalement distant
                            head, tail = os.path.split(pathFileCur) 
                            
                            #pour le remplacer par le chemin local
                            #on replace head (chemin distant) par localPath
                            newpathFileName = localPath+tail
                            newpathFileName = newpathFileName.replace("'",'')
                                                            
                            #on en profite pour tester l'existance du fichier en local et lever une exeption si ce n'est pas le cas
                            if not(os.path.isfile(newpathFileName)):
                                raise IOError("le fichier ",newpathFileName, "n'existe pas localement")
                            
                            rowOut.append([newpathFileName])
                    else:
                        rowOut.append(dicSourceCur[columName])
                                                        
                    
                csvfileOut.writerow(rowOut)
    
    
    
    
    
def test_changeColumnFileWithLocalPath():
    pathFileCSV_Source = "./../../Guarnido/03-metadatas/extractionDepuisSiteExistant/dirOutCSVGuarnido/merge/Guarnido_part1-12_lineByFile.csv"
    pathFileCSV_Out = "./../../Guarnido/03-metadatas/extractionDepuisSiteExistant/dirOutCSVGuarnido/merge/Guarnido_part1-12_lf_localPath.csv"
    fileColumnName = "file"
    localPath = "./../../Guarnido/02-numerisation/compress-Jpg/"
    
    changeColumnFileWithLocalPath(pathFileCSV_Source, pathFileCSV_Out, fileColumnName, localPath)
    
    

    
    
def main(argv):

    #test_saveWebImagesFromCSV()
    #test_orientedOmekaCsv2LineByFileCsv()
    #test_changeColumnFileWithLocalPath()
    #test_renameFileFromCSV()
    
    #test_remappForOmekaImportCSV()
    
    pass
    

    


if __name__ == "__main__":
    main(sys.argv) 
    
