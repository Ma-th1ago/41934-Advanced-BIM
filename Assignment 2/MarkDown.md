<style>
</style>

# Assignment 2

#### Use case: Cost Estimation of structural materials

This use case focuses on estimating the costs associated with structural elements and materials in construction projects. The objective is to predict quantities, costs, and prices for all the structural components, enabling stakeholders to make informed decisions about project feasibility and profitability.

#### What does our script try toidentify?

The purpose of this assignment is to provide contractors and subcontractors
with a tool to estimate quantities and properties of structural elements within
an IFC file. By doing so, the use case facilitates early-stage cost estimation,
allowing contractors to assess project profitability and competitiveness in
tender competitions.

#### How does our script address this problem?

To address this challenge, our script analyzes material quantities and
dimensions within the IFC file using IFCOpenShell. The specific tool extracts
the most relevant information from the IFC file for the purpose. This script
focuses only on Ifcwalls, extracting their Id, description, material, and
volume in m3. In this case, not all elements have associated materials, so the
script can define materials and link them to the elements on its own. The
script then sorts the elements based on description and material. Finally, a
price is provided by uploading a JSON file containing prices. This allows for a
quick estimated cost estimate.

#### What disciplinary expertise have we used to solve this case?

Our knowledge comes from the 5 semesters we have had at DTU. We have previously
had the subject "construction process management", which gives an
insight into how things work with contractors. From the subject, we have gained
knowledge about bidding rounds and early planning. It is still done the
old-fashioned way in some companies in terms of quantity calculation. However,
if it is a smaller company that does not spend money on, e.g. Revit, then this
script can help provide a quick estimation of prices in relation to material
quantities.

#### What IFC concepts have we used in our scripts?

The script primarily focuses on IfcObjectDefinition, IfcPropertyDefinition (Qto_XXBaseQuantities) to extract values for different elements in the model. This enables the identification and analysis of specific objects, utilizing their properties to fulfill the requirements of our use case.

#### What disciplinary analysis does it require?

The use case demands cost and value analysis,
emphasizing material quantity. Structural analysis is essential to ensure the
integrity of the estimated costs.

#### What building elements are we interested in?

Our primary interest encompasses the costs associated with crucial building
elements, including beams, columns, walls, and slabs. Can be any elements.

What use cases must be done
before we can start our use case?  
Before initiating our use case, a detailed structural and architectural model
must be available.  

#### What is the input data for our use case?

The input data for our use case includes prices per unit of quantity and quality, enabling accurate cost estimation for the identified structural elements. Our script is designed in a way that only elements measurable in cubic meters (m3) can be analyzed. However, it is a minor modification if one wants it in quantity, linear meters, or square meters (m2).  

#### What other use cases are waiting for ours to be completed?

Upon completion, our use case will pave the way
for subsequent use cases, specifically in the build/operate domain, ensuring a
seamless integration of cost estimation into the broader project lifecycle. Our
script can also be used as a part of an LCA. The quantities of the various
building materials are essential to be able to carry out an LCA.
