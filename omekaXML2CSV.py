#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python 3 

#author : Nauge Michael 
#description : script permettant de parcourir les exports XML d'une la base OMEKA et de les convertir en un fichier CSV de sortie

#lib pour les requetes GET 
import urllib.request

#lib pour le parsing de xml ou html
from bs4 import BeautifulSoup
import re

#lib pour la gestion de fichiers CSV
import csv

#libs pr la gestion de fonctions system (parcour de dossier, creation de dossier, lancement de ligne de commande, etc)
import sys
import time
import glob
import os

import toolsForCSV


#les csv par defaut on une taille limite de texte par cellule
#on l'augmente au maximum, 
#car certains mettent la transcription complete ou leurs analyses dans un champs DC:Description par exemple ;-)
csv.field_size_limit(sys.maxsize)

def read_OMEKA_XML2dictionnary(url): 
    """Cette fonction effectue une requeque GET sur un site OMEKA de demande de sortie XML d'une collection,
    il est utile de spécifier le numéro de la collection et le numéro de la page
    
    Les données XML de retour sont analysées pour extraires chaque champs et leurs valeurs 
    ces couples champs et valeurs sont memorisées dans un dictionnaire key = champs, value = value

    exemple de requete : "https://guarnido.nakalona.fr/items/browse?page=2&output=omeka-xml"

    :param url: l'adresse du site web de la base OMEKA.
    :type url: str. 
    

    :returns:  Une collection de Dict - chaque dictionnaire contenant les noms des champs et les valeurs. NB: il peut etre utile de parser les valeurs pour les reformater, decouper, etc... retourne None si la fiche demandee n'existe pas
    :raises: urllib.URLError, BeautifulSoup.AttributeError
    """
    
    ListDicRes = []
    print(" **************************** ")
    print (" start extraction ")
    #url = baseUrl+str(collection)+"&page="+str(numPage)+"&output=omeka-xml"
    
    print("url : ",url)  
    #with contextlib.closing(urllib.request.urlopen(url)) as x:
    with urllib.request.urlopen(url) as x:
        
        html = x.read()

        soup = BeautifulSoup(html,'html.parser')

        if not(soup==None):
            ########################################
            ### on cherche tous les items de la page
            ### generalement 10 par page
            ########################################
            
            listitem = soup.findAll('item')
            for item in listitem:
                print(" ---- item ---- ")
                #print(item)
                
                itemId = item["itemid"]
                #print('item ID : ',itemId)
                                
                #https://guarnido.nakalona.fr/admin/items/edit/1798
                decoupeUrlPartA = url.split('browse')
                urlShowItem = decoupeUrlPartA[0]+'show/'+itemId
                print('Show Item Url : ',urlShowItem)
                
                decouperUrlPartB = url.split('items')
                urlEditItem = decouperUrlPartB[0]+'admin/items/edit/'+itemId
                #print('Edit Item Url : ', urlEditItem)
                
               
                
                #le dictionnaire pour contenir les couples champs et valeur de l'tiem actuel
                dicCur = {}
                
                dicCur['urlShowItem'] = [urlShowItem]
                dicCur['urlEditItem']= [urlEditItem]
                
                souplette = BeautifulSoup(str(item),'html.parser')

                if not(souplette==None):
                
                    #############################################
                    ###              File 
                    ### souvent c'est là qu'est la collection de
                    ### de liens vers la ou les images 
                    ### ex: 
                    ### <fileContainer>
                    ###      <file fileId="9531">
                    ###        <src>http://lorem.org/files/original/39c082cf62fd5de668403591f8376faf.jpg</src>
                    ###        <authentication>528e581e33294176645d3bd82ebcd2eb</authentication>
                    ###      </file>
                    ###      <file fileId="9532">
                    ###        <src>http://lorem.org/files/original/17f86656b014e9f5fe4abb89a975b8c0.jpg</src>
                    ###        <authentication>72f3f013893885c171ecf75ebbdc4840</authentication>
                    ###      </file>
                    ### </fileContainer>
                    #############################################
                    listFile = souplette.findAll('file')
                    for file in listFile:
                        #print "file ", file
                        #on s'interesse a extraire les sources
                        
                        soupeletteSRC = BeautifulSoup(str(file),'html.parser')
                        src = soupeletteSRC.find('src').text
                        
                        #on test l'existance de la cle dans le dico
                        #si elle n'existe pas on la creer
                        #sinon on complete la liste de sources file
                        
                        #if dicCur.has_key('file')==1:
                        if 'file' in dicCur:
                            dicCur['file'].append(src)
                        else:
                            dicCur['file'] = [src]
                        #print("file src ", src)
                    
                    
                    #############################################
                    ###              elementSet 
                    ###
                    ###    <element elementId="49">
                    ###        <name>Subject</name>
                    ###        <description>The topic of the resource</description>
                    ###        <elementTextContainer>
                    ###          <elementText elementTextId="166">
                    ###            <text>Littérature</text>
                    ###          </elementText>
                    ###          <elementText elementTextId="184">
                    ###            <text>Poésie</text>
                    ###          </elementText>
                    ###          <elementText elementTextId="71147">
                    ###            <text>Zorrilla de San Martín </text>
                    ###          </elementText>
                    ###          <elementText elementTextId="102780">
                    ###            <text>Desde el Uruguay</text>
                    ###          </elementText>
                    ###        </elementTextContainer>
                    ###      </element>
                    #############################################
                    
                    listElement = souplette.findAll('element')
                    for element in listElement:
                   
                        
                        #print "element ", element
                        #on s'interesse a extraire le nom et le text (champ et valeur)
                        soupeletteElement = BeautifulSoup(str(element),'html.parser')
                        
                        name = soupeletteElement.find('name').text 
                        listText = soupeletteElement.findAll('text')
                        
                        for t in listText:

                            if name in dicCur:
                                dicCur[name].append(t.text)
                            else:
                                dicCur[name] = [t.text]
                            
                            

                    #############################################
                    ###              Tag
                    ###
                    ### <tagContainer>
                    ###     <tag tagId="982">
                    ###         <name>Desde el Uruguay</name>
                    ###     </tag>
                    ###    <tag tagId="109">
                    ###        <name>Littérature</name>
                    ###    </tag>
                    ### </tagContainer>
                    #############################################
                    listTag = souplette.findAll('tag')
                    for tag in listTag:
                        #print "element ", element
                        #on s'interesse a extraire le nom et le text (champ et valeur)
                        soupeletteTag = BeautifulSoup(str(tag),'html.parser')
                        nameTag = soupeletteTag.find('name').text

                        
                        #if dicCur.has_key(name)==1:
                        if 'tag' in dicCur:
                            dicCur['tag'].append(nameTag)
                        else:
                            dicCur['tag'] = [nameTag]
                        
                        
                #on ajoute le dictionnaire de cet item dans la liste des dico de cette page
                ListDicRes.append(dicCur)
                
                print(" ---------------")
                
            print("nb items in this page ", len(listitem))
        x.close()           
        
    """        
    #on peut tester les keys des dictionnaires
    for dico in ListDicRes:
        print " ---- dico ----"
        for key in dico.keys():
            print key
        print " ---- /dico ----"
    
    print " ****************************\r\n "
    """

    return ListDicRes
    
   
   
   
    

