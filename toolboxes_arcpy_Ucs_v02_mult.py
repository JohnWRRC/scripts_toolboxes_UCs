import arcpy
from arcpy import env
import os
import sys
import arcpy.mapping
arcpy.env.overwriteOutput = True

UCs=arcpy.GetParameterAsText(0)
inputCol=arcpy.GetParameterAsText(1)
UCsApoio=UCs.split("\\")
UCsApoio=UCsApoio[-1]
Veg=arcpy.GetParameterAsText(2)

escale=arcpy.GetParameterAsText(3)
escale=int(escale)
mult=arcpy.GetParameterAsText(4)
mult=int(mult)
boll=arcpy.GetParameterAsText(5)
feature_count=arcpy.GetParameterAsText(6)
OutPutTxt=arcpy.GetParameterAsText(7)
OutPutFolder=arcpy.GetParameterAsText(8)


















class FuncArcpy(object):
    def __init__(self,UCs,UCsApoio,Veg,OutPutFolder,escale,mult,OutPutTxt,feature_count,boll,inputCol):
	self.inpuCol=inputCol
	self.lista_escala_buffers=[]
	self.scale=escale
	self.mult=mult
	self.OutPutTxt=OutPutTxt
	self.lista_erases=[]
	self.fielArea=''
	self.fielPoint=''
        self.UCs=UCs
	self.UCsApoio=UCsApoio
        self.Veg=Veg
        self.OutPutFolder=OutPutFolder
        self.listbuffers=''
	self.Listerase=''
	self.listclip=''
	self.FieldList=[]
	self.cout=0
	self.feature=feature_count
	self.boll=boll
	self.countList=[]
	self.listaAreaFeatures=[]
	self.referenceListquery=[]
	self.listAreaAnalise=[]
	self.txtAreaAnalise=''
	self.txtFuncarea=''
	self.ListIDcod=[]
	self.txtCountFeat=''

        self.lista='' # para usar na def selectINlist
        self.pattern='' # para usar na def selectINlist
    def DefineEscale(self):
	con_esc=self.scale 
	for i in range(self.mult):	
		self.lista_escala_buffers.append(con_esc) #criando lista de escala
		con_esc=con_esc+self.scale
		
    def CreateListaFieldReference(self):
	with arcpy.da.SearchCursor(self.UCs, self.inpuCol) as cursor:
	    for row in cursor:
		try:
		    temp=int(row[0])
		    self.ListIDcod.append(temp)
		    query="\""+self.inpuCol+"\"="+`temp`
		    self.referenceListquery.append(query)
		except:
		    self.ListIDcod.append(row[0])
		    query =  self.inpuCol+"='%s'" % row[0]
		    self.referenceListquery.append(query)
		    
		
		    
		
    def dropfiles(self):
	if os.path.exists(self.OutPutFolder+'/ArcGisDataBase.gdb'):
	    arcpy.env.workspace=self.OutPutFolder+'/ArcGisDataBase.gdb'
	    lista=arcpy.ListFeatureClasses()
	    for i in lista:
		inp=i.replace(".shp",'')
		arcpy.Delete_management(i)
		arcpy.Delete_management(inp)
		
    def selecInList(self):
        lista=[]
        for i in self.lista:
            if self.pattern in i:
                lista.append(i)
        return lista
        
    #criando um geobata base    
    def createDb(self):
        if not os.path.exists(self.OutPutFolder+'/ArcGisDataBase.gdb'):
            arcpy.CreateFileGDB_management(self.OutPutFolder,"ArcGisDataBase")
        
    #criando os buffers    
    def GeraBuffers(self):
        arcpy.env.workspace=self.OutPutFolder+'/ArcGisDataBase.gdb'
        for i in self.lista_escala_buffers:
            formatName="00000"+`i`
            formatName=formatName[-5:]
	    self.UCsApoio=self.UCsApoio.replace(".shp",'')
            OutPutName=self.UCsApoio+"_Buffer_"+formatName
            arcpy.Buffer_analysis(self.UCs,OutPutName,i,"FULL","FLAT","ALL")
	listbuffers=arcpy.ListFeatureClasses()
	self.lista=listbuffers
	self.pattern="_Buffer_"
	self.listbuffers=FuncArcpy.selecInList(self)	
    
    
    
    def erase(self):
	for i in self.listbuffers:
		out_name=i.replace("Buffer","Erase")
		arcpy.Erase_analysis(i,self.UCs,out_name,'')   
		self.lista_erases.append(out_name)
	Listerase=arcpy.ListFeatureClasses()
	self.lista=Listerase
	
	self.pattern="_Erase_"
	self.Listerase=FuncArcpy.selecInList(self)
    def typeFeature(self):
	desc = arcpy.Describe(self.feature)
	geometryType = desc.shapeType
	if geometryType == 'polygon':
	    self.fielArea=True # vendo se eh um poligono ou nao se nao for sera ponto
	    try:
		arcpy.AddField_management(self.feature, "area_ha", "DOUBLE", 10, 10)
		arcpy.CalculateField_management(self.feature,"area_ha","!shape.area@squaremeters!","PYTHON_9.3","#")
		expression="!Area_ha!/10000"
		arcpy.CalculateField_management(self.feature,"area_ha",expression,"PYTHON_9.3","#")		
	    except Exception as e:
		pass
	else:
	    self.fielPoint=True # neste cado eh um ponto
	
    
	    
	
    def count_Features(self):
	if self.fielArea:
	    self.countList=[]
	    for erase in self.lista_erases:
		arcpy.SelectLayerByLocation_management(self.feature,"INTERSECT",erase)
		cursor = arcpy.da.SearchCursor(self.feature, ['FID'])
		count=0
		for i in cursor:
		    count=count+1
		self.countList.append(count)
		
		with arcpy.da.SearchCursor(self.feature, "area_ha") as cursor:
		    summed_total=0
		    for row in cursor:
			    summed_total = summed_total + row[0]
		    summed_total=round(summed_total, ndigits=2)
		    self.listaAreaFeatures.append(summed_total)
			
	if self.fielPoint:
	    self.countList=[]
	    for erase in self.lista_erases:
		arcpy.SelectLayerByLocation_management(self.feature,"INTERSECT",erase)
		cursor = arcpy.da.SearchCursor(self.feature, ['FID'])
		count=0
		for i in cursor:
		    count=count+1
		self.countList.append(count)	    
	    
		
		
	    
		
		
    def clipVegByErase(self):
	for i in self.Listerase:
	    out_name=i.replace("Erase","Erase_Clip_Veg")
	    arcpy.Clip_analysis(self.Veg,i,out_name,"")
	    
	    Listclip=arcpy.ListFeatureClasses()
	    self.lista=Listclip
	    self.pattern="_Erase_Clip_Veg_"
	    self.listclip=FuncArcpy.selecInList(self)	    
	    
    
    def checkField(self,mapa):
	fields = arcpy.ListFields(mapa)
	for field in fields:
	    self.FieldList.append(field.name)	
	return self.FieldList
    
    
    def deletefield(self):
	for i in self.listclip:
	    fields=FuncArcpy.checkField(self, i)
	    if "Area_ha" in fields:
		arcpy.DeleteField_management(i, ["Area_ha"])    
    
    def addfield(self):
	for i in self.listclip:
	    try:
		arcpy.AddField_management(i, "Area_ha", "DOUBLE", 10, 10)
		arcpy.CalculateField_management(i,"Area_ha","!shape.area@squaremeters!","PYTHON_9.3","#")
		expression="!Area_ha!/10000"
		arcpy.CalculateField_management(i,"Area_ha",expression,"PYTHON_9.3","#")
	    except:
		print "pass"
    
    
    def calculateAreaAnalises(self):
	for i in self.listclip:
	    summed_total =0 
	    with arcpy.da.SearchCursor(i, "Shape_Area") as cursor:
		for row in cursor:
		    summed_total = summed_total + row[0]
		summed_total=round(summed_total, ndigits=2)
		summed_total=summed_total/10000
		self.listAreaAnalise.append(summed_total)

    def removeDuplicateList(self,lista):
	listaapoio=[]
	for i in lista:
	    if not i in listaapoio:
		listaapoio.append(i)
	
	return listaapoio
	    
	
    def criatxtArea_Analise(self):
	
	
	FuncArcpy.calculateAreaAnalises(self)
	
	idcod=str(self.ListIDcod[self.cout])
	
	
	
	##----------------TXTAREAAnalise------------------------------------------------------
	self.listAreaAnalise=FuncArcpy.removeDuplicateList(self, self.listAreaAnalise)
	self.txtAreaAnalise.write(idcod+','+','.join(str(x) for x in self.listAreaAnalise))
	self.txtAreaAnalise.write('\n')
	self.listAreaAnalise=[]
	#-------------------------------------------------------------------------------------
	
	if self.fielArea:
	    self.listaAreaFeatures=FuncArcpy.removeDuplicateList(self, self.listaAreaFeatures)
	    ##----------------TXTFunarea------------------------------------------------------
	    self.txtFuncarea.write(idcod+','+','.join(str(x) for x in self.listaAreaFeatures))
	    self.txtFuncarea.write('\n')
	    self.listaAreaFeatures=[]
	    #-------------------------------------------------------------------------------------	
	
	
	if self.boll:
	    #----------------TXTAREAAnalise------------------------------------------------------
	    self.countList=FuncArcpy.removeDuplicateList(self, self.countList)
	    self.txtCountFeat.write(idcod+','+','.join(str(x) for x in self.countList))
	    self.txtCountFeat.write('\n')
	    self.countList=[]
	    #-------------------------------------------------------------------------------------		
	
	
	
			    
		
			
	

	
	
	
	
	
	
