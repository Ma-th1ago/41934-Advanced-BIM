from pathlib import Path
import ifcopenshell
import ifcopenshell.util.selector
import json

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


def define_material_based_on_description(description):
    if "Vægelement" in description:
        return "Concrete (precast)"
    elif "Væg" in description or "Støttemur" in description or "Fundament" in description:
        return "Concrete (in-situ)"
    elif "Isolering" in description:
        return "EPS S80"
    elif "Drænplade" in description:
        return "Drain plate (EPS and vapor barrier)"
    else:
        return "undefined"


def list_of_custom_elements_from_model():
    elements = ifcopenshell.util.selector.filter_elements(model, "IfcWall")

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
            print("you got nuked son")
            continue
        matertial = define_material_based_on_description(description)
        test = Custom_element(id=id, description=description, volume=net_volume, material=matertial)
        list_of_custom_elements.append(test)

    return list_of_custom_elements

wall_concrete_in_situ_sum = 0
wall_concrete_precast_sum = 0
fundament_sum = 0
isolation_sum = 0
drain_plate_sum = 0
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
    else:
        print(ele)

print(f"""
Building Wall Volumes:
      The total volume (m3) of concrete (precast) Walls is: {wall_concrete_precast_sum}
      The total volume (m3) of concrete (in-situ) Walls is: {wall_concrete_in_situ_sum}
      The total volume (m3) of concrete (in-situ) Fundament is: {fundament_sum}
      The total volume (m3) of EPS S80 Isolation is: {isolation_sum}
      The total volume (m3) of Drain Plate is: {drain_plate_sum}
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