def fonctionTestOmeka():
    """
    une fonction de test parsing de page omeka
    avec pas mal de commentaires
    """   

    print("test omeka ")
    
    #voir un item : http://lorem.org/hispanique/items/show/7
    #item avec une image : http://lorems.org/hispanique/items/show/9
    #pour comparaison
    #http://lorem.org/hispanique/items/browse?collection=1&output=omeka-xml
    # et http://lorems.org/hispanique/items/show/9
    
    with urllib.request.urlopen(url) as x:
        html = x.read()
        soup = BeautifulSoup(html,'html.parser')
        
        #print soup
        if not(soup==None):
            #print soup
            print("j'ai bien recuperer du contenu ")
            
            #############################################
            ###              Pagination 
            ##############################################
            ### on recherche le contenu contenu en les balises :
            ### <pagination>
            ###     <pageNumber>1</pageNumber>
            ###     <perPage>10</perPage>
            ###     <totalResults>1597</totalResults>
            ### </pagination>
            #############################################
            #il n'est pas possible d'obtenir en une fois toutes les donnees
            #elles sont paginees. Il est donc utile de savoir si il reste des pages a visiter
            #Pour cela on traite la partie pagination 
            
            listPagination = soup.findAll('pagination')
            #normalement il y a une seule pagination !! donc un tour de boucle sinon c'est louche...
            nbPagination = len(listPagination)
            if not(nbPagination == 1):
                print("Warning ---- pagination anormale : ", nbPagination)
            else:
                print("pagination [OK]")
                
            for pagination in listPagination:
                #print "  ",pagination
                soupelette = BeautifulSoup(str(pagination),'html.parser')
                
                pagenumber = soupelette.find('pagenumber').text
                perpage = soupelette.find('perpage').text
                totalresults = soupelette.find('totalresults').text
                restpage = (int(totalresults)/int(perpage)) - int(pagenumber)
                print("page Number ",pagenumber, " per page ", perpage, " total result", totalresults, " nb page restante ",restpage)
            
            ##############################################
            
            
            listitem = soup.findAll('item')
            
            #print 
            for item in listitem:
                print(" ---- item ---- ")
                #print item
                
                souplette = BeautifulSoup(str(item),'html.parser')

                if not(souplette==None):
                
                    #############################################
                    ###              File 
                    ### souvent c'est là qu'est la collection de
                    ### de liens vers la ou les images 
                    ### ex: 
                    ### <fileContainer>
                    ###      <file fileId="9531">
                    ###        <src>http://lorem.org/files/original/39c082cf62fd5de668403591f8376faf.jpg</src>
                    ###        <authentication>528e581e33294176645d3bd82ebcd2eb</authentication>
                    ###      </file>
                    ###      <file fileId="9532">
                    ###        <src>http://lorem.org/files/original/17f86656b014e9f5fe4abb89a975b8c0.jpg</src>
                    ###        <authentication>72f3f013893885c171ecf75ebbdc4840</authentication>
                    ###      </file>
                    ### </fileContainer>
                    #############################################
                    listFile = souplette.findAll('file')
                    for file in listFile:
                        #print "file ", file
                        #on s'interesse a extraire les sources
                        soupeletteSRC = BeautifulSoup(str(file),'html.parser')
                        src = soupeletteSRC.find('src').text
                        print("file src ", src)
                    
                    
                    #############################################
                    ###              elementSet 
                    ### souvent c'est là qu'est la collection de
                    ### de champs dublin core
                    ### ex: 
                    ### <elementSet elementSetId="1">
                    ###      <name>Dublin Core</name>
                    ###      <description>The Dublin Core metadata element set is common to all Omeka records, including items, files, and collections. For more information see, http://dublincore.org/documents/dces/.</description>
                    ###      <elementContainer>
                    ###       <element elementId="50">
                    ###          <name>Title</name>
                    ###          <description>A name given to the resource</description>
                    ###          <elementTextContainer>
                    ###            <elementText elementTextId="1">
                    ###              <text>MORA GUARNIDO José</text>
                    ###            </elementText>
                    ###          </elementTextContainer>
                    ###        </element>
                    ###        <element elementId="41">
                    ###          <name>Description</name>
                    ###          <description>An account of the resource</description>
                    ###          <elementTextContainer>
                    ###            <elementText elementTextId="81">
                    ###              <text>Oeuvres de José Mora Guarnido</text>
                    ###            </elementText>
                    ###          </elementTextContainer>
                    ###        </element>
                    ###        <element elementId="39">
                    ###          <name>Creator</name>
                    ###          <description>An entity primarily responsible for making the resource</description>
                    ###          <elementTextContainer>
                    ###            <elementText elementTextId="82">
                    ###              <text>José Mora Guarnido</text>
                    ###            </elementText>
                    ###          </elementTextContainer>
                    ###        </element>
                    ###        <element elementId="37">
                    ###          <name>Contributor</name>
                    ###          <description>An entity responsible for making contributions to the resource</description>
                    ###          <elementTextContainer>
                    ###            <elementText elementTextId="99860">
                    ###              <text>test contri</text>
                    ###            </elementText>
                    ###          </elementTextContainer>
                    ###        </element>
                    ###      </elementContainer>
                    ### </elementSet>
                    #############################################
                    listElement = souplette.findAll('element')
                    for element in listElement:
                        #print "element ", element
                        #on s'interesse a extraire le nom est le text
                        soupeletteElement = BeautifulSoup(str(element),'html.parser')
                        name = soupeletteElement.find('name').text
                        text = soupeletteElement.find('text').text
                        #il faudrait faire un findAll, car on risque de rater des valeurs ...
                        
                        ###############################################
                        #certains textes contiennent des caractere non ASCII
                        #qui ont du mal a etre affichés dans le terminal
                        #pour mieux comprendre unicode, ascii et utf8 :
                        #http://sebsauvage.net/comprendre/ascii/
                        ###############################################
                        if not(text == None):
                            textPrint = text.encode("ascii","ignore") 
                            print("element name : ", name, " -- value : ", textPrint)

                print(" ---------------")
            
            
        
