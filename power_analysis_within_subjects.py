#!/usr/bin/env python3
"""
Power Analysis: Within-Subjects (Repeated Measures) Design
Each labeler rates prompts in all 3 formats (randomized order)
"""

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from typing import Dict, List, Tuple
import pandas as pd

np.random.seed(42)
sns.set_style("whitegrid")
sns.set_palette("husl")

@dataclass
class WithinSubjectsConfig:
    """Configuration for within-subjects design"""
    name: str
    
    # Sample parameters
    n_labelers: int = 10  # Total labelers
    n_prompts_per_format: int = 5  # Prompts per format per labeler
    
    # Effect sizes (relative improvement over pairwise)
    bws_improvement: float = 0.30
    pp_improvement: float = 0.25
    
    # Variance components
    baseline_accuracy: float = 0.70
    between_labeler_sd: float = 0.12  # Individual differences (removed by within-design!)
    within_labeler_sd: float = 0.08   # Measurement noise (remains)
    
    # Learning/fatigue effects
    learning_effect: float = 0.02  # Improvement per 5 annotations (practice)
    fatigue_effect: float = -0.01  # Decline per 5 annotations (tiredness)
    
    # Statistical parameters
    alpha: float = 0.05
    bonferroni_correction: bool = True
    n_simulations: int = 10000

def simulate_within_subjects_experiment(config: WithinSubjectsConfig) -> Dict:
    """
    Simulate within-subjects design where each labeler uses all formats
    
    Design:
    - Each labeler completes n_prompts_per_format in each of 3 formats
    - Total per labeler: 3 × n_prompts_per_format annotations
    - Format order randomized per labeler
    - Prompt order randomized
    """
    
    total_annotations_per_labeler = config.n_prompts_per_format * 3
    
    # True accuracies for each format
    acc_pairwise = config.baseline_accuracy
    acc_bws = acc_pairwise * (1 + config.bws_improvement)
    acc_pp = acc_pairwise * (1 + config.pp_improvement)
    
    # Generate labeler-specific baseline abilities (individual differences)
    labeler_abilities = np.random.normal(0, config.between_labeler_sd, config.n_labelers)
    
    # For each labeler, simulate their performance in each format
    data = []
    
    for labeler_id in range(config.n_labelers):
        # This labeler's baseline ability
        ability = labeler_abilities[labeler_id]
        
        # Randomize format order for this labeler (counterbalancing)
        formats = ['pairwise', 'bws', 'pp']
        np.random.shuffle(formats)
        
        annotation_count = 0
        
        for format_name in formats:
            # True accuracy for this format
            if format_name == 'pairwise':
                true_acc = acc_pairwise
            elif format_name == 'bws':
                true_acc = acc_bws
            else:  # pp
                true_acc = acc_pp
            
            # Generate prompts for this format
            for prompt_num in range(config.n_prompts_per_format):
                annotation_count += 1
                
                # Learning and fatigue effects (based on total annotations so far)
                learning = config.learning_effect * (annotation_count / 5)
                fatigue = config.fatigue_effect * (annotation_count / 5)
                
                # Observed accuracy = true + labeler ability + learning + fatigue + noise
                observed_acc = (true_acc + ability + learning + fatigue + 
                               np.random.normal(0, config.within_labeler_sd))
                
                data.append({
                    'labeler_id': labeler_id,
                    'format': format_name,
                    'accuracy': observed_acc,
                    'annotation_num': annotation_count
                })
    
    df = pd.DataFrame(data)
    
    # Calculate mean accuracy per format per labeler (for paired tests)
    labeler_means = df.groupby(['labeler_id', 'format'])['accuracy'].mean().unstack()
    
    # Paired t-tests (within-subjects comparison)
    # BWS vs Pairwise
    bws_diff = labeler_means['bws'] - labeler_means['pairwise']
    t_stat_bws, p_value_bws = stats.ttest_1samp(bws_diff, 0)
    
    # PP vs Pairwise
    pp_diff = labeler_means['pp'] - labeler_means['pairwise']
    t_stat_pp, p_value_pp = stats.ttest_1samp(pp_diff, 0)
    
    # Apply Bonferroni correction
    alpha_threshold = config.alpha / 2 if config.bonferroni_correction else config.alpha
    
    detected_bws = (p_value_bws < alpha_threshold) and (t_stat_bws > 0)
    detected_pp = (p_value_pp < alpha_threshold) and (t_stat_pp > 0)
    detected_either = detected_bws or detected_pp
    detected_both = detected_bws and detected_pp
    
    return {
        'p_value_bws': p_value_bws,
        'p_value_pp': p_value_pp,
        'detected_bws': detected_bws,
        'detected_pp': detected_pp,
        'detected_either': detected_either,
        'detected_both': detected_both,
        'mean_diff_bws': bws_diff.mean(),
        'mean_diff_pp': pp_diff.mean()
    }

