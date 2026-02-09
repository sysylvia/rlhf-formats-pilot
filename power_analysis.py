#!/usr/bin/env python3
"""
Power Analysis for RLHF Elicitation Format Comparison
Simulates different scenarios to estimate required sample sizes and expected effect detection
"""

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from typing import Dict, List, Tuple
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

# Styling
sns.set_style("whitegrid")
sns.set_palette("husl")

@dataclass
class ExperimentConfig:
    """Configuration for one experimental scenario"""
    name: str
    n_prompts: int = 100
    n_labelers_per_format: int = 10
    
    # Effect sizes (relative improvement over pairwise baseline)
    bws_improvement: float = 0.30  # Best-worst scaling
    pp_improvement: float = 0.25   # Peer prediction
    
    # Noise parameters
    baseline_accuracy: float = 0.70  # Pairwise baseline
    noise_std: float = 0.15  # Inter-rater disagreement
    
    # Statistical parameters
    alpha: float = 0.05
    n_simulations: int = 10000

def simulate_single_experiment(config: ExperimentConfig) -> Tuple[float, bool]:
    """
    Simulate one experiment instance
    Returns: (p_value, detected_effect)
    """
    # True underlying accuracies for each format
    acc_pairwise = config.baseline_accuracy
    acc_bws = acc_pairwise * (1 + config.bws_improvement)
    acc_pp = acc_pairwise * (1 + config.pp_improvement)
    
    # Simulate measured accuracies (with noise from inter-rater disagreement)
    results_pairwise = np.random.normal(acc_pairwise, config.noise_std, 
                                        config.n_labelers_per_format)
    results_bws = np.random.normal(acc_bws, config.noise_std, 
                                   config.n_labelers_per_format)
    results_pp = np.random.normal(acc_pp, config.noise_std, 
                                  config.n_labelers_per_format)
    
    # One-way ANOVA: Do formats differ?
    f_stat, p_value = stats.f_oneway(results_pairwise, results_bws, results_pp)
    
    detected = p_value < config.alpha
    
    return p_value, detected

def run_power_analysis(config: ExperimentConfig) -> Dict:
    """
    Run full power analysis for given configuration
    """
    print(f"\nRunning power analysis: {config.name}")
    print(f"  Simulations: {config.n_simulations:,}")
    print(f"  Sample size: {config.n_labelers_per_format} labelers/format")
    print(f"  Effect sizes: BWS={config.bws_improvement:.1%}, PP={config.pp_improvement:.1%}")
    
    results = []
    for i in range(config.n_simulations):
        p_value, detected = simulate_single_experiment(config)
        results.append({
            'p_value': p_value,
            'detected': detected,
            'sim_num': i
        })
        
        if (i + 1) % 2000 == 0:
            current_power = np.mean([r['detected'] for r in results])
            print(f"  Progress: {i+1:,}/{config.n_simulations:,} ({current_power:.1%} power so far)")
    
    df = pd.DataFrame(results)
    power = df['detected'].mean()
    
    print(f"  ✓ Final power: {power:.1%}")
    
    return {
        'config': config,
        'power': power,
        'results_df': df,
        'mean_p_value': df['p_value'].mean(),
        'median_p_value': df['p_value'].median()
    }

def power_vs_sample_size(base_config: ExperimentConfig, 
                         sample_sizes: List[int]) -> pd.DataFrame:
    """
    Calculate power for different sample sizes
    """
    print("\n" + "="*60)
    print("POWER vs SAMPLE SIZE ANALYSIS")
    print("="*60)
    
    results = []
    for n in sample_sizes:
        config = ExperimentConfig(
            name=f"N={n}",
            n_labelers_per_format=n,
            bws_improvement=base_config.bws_improvement,
            pp_improvement=base_config.pp_improvement,
            baseline_accuracy=base_config.baseline_accuracy,
            noise_std=base_config.noise_std,
            n_simulations=5000  # Fewer sims for speed
        )
        
        result = run_power_analysis(config)
        results.append({
            'n_labelers': n,
            'power': result['power']
        })
    
    return pd.DataFrame(results)

def power_vs_effect_size(base_config: ExperimentConfig,
                         effect_sizes: List[float]) -> pd.DataFrame:
    """
    Calculate power for different effect sizes (BWS improvement)
    """
    print("\n" + "="*60)
    print("POWER vs EFFECT SIZE ANALYSIS")
    print("="*60)
    
    results = []
    for effect in effect_sizes:
        config = ExperimentConfig(
            name=f"Effect={effect:.1%}",
            n_labelers_per_format=base_config.n_labelers_per_format,
            bws_improvement=effect,
            pp_improvement=effect * 0.8,  # PP slightly less than BWS
            baseline_accuracy=base_config.baseline_accuracy,
            noise_std=base_config.noise_std,
            n_simulations=5000
        )
        
        result = run_power_analysis(config)
        results.append({
            'effect_size': effect,
            'power': result['power']
        })
    
    return pd.DataFrame(results)