class principal(FuncArcpy):
    def __init__(self, UCs, UCsApoio, Veg, OutPutFolder, escale, mult, 
                OutPutTxt, feature_count, boll, inputCol):
	FuncArcpy.__init__(self, UCs, UCsApoio, Veg, OutPutFolder, escale, mult, 
	                  OutPutTxt, feature_count, boll, 
	                  inputCol)
    
    
		
		
    def run(self):
	
	if self.boll:
	    fields=FuncArcpy.checkField(self, self.feature)
	    FuncArcpy.typeFeature(self)	    
	
	FuncArcpy.CreateListaFieldReference(self)
	FuncArcpy.DefineEscale(self) #definindo a lista de escalas
	FuncArcpy.createDb(self)
	
	#area analises
	os.chdir(OutPutFolder)
	
	self.txtAreaAnalise=open("__AreaAnalises_"+self.OutPutTxt+".txt",'w')
	self.txtAreaAnalise.write(self.inpuCol+','+','.join(str(x) for x in self.lista_escala_buffers)) #cabecalho
	self.txtAreaAnalise.write('\n')
	#--------
	
	#Fuctional area
	if self.fielArea:
	    self.txtFuncarea=open("__FunctionalArea"+self.OutPutTxt+".txt",'w')
	    self.txtFuncarea.write(self.inpuCol+','+','.join(str(x) for x in self.lista_escala_buffers)) #cabecalho
	    self.txtFuncarea.write('\n')	
	
	if self.boll:
	    #Fuctional area
	    self.txtCountFeat=open("__CountFeatures_"+self.OutPutTxt+".txt",'w')
	    self.txtCountFeat.write(self.inpuCol+','+','.join(str(x) for x in self.lista_escala_buffers)) #cabecalho
	    self.txtCountFeat.write('\n')	    
	
	self.cout=0
	
	for i in self.referenceListquery:
	    FuncArcpy.dropfiles(self)
	    arcpy.SelectLayerByAttribute_management(self.UCs,"NEW_SELECTION",i)
	    FuncArcpy.GeraBuffers(self)
	    FuncArcpy.erase(self)
	    FuncArcpy.count_Features(self)
	    FuncArcpy.clipVegByErase(self)
	    FuncArcpy.deletefield(self)
	    FuncArcpy.addfield(self)
	    FuncArcpy.criatxtArea_Analise(self)
	
	    
	    
	    self.cout=self.cout+1
	self.txtAreaAnalise.close()
	
	if self.fielArea:
	    self.txtFuncarea.close()
	if self.fielPoint:
	    self.txtCountFeat.close()
	    
		    
	
fun=principal(UCs, UCsApoio, Veg, OutPutFolder, escale, mult, OutPutTxt, 
             feature_count, boll, inputCol)
fun.run()