def run_within_subjects_power_analysis(config: WithinSubjectsConfig) -> Dict:
    """
    Run full power analysis for within-subjects design
    """
    total_annotations = config.n_labelers * config.n_prompts_per_format * 3
    
    print(f"\nRunning within-subjects power analysis: {config.name}")
    print(f"  Labelers: {config.n_labelers}")
    print(f"  Prompts per format per labeler: {config.n_prompts_per_format}")
    print(f"  Total annotations per labeler: {config.n_prompts_per_format * 3}")
    print(f"  Total annotations across all: {total_annotations}")
    print(f"  Effect sizes: BWS={config.bws_improvement:.1%}, PP={config.pp_improvement:.1%}")
    print(f"  Variance: Between-labeler SD={config.between_labeler_sd:.3f}, Within SD={config.within_labeler_sd:.3f}")
    
    results = []
    for i in range(config.n_simulations):
        result = simulate_within_subjects_experiment(config)
        results.append(result)
        
        if (i + 1) % 2000 == 0:
            power_bws = np.mean([r['detected_bws'] for r in results])
            power_pp = np.mean([r['detected_pp'] for r in results])
            print(f"  Progress: {i+1:,}/{config.n_simulations:,} (BWS: {power_bws:.1%}, PP: {power_pp:.1%})")
    
    df = pd.DataFrame(results)
    
    power_bws = df['detected_bws'].mean()
    power_pp = df['detected_pp'].mean()
    power_either = df['detected_either'].mean()
    power_both = df['detected_both'].mean()
    
    print(f"  ✓ Power to detect BWS: {power_bws:.1%}")
    print(f"  ✓ Power to detect PP: {power_pp:.1%}")
    print(f"  ✓ Power to detect at least one: {power_either:.1%}")
    print(f"  ✓ Power to detect both: {power_both:.1%}")
    
    return {
        'config': config,
        'power_bws': power_bws,
        'power_pp': power_pp,
        'power_either': power_either,
        'power_both': power_both,
        'total_annotations': total_annotations,
        'results_df': df
    }

def power_curves_n_labelers(base_config: WithinSubjectsConfig,
                             n_labelers_list: List[int]) -> pd.DataFrame:
    """
    Power curves varying number of labelers
    """
    print("\n" + "="*60)
    print("POWER CURVES: Number of Labelers")
    print("="*60)
    
    results = []
    for n in n_labelers_list:
        config = WithinSubjectsConfig(
            name=f"N={n}",
            n_labelers=n,
            n_prompts_per_format=base_config.n_prompts_per_format,
            bws_improvement=base_config.bws_improvement,
            pp_improvement=base_config.pp_improvement,
            baseline_accuracy=base_config.baseline_accuracy,
            between_labeler_sd=base_config.between_labeler_sd,
            within_labeler_sd=base_config.within_labeler_sd,
            learning_effect=base_config.learning_effect,
            fatigue_effect=base_config.fatigue_effect,
            bonferroni_correction=base_config.bonferroni_correction,
            n_simulations=5000
        )
        
        result = run_within_subjects_power_analysis(config)
        results.append({
            'n_labelers': n,
            'total_annotations': result['total_annotations'],
            'annotations_per_labeler': config.n_prompts_per_format * 3,
            'power_bws': result['power_bws'],
            'power_pp': result['power_pp'],
            'power_either': result['power_either']
        })
    
    return pd.DataFrame(results)