def test_extractNumberPagesOmeka():
    
    baseUrl = "http://lorem.org/items/browse?collection=1"
    
    nbPages = getNumberPagesOmeka(baseUrl,1)
      
def getNumberPagesOmeka(baseUrl, numPage):    
    """Dans Omeka il n'est pas possible d'extraire en une fois toutes
    les fiches (les items) d'une collection.
    il est utile de lire les donnees presente dans la section <pagination>

    exemple de requete : "http://lorem.org/items/browse?collection=1&page=1&output=omeka-xml"
    on peut meme specifier des contraintes de filtrage :
    http://lorem.org/items/browse?collection=1&page=1&tags=Politique&output=omeka-xml
    
    :param baseUrl: l'adresse du site web de la base OMEKA.
    :type baseUrl: str. 
    
    :param numPage: si le numero de page est 1 on obtient le nombre total de page a parcourir, sinon on obtient le nombre de pages restantes
    :type numPage: int
    
    :returns:  Un entier representant le nombre de page a consulter
    :raises: urllib.URLError, BeautifulSoup.AttributeError
    """
    
    resNbPages = 0
    
    url = baseUrl+"&page="+str(numPage)+"&output=omeka-xml"
    print("opening ", url)

    with urllib.request.urlopen(url) as x:  
    
        html = x.read()
        soup = BeautifulSoup(html,'html.parser')
              
        if not(soup==None):
            
            #############################################
            ###              Pagination 
            ##############################################
            ### on recherche le contenu contenu entre les balises :
            ### <pagination>
            ###     <pageNumber>1</pageNumber>
            ###     <perPage>10</perPage>
            ###     <totalResults>1597</totalResults>
            ### </pagination>
            #############################################
             
            listPagination = soup.findAll('pagination')
            #normalement il y a une seule pagination !! donc un tour de boucle sinon c'est louche...
            nbPagination = len(listPagination)
            if not(nbPagination == 1):
                print("Warning ---- pagination anormale : ", nbPagination)
                return -1
            else:
                print("pagination [OK]")
                
            for pagination in listPagination:
                #print (pagination)
                soupelette = BeautifulSoup(str(pagination),'html.parser')
                
                pagenumber = soupelette.find('pagenumber').text
                perpage = soupelette.find('perpage').text
                totalresults = soupelette.find('totalresults').text

                
                resNbPages = int(int(totalresults)/int(perpage))+1
                
                print("page Number ",pagenumber, " per page ", perpage, " nb page restante ", resNbPages)
            ##############################################
        x.close()
    
    return resNbPages
  
    
    

