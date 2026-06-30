
# These are hand-crafted questions covering all three parts.

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))



import json
from config import QA_DIR
from utils.logger import get_logger

log = get_logger(__name__)

QA_PAIRS = [
    # IS 875 Part 1 — Dead Loads
    {
        "id": "p1_001",
        "question": "What is the unit weight of plain concrete as per IS 875 Part 1?",
        "expected_answer": "The unit weight of plain concrete is 24 kN/m³ as per IS 875 Part 1.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p1_002",
        "question": "What is the unit weight of reinforced cement concrete (RCC)?",
        "expected_answer": "The unit weight of reinforced cement concrete is 25 kN/m³.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p1_003",
        "question": "What is the unit weight of steel as per IS 875 Part 1?",
        "expected_answer": "The unit weight of steel is 78.5 kN/m³.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p1_004",
        "question": "What is the unit weight of brick masonry with lime mortar?",
        "expected_answer": "The unit weight of brick masonry with lime mortar is approximately 19 kN/m³.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p1_005",
        "question": "How should the dead load of a partition wall be considered if its position is not fixed?",
        "expected_answer": "If the position of a partition wall is not fixed, a uniformly distributed load per unit area is added to the imposed floor load.",
        "expected_clauses": ["3.3"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p1_006",
        "question": "What is the unit weight of timber (teak)?",
        "expected_answer": "The unit weight of teak timber is approximately 6.3 to 10.5 kN/m³ as per IS 875 Part 1.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p1_007",
        "question": "What is the unit weight of granite stone?",
        "expected_answer": "The unit weight of granite is 26.4 to 27.0 kN/m³.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p1_008",
        "question": "What is the unit weight of water?",
        "expected_answer": "The unit weight of water is 10 kN/m³.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p1_009",
        "question": "How is dead load of a floor finish calculated?",
        "expected_answer": "The dead load of a floor finish is calculated by multiplying its thickness by its unit weight.",
        "expected_clauses": ["3.1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p1_010",
        "question": "What is the unit weight of aluminium?",
        "expected_answer": "The unit weight of aluminium is 27.0 kN/m³.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },

    # IS 875 Part 2 — Imposed Loads
    {
        "id": "p2_001",
        "question": "What is the imposed floor load for a residential dwelling (bedrooms)?",
        "expected_answer": "The imposed floor load for residential dwellings (bedrooms and living rooms) is 2.0 kN/m².",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_002",
        "question": "What is the live load for office floors?",
        "expected_answer": "The imposed load for office floors is 2.5 kN/m² for general use.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_003",
        "question": "What is the imposed load for a public assembly hall with fixed seating?",
        "expected_answer": "The imposed load for assembly halls with fixed seating is 4.0 kN/m².",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_004",
        "question": "What load should be applied on stairs in residential buildings?",
        "expected_answer": "For stairs in residential buildings, the imposed load is 3.0 kN/m².",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_005",
        "question": "What is the imposed load for flat roofs accessible for normal maintenance only?",
        "expected_answer": "For flat roofs accessible only for maintenance, the imposed load is 0.75 kN/m².",
        "expected_clauses": ["4.1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_006",
        "question": "What concentrated load should be used for designing floor beams?",
        "expected_answer": "A concentrated load of 4.5 kN acting over an area of 50mm x 50mm is used for local checking.",
        "expected_clauses": ["3.1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_007",
        "question": "What is the imposed load reduction clause for beams and girders supporting large floor areas?",
        "expected_answer": "Imposed loads may be reduced depending on the tributary area supported by the member.",
        "expected_clauses": ["3.2"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_008",
        "question": "What is the imposed load for hospital wards?",
        "expected_answer": "Hospital wards have an imposed floor load of 3.0 kN/m².",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_009",
        "question": "What is the live load for parking floors for light vehicles?",
        "expected_answer": "The imposed load for parking areas with light vehicles (up to 25 kN GVW) is 2.5 kN/m².",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_010",
        "question": "What is the horizontal imposed load on hand rails and balustrades?",
        "expected_answer": "A horizontal load of 0.75 kN/m is applied on hand rails and balustrades.",
        "expected_clauses": ["5.1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },

    # IS 875 Part 3 — Wind Loads
    {
        "id": "p3_001",
        "question": "What is the design wind speed formula as per IS 875 Part 3?",
        "expected_answer": "The design wind speed Vz = Vb × k1 × k2 × k3 × k4, where Vb is the basic wind speed.",
        "expected_clauses": ["6.3"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_002",
        "question": "What is the basic wind speed for Chennai?",
        "expected_answer": "The basic wind speed for Chennai is 50 m/s as per the wind zone map in IS 875 Part 3.",
        "expected_clauses": ["Annex A", "Fig. 1"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_003",
        "question": "What is the basic wind speed for Mumbai?",
        "expected_answer": "The basic wind speed for Mumbai is 44 m/s.",
        "expected_clauses": ["Annex A"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_004",
        "question": "What does the k1 factor in wind load calculation represent?",
        "expected_answer": "k1 is the probability factor (risk coefficient) that accounts for the design life and return period of the structure.",
        "expected_clauses": ["6.3.1"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_005",
        "question": "What does the k2 factor represent in IS 875 Part 3?",
        "expected_answer": "k2 is the terrain, height, and structure size factor that accounts for the variation of wind speed with height and terrain category.",
        "expected_clauses": ["6.3.2"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_006",
        "question": "What is the formula for design wind pressure?",
        "expected_answer": "Design wind pressure pz = 0.6 × Vz², where Vz is the design wind speed in m/s and pz is in N/m².",
        "expected_clauses": ["7.2"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_007",
        "question": "How many terrain categories are defined in IS 875 Part 3?",
        "expected_answer": "IS 875 Part 3 defines four terrain categories (Category 1 to Category 4).",
        "expected_clauses": ["6.3.2.1"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_008",
        "question": "What does terrain category 1 represent?",
        "expected_answer": "Terrain Category 1 represents open sea coasts, flat plains, or open land with very few obstructions.",
        "expected_clauses": ["6.3.2.1"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_009",
        "question": "What is the k3 factor in wind load calculation?",
        "expected_answer": "k3 is the topography factor that accounts for the effect of local topography such as hills and cliffs on wind speed.",
        "expected_clauses": ["6.3.3"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_010",
        "question": "What is the design wind pressure for a building at 10m height in terrain category 2 with Vb = 47 m/s?",
        "expected_answer": "First compute Vz = 47 × k1 × k2 × k3. For TC2 at 10m, k2 ≈ 1.00, k1=1, k3=1 → Vz ≈ 47 m/s. pz = 0.6 × 47² ≈ 1325 N/m².",
        "expected_clauses": ["6.3", "7.2", "Table 2"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_011",
        "question": "What is the internal pressure coefficient for a building with medium permeability?",
        "expected_answer": "For buildings with medium permeability, the internal pressure coefficient Cpi is ±0.5.",
        "expected_clauses": ["7.3.2"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_012",
        "question": "What is the wind pressure on a wall with Cp external = +0.7 and Cp internal = -0.5?",
        "expected_answer": "Net pressure coefficient = Cpe - Cpi = 0.7 - (-0.5) = 1.2. Net wind pressure = 1.2 × pz.",
        "expected_clauses": ["7.3"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_013",
        "question": "What return period is used for normal structures in IS 875 Part 3?",
        "expected_answer": "A return period of 50 years is used for normal permanent structures.",
        "expected_clauses": ["6.3.1"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_014",
        "question": "What is the basic wind speed for Delhi?",
        "expected_answer": "The basic wind speed for Delhi is 47 m/s.",
        "expected_clauses": ["Annex A"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_015",
        "question": "What is the k4 factor introduced in IS 875 Part 3 2015 edition?",
        "expected_answer": "k4 is the importance factor for cyclonic regions. For important structures in cyclone-prone areas, k4 = 1.15.",
        "expected_clauses": ["6.3.4"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },

    #  Multi-hop queries (across parts) 
    {
        "id": "mh_001",
        "question": "For a 10-storey RCC office building in Chennai, what are the key loads to consider from IS 875?",
        "expected_answer": "Dead load: RCC at 25 kN/m³ (Part 1). Imposed load: office floors at 2.5 kN/m² (Part 2). Wind load: Vb = 50 m/s for Chennai (Part 3).",
        "expected_clauses": ["Table 1", "6.3", "Annex A"],
        "part": "",
        "is_multi_hop": True,
    },
    {
        "id": "mh_002",
        "question": "How do dead loads and wind loads combine for a warehouse building?",
        "expected_answer": "Dead loads from materials (Part 1) are combined with wind pressures computed using the design wind speed (Part 3) per applicable load combinations.",
        "expected_clauses": ["3.1", "7.2"],
        "part": "",
        "is_multi_hop": True,
    },
    {
        "id": "mh_003",
        "question": "Compare the imposed roof loads and wind uplift for a flat roof in Mumbai.",
        "expected_answer": "Flat roof imposed load = 0.75 kN/m² (Part 2). Wind uplift depends on Vb = 44 m/s for Mumbai and roof pressure coefficients (Part 3).",
        "expected_clauses": ["4.1", "7.3", "Annex A"],
        "part": "",
        "is_multi_hop": True,
    },
    {
        "id": "mh_004",
        "question": "What total load acts on a residential floor slab including self-weight and imposed load?",
        "expected_answer": "Self-weight from RCC (Part 1, 25 kN/m³ × thickness) plus imposed load of 2.0 kN/m² for bedrooms (Part 2).",
        "expected_clauses": ["Table 1", "Table 1"],
        "part": "",
        "is_multi_hop": True,
    },
    {
        "id": "mh_005",
        "question": "For a school building in Kolkata, what basic wind speed and imposed floor load apply?",
        "expected_answer": "Basic wind speed for Kolkata is 50 m/s (Part 3). Imposed load for classrooms is 3.0 kN/m² (Part 2).",
        "expected_clauses": ["Annex A", "Table 1"],
        "part": "",
        "is_multi_hop": True,
    },

    # Additional Part 3 questions 
    {
        "id": "p3_016",
        "question": "What are the different wind zones defined in IS 875 Part 3?",
        "expected_answer": "IS 875 Part 3 defines six wind zones with basic wind speeds of 33, 39, 44, 47, 50, and 55 m/s.",
        "expected_clauses": ["Fig. 1", "5.2"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_017",
        "question": "What is terrain category 4 in IS 875 Part 3?",
        "expected_answer": "Terrain Category 4 represents large city centres with numerous closely spaced obstructions having heights generally exceeding 25 m.",
        "expected_clauses": ["6.3.2.1"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_018",
        "question": "What is the basic wind speed for Bangalore?",
        "expected_answer": "The basic wind speed for Bangalore is 33 m/s.",
        "expected_clauses": ["Annex A"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_019",
        "question": "What is gust factor and when is it applicable in IS 875 Part 3?",
        "expected_answer": "The gust factor method is used for dynamically sensitive structures. It accounts for the dynamic amplification of wind loads.",
        "expected_clauses": ["8"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p3_020",
        "question": "What is the wind pressure formula at height z?",
        "expected_answer": "pz = 0.6 Vz² N/m², where Vz is the design wind speed in m/s at height z.",
        "expected_clauses": ["7.2"],
        "part": "IS 875 Part 3 - Wind Loads",
        "is_multi_hop": False,
    },

    # Additional Part 1 and Part 2 
    {
        "id": "p1_011",
        "question": "What is the unit weight of sand (dry)?",
        "expected_answer": "The unit weight of dry sand is approximately 15.7 to 18.9 kN/m³.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p1_012",
        "question": "What is the unit weight of fly ash concrete?",
        "expected_answer": "Fly ash concrete has a unit weight typically of 19 to 22 kN/m³.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 1 - Dead Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_011",
        "question": "What is the imposed load for corridors and passages in public buildings?",
        "expected_answer": "Corridors and passages in public buildings carry an imposed load of 4.0 kN/m².",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_012",
        "question": "What is the live load for a library reading room?",
        "expected_answer": "The imposed load for library reading rooms is 3.0 kN/m².",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "p2_013",
        "question": "What is the imposed load for library stack rooms?",
        "expected_answer": "Library stack rooms have an imposed load of 6.0 to 10.0 kN/m² depending on shelf height.",
        "expected_clauses": ["Table 1"],
        "part": "IS 875 Part 2 - Imposed Loads",
        "is_multi_hop": False,
    },
    {
        "id": "mh_006",
        "question": "What is the total design load on a ground floor slab of a hospital building in Hyderabad including wind?",
        "expected_answer": "Dead load from RCC 25 kN/m³ (Part 1), imposed hospital floor load 3.0 kN/m² (Part 2), and wind load from Vb for Hyderabad (Part 3).",
        "expected_clauses": ["Table 1", "Table 1", "Annex A"],
        "part": "",
        "is_multi_hop": True,
    },
]


def generate_qa_file():
    output_path = QA_DIR / "qa_pairs.json"
    with open(output_path, "w") as f:
        json.dump(QA_PAIRS, f, indent=2)
    log.success(f"Generated {len(QA_PAIRS)} QA pairs → {output_path}")


if __name__ == "__main__":
    generate_qa_file()
