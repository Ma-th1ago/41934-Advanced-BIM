
###Importing necessary libraries and modules###
##Here, necessary libraries and modules are imported to handle IFC models and perform operations on them.##

from pathlib import Path
import ifcopenshell
import ifcopenshell.util.selector
import json
from ifcopenshell.api import run
import ifcopenshell.api.material.assign_material   



###Opening the IFC model###
##This opens the IFC model by attempting to find it in the same folder as the script, and if that fails, it tries to locate the model based on the context of the Blender library.##

modelname = "LLYN-STRU"

try:
    dir_path = Path(__file__).parent
    model_url = Path.joinpath(dir_path, modelname).with_suffix('.ifc')
    model = ifcopenshell.open(model_url)
except OSError:
    try:
        import bpy
        model_url = Path.joinpath(Path(bpy.context.space_data.text.filepath).parent, modelname).with_suffix('.ifc')
        model = ifcopenshell.open(model_url)
    except OSError:
        print(f"ERROR: please check your model folder : {model_url} does not exist")



###Definition of a custom class for elements###
##This class is used to represent custom elements with properties such as ID, description, volume, and material.##

class  Custom_element():
    def __init__(self, id, description, volume, material):
        self.id = id
        self.description = description
        self.volume = volume
        self.material = material

    def __repr__(self):
        return f"""
                the object has the following properties:
                id = {self.id}
                description = {self.description}
                material = {self.material}
                volume = {self.volume}m3
               """



###Function to define material based on description###
##This function takes in a description of an element and returns a material based on certain conditions.##

def define_material_based_on_description(description):
    if "Vægelement" in description:
        return "Concrete (precast)"
    elif "Væg" in description or "Støttemur" in description or "Fundament" in description or \
            "Brønd" in description or "dæk" in description or "Dæk" in description or \
            "Afretning" in description:
        return "Concrete (in-situ)"
    elif "Isolering" in description:
        return "EPS S80"
    elif "Drænplade" in description:
        return "Drain plate (EPS and vapor barrier)"
    elif "Dækelement" in description:
        return "Concrete with rebar"
    elif "Trapez" in description:
        return "Aluminium"
    elif "Stål" in description:
        return "Steel"
    else:
        return "undefined"



###Function to assign IFC material to an element###
##This function assigns an IFC material to an element.##

def assign_ifc_material(element):
    concrete = run("material.add_material", model, name="CON01", category="concrete")
    run("material.assign_material", model, product=element, type="Ifcmaterial" , material=concrete)



###Function to create a list of custom elements from the model###
##This function retrieves elements from the model, filters them (e.g., walls and slabs), and creates a list of custom elements.##

def list_of_custom_elements_from_model():
    elements = ifcopenshell.util.selector.filter_elements(model, "IfcWall, IfcSlab")

    list_of_custom_elements = []

    for element in elements:
        id = str(element[7])
        qtos_psets = ifcopenshell.util.element.get_psets(element, qtos_only=True)
        qtos_identifier_key, _ = next(iter(qtos_psets.items()))
        net_volume = str(qtos_psets[qtos_identifier_key]['NetVolume'])
        description_psets = ifcopenshell.util.element.get_psets(element)
        description_identi_key, _ = next(iter(description_psets.items()))
        try:
            description = str(description_psets[description_identi_key]['Description'])
        except Exception as e:
            print("Element had no description and was removed.")
            continue
        matertial = define_material_based_on_description(description)
        test = Custom_element(id=id, description=description, volume=net_volume, material=matertial)
        list_of_custom_elements.append(test)

    return list_of_custom_elements



###Based on desciption and volumes we calculate the prices on the specific elements###

