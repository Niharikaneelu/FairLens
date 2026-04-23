"""
Generate Expected Results JSON File
Run this to create the expected_outputs.json for validation
"""

import json

def create_expected_results():
    results = {
        "hr_hiring_demo": {
            "bias_detected": True,
            "bias_types": ["gender"],
            "confidence": 0.92,
            "statistics": {
                "male_hiring_rate": 1.0,
                "female_hiring_rate": 0.0,
                "total_male": 30,
                "total_female": 30,
                "male_hired": 30,
                "female_hired": 0
            },
            "findings": [
                {
                    "category": "gender",
                    "observation": "All male candidates hired (100%), zero female candidates hired (0%)",
                    "evidence": "30 males hired out of 30, 0 females hired out of 30. Statistical significance: p < 0.001",
                    "severity": "high"
                }
            ],
            "explanation": "Severe gender bias detected. Male candidates were hired at 100% rate while female candidates with identical qualifications were not hired at all. This represents a clear pattern of gender discrimination.",
            "recommendations": [
                "Implement blind resume screening",
                "Standardize evaluation criteria",
                "Diverse hiring panels",
                "Regular bias audits"
            ],
            "fairness_score": 2.0
        },
        "loan_approval_demo": {
            "bias_detected": True,
            "bias_types": ["gender", "name_ethnicity"],
            "confidence": 0.88,
            "statistics": {
                "male_approval_rate": 1.0,
                "female_approval_rate": 0.0,
                "total_male": 25,
                "total_female": 25,
                "male_approved": 25,
                "female_approved": 0
            },
            "findings": [
                {
                    "category": "gender",
                    "observation": "All male applicants approved (100%), zero female applicants approved (0%)",
                    "evidence": "25 males approved, 0 females approved despite similar credit scores and income",
                    "severity": "high"
                },
                {
                    "category": "name_ethnicity",
                    "observation": "Western names show higher approval patterns",
                    "evidence": "Disparate approval rates between Western and ethnic names",
                    "severity": "medium"
                }
            ],
            "explanation": "Significant gender and name bias in loan approvals. Female applicants denied despite comparable financial profiles. Ethnic names face additional barriers.",
            "recommendations": [
                "Remove demographic data from initial review",
                "Automated underwriting based on financial metrics only",
                "Monthly disparity analysis",
                "Fair lending training"
            ],
            "fairness_score": 2.5
        },
        "college_admissions_demo": {
            "bias_detected": True,
            "bias_types": ["gender", "legacy_status"],
            "confidence": 0.85,
            "statistics": {
                "male_acceptance_rate": 0.83,
                "female_acceptance_rate": 0.0,
                "legacy_acceptance_rate": 1.0,
                "non_legacy_acceptance_rate": 0.43,
                "total_male": 30,
                "total_female": 30,
                "male_accepted": 25,
                "female_accepted": 0
            },
            "findings": [
                {
                    "category": "gender",
                    "observation": "Male acceptance rate 83% vs female 0%",
                    "evidence": "25 males accepted vs 0 females despite similar GPAs and SAT scores",
                    "severity": "high"
                },
                {
                    "category": "legacy_status",
                    "observation": "Legacy applicants accepted at 100% rate",
                    "evidence": "All 15 legacy students accepted regardless of other factors",
                    "severity": "high"
                }
            ],
            "explanation": "Multiple biases detected: gender bias against female applicants and strong legacy preference. Legacy status guarantees acceptance while equally qualified non-legacy and female applicants are rejected.",
            "recommendations": [
                "Blind admissions review",
                "Eliminate or reduce legacy preference",
                "Merit-based evaluation focus",
                "Demographic tracking and reporting"
            ],
            "fairness_score": 3.0
        }
    }
    
    return results

if __name__ == "__main__":
    results = create_expected_results()
    
    with open("expected_outputs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print("Expected outputs saved to expected_outputs.json")
    print("\nDatasets covered:")
    for dataset in results.keys():
        print(f"  - {dataset}")
