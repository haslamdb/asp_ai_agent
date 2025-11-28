#!/usr/bin/env python3
"""
Utility script to add expert knowledge from various sources
Supports CSV (Google Forms export) and JSON formats
"""

import sys
import csv
import json
import uuid
from pathlib import Path
from expert_knowledge_rag import ExpertKnowledgeRAG, ExpertCorrection, ExpertExemplar


def add_corrections_from_csv(csv_file: str):
    """
    Add corrections from Google Form CSV export

    Expected columns:
    - Timestamp
    - Expert Name
    - Module ID
    - Scenario ID
    - Difficulty Level
    - Competency Area
    - User Response
    - AI Feedback
    - Expert Correction
    - Expert Reasoning
    - What AI Missed (comma-separated)
    - What AI Did Well (comma-separated)
    """
    expert_rag = ExpertKnowledgeRAG()
    added_count = 0
    errors = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    correction = ExpertCorrection(
                        correction_id=str(uuid.uuid4()),
                        module_id=row['Module ID'].strip(),
                        scenario_id=row['Scenario ID'].strip(),
                        difficulty_level=row['Difficulty Level'].strip().lower(),
                        competency_area=row['Competency Area'].strip(),
                        user_response=row['User Response'].strip(),
                        ai_feedback_original=row['AI Feedback'].strip(),
                        expert_correction=row['Expert Correction'].strip(),
                        expert_reasoning=row.get('Expert Reasoning', '').strip(),
                        expert_name=row.get('Expert Name', 'Unknown').strip(),
                        what_ai_missed=[x.strip() for x in row.get('What AI Missed', '').split(',') if x.strip()],
                        what_ai_did_well=[x.strip() for x in row.get('What AI Did Well', '').split(',') if x.strip()]
                    )

                    expert_rag.add_correction(correction)
                    added_count += 1
                    print(f"✓ Row {row_num}: Added correction from {correction.expert_name}")

                except KeyError as e:
                    error_msg = f"Row {row_num}: Missing required column: {e}"
                    errors.append(error_msg)
                    print(f"✗ {error_msg}")
                except Exception as e:
                    error_msg = f"Row {row_num}: Error - {e}"
                    errors.append(error_msg)
                    print(f"✗ {error_msg}")

    except FileNotFoundError:
        print(f"Error: File not found: {csv_file}")
        return 0
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return 0

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Successfully added: {added_count} corrections")
    print(f"  Errors: {len(errors)}")
    if errors:
        print(f"\nError details:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    print(f"{'='*60}")

    return added_count


def add_exemplars_from_json(json_file: str):
    """
    Add exemplar responses from JSON file

    JSON format:
    [
        {
            "module_id": "cicu_prolonged_antibiotics",
            "scenario_id": "cicu_beginner_data_analysis",
            "difficulty_level": "beginner",
            "mastery_level": "exemplary",
            "response_text": "...",
            "expert_commentary": "...",
            "what_makes_it_good": [...],
            "what_would_improve": [...],
            "competency_scores": {...},
            "expert_name": "..."
        }
    ]
    """
    expert_rag = ExpertKnowledgeRAG()
    added_count = 0
    errors = []

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            exemplars_data = json.load(f)

        if not isinstance(exemplars_data, list):
            print("Error: JSON file should contain an array of exemplars")
            return 0

        for idx, data in enumerate(exemplars_data, 1):
            try:
                exemplar = ExpertExemplar(
                    exemplar_id=str(uuid.uuid4()),
                    module_id=data['module_id'],
                    scenario_id=data['scenario_id'],
                    difficulty_level=data['difficulty_level'],
                    mastery_level=data['mastery_level'],
                    response_text=data['response_text'],
                    expert_commentary=data.get('expert_commentary', ''),
                    what_makes_it_good=data.get('what_makes_it_good', []),
                    what_would_improve=data.get('what_would_improve', []),
                    competency_scores=data.get('competency_scores', {}),
                    expert_name=data.get('expert_name', 'Unknown')
                )

                expert_rag.add_exemplar(exemplar)
                added_count += 1
                print(f"✓ Exemplar {idx}: Added {exemplar.mastery_level} response")

            except KeyError as e:
                error_msg = f"Exemplar {idx}: Missing required field: {e}"
                errors.append(error_msg)
                print(f"✗ {error_msg}")
            except Exception as e:
                error_msg = f"Exemplar {idx}: Error - {e}"
                errors.append(error_msg)
                print(f"✗ {error_msg}")

    except FileNotFoundError:
        print(f"Error: File not found: {json_file}")
        return 0
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return 0
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return 0

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Successfully added: {added_count} exemplars")
    print(f"  Errors: {len(errors)}")
    if errors:
        print(f"\nError details:")
        for error in errors[:10]:
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    print(f"{'='*60}")

    return added_count


def create_sample_csv_template(output_file: str = "expert_corrections_template.csv"):
    """Create a sample CSV template for expert corrections"""
    headers = [
        "Timestamp",
        "Expert Name",
        "Module ID",
        "Scenario ID",
        "Difficulty Level",
        "Competency Area",
        "User Response",
        "AI Feedback",
        "Expert Correction",
        "Expert Reasoning",
        "What AI Missed",
        "What AI Did Well"
    ]

    sample_row = [
        "2025-01-16 10:30:00",
        "Dr. Sarah Martinez",
        "cicu_prolonged_antibiotics",
        "cicu_beginner_data_analysis",
        "beginner",
        "data_analysis",
        "We should reduce antibiotic use by tracking DOT",
        "Good approach. Tracking DOT is appropriate.",
        "You identified the problem but didn't specify HOW to calculate DOT. Provide the formula: DOT/1000 patient-days = (total antibiotic days / total patient days) × 1000",
        "Fellows need concrete formulas, not just concepts",
        "Requiring specific formula, Asking for benchmark source",
        "Acknowledged correct direction"
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(sample_row)

    print(f"✓ Created sample CSV template: {output_file}")
    print(f"  Edit this file and use: python add_expert_knowledge.py corrections {output_file}")


def create_sample_json_template(output_file: str = "expert_exemplars_template.json"):
    """Create a sample JSON template for exemplar responses"""
    sample_exemplars = [
        {
            "module_id": "cicu_prolonged_antibiotics",
            "scenario_id": "cicu_beginner_data_analysis",
            "difficulty_level": "beginner",
            "mastery_level": "exemplary",
            "response_text": "To analyze CICU antibiotic use, I would calculate DOT/1000 patient-days using the formula: (Total antibiotic days / Total patient days) × 1000. For example, if we had 450 meropenem days and 1000 total patient days, that's 450 DOT/1000 PD. I'd compare this to NHSN PICU benchmark of ~380 DOT/1000 PD, showing we're 70 days above benchmark.",
            "expert_commentary": "This response demonstrates exemplary data analysis with specific formulas, actual calculations, and appropriate benchmark selection.",
            "what_makes_it_good": [
                "Provided actual DOT formula",
                "Calculated specific numbers",
                "Named specific benchmark source (NHSN)",
                "Quantified the gap"
            ],
            "what_would_improve": [
                "Could add visualization plan",
                "Could mention risk-adjustment"
            ],
            "competency_scores": {
                "data_analysis": 5,
                "clinical_decision_making": 4
            },
            "expert_name": "Dr. Sarah Martinez"
        }
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_exemplars, f, indent=2)

    print(f"✓ Created sample JSON template: {output_file}")
    print(f"  Edit this file and use: python add_expert_knowledge.py exemplars {output_file}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Expert Knowledge Import Utility")
        print("=" * 60)
        print("\nUsage:")
        print("  python add_expert_knowledge.py corrections <csv_file>")
        print("  python add_expert_knowledge.py exemplars <json_file>")
        print("  python add_expert_knowledge.py template-csv [output_file]")
        print("  python add_expert_knowledge.py template-json [output_file]")
        print("\nExamples:")
        print("  python add_expert_knowledge.py corrections expert_reviews.csv")
        print("  python add_expert_knowledge.py exemplars cicu_exemplars.json")
        print("  python add_expert_knowledge.py template-csv")
        print("  python add_expert_knowledge.py template-json")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'corrections':
        if len(sys.argv) < 3:
            print("Error: Please specify CSV file")
            print("Usage: python add_expert_knowledge.py corrections <csv_file>")
            sys.exit(1)
        csv_file = sys.argv[2]
        print(f"Importing expert corrections from: {csv_file}\n")
        add_corrections_from_csv(csv_file)

    elif command == 'exemplars':
        if len(sys.argv) < 3:
            print("Error: Please specify JSON file")
            print("Usage: python add_expert_knowledge.py exemplars <json_file>")
            sys.exit(1)
        json_file = sys.argv[2]
        print(f"Importing exemplar responses from: {json_file}\n")
        add_exemplars_from_json(json_file)

    elif command == 'template-csv':
        output_file = sys.argv[2] if len(sys.argv) > 2 else "expert_corrections_template.csv"
        create_sample_csv_template(output_file)

    elif command == 'template-json':
        output_file = sys.argv[2] if len(sys.argv) > 2 else "expert_exemplars_template.json"
        create_sample_json_template(output_file)

    else:
        print(f"Unknown command: {command}")
        print("Valid commands: corrections, exemplars, template-csv, template-json")
        sys.exit(1)


if __name__ == "__main__":
    main()
