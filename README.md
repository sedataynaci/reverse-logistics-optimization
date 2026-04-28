# Reverse Logistics Optimization

## Overview
This project focuses on designing an optimized reverse logistics network to minimize total operational cost while considering environmental impact. The system models the flow of returned products and determines optimal facility locations, transportation routes, and capacity allocation using a Mixed-Integer Linear Programming (MILP) approach.

## Problem Definition
Increasing waste volumes and product returns create significant challenges in logistics systems, including:
- High transportation costs
- Inefficient routing
- Poor facility utilization
- Environmental impact (carbon emissions)

This project aims to develop a data-driven decision support model to address these issues.

## Methodology
The problem is modeled as a **Capacitated Facility Location Problem** and solved using MILP.

Key components:
- Facility location decisions
- Waste allocation and flow optimization
- Transportation cost minimization
- Environmental cost (carbon emissions)

Additionally, scenario analysis was conducted using Excel to evaluate different system configurations.

## Technologies Used
- **Python** (PuLP)
- **Microsoft Excel**
- **Optimization Modeling (MILP)**

## Model Features
- Multi-city logistics network
- Facility capacity constraints
- Transportation cost calculation (ton-km based)
- Carbon emission cost integration
- Scenario-based decision analysis

## Dataset
This project uses **synthetic and anonymized data** inspired by real-world logistics scenarios.  
No confidential company data is included.

## Results
The model provides:
- Optimal facility selection
- Efficient material flow distribution
- Reduced total system cost
- Improved logistics efficiency
- Environmentally conscious decision-making

## Project Structure
- `Thesis.py` → Optimization model implementation (Python)
- `report_clean_final.pdf` → Detailed project report
- `presentation.pdf` → Project presentation slides
- `Analysis.xlsx` → Scenario analysis and results

## Contributors
- Sedat Can Aynacı  
- Mehmet Okay Özaydın  
- Çağatay Onay  

## My Contribution
This project was developed as part of a team.  
I contributed to:
- Data analysis and preprocessing
- Model implementation in Python (PuLP)
- Evaluation and interpretation of optimization results

## How to Run
1. Install required libraries:
```bash
pip install pandas pulp matplotlib networkx
python Thesis.py
