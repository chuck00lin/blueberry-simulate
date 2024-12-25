# Blueberry Plant Growth Model Documentation

This document describes the mathematical model of blueberry plant growth, including the mechanisms of branching, leaf development, and photosynthesis.

## 1. Model Components

The model consists of three main classes: Blueberry (plant), Branch, and Leaf, each with their own parameters and mechanisms.

### 1.1 Leaf Class

A leaf is the basic unit of photosynthesis in the model.

#### Parameters:
- $A_l$: Leaf area (default: 0.01 m²)
- $\eta_p$: Photosynthesis efficiency (default: 0.8)
- $f_c$: Structure complexity factor (range: [0,1])
- $(x_l, y_l)$: Leaf position coordinates

#### Light Gain Equation:
The light gain for each leaf follows the Beer-Lambert law:

$$
L_g = I_0 \cdot (1 - e^{-k \cdot LAI}) \cdot \eta_p \cdot f_c
$$

Where:
- $L_g$: Light gain
- $I_0$: Incident light intensity
- $k$: Light extinction coefficient
- $LAI$: Leaf Area Index (total leaf area per ground area)

### 1.2 Branch Class

Branches are the structural components that support leaves and can produce sub-branches.

#### Parameters:
- $(x_s, y_s)$: Start position
- $\theta$: Branch angle
- $l$: Current length
- $l_{max}$: Maximum length (default: 1.0 m)
- $g_r$: Growth rate (default: 0.1 m/step)
- $g$: Generation number
- $g_{max}$: Maximum generation (default: 4)
- $l_{threshold}$: Branching threshold (default: 0.4 m)
- $d_{node}$: Node spacing (default: 0.2 m)
- $n_{max}^{leaf}$: Maximum leaves per node (default: 3)

#### Growth Mechanisms:

1. Length Growth:

$$
L_{t+1} = \min(L_t + g_r, L_{max})
$$

2. Structure Complexity:

$$
f_c = \min(1.0, 0.1 \cdot \text{age})
$$

3. Node Position:

$$
x_{node} = x_s + l \cdot \cos(\theta)
$$

$$
y_{node} = y_s + l \cdot \sin(\theta)
$$

4. Branching Conditions:
- Length condition: $l \geq l_{threshold}$
- Generation condition: $g < g_{max}$
- Space condition: $n_{nearby} < 2$ within radius $r = 0.3$

5. Sub-branch Angles:

$$
\theta_{sub1} = \theta + \frac{\pi}{4}
$$

$$
\theta_{sub2} = \theta - \frac{\pi}{6}
$$

### 1.3 Blueberry (Plant) Class

The main plant class that manages overall growth and resource allocation.

#### Parameters:
- $A_{total}$: Total available area (default: 3.0 m²)
- $A_{branch}$: Area occupied by each branch (default: 0.1 m²)
- $(x_c, y_c)$: Center position (0,0)

#### Growth Constraints:

1. Total Branch Area Constraint:

$$
\sum_{i=1}^{n} (1 + n_{sub,i}) \cdot A_{branch} \leq A_{total}
$$

Where $n_{sub,i}$ is the number of sub-branches for branch $i$

2. Branch Spacing Constraint:

$$
|\theta_i - \theta_j| > \frac{\pi}{6} \text{ for all main branches } i,j
$$

## 2. Growth Process

The growth process follows these steps each iteration:

1. Branch Growth:
   - Increment length if below maximum
   - Add leaves at nodes
   - Check for branching conditions
   - Grow sub-branches recursively

2. Photosynthesis Calculation:
   For each branch system:
   $$ P_{total} = \sum_{branches} \sum_{leaves} L_g $$

3. Space Management:
   - Check available area before adding new branches
   - Maintain minimum angular separation between main branches
   - Prevent overcrowding through nearby branch detection

## 3. Visualization

The model visualizes:
1. Plant Structure:
   - Branches as lines with thickness decreasing by generation
   - Leaves as green dots at nodes
   - Available growth area as a circle

2. Photosynthesis History:
   - Plot of total photosynthesis over time
   - Real-time statistics including branch count and current photosynthesis rate