def power_curves_prompts_per_format(base_config: WithinSubjectsConfig,
                                     prompts_list: List[int]) -> pd.DataFrame:
    """
    Power curves varying prompts per format per labeler
    """
    print("\n" + "="*60)
    print("POWER CURVES: Prompts per Format")
    print("="*60)
    
    results = []
    for n_prompts in prompts_list:
        config = WithinSubjectsConfig(
            name=f"Prompts={n_prompts}",
            n_labelers=base_config.n_labelers,
            n_prompts_per_format=n_prompts,
            bws_improvement=base_config.bws_improvement,
            pp_improvement=base_config.pp_improvement,
            baseline_accuracy=base_config.baseline_accuracy,
            between_labeler_sd=base_config.between_labeler_sd,
            within_labeler_sd=base_config.within_labeler_sd,
            learning_effect=base_config.learning_effect,
            fatigue_effect=base_config.fatigue_effect,
            bonferroni_correction=base_config.bonferroni_correction,
            n_simulations=5000
        )
        
        result = run_within_subjects_power_analysis(config)
        results.append({
            'n_prompts_per_format': n_prompts,
            'total_annotations': result['total_annotations'],
            'annotations_per_labeler': n_prompts * 3,
            'power_bws': result['power_bws'],
            'power_pp': result['power_pp'],
            'power_either': result['power_either']
        })
    
    return pd.DataFrame(results)

def compare_designs(between_config, within_config) -> pd.DataFrame:
    """
    Compare between-subjects vs within-subjects power
    """
    print("\n" + "="*60)
    print("DESIGN COMPARISON: Between vs Within Subjects")
    print("="*60)
    
    # For fair comparison, match total annotations
    # Between: 30 labelers × 1 annotation each = 30 annotations (simplified)
    # Within: Fewer labelers but multiple annotations each
    
    results = []
    
    # Between-subjects (from earlier analysis)
    # Approximate based on previous runs - would need actual simulation
    results.append({
        'design': 'Between-Subjects',
        'n_labelers': 30,
        'annotations_per_labeler': 1,
        'total_annotations': 30,
        'power_bws': 0.60,  # From pairwise analysis
        'power_pp': 0.50,
        'power_either': 0.70,
        'cost_estimate': 1000
    })
    
    # Within-subjects
    within_result = run_within_subjects_power_analysis(within_config)
    results.append({
        'design': 'Within-Subjects',
        'n_labelers': within_config.n_labelers,
        'annotations_per_labeler': within_config.n_prompts_per_format * 3,
        'total_annotations': within_result['total_annotations'],
        'power_bws': within_result['power_bws'],
        'power_pp': within_result['power_pp'],
        'power_either': within_result['power_either'],
        'cost_estimate': within_config.n_labelers * 33 * 2  # Rough estimate
    })
    
    return pd.DataFrame(results)