def test_extractAndSaveOnePage(numPage):
    """fonction permettant de tester l'extraction
    de tous les items contenus dans une page

    :param numPage: l'adresse du site web de la base OMEKA.
    :type numPage: int. 
    """
    
    baseUrl = "https://guarnido.nakalona.fr/items/browse?"
    #baseUrl = "http://lorem.org/items/browse?collection="
    #collection = 1
    #numPage = 1 
    #collection = 1 
    #url = baseUrl+str(collection)+"&page="+str(numPage)+"&output=omeka-xml"
    url = baseUrl+"page="+str(numPage)+"&output=omeka-xml"
    listDico = read_OMEKA_XML2dictionnary(url)
    
    pathOutput = "./output/"
    nameCsvFile = "page_"+str(numPage)+".csv"
    dicoToCsv(pathOutput,nameCsvFile, listDico)
    
    
def test_extractAndSaveOneItem(itemId):
    """fonction permettant de tester l'extraction
    de d'un item particulier specifier par son id
    
    
    :param itemId: l'id de l'item choisi
    :type itemId: int. 
    """
    
    baseUrl = "http://lorem.org/items/show/"    
    url = baseUrl+str(itemId)+"?output=omeka-xml"
    listDico = read_OMEKA_XML2dictionnary(url)
    
    pathOutput = "./outputCSVoneItem/"
    nameCsvFile = "test_item"+str(itemId)+".csv"
    
    dicoToCsv(pathOutput,nameCsvFile, listDico)

    