wall_concrete_in_situ_sum = 0
wall_concrete_precast_sum = 0
fundament_sum = 0
isolation_sum = 0
drain_plate_sum = 0
cover_plate_sum = 0
well_sum = 0
gravel_sum = 0
steel_sum = 0
slab_con_with_rebar = 0
slab_alu_sum = 0
for ele in list_of_custom_elements_from_model():
    if "Vægelement" in ele.description:
        wall_concrete_precast_sum += float(ele.volume)
    elif "Væg" in ele.description:
        wall_concrete_in_situ_sum += float(ele.volume)
    elif "Fundament" in ele.description:
        fundament_sum += float(ele.volume)
    elif "Støttemur" in ele.description:
        wall_concrete_in_situ_sum += float(ele.volume)
    elif "Isolering" in ele.description:
        isolation_sum += float(ele.volume)
    elif "Drænplade" in ele.description:
        drain_plate_sum += float(ele.volume)
    elif "Dækelement" in ele.description:
        slab_con_with_rebar += float(ele.volume)
    elif "dæk" in ele.description:
        cover_plate_sum += float(ele.volume)
    elif "Brønd" in ele.description:
        well_sum += float(ele.volume)
    elif "Afretning" in ele.description:
        gravel_sum += float(ele.volume)
    elif "Trapezplade" in ele.description:
        slab_alu_sum += float(ele.volume)
    elif "Stål" in ele.description:
        steel_sum += float(ele.volume)
    else:
        print(ele)


###Print the results###
##We print the results to a list##

print(f"""
Building Wall Volumes:
      The total volume (m3) of concrete (precast) Walls is: {wall_concrete_precast_sum}
      The total volume (m3) of concrete (in-situ) Walls is: {wall_concrete_in_situ_sum}
      The total volume (m3) of concrete (in-situ) Fundament is: {fundament_sum}
      The total volume (m3) of EPS S80 Isolation is: {isolation_sum}
      The total volume (m3) of Drain Plate is: {drain_plate_sum}
      """)


print(f"""
Building Slab Volumes:
      The total volume (m3) of concrete (in-situ) slabs is: {cover_plate_sum + well_sum + gravel_sum}
      The total volume (m3) of concrete with rebar slabs is: {slab_con_with_rebar}
      The total volume (m3) of aluminium slabs is: {slab_alu_sum}
      The total volume (m3) of steel slabs is: {steel_sum}
      """)

prices_dict = {}
with open("prices.json", "r") as json_file:
    prices_dict = json.load(json_file)

print(f"""
Building Wall Prices:
      The total price (DKK) of concrete (precast) Walls is: {wall_concrete_precast_sum * prices_dict["Concrete (precast)"]}
      The total price (DKK) of concrete (in-situ) Walls is: {wall_concrete_in_situ_sum * prices_dict["Concrete (in-situ)"]}
      The total price (DKK) of concrete (in-situ) Fundament is: {fundament_sum * prices_dict["Concrete (in-situ)"]}
      The total price (DKK) of EPS S80 Isolation is: {isolation_sum * prices_dict["EPS S80"]}
      The total price (DKK) of Drain Plate is: {drain_plate_sum * prices_dict["Drain plate (EPS and vapor barrier)"]}
      """)


print(f"""
Building Slab Volumes:
      The total volume (m3) of concrete (in-situ) slabs is: {(cover_plate_sum + well_sum + gravel_sum) * prices_dict["Concrete (in-situ)"]}
      The total volume (m3) of concrete with rebar slabs is: {slab_con_with_rebar * prices_dict["Concrete with rebar"]}
      The total volume (m3) of aluminium slabs is: {slab_alu_sum * prices_dict["Aluminium"]}
      The total volume (m3) of steel slabs is: {steel_sum * prices_dict["Steel"]}
      """)


###Assign material to elemets###
##This script assign a material to a element, if the element doesnt have a assigned material, and makes it highlighted in red##

def create_and_assign_new_material():
    # Create a new material
    material = model.createIfcMaterial("test material")
    ## Define the material properties such as color 
    color = model.create_entity('IfcColourRgb', Red=1.0, Green=0.0, Blue=0.0)
    surface_style_rendering = model.create_entity('IfcSurfaceStyleRendering', SurfaceColour=color)

    material_layer = model.create_entity('IfcMaterialLayer', Material=material, LayerThickness=0.2)
    material_layer_set = model.create_entity('IfcMaterialLayerSet', MaterialLayers=[material_layer])
    material_layer_set_usage = model.create_entity('IfcMaterialLayerSetUsage', ForLayerSet=material_layer_set)
    wall = model.by_type("IfcWall")[50]


    # Create the relationship
    rel_associates_material = model.create_entity('IfcRelAssociatesMaterial', GlobalId=ifcopenshell.guid.new(), RelatedObjects=[wall], RelatingMaterial=material_layer_set_usage)
    model.write("mainpulated_model.ifc")