def create_within_subjects_visualization(
    power_labelers: pd.DataFrame,
    power_prompts: pd.DataFrame,
    scenario_results: Dict,
    design_comparison: pd.DataFrame
):
    """
    Create visualizations for within-subjects design
    """
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    fig.suptitle('Within-Subjects Design Power Analysis\n(Each labeler rates prompts in all 3 formats)', 
                 fontsize=16, fontweight='bold')
    
    # 1. Power vs Number of Labelers
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(power_labelers['n_labelers'], power_labelers['power_bws'], 
             'o-', linewidth=2, markersize=8, label='BWS vs Pairwise')
    ax1.plot(power_labelers['n_labelers'], power_labelers['power_pp'], 
             's-', linewidth=2, markersize=8, label='PP vs Pairwise')
    ax1.plot(power_labelers['n_labelers'], power_labelers['power_either'], 
             '^-', linewidth=2, markersize=8, label='Detect Either', alpha=0.7)
    ax1.axhline(0.80, color='red', linestyle='--', linewidth=1, label='80% threshold')
    ax1.set_xlabel('Number of Labelers', fontsize=11)
    ax1.set_ylabel('Statistical Power', fontsize=11)
    ax1.set_title('A) Power vs Number of Labelers', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=9)
    ax1.set_ylim(0, 1)
    
    # 2. Power vs Prompts per Format
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(power_prompts['n_prompts_per_format'], power_prompts['power_bws'], 
             'o-', linewidth=2, markersize=8, label='BWS vs Pairwise')
    ax2.plot(power_prompts['n_prompts_per_format'], power_prompts['power_pp'], 
             's-', linewidth=2, markersize=8, label='PP vs Pairwise')
    ax2.axhline(0.80, color='red', linestyle='--', linewidth=1)
    ax2.set_xlabel('Prompts per Format per Labeler', fontsize=11)
    ax2.set_ylabel('Statistical Power', fontsize=11)
    ax2.set_title('B) Power vs Annotation Load', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=9)
    ax2.set_ylim(0, 1)
    
    # 3. Total Annotations vs Power
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(power_labelers['total_annotations'], power_labelers['power_bws'], 
             'o-', linewidth=2, markersize=8, label='BWS')
    ax3.plot(power_labelers['total_annotations'], power_labelers['power_pp'], 
             's-', linewidth=2, markersize=8, label='PP')
    ax3.axhline(0.80, color='red', linestyle='--', linewidth=1)
    ax3.set_xlabel('Total Annotations', fontsize=11)
    ax3.set_ylabel('Statistical Power', fontsize=11)
    ax3.set_title('C) Power vs Total Annotation Count', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=9)
    ax3.set_ylim(0, 1)
    
    # 4. Scenario Comparison
    ax4 = fig.add_subplot(gs[1, 0])
    scenario_names = list(scenario_results.keys())
    powers_bws = [scenario_results[s]['power_bws'] for s in scenario_names]
    powers_pp = [scenario_results[s]['power_pp'] for s in scenario_names]
    
    x = np.arange(len(scenario_names))
    width = 0.35
    
    bars1 = ax4.barh(x - width/2, powers_bws, width, label='BWS')
    bars2 = ax4.barh(x + width/2, powers_pp, width, label='PP')
    
    ax4.set_yticks(x)
    ax4.set_yticklabels(scenario_names)
    ax4.set_xlabel('Statistical Power', fontsize=11)
    ax4.set_title('D) Power Across Scenarios', fontsize=12, fontweight='bold')
    ax4.axvline(0.80, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax4.legend(fontsize=9)
    ax4.set_xlim(0, 1)
    
    for i, (p_bws, p_pp) in enumerate(zip(powers_bws, powers_pp)):
        ax4.text(p_bws + 0.02, i - width/2, f'{p_bws:.1%}', va='center', fontsize=9)
        ax4.text(p_pp + 0.02, i + width/2, f'{p_pp:.1%}', va='center', fontsize=9)
    
    # 5. Between vs Within Design Comparison
    ax5 = fig.add_subplot(gs[1, 1])
    x = np.arange(len(design_comparison))
    width = 0.25
    
    ax5.bar(x - width, design_comparison['power_bws'], width, label='BWS', alpha=0.8)
    ax5.bar(x, design_comparison['power_pp'], width, label='PP', alpha=0.8)
    ax5.bar(x + width, design_comparison['power_either'], width, label='Either', alpha=0.8)
    
    ax5.set_xticks(x)
    ax5.set_xticklabels(design_comparison['design'])
    ax5.set_ylabel('Statistical Power', fontsize=11)
    ax5.set_title('E) Between vs Within Design', fontsize=12, fontweight='bold')
    ax5.axhline(0.80, color='red', linestyle='--', linewidth=1, label='80%')
    ax5.legend(fontsize=9)
    ax5.set_ylim(0, 1)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. Efficiency: Power per Labeler
    ax6 = fig.add_subplot(gs[1, 2])
    efficiency_bws = power_labelers['power_bws'] / power_labelers['n_labelers']
    efficiency_pp = power_labelers['power_pp'] / power_labelers['n_labelers']
    
    ax6.plot(power_labelers['n_labelers'], efficiency_bws, 
             'o-', linewidth=2, markersize=8, label='BWS efficiency')
    ax6.plot(power_labelers['n_labelers'], efficiency_pp, 
             's-', linewidth=2, markersize=8, label='PP efficiency')
    ax6.set_xlabel('Number of Labelers', fontsize=11)
    ax6.set_ylabel('Power per Labeler', fontsize=11)
    ax6.set_title('F) Statistical Efficiency', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    ax6.legend(fontsize=9)
    
    plt.tight_layout()
    
    output_path = 'power_curves_within_subjects.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Within-subjects visualization saved: {output_path}")
    
    return fig

def main():
    """
    Run complete within-subjects power analysis
    """
    print("="*60)
    print("WITHIN-SUBJECTS DESIGN POWER ANALYSIS")
    print("Each labeler rates prompts in all 3 formats")
    print("="*60)
    
    # Scenarios
    scenarios = {
        'Conservative': WithinSubjectsConfig(
            name="Conservative (15% improvement)",
            n_labelers=10,
            n_prompts_per_format=5,
            bws_improvement=0.15,
            pp_improvement=0.12,
            between_labeler_sd=0.15,
            within_labeler_sd=0.10,
            n_simulations=10000
        ),
        'Moderate': WithinSubjectsConfig(
            name="Moderate (30% improvement)",
            n_labelers=10,
            n_prompts_per_format=5,
            bws_improvement=0.30,
            pp_improvement=0.25,
            between_labeler_sd=0.12,
            within_labeler_sd=0.08,
            n_simulations=10000
        ),
        'Optimistic': WithinSubjectsConfig(
            name="Optimistic (50% improvement)",
            n_labelers=10,
            n_prompts_per_format=5,
            bws_improvement=0.50,
            pp_improvement=0.40,
            between_labeler_sd=0.10,
            within_labeler_sd=0.06,
            n_simulations=10000
        )
    }
    
    # Run scenarios
    print("\n" + "="*60)
    print("SCENARIO ANALYSIS")
    print("="*60)
    
    scenario_results = {}
    for name, config in scenarios.items():
        result = run_within_subjects_power_analysis(config)
        scenario_results[name] = result
    
    # Power curves
    n_labelers_list = [5, 6, 7, 8, 10, 12, 15, 20]
    power_labelers = power_curves_n_labelers(scenarios['Moderate'], n_labelers_list)
    
    prompts_list = [3, 4, 5, 6, 7, 8, 10]
    power_prompts = power_curves_prompts_per_format(scenarios['Moderate'], prompts_list)
    
    # Design comparison
    design_comparison = compare_designs(None, scenarios['Moderate'])
    
    # Create visualizations
    fig = create_within_subjects_visualization(
        power_labelers,
        power_prompts,
        scenario_results,
        design_comparison
    )
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nOutputs:")
    print("  - power_curves_within_subjects.png (6-panel visualization)")
    
    return scenario_results, power_labelers, power_prompts, design_comparison

if __name__ == "__main__":
    results = main()