def test_extractAndSaveMergeAllPages():
    
    """
    fonction permettant de tester la fonction extractAndSaveAllPages
    """
    
    baseUrl = "http://lorem.org/items/browse?collection=1"
    
   
    pathOutput = "./dirOutCSVGuarnido/"
    
    #url = baseUrl+"&page="+str(numPage)+"&output=omeka-xml"
    nbPages = getNumberPagesOmeka(baseUrl)
    
    extractAndSaveAllPages(baseUrl, nbPages, pathOutput)
        
    
        
def extractAndSaveAllPages(baseUrl, nbPages, pathOutput) :
    """fonction permettant d'extraire tous les items d'un omeka 
    et de sauvegarder toutes les metadatas dans des tableurs CSV (un tableur par page)
    
    Pour realiser cette operation nous utilisons l'expostion des donnees au format XML
    accessible via une requete GET de la forme baseUrlOmeka+"&page="+str(numPage)+"&output=omeka-xml"
    puisqu'il n'est pas possible d'extraire en une fois toutes les donnees il faut connaitre le nombre de page a parcurir.
    pour ce faire, il est conseiller d'utiliser la fonction getNumberPagesOmeka
    
    :param baseUrl: l'adresse du omeka a extraire 
    :type baseUrl: int. 
    
    :param nbPages: le nbPages de traiter de 1 à nb page obtenu par getNumberPagesOmeka
    :type nbPages: int. 
    
    :param pathOutput: le chemin vers le dossier de destination des fichiers csv
    :type pathOutput: str.
    """
    
    
    #il est possible que l'extraction d'une page ne se produise pas correctement.
    #par exemple le serveur omeka ne repond plus 
    #ou l'antivirus local bloque la 30ieme requetes sur le meme site en mois de 1 seconde 
    #(comportement suspect) nb:penser a autoriser cette application
    
    
    completed = True
    for pageNumber in range(1, int(nbPages)+1):
    
        url = baseUrl+"&page="+str(pageNumber)+"&output=omeka-xml"

        print('page number ', pageNumber, ' / ', nbPages)
        print("url cur :",url)
        nameCsvFile = str(pageNumber)+".csv"
        pathFileOut = pathOutput+nameCsvFile
        
        if not(os.path.isfile(pathFileOut)):
        
            try :
                listDico = read_OMEKA_XML2dictionnary(url)
                    
                dicoToCsv(pathOutput, nameCsvFile, listDico)
            
                time.sleep(1)
            except:
                print("error ... during extraction page number ",pageNumber)
                completed = False
        
                
    return completed
            
      


