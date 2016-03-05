import arcpy
from arcpy import env
import os
import sys
import arcpy.mapping
arcpy.env.overwriteOutput = True

UCs=arcpy.GetParameterAsText(0)
UCsApoio=UCs.split("\\")
UCsApoio=UCsApoio[-1]
Veg=arcpy.GetParameterAsText(1)
escale=arcpy.GetParameterAsText(2)
escale=int(escale)
mult=arcpy.GetParameterAsText(3)
mult=int(mult)

OutPutFolder=arcpy.GetParameterAsText(4)
OutPutTxt=arcpy.GetParameterAsText(5)
boll=arcpy.GetParameterAsText(6)






feature_count=arcpy.GetParameterAsText(7)








class FuncArcpy(object):
    def __init__(self,UCs,UCsApoio,Veg,OutPutFolder,escale,mult,OutPutTxt,feature_count,boll):
	self.lista_escala_buffers=[]
	self.scale=escale
	self.mult=mult
	self.OutPutTxt=OutPutTxt
	self.lista_erases=[]
	self.fielArea=''
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

        self.lista='' # para usar na def selectINlist
        self.pattern='' # para usar na def selectINlist
    def DefineEscale(self):
	con_esc=self.scale
	for i in range(self.mult):	
		self.lista_escala_buffers.append(con_esc)
		con_esc=con_esc+self.scale
		
    def dropfiles(self):
	if os.path.exists(self.OutPutFolder+'/ArcGisDataBase.gdb'):
	    arcpy.env.workspace=self.OutPutFolder+'/ArcGisDataBase.gdb'
	    lista=arcpy.ListFeatureClasses()
	    for i in lista:
		inp=i.replace(".shp",'')
		arcpy.Delete_management(i)
		
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
	    try:
		arcpy.AddField_management(self.feature, "area_ha", "DOUBLE", 10, 10)
		arcpy.CalculateField_management(self.feature,"area_ha","!shape.area@squaremeters!","PYTHON_9.3","#")
		expression="!Area_ha!/10000"
		arcpy.CalculateField_management(self.feature,"area_ha",expression,"PYTHON_9.3","#")		
	    except Exception as e:
		print "An error has occurred"
		print "xxx"
	
    
	    
	
    def count_Features(self):
	if self.boll:
	    fields=FuncArcpy.checkField(self, self.feature)
	    if "area_ha" in fields:
		self.fielArea=True    
	    FuncArcpy.typeFeature(self)
	    
	    for erase in self.lista_erases:
		arcpy.SelectLayerByLocation_management(self.feature,"INTERSECT",erase)
		cursor = arcpy.da.SearchCursor(self.feature, ['FID'])
		count=0
		for i in cursor:
		    count=count+1
		self.countList.append(count)
		
		if self.fielArea:
		    with arcpy.da.SearchCursor(self.feature, "area_ha") as cursor:
			summed_total=0
			for row in cursor:
				summed_total = summed_total + row[0]
			summed_total=round(summed_total, ndigits=2)
			self.listaAreaFeatures.append(summed_total)
		
		
	    
		
		
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
		
    def criatxt(self):
	os.chdir(self.OutPutFolder)
	teste=open(self.OutPutTxt+".txt",'w')
	if self.fielArea==True:
	    cab="Scale,Area_Tot,NF,FuncionalArea\n"
	else:
	    cab="Scale,Area_Tot\n"

	teste.write(cab)
	for i in self.listclip:
		summed_total =0 
		with arcpy.da.SearchCursor(i, "Shape_Area") as cursor:
			for row in cursor:
				summed_total = summed_total + row[0]
			summed_total=round(summed_total, ndigits=2)
			summed_total=summed_total/10000
			if self.fielArea==True:
			    teste.write(`self.lista_escala_buffers[self.cout]`+","+`summed_total`+','+`self.countList[self.cout]`+","+`self.listaAreaFeatures[self.cout]`+'\n')
			else:
			    teste.write(`self.lista_escala_buffers[self.cout]`+","+`summed_total`+'\n')
			    
		self.cout=self.cout+1
			
	teste.close()
	self.cout=0

	
	
	
	
	
	
class principal(FuncArcpy):
    def __init__(self, UCs, UCsApoio, Veg, OutPutFolder, escale,mult,OutPutTxt,feature_count,boll):
	FuncArcpy.__init__(self, UCs, UCsApoio, Veg, OutPutFolder, 
	                  escale,mult,OutPutTxt,feature_count,boll)
    
    def run(self):
	FuncArcpy.DefineEscale(self)
	FuncArcpy.dropfiles(self)
	FuncArcpy.createDb(self)
	FuncArcpy.GeraBuffers(self)
	FuncArcpy.erase(self)
	FuncArcpy.count_Features(self)
	FuncArcpy.clipVegByErase(self)
	FuncArcpy.deletefield(self)
	FuncArcpy.addfield(self)
	FuncArcpy.criatxt(self)
	
	
fun=principal(UCs, UCsApoio, Veg, OutPutFolder,escale,mult,OutPutTxt,feature_count,boll)
fun.run()