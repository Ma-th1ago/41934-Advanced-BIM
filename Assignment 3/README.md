# A3-OpenBIM

Lucas Malthe Mikkelsen s215310, Mathias Nielsen s215273

Assignment 3

# 1. Analyzing the Use Case

**1.1 Objective:**

The main goal is to automate the cost
estimation of the structural elements within any IFC model. In previous tasks,
we encountered issues regarding missing materials and dimensions. This information
is crucial for creating an estimated price. Therefore, assumptions were made
based on the only useful information provided in the IFC file, which is the
description of the elements. This task/script will attempt to add materials to
the IFC file based on the description.

**1.2 Use Case Description:**

This use case focuses on structural
elements, emphasizing cost estimation. It falls under the 'Analyse (forecast)'
category within BIM use. The tool caters primarily to Structural Engineers,
providing cost on the structural layouts. Designers can assess various layout
systems' conformity regarding cost. This iterative approach enhances
decision-making in structural design.

# 2. Proposed Tool/Workflow Design

**2.1 BPMN Workflow**

In the img folder, we have an BPMN Workflow Chart

**2.2 Workflow Details:**

The tool extracts essential data from IFC
models such as material properties. Simple calculations yield parameters needed
for the use case, such as element volume.

# 3. Information Exchange

**3.1 Data Sources: **
IFC Data: Elements (IfcBeam, IfcSlab, IfcWall, IfcColumn, IfcFoundation),
Properties (Material type, Dimensions)

External Sources: Cost data (SIGMA), Material Densities

**3.2 Assumptions:**

-          Structural elements fall into specified IFC categories.

-          Acceptable cost/budget is assumed until specified.

-          Composite details (e.g., slabs with concrete and reinforcement) are simplified.

# 4. Value and Business Need

**4.1 Business Value:**

The tool saves time and costs, aiding
decision-making. Designers can identify elements contributing significantly to
budget adherence.

**4.2 Societal Value:**

Enables designing structures within budget.

# 5. Delivery

**5.1 Use Case Resolution:**

The use case is solved by loading an IFC
model. The analysis, an automated process, extracts data, performs
calculations, and checks conformity with limits.

**5.2 Tool Development Methodology:**

The tool evolves in stages, initially
focusing on extracting structural elements. Subsequent iterations include
dimensional and material data extraction, volume computation, and integration
of cost. The final stage validates the process against the BPMN diagram,
ensuring accuracy and completeness.