def dicoToCsv(pathOutput, nameCsvFile, listDico):
    """fonction permettant de sauvegarder dans un fichier CSV les donnees extraites d'un item stockées dans une liste de dico
    
    :param pathOutput: le chemin du dossier de destination du fichier CSV
    :type pathOutput: str 
    
    :param nameCsvFile: le nom du fichier CSV
    :type nameCsvFile: str 
    
    :param pathOutput: le chemin vers le dossier de destination des fichiers csv
    :type pathOutput: str.
    """
    
    outputCSV = pathOutput+nameCsvFile
    #ouverture du csv de sortie
    with open(outputCSV, 'w', encoding='utf-8',newline="\n") as csvfile:
        
        #on fusionne toutes les cles 
        #il y a une probabilite forte pour que certains dico est moins de cles que d'autre...
        
        listKey = []
        
        for dico in listDico:
            
            for k in dico.keys():
                #si la cle n'existe pas encore ds la liste de cles fusionnees
                if listKey.count(k) == 0:

                    listKey.append(k)
                
        #print "fusion list Keys  ", listKey   
        writer = csv.writer(csvfile,delimiter=';')
        listKeyS = sorted(listKey)
        
        #ecriture de la ligne d'entete contenant les noms des champs 
        writer.writerow(listKeyS)
        
        for dico in listDico:
            rowCur = []

            for k in listKeyS:
                #if dico.has_key(k):
                if k in dico:
                    rowCur.append(dico[k])
                else:
                    rowCur.append("none")
            
            #on ecrit une ligne par dico
            writer.writerow(rowCur)
             
  
def mergeCSV(listCSVfilePath, pathOut, nameCsvFileOut,tiny=True):
    """fusionne une collection de csv en 1 seul
    NB: une premiere passe permet d'extraire et de fusionner les differentes colonnes
        
    :param listCSVfilePath: la liste des fichiers CSV a fusionner
    :type baseUrl: str. 
    
    :returns:  None
    :raises: csv.Error
    """    
    

    
    #dans un premier temps on ouvre chaque fichier pour en extraire les noms de colonnes
    listUniqueColumnName = []
    
    
    print('Merge to file :', nameCsvFileOut)
    
    for filepath in listCSVfilePath:
        print("read file",filepath)
        
        f = open(filepath, encoding='utf-8',newline="\n")
        
        reader = csv.reader(f, delimiter=';') 
        

        for i, row in enumerate(reader):
            if i == 0:
                #print(row)
                for nameColumn in row:
                    #print(nameColumn)
                    
                    #on ajoute le nom de la column si on la connait pas deja
                    if not(nameColumn in listUniqueColumnName):
                        listUniqueColumnName.append(nameColumn)
            else:
                break
        #print ("row",row1) 
        f.close()
        
    
    #print(listUniqueColumnName)
     
    #maintenant que nous avons toute la liste des noms de colonnes    
    #on peut commencer a ecrire le fichier CSV de sortie
    outputCSV = pathOut+nameCsvFileOut
    #ouverture du csv de sortie
    with open(outputCSV, 'w', encoding='utf-8',newline="\n") as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        listKeyS = sorted(listUniqueColumnName)
        #ecriture de la ligne d'entete contenant les noms des champs 
        writer.writerow(listKeyS)
        
        #maintenant on va ouvoir relire tous les CSV pour les fusionner les uns apres les autres
        for filepath in listCSVfilePath:
            #print("RE-read file",filepath)
            
            stream = open(filepath, encoding='utf-8')
            dicReader = csv.DictReader(stream, delimiter=';') 
            
    
            for row in dicReader:
                rowOut = []
                
                for nameCol in listKeyS:
                    #si le nom de colum existe bien dans ce fichier
                    if nameCol in row:
                        
                        if(tiny):
                            strColCur = row[nameCol].replace('[','').replace(']','').replace("'","")
                            rowOut.append(strColCur)
                        else:
                            rowOut.append(row[nameCol])

                    else:
                        rowOut.append('none')
                        
                writer.writerow(rowOut)       
                
            f.close()

            
   
