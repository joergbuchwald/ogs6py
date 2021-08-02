# make sure path ogs6py is known via pip or 
# export PYTHONPATH=$PYTHONPATH:<PATH>/ogs6py/ogs6py

# This script generates an OGS input-file (prj) for a variable number of
# materials which are included as separate xml-files inside <medium> sections.
#
# It reads three files
# - parameterTable.csv      with the parameters of the layers (materials)
# - OGStemplate_main.prj    with empty media block, i.e. only whitespaces between <media> tags.
# - OGStemplate_medium.xml  with the medium parameters, to be set inside <medium> 
#
# The output is written to (existing files get overwritten)
# - OGSmain.prj		containing include-directives to
# - OGSmedium_0.xml
# - OGSmedium_1.xml
# - ...
import ogs6py as ogs
import pandas as pd


###   READ MEDIA (MATERIALS) FROM TABLE   ### 
parameter_table = pd.read_csv('parameterTable.csv')  
print(parameter_table.info())

N_mat = len(parameter_table.index)   # number of data rows (without header)
names_list = list(parameter_table['„stratigraphy_unit“']) # TODO add as comment  
density_list = list(parameter_table['„solid_mass_density_[kg/m³]_max“']) 
viscosity_list = list(parameter_table['„viscosity“']) 
permeability_list = list(parameter_table['„hydraulic_permeability_[m²]_mean“'])
porosity_list = list(parameter_table['„Porosity_[-]_mean“'])    
storage_list = list(parameter_table['„hydraulic_storage_[1/Pa]_mean“'])


###   PROCESS MEDIA FILES   ###

# enter parameters into template (ogs6py)
medium_template_filename = "OGStemplate_medium.xml"
medium_filenames=[]	
for n in range(N_mat):
    medium_filename="OGSmedium_"+str(n)+".xml"
    medium_filenames.append(medium_filename)
    medium_xml= ogs.OGS(INPUT_FILE=medium_template_filename, PROJECT_FILE=medium_filename)

    medium_xml.replace_text(viscosity_list[n], xpath="./phases/phase/properties/property[name='viscosity']/value")
    medium_xml.replace_text(density_list[n], xpath="./phases/phase/properties/property[name='density']/value")
    medium_xml.replace_text(permeability_list[n], xpath="./properties/property[name='permeability']/value")
    medium_xml.replace_text(porosity_list[n], xpath="./properties/property[name='porosity']/value")
    medium_xml.replace_text(storage_list[n], xpath="./properties/property[name='storage']/type") 
    
    medium_xml.write_input()


# The <medium> tags were needed for ogs6py but are removed now,
# they will be reinserted as numbered <medium id ...>  in main.prj.
# This approach was chosen, as OGS allows only one file inclusion per XML-tag
for n in range(N_mat):
    medium_filedata = open(medium_filenames[n]).read()
    medium_filedata = medium_filedata.replace('<medium>', '<!-- stratigraphy unit: ' + names_list[n] + '-->' )
    medium_filedata = medium_filedata.replace('</medium>','')
    medium_file = open(medium_filenames[n], 'w')
    medium_file.write(medium_filedata)
    medium_file.close


###   PROCESS MAIN FILE   ###

# add medium blocks (ogs6py)
main_template_filename='OGStemplate_main.prj'
main_filename="OGSmain.prj"
main_prj= ogs.OGS(INPUT_FILE=main_template_filename, PROJECT_FILE=main_filename)

for n in range(N_mat):
    include_file="<include file="+medium_filenames[n]+"/>"    
    main_prj.add_entry(parent_xpath="./media", tag="medium", text=include_file, attrib="id", attrib_value=str(n))

main_prj.write_input()  

# ogs6py codes "<" as "&lt;" and ">" as  "&gt;", although XML readers should accept this, we replace it for sake of beauty
main_filedata = open(main_filename).read()
main_filedata = main_filedata.replace('&lt;', '<')
main_filedata = main_filedata.replace('&gt;','>')
main_file = open(main_filename, 'w')
main_file.write(main_filedata)
main_file.close


# this is how to replace other parameters than media (ogs6py)
#medium_prj.= ogs.OGS(INPUT_FILE=in, PROJECT_FILE=out)
#medium_prj.replace_text(9.81, xpath="./processes/process/darcy_gravity/g")
