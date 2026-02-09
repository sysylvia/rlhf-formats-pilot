#!/usr/bin/env python3
"""
Power Analysis: Pairwise Comparisons vs. Standard of Care
Testing BWS vs Pairwise and PP vs Pairwise with Bonferroni correction
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
class PairwiseConfig:
    """Configuration for pairwise comparison design"""
    name: str
    
    # Sample sizes
    n_pairwise: int = 10  # Standard of care (control)
    n_bws: int = 10       # Best-worst scaling
    n_pp: int = 10        # Peer prediction
    
    # Effect sizes (relative improvement over pairwise baseline)
    bws_improvement: float = 0.30
    pp_improvement: float = 0.25
    
    # Noise parameters
    baseline_accuracy: float = 0.70
    noise_std: float = 0.15
    
    # Statistical parameters
    alpha: float = 0.05
    bonferroni_correction: bool = True  # Correct for 2 comparisons
    n_simulations: int = 10000

def simulate_pairwise_comparisons(config: PairwiseConfig) -> Dict:
    """
    Simulate one experiment with two pairwise comparisons:
    1. BWS vs Pairwise
    2. PP vs Pairwise
    
    Returns detection status for each comparison
    """
    # True underlying accuracies
    acc_pairwise = config.baseline_accuracy
    acc_bws = acc_pairwise * (1 + config.bws_improvement)
    acc_pp = acc_pairwise * (1 + config.pp_improvement)
    
    # Simulate measured accuracies
    results_pairwise = np.random.normal(acc_pairwise, config.noise_std, config.n_pairwise)
    results_bws = np.random.normal(acc_bws, config.noise_std, config.n_bws)
    results_pp = np.random.normal(acc_pp, config.noise_std, config.n_pp)
    
    # Two-sample t-tests
    # Comparison 1: BWS vs Pairwise
    t_stat_bws, p_value_bws = stats.ttest_ind(results_bws, results_pairwise)
    
    # Comparison 2: PP vs Pairwise  
    t_stat_pp, p_value_pp = stats.ttest_ind(results_pp, results_pairwise)
    
    # Apply Bonferroni correction if requested
    alpha_threshold = config.alpha / 2 if config.bonferroni_correction else config.alpha
    
    detected_bws = (p_value_bws < alpha_threshold) and (t_stat_bws > 0)  # BWS better
    detected_pp = (p_value_pp < alpha_threshold) and (t_stat_pp > 0)    # PP better
    detected_either = detected_bws or detected_pp
    detected_both = detected_bws and detected_pp
    
    return {
        'p_value_bws': p_value_bws,
        'p_value_pp': p_value_pp,
        'detected_bws': detected_bws,
        'detected_pp': detected_pp,
        'detected_either': detected_either,
        'detected_both': detected_both
    }

def run_pairwise_power_analysis(config: PairwiseConfig) -> Dict:
    """
    Run full power analysis for pairwise comparison design
    """
    print(f"\nRunning pairwise power analysis: {config.name}")
    print(f"  Sample sizes: {config.n_pairwise} Pairwise, {config.n_bws} BWS, {config.n_pp} PP")
    print(f"  Effect sizes: BWS={config.bws_improvement:.1%}, PP={config.pp_improvement:.1%}")
    print(f"  Bonferroni correction: {config.bonferroni_correction}")
    
    results = []
    for i in range(config.n_simulations):
        result = simulate_pairwise_comparisons(config)
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
        'results_df': df
    }

def power_curves_sample_size(base_config: PairwiseConfig,
                              sample_sizes: List[int],
                              allocation: str = 'equal') -> pd.DataFrame:
    """
    Generate power curves varying sample size
    
    allocation options:
    - 'equal': All 3 arms get same N
    - 'control_2x': Control arm gets 2× the sample size of treatment arms
    - 'control_only': Vary control, keep treatments at 10
    """
    print("\n" + "="*60)
    print(f"POWER CURVES: Sample Size (allocation={allocation})")
    print("="*60)
    
    results = []
    for n in sample_sizes:
        if allocation == 'equal':
            n_pairwise = n_bws = n_pp = n
        elif allocation == 'control_2x':
            n_pairwise = 2 * n
            n_bws = n_pp = n
        elif allocation == 'control_only':
            n_pairwise = n
            n_bws = n_pp = 10
        
        config = PairwiseConfig(
            name=f"N={n}",
            n_pairwise=n_pairwise,
            n_bws=n_bws,
            n_pp=n_pp,
            bws_improvement=base_config.bws_improvement,
            pp_improvement=base_config.pp_improvement,
            baseline_accuracy=base_config.baseline_accuracy,
            noise_std=base_config.noise_std,
            bonferroni_correction=base_config.bonferroni_correction,
            n_simulations=5000
        )
        
        result = run_pairwise_power_analysis(config)
        results.append({
            'sample_size_param': n,
            'n_pairwise': n_pairwise,
            'n_bws': n_bws,
            'n_pp': n_pp,
            'total_n': n_pairwise + n_bws + n_pp,
            'power_bws': result['power_bws'],
            'power_pp': result['power_pp'],
            'power_either': result['power_either'],
            'power_both': result['power_both']
        })
    
    return pd.DataFrame(results)

def power_curves_effect_size(base_config: PairwiseConfig,
                              effect_sizes: List[float]) -> pd.DataFrame:
    """
    Generate power curves varying effect size (BWS improvement)
    """
    print("\n" + "="*60)
    print("POWER CURVES: Effect Size")
    print("="*60)
    
    results = []
    for effect in effect_sizes:
        config = PairwiseConfig(
            name=f"Effect={effect:.1%}",
            n_pairwise=base_config.n_pairwise,
            n_bws=base_config.n_bws,
            n_pp=base_config.n_pp,
            bws_improvement=effect,
            pp_improvement=effect * 0.8,  # PP slightly less
            baseline_accuracy=base_config.baseline_accuracy,
            noise_std=base_config.noise_std,
            bonferroni_correction=base_config.bonferroni_correction,
            n_simulations=5000
        )
        
        result = run_pairwise_power_analysis(config)
        results.append({
            'effect_size': effect,
            'power_bws': result['power_bws'],
            'power_pp': result['power_pp'],
            'power_either': result['power_either'],
            'power_both': result['power_both']
        })
    
    return pd.DataFrame(results)

def create_power_curves_visualization(
    power_sample_equal: pd.DataFrame,
    power_sample_control2x: pd.DataFrame,
    power_effect: pd.DataFrame,
    scenario_results: Dict
):
    """
    Create comprehensive power curves visualization
    """
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    fig.suptitle('Power Analysis: Pairwise Comparisons vs. Standard of Care', 
                 fontsize=16, fontweight='bold')
    
    # 1. Power vs Sample Size (Equal Allocation)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(power_sample_equal['sample_size_param'], 
             power_sample_equal['power_bws'], 
             'o-', linewidth=2, markersize=8, label='BWS vs Pairwise')
    ax1.plot(power_sample_equal['sample_size_param'], 
             power_sample_equal['power_pp'], 
             's-', linewidth=2, markersize=8, label='PP vs Pairwise')
    ax1.plot(power_sample_equal['sample_size_param'], 
             power_sample_equal['power_either'], 
             '^-', linewidth=2, markersize=8, label='Detect Either', alpha=0.7)
    ax1.axhline(0.80, color='red', linestyle='--', linewidth=1, label='80% threshold')
    ax1.set_xlabel('Sample Size per Arm', fontsize=11)
    ax1.set_ylabel('Statistical Power', fontsize=11)
    ax1.set_title('A) Power vs Sample Size (Equal Allocation)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower right', fontsize=9)
    ax1.set_ylim(0, 1)
    
    # 2. Power vs Sample Size (2:1 Control Allocation)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(power_sample_control2x['sample_size_param'], 
             power_sample_control2x['power_bws'], 
             'o-', linewidth=2, markersize=8, label='BWS vs Pairwise')
    ax2.plot(power_sample_control2x['sample_size_param'], 
             power_sample_control2x['power_pp'], 
             's-', linewidth=2, markersize=8, label='PP vs Pairwise')
    ax2.axhline(0.80, color='red', linestyle='--', linewidth=1, label='80% threshold')
    ax2.set_xlabel('Sample Size per Treatment Arm (Control = 2×)', fontsize=11)
    ax2.set_ylabel('Statistical Power', fontsize=11)
    ax2.set_title('B) Power vs Sample Size (2:1 Allocation)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='lower right', fontsize=9)
    ax2.set_ylim(0, 1)
    
    # 3. Power vs Effect Size
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(power_effect['effect_size'] * 100, 
             power_effect['power_bws'], 
             'o-', linewidth=2, markersize=8, label='BWS vs Pairwise', color='darkorange')
    ax3.plot(power_effect['effect_size'] * 100, 
             power_effect['power_pp'], 
             's-', linewidth=2, markersize=8, label='PP vs Pairwise', color='darkgreen')
    ax3.axhline(0.80, color='red', linestyle='--', linewidth=1)
    ax3.set_xlabel('BWS Improvement over Pairwise (%)', fontsize=11)
    ax3.set_ylabel('Statistical Power', fontsize=11)
    ax3.set_title('C) Power vs Effect Size (N=10 per arm)', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=9)
    ax3.set_ylim(0, 1)
    
    # 4. Scenario Comparison (BWS)
    ax4 = fig.add_subplot(gs[1, 1])
    scenario_names = list(scenario_results.keys())
    powers_bws = [scenario_results[s]['power_bws'] for s in scenario_names]
    powers_pp = [scenario_results[s]['power_pp'] for s in scenario_names]
    
    x = np.arange(len(scenario_names))
    width = 0.35
    
    bars1 = ax4.barh(x - width/2, powers_bws, width, label='BWS vs Pairwise')
    bars2 = ax4.barh(x + width/2, powers_pp, width, label='PP vs Pairwise')
    
    ax4.set_yticks(x)
    ax4.set_yticklabels(scenario_names)
    ax4.set_xlabel('Statistical Power', fontsize=11)
    ax4.set_title('D) Power Across Scenarios (N=10/arm)', fontsize=12, fontweight='bold')
    ax4.axvline(0.80, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax4.legend(fontsize=9)
    ax4.set_xlim(0, 1)
    
    # Add power values
    for i, (p_bws, p_pp) in enumerate(zip(powers_bws, powers_pp)):
        ax4.text(p_bws + 0.02, i - width/2, f'{p_bws:.1%}', va='center', fontsize=9)
        ax4.text(p_pp + 0.02, i + width/2, f'{p_pp:.1%}', va='center', fontsize=9)
    
    # 5. Total Cost vs Power (Equal Allocation)
    ax5 = fig.add_subplot(gs[2, 0])
    cost_per_labeler = 33  # $15/hr × 2.2 hours
    costs = power_sample_equal['total_n'] * cost_per_labeler
    
    ax5.plot(costs, power_sample_equal['power_bws'], 
             'o-', linewidth=2, markersize=8, label='BWS vs Pairwise')
    ax5.plot(costs, power_sample_equal['power_pp'], 
             's-', linewidth=2, markersize=8, label='PP vs Pairwise')
    ax5.axhline(0.80, color='red', linestyle='--', linewidth=1)
    ax5.set_xlabel('Total Study Cost ($)', fontsize=11)
    ax5.set_ylabel('Statistical Power', fontsize=11)
    ax5.set_title('E) Power vs Cost (Equal Allocation)', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.legend(fontsize=9)
    ax5.set_ylim(0, 1)
    
    # Annotate budget point
    ax5.plot(1000, power_sample_equal[power_sample_equal['sample_size_param']==10]['power_bws'].values[0],
             'r*', markersize=15)
    ax5.text(1000, 0.65, 'Planned\nbudget', ha='center', fontsize=9, color='red')
    
    # 6. Sample Size Efficiency Comparison
    ax6 = fig.add_subplot(gs[2, 1])
    
    # For 80% power, what sample sizes needed?
    target_power = 0.80
    
    # Equal allocation
    equal_80_bws = power_sample_equal[power_sample_equal['power_bws'] >= target_power]
    equal_n_bws = equal_80_bws['total_n'].min() if len(equal_80_bws) > 0 else np.nan
    
    # 2:1 allocation
    control2x_80_bws = power_sample_control2x[power_sample_control2x['power_bws'] >= target_power]
    control2x_n_bws = control2x_80_bws['total_n'].min() if len(control2x_80_bws) > 0 else np.nan
    
    allocations = ['Equal\n(1:1:1)', '2:1\n(Control:Treatment)']
    total_ns = [equal_n_bws, control2x_n_bws]
    
    bars = ax6.bar(allocations, total_ns, color=['steelblue', 'orange'])
    ax6.set_ylabel('Total Sample Size for 80% Power', fontsize=11)
    ax6.set_title('F) Sample Size Efficiency by Allocation', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # Add values on bars
    for bar, val in zip(bars, total_ns):
        if not np.isnan(val):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2, height + 1,
                    f'{int(val)}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    output_path = 'power_curves_pairwise.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Power curves visualization saved: {output_path}")
    
    return fig

def main():
    """
    Run complete pairwise comparison power analysis
    """
    print("="*60)
    print("POWER ANALYSIS: Pairwise Comparisons")
    print("BWS vs Pairwise + PP vs Pairwise (Bonferroni corrected)")
    print("="*60)
    
    # Scenarios
    scenarios = {
        'Conservative': PairwiseConfig(
            name="Conservative (15% improvement)",
            bws_improvement=0.15,
            pp_improvement=0.12,
            noise_std=0.20,
            n_simulations=10000
        ),
        'Moderate': PairwiseConfig(
            name="Moderate (30% improvement)",
            bws_improvement=0.30,
            pp_improvement=0.25,
            noise_std=0.15,
            n_simulations=10000
        ),
        'Optimistic': PairwiseConfig(
            name="Optimistic (50% improvement)",
            bws_improvement=0.50,
            pp_improvement=0.40,
            noise_std=0.10,
            n_simulations=10000
        )
    }
    
    # Run scenarios
    print("\n" + "="*60)
    print("SCENARIO ANALYSIS")
    print("="*60)
    
    scenario_results = {}
    for name, config in scenarios.items():
        result = run_pairwise_power_analysis(config)
        scenario_results[name] = result
    
    # Power curves: Sample size (equal allocation)
    sample_sizes = [5, 8, 10, 12, 15, 20, 25, 30]
    power_sample_equal = power_curves_sample_size(
        scenarios['Moderate'], 
        sample_sizes, 
        allocation='equal'
    )
    
    # Power curves: Sample size (2:1 control allocation)
    power_sample_control2x = power_curves_sample_size(
        scenarios['Moderate'], 
        sample_sizes, 
        allocation='control_2x'
    )
    
    # Power curves: Effect size
    effect_sizes = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    power_effect = power_curves_effect_size(scenarios['Moderate'], effect_sizes)
    
    # Create visualizations
    fig = create_power_curves_visualization(
        power_sample_equal,
        power_sample_control2x,
        power_effect,
        scenario_results
    )
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nOutputs:")
    print("  - power_curves_pairwise.png (6-panel visualization)")
    
    return scenario_results, power_sample_equal, power_sample_control2x, power_effect

if __name__ == "__main__":
    results = main()
