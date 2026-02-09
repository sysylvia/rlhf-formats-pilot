#!/usr/bin/env python3
"""
Experiment Coordinator: Within-Subjects Design
Manages counterbalancing, randomization, and data collection
"""

import random
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import itertools

class ExperimentCoordinator:
    """
    Coordinates within-subjects experiment with counterbalancing
    """
    
    def __init__(self, 
                 n_labelers: int = 8,
                 n_prompts_per_format: int = 5,
                 prompts_file: str = 'prompts.json',
                 output_dir: str = 'experiment_data'):
        """
        Initialize experiment coordinator
        
        Args:
            n_labelers: Total number of labelers
            n_prompts_per_format: Prompts per format per labeler (5 means 15 total)
            prompts_file: JSON file with prompt data
            output_dir: Where to save experimental data
        """
        self.n_labelers = n_labelers
        self.n_prompts_per_format = n_prompts_per_format
        self.prompts_file = prompts_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Format types
        self.formats = ['pairwise', 'bws', 'peer_prediction']
        
        # Generate counterbalancing scheme
        self.format_orders = self._generate_format_orders()
        
        # Load prompts
        self.prompts = self._load_or_create_prompts()
        
        # Assign labelers to conditions
        self.labeler_assignments = self._assign_labelers()
        
    def _generate_format_orders(self) -> List[List[str]]:
        """
        Generate all possible format orderings (6 total for 3 formats)
        Using complete counterbalancing
        """
        return list(itertools.permutations(self.formats))
    
    def _load_or_create_prompts(self) -> List[Dict]:
        """
        Load prompts from file or create placeholder
        """
        prompts_path = Path(self.prompts_file)
        
        if prompts_path.exists():
            with open(prompts_path, 'r') as f:
                return json.load(f)
        else:
            # Create placeholder prompts
            print(f"⚠️  {self.prompts_file} not found. Creating placeholder prompts.")
            prompts = self._create_placeholder_prompts()
            
            # Save for future use
            with open(prompts_path, 'w') as f:
                json.dump(prompts, f, indent=2)
            
            print(f"✓ Created {len(prompts)} placeholder prompts in {self.prompts_file}")
            return prompts
    
    def _create_placeholder_prompts(self) -> List[Dict]:
        """
        Create placeholder prompts for testing
        """
        total_needed = self.n_labelers * self.n_prompts_per_format * len(self.formats)
        # Add 20% extra for flexibility
        total_prompts = int(total_needed * 1.2)
        
        prompts = []
        for i in range(total_prompts):
            prompts.append({
                'id': f'prompt_{i+1:03d}',
                'text': f'[Placeholder prompt {i+1}] This is a sample prompt text that would be replaced with actual RLHF prompts.',
                'responses': {
                    'A': f'Response A for prompt {i+1}',
                    'B': f'Response B for prompt {i+1}',
                    'C': f'Response C for prompt {i+1}',
                    'D': f'Response D for prompt {i+1}'
                },
                'metadata': {
                    'source': 'placeholder',
                    'difficulty': random.choice(['easy', 'medium', 'hard'])
                }
            })
        
        return prompts
    
    def _assign_labelers(self) -> List[Dict]:
        """
        Assign each labeler to a format order and prompts
        """
        assignments = []
        
        # Cycle through format orders to balance across labelers
        for labeler_id in range(1, self.n_labelers + 1):
            # Assign format order (cycle through all 6 orders)
            format_order = self.format_orders[(labeler_id - 1) % len(self.format_orders)]
            
            # Sample prompts for this labeler (15 prompts total, 5 per format)
            # Make sure no prompt is repeated for this labeler
            available_prompts = list(range(len(self.prompts)))
            random.shuffle(available_prompts)
            
            labeler_prompts = available_prompts[:self.n_prompts_per_format * 3]
            
            # Assign prompts to formats
            prompt_assignments = {}
            for i, format_name in enumerate(format_order):
                start_idx = i * self.n_prompts_per_format
                end_idx = start_idx + self.n_prompts_per_format
                prompt_assignments[format_name] = labeler_prompts[start_idx:end_idx]
            
            assignments.append({
                'labeler_id': labeler_id,
                'format_order': list(format_order),
                'prompt_assignments': prompt_assignments,
                'total_annotations': len(labeler_prompts)
            })
        
        return assignments
    
    def generate_labeler_sequence(self, labeler_id: int) -> Dict:
        """
        Generate complete annotation sequence for one labeler
        """
        assignment = self.labeler_assignments[labeler_id - 1]
        
        sequence = []
        annotation_number = 1
        
        for format_name in assignment['format_order']:
            prompt_indices = assignment['prompt_assignments'][format_name]
            
            for prompt_idx in prompt_indices:
                prompt = self.prompts[prompt_idx]
                
                sequence.append({
                    'annotation_number': annotation_number,
                    'format': format_name,
                    'prompt_id': prompt['id'],
                    'prompt_text': prompt['text'],
                    'responses': prompt['responses'],
                    'metadata': prompt.get('metadata', {})
                })
                
                annotation_number += 1
        
        return {
            'labeler_id': labeler_id,
            'format_order': assignment['format_order'],
            'sequence': sequence
        }
    
    def save_labeler_sequences(self):
        """
        Save all labeler sequences to files
        """
        sequences_dir = self.output_dir / 'labeler_sequences'
        sequences_dir.mkdir(exist_ok=True)
        
        for labeler_id in range(1, self.n_labelers + 1):
            sequence = self.generate_labeler_sequence(labeler_id)
            
            output_file = sequences_dir / f'labeler_{labeler_id:02d}_sequence.json'
            with open(output_file, 'w') as f:
                json.dump(sequence, f, indent=2)
            
            print(f"✓ Saved sequence for Labeler {labeler_id}: {output_file}")
    
    def generate_summary_report(self) -> str:
        """
        Generate experiment summary report
        """
        report = []
        report.append("="*60)
        report.append("EXPERIMENT SUMMARY")
        report.append("="*60)
        report.append(f"Design: Within-Subjects (Repeated Measures)")
        report.append(f"Total Labelers: {self.n_labelers}")
        report.append(f"Annotations per Labeler: {self.n_prompts_per_format * 3}")
        report.append(f"Prompts per Format: {self.n_prompts_per_format}")
        report.append(f"Total Annotations: {self.n_labelers * self.n_prompts_per_format * 3}")
        report.append("")
        
        report.append("FORMAT COUNTERBALANCING:")
        for i, order in enumerate(self.format_orders):
            count = sum(1 for a in self.labeler_assignments if tuple(a['format_order']) == order)
            report.append(f"  Order {i+1}: {' → '.join(order)} ({count} labelers)")
        report.append("")
        
        report.append("LABELER ASSIGNMENTS:")
        for assignment in self.labeler_assignments:
            report.append(f"  Labeler {assignment['labeler_id']:02d}: {' → '.join(assignment['format_order'])}")
        report.append("")
        
        report.append("ESTIMATED TIMING:")
        avg_time_per_annotation = 4  # minutes (rough estimate)
        total_time_per_labeler = avg_time_per_annotation * self.n_prompts_per_format * 3
        report.append(f"  Time per annotation: ~{avg_time_per_annotation} minutes")
        report.append(f"  Time per labeler: ~{total_time_per_labeler} minutes (~{total_time_per_labeler/60:.1f} hours)")
        report.append("")
        
        report.append("="*60)
        
        return "\n".join(report)
    
    def save_summary(self):
        """
        Save experiment summary to file
        """
        summary = self.generate_summary_report()
        
        output_file = self.output_dir / 'experiment_summary.txt'
        with open(output_file, 'w') as f:
            f.write(summary)
        
        print(summary)
        print(f"\n✓ Summary saved to: {output_file}")
    
    def generate_data_collection_template(self):
        """
        Generate CSV template for data collection
        """
        csv_file = self.output_dir / 'annotation_data_template.csv'
        
        fieldnames = [
            'labeler_id',
            'annotation_number',
            'format',
            'prompt_id',
            'choice',  # A/B for pairwise, best/worst for BWS, A/B for PP
            'prediction_pct',  # For PP only
            'confidence',
            'time_seconds',
            'timestamp',
            'notes'
        ]
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
        
        print(f"✓ Data collection template: {csv_file}")

def main():
    """
    Set up experiment
    """
    print("="*60)
    print("WITHIN-SUBJECTS EXPERIMENT SETUP")
    print("="*60)
    print()
    
    # Initialize coordinator
    coordinator = ExperimentCoordinator(
        n_labelers=8,
        n_prompts_per_format=5,
        prompts_file='prompts.json',
        output_dir='experiment_data'
    )
    
    # Save labeler sequences
    print("\nGenerating labeler sequences...")
    coordinator.save_labeler_sequences()
    
    # Generate summary
    print("\nGenerating experiment summary...")
    coordinator.save_summary()
    
    # Generate data template
    print("\nGenerating data collection template...")
    coordinator.generate_data_collection_template()
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review experiment_data/experiment_summary.txt")
    print("2. Check labeler_sequences/ directory")
    print("3. Load prompts.json with real RLHF data (or use placeholders for testing)")
    print("4. Deploy interfaces and start data collection")
    print()

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    main()
