from pathlib import Path
import ifcopenshell
import ifcopenshell.util.selector
import json
from ifcopenshell.api import run
import ifcopenshell.api.material.assign_material   

modelname = "LLYN-STRU"

#This part of the script is importing the IFCfile based on the directory path. If it can't, it will throw a exception.

try:
    dir_path = Path(__file__).parent
    model_url = Path.joinpath(dir_path, modelname).with_suffix('.ifc')
    model = ifcopenshell.open(model_url)
except OSError:
    print(f"ERROR: please check your model folder : {model_url} does not exist")


# Next up the script is defining a class so can encapsulate the information. It defines the id, description, volume and material.
# The class also has a __repr__ method for better printing.

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


# This part of the script defines the a material based on the description of the element. 
# IFCmaterial's does of course need a non-empty description, otherwise it will be classified undefined.


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

# Here the material is assiged to the element
# Molios data could be used here

def assign_ifc_material(element):
    concrete = run("material.add_material", model, name="CON01", category="concrete")
    run("material.assign_material", model, product=element, type="Ifcmaterial" , material=concrete)

# Here we create the list of our custom ifc-element(the class declared above).
# It find all elements of the model based on the string input, and assigns the ID, volume material and description  
# If there is no description, it prints "You just got nuked" (no element).

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
            print("You just got nuked")
            continue
        matertial = define_material_based_on_description(description)
        test = Custom_element(id=id, description=description, volume=net_volume, material=matertial)
        list_of_custom_elements.append(test)

    return list_of_custom_elements

# This part of the script calculates the m3 over all custom elements. It sums the m3 up basically. 
# For example: If there is a "vægelement" in the description we assume it is made out of concrete (precast)#

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



# Printing the result

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

# After finding all the volumes the script then multiplies the volume in m3 with the price of 1 m3 of a certain material
# Here we could have used the Molio data instead.
# The prices is defined in a json format in the file prices.json

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

# This part of the script is trying to change the materal and assign it to the element and also changing the colour
# This can be used to highligt all the elements made out of a certain material and to see where the material is used in the model

def create_and_assign_new_material():
    # Create a new material
    material = model.createIfcMaterial("test material")
    # Define the material properties such as color 
    color = model.create_entity('IfcColourRgb', Red=1.0, Green=0.0, Blue=0.0)
    surface_style_rendering = model.create_entity('IfcSurfaceStyleRendering', SurfaceColour=color)

    material_layer = model.create_entity('IfcMaterialLayer', Material=material, LayerThickness=0.2)
    material_layer_set = model.create_entity('IfcMaterialLayerSet', MaterialLayers=[material_layer])
    material_layer_set_usage = model.create_entity('IfcMaterialLayerSetUsage', ForLayerSet=material_layer_set)
    wall = model.by_type("IfcWall")[50]


    # Create the relationship
    rel_associates_material = model.create_entity('IfcRelAssociatesMaterial', GlobalId=ifcopenshell.guid.new(), RelatedObjects=[wall], RelatingMaterial=material_layer_set_usage)
    model.write("mainpulated_model.ifc")