def create_visualizations(power_sample_df: pd.DataFrame, 
                          power_effect_df: pd.DataFrame,
                          scenario_results: Dict):
    """
    Create publication-quality visualizations
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('RLHF Format Comparison: Power Analysis Results', 
                 fontsize=16, fontweight='bold')
    
    # 1. Power vs Sample Size
    ax = axes[0, 0]
    ax.plot(power_sample_df['n_labelers'], power_sample_df['power'], 
            'o-', linewidth=2, markersize=8)
    ax.axhline(0.80, color='red', linestyle='--', linewidth=1, 
               label='80% power threshold')
    ax.set_xlabel('Labelers per Format', fontsize=12)
    ax.set_ylabel('Statistical Power', fontsize=12)
    ax.set_title('A) Power vs Sample Size', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim(0, 1)
    
    # Add annotation for recommended sample size
    target_power = 0.80
    recommended_n = power_sample_df[power_sample_df['power'] >= target_power]['n_labelers'].min()
    if not np.isnan(recommended_n):
        ax.annotate(f'Recommended:\n{int(recommended_n)} labelers', 
                    xy=(recommended_n, target_power),
                    xytext=(recommended_n + 3, 0.65),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=10, color='red')
    
    # 2. Power vs Effect Size
    ax = axes[0, 1]
    ax.plot(power_effect_df['effect_size'] * 100, power_effect_df['power'], 
            'o-', linewidth=2, markersize=8, color='darkorange')
    ax.axhline(0.80, color='red', linestyle='--', linewidth=1)
    ax.set_xlabel('BWS Improvement over Pairwise (%)', fontsize=12)
    ax.set_ylabel('Statistical Power', fontsize=12)
    ax.set_title('B) Power vs Effect Size', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    
    # 3. Scenario Comparison
    ax = axes[1, 0]
    scenario_names = list(scenario_results.keys())
    powers = [scenario_results[s]['power'] for s in scenario_names]
    bars = ax.barh(scenario_names, powers)
    
    # Color code by power level
    for i, (bar, power) in enumerate(zip(bars, powers)):
        if power >= 0.80:
            bar.set_color('green')
        elif power >= 0.60:
            bar.set_color('orange')
        else:
            bar.set_color('red')
    
    ax.axvline(0.80, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlabel('Statistical Power', fontsize=12)
    ax.set_title('C) Power Across Scenarios', fontsize=13, fontweight='bold')
    ax.set_xlim(0, 1)
    
    # Add power values as text
    for i, (name, power) in enumerate(zip(scenario_names, powers)):
        ax.text(power + 0.02, i, f'{power:.1%}', va='center', fontsize=10)
    
    # 4. P-value Distribution (Conservative scenario)
    ax = axes[1, 1]
    conservative_pvals = scenario_results['Conservative']['results_df']['p_value']
    ax.hist(conservative_pvals, bins=50, edgecolor='black', alpha=0.7)
    ax.axvline(0.05, color='red', linestyle='--', linewidth=2, 
               label='α = 0.05')
    ax.set_xlabel('P-value', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('D) P-value Distribution (Conservative Scenario)', 
                 fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save figure
    output_path = 'power_analysis_results.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualization saved: {output_path}")
    
    return fig

def generate_summary_tables(scenario_results: Dict,
                             power_sample_df: pd.DataFrame,
                             power_effect_df: pd.DataFrame):
    """
    Generate markdown summary tables
    """
    # Scenario comparison table
    scenario_table = pd.DataFrame([
        {
            'Scenario': name,
            'BWS Improvement': f"{res['config'].bws_improvement:.1%}",
            'PP Improvement': f"{res['config'].pp_improvement:.1%}",
            'Noise (SD)': f"{res['config'].noise_std:.2f}",
            'Power': f"{res['power']:.1%}",
            'Median p-value': f"{res['median_p_value']:.4f}"
        }
        for name, res in scenario_results.items()
    ])
    
    # Sample size recommendations
    target_power = 0.80
    sample_size_table = power_sample_df.copy()
    sample_size_table['Achieves 80%'] = sample_size_table['power'] >= target_power
    sample_size_table['Power'] = sample_size_table['power'].apply(lambda x: f"{x:.1%}")
    sample_size_table = sample_size_table.rename(columns={
        'n_labelers': 'Labelers per Format'
    })
    
    # Effect size detection
    effect_table = power_effect_df.copy()
    effect_table['Detectable at 80%'] = effect_table['power'] >= target_power
    effect_table['Effect Size (%)'] = (effect_table['effect_size'] * 100).round(1)
    effect_table['Power'] = effect_table['power'].apply(lambda x: f"{x:.1%}")
    effect_table = effect_table[['Effect Size (%)', 'Power', 'Detectable at 80%']]
    
    # Save tables
    with open('power_analysis_summary.md', 'w') as f:
        f.write("# Power Analysis Summary\n\n")
        f.write("## Scenario Comparison\n\n")
        f.write(scenario_table.to_markdown(index=False))
        f.write("\n\n## Sample Size Requirements\n\n")
        f.write(sample_size_table.to_markdown(index=False))
        f.write("\n\n## Detectable Effect Sizes (N=10 per format)\n\n")
        f.write(effect_table.to_markdown(index=False))
        f.write("\n\n## Key Findings\n\n")
        
        # Recommendations
        min_n_80 = sample_size_table[sample_size_table['Achieves 80%'] == True]['Labelers per Format'].min()
        min_effect_80 = effect_table[effect_table['Detectable at 80%'] == True]['Effect Size (%)'].min()
        
        f.write(f"- **Recommended sample size**: {int(min_n_80)} labelers per format (achieves 80% power)\n")
        f.write(f"- **Minimum detectable effect**: {min_effect_80:.1f}% improvement (at 80% power, N=10/format)\n")
        f.write(f"- **Our planned pilot**: 10 labelers/format has {scenario_results['Moderate']['power']:.1%} power for moderate scenario\n")
        
        # Interpret results
        moderate_power = scenario_results['Moderate']['power']
        if moderate_power >= 0.80:
            f.write(f"\n✅ **CONCLUSION**: Planned sample size (10/format) is adequate for detecting moderate effects (30% improvement)\n")
        elif moderate_power >= 0.70:
            f.write(f"\n⚠️ **CONCLUSION**: Planned sample size has moderate power ({moderate_power:.1%}). Consider increasing to {int(min_n_80)}/format for 80% power.\n")
        else:
            f.write(f"\n❌ **CONCLUSION**: Planned sample size is underpowered. Increase to {int(min_n_80)}/format recommended.\n")
    
    print(f"✓ Summary tables saved: power_analysis_summary.md")
    
    return scenario_table, sample_size_table, effect_table

def main():
    """
    Run complete power analysis
    """
    print("="*60)
    print("RLHF ELICITATION FORMAT COMPARISON")
    print("Power Analysis Simulation")
    print("="*60)
    
    # Define scenarios
    scenarios = {
        'Conservative': ExperimentConfig(
            name="Conservative (15% improvement)",
            bws_improvement=0.15,
            pp_improvement=0.12,
            noise_std=0.20,  # Higher noise
            n_simulations=10000
        ),
        'Moderate': ExperimentConfig(
            name="Moderate (30% improvement)",
            bws_improvement=0.30,
            pp_improvement=0.25,
            noise_std=0.15,  # Medium noise
            n_simulations=10000
        ),
        'Optimistic': ExperimentConfig(
            name="Optimistic (50% improvement)",
            bws_improvement=0.50,
            pp_improvement=0.40,
            noise_std=0.10,  # Lower noise
            n_simulations=10000
        )
    }
    
    # Run all scenarios
    print("\n" + "="*60)
    print("SCENARIO ANALYSIS")
    print("="*60)
    
    scenario_results = {}
    for name, config in scenarios.items():
        result = run_power_analysis(config)
        scenario_results[name] = result
    
    # Power vs sample size (using moderate scenario as base)
    sample_sizes = [5, 8, 10, 12, 15, 20, 25, 30]
    power_sample_df = power_vs_sample_size(scenarios['Moderate'], sample_sizes)
    
    # Power vs effect size (using N=10 as base)
    effect_sizes = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    power_effect_df = power_vs_effect_size(scenarios['Moderate'], effect_sizes)
    
    # Create visualizations
    fig = create_visualizations(power_sample_df, power_effect_df, scenario_results)
    
    # Generate summary tables
    tables = generate_summary_tables(scenario_results, power_sample_df, power_effect_df)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nOutputs:")
    print("  - power_analysis_results.png (visualizations)")
    print("  - power_analysis_summary.md (tables & recommendations)")
    
    return scenario_results, power_sample_df, power_effect_df

if __name__ == "__main__":
    results = main()
