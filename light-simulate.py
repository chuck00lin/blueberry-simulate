import math
import matplotlib.pyplot as plt

# -------------------------------
# 1. Define Parameters
# -------------------------------

# Environmental Variables (Dotted Line Parameters)
I0 = 20.0          # Incident light (e.g., MJ/m²/day)
k = 0.5            # Beer-Lambert extinction coefficient
A_ground = 1.0     # Ground area occupied by the plant canopy (m²)

# Model Parameters
epsilon = 0.1      # Conversion efficiency from light to biomass
r = 0.05           # Fraction of assimilation allocated to leaf area growth
mu = 0.01          # Leaf area senescence rate (fraction lost per time step)

# Simulation Parameters
T_max = 365        # Total simulation time steps (e.g., days)

# Add pruning strategies
pruning_strategies = {
    "No Pruning": {"rho": 0.0, "prune_interval": None},
    "Light Pruning": {"rho": 0.2, "prune_interval": 30},
    "Moderate Pruning": {"rho": 0.3, "prune_interval": 30},
    "Heavy Pruning": {"rho": 0.5, "prune_interval": 30},
}

# Initialize results dictionary
results = {strategy: {"time_steps": [], "leaf_areas": []} for strategy in pruning_strategies}

# -------------------------------
# 2. Initialize State Variables
# -------------------------------

LA_initial = 0.1    # Initial leaf area (m²)
LA = LA_initial     # Current leaf area

# -------------------------------
# 3. Simulation Loop
# -------------------------------

for strategy_name, params in pruning_strategies.items():
    LA = LA_initial  # Reset leaf area for each strategy
    print(f"\nRunning simulation: {strategy_name}")
    for t in range(1, T_max + 1):
        # Compute Leaf Area Index (LAI)
        LAI = LA / A_ground
        
        # Compute Intercepted Light using Beer-Lambert
        I_avg = I0 * (1 - math.exp(-k * LAI))
        
        # Compute Photosynthesis (Assimilation)
        A_t = epsilon * I_avg
        
        # Compute Leaf Area Growth
        delta_LA = r * A_t - mu * LA
        
        # Update Leaf Area
        LA += delta_LA
        
        # Ensure Leaf Area doesn't become negative
        LA = max(LA, 0)
        
        # Apply Pruning if applicable
        if params["prune_interval"] and t % params["prune_interval"] == 0:
            LA_before_pruning = LA
            LA *= (1 - params["rho"])
            print(f"Strategy '{strategy_name}': Day {t}: Pruning applied. LA reduced from {LA_before_pruning:.3f} to {LA:.3f} m²")
        
        # Store Results for Plotting
        results[strategy_name]["time_steps"].append(t)
        results[strategy_name]["leaf_areas"].append(LA)

# -------------------------------
# 4. Plot the Results
# -------------------------------

plt.figure(figsize=(12, 6))
for strategy_name, data in results.items():
    plt.plot(data["time_steps"], data["leaf_areas"], label=strategy_name)

# Highlight pruning points only for strategies with pruning
for strategy_name, params in pruning_strategies.items():
    if params["prune_interval"]:
        prune_days = list(range(params["prune_interval"], T_max + 1, params["prune_interval"]))
        prune_LA = [results[strategy_name]["leaf_areas"][day - 1] for day in prune_days]
        plt.scatter(prune_days, prune_LA, label=f'{strategy_name} Pruning Events', zorder=5)

# Adding titles and labels
plt.title('Comparison of Leaf Area Growth Over Time with Different Pruning Strategies')
plt.xlabel('Time (Days)')
plt.ylabel('Leaf Area (m²)')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()