def test_mergeAllCsvInDir():
    """
    fonction permettant de tester la fonction mergeCSV
    """
    csvfiles = glob.glob('./outputCSV/*.csv')
    
    pathOut = './outputCSV/merge/'
    
    nameCsvFileOut = 'fusion-All.csv'
    
    mergeCSV(csvfiles,pathOut,nameCsvFileOut)
                
  




def test_extractBaseCordel():
    """
    fonction d'extraction de la base omeka Cordel
    appel successsivement 
    l'extraction des items vers des CSV
    puis fusionne les fichier 
    
    """
    #extraction des csv
    
    baseUrl = "http://cordel.edel.univ-poitiers.fr/items/browse?"
    pathOutput = "./dirOutCordel/"
    
    nbPages = getNumberPagesOmeka(baseUrl,1)
    print ("nb pages a traiter ", nbPages)

    
    completed = False
    
    while not(completed):
        completed = extractAndSaveAllPages(baseUrl, nbPages, pathOutput)
        time.sleep(5)
        
    #fusion des CSV
   
    csvfiles = glob.glob(pathOutput+'*.csv')  
    pathOutMerge = pathOutput+'/merge/'
   
    nameCsvFileOut = 'Cordel-All.csv'
    mergeCSV(csvfiles,pathOutMerge,nameCsvFileOut,False)
    
    nameCsvFileOut = 'Cordel-All-tiny.csv'
    mergeCSV(csvfiles,pathOutMerge,nameCsvFileOut,True)
    

    


def runScraping(url, dirOut):
    print("url cible : ", url)
    print("dossier de sortie : ", dirOut)
    
    #-------------------------------------------
    #creation du dossier de sortie
    #et de son sous dossier merge
    #contenant la fusion des differents CSV extraits
    if not os.path.exists(dirOut):
        os.makedirs(dirOut)
        
    dirOutMerge = dirOut+'merge/'
    if not os.path.exists(dirOutMerge):
        os.makedirs(dirOutMerge)
    #-------------------------------------------
    
    baseUrl = url
    pathOutput = dirOut
    
    nbPages = getNumberPagesOmeka(baseUrl,1)
    if nbPages ==-1:
        #☺cas d'une pagination anormale car url non correct
        return -1
    print ("nb pages a traiter ", nbPages)

    completed = False
    while not(completed):
        completed = extractAndSaveAllPages(baseUrl, nbPages, pathOutput)
        time.sleep(5)
        
    #fusion des CSV
    csvfiles = glob.glob(pathOutput+'*.csv')  
    pathOutMerge = pathOutput+'/merge/'
   
    #nameCsvFileOut = 'Cordel-All.csv'
    #mergeCSV(csvfiles,pathOutMerge,nameCsvFileOut,False)
    
    

    newName = dirOut.split('/')[-2]
    
    nameCsvFileOut = newName+'-All-tiny.csv'
    mergeCSV(csvfiles,pathOutMerge,nameCsvFileOut,True)
    
    nameCsvFileOut = newName+'-All.csv'   
    mergeCSV(csvfiles,pathOutMerge,nameCsvFileOut,False)
    
    return 0
    
    
              
def main(argv):
   
    #test_extractAndSaveOneItem(40)
    
    test_extractAndSaveOnePage(12)
    
    #test_extractAndSaveMergeAllPages()
    #test_mergeAllCsvInDir()

    #test_extractBaseCordel()

    """
    if len(argv)==2:
        runScraping(argv[0],argv[1])
    else:
        print("omekaXML2CVS urlOmeka pathOutput")
        print("exemple: 'https://guarnido.nakalona.fr/items/browse?' './DirOut/'")
    """

if __name__ == "__main__":
    main(sys.argv) 
    
