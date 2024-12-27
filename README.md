# Blueberry Plant Growth Simulation

A simulation model for blueberry plant growth, branching patterns, and pruning strategies.

## Core Components

### Branch Status Types
- `GROWING`: Active growth phase
- `STOPPED_MAX_LENGTH`: Reached maximum length limit
- `STOPPED_SPACE_CONSTRAINT`: Stopped due to space limitations
- `STOPPED_MAX_GENERATION`: Reached maximum generation limit
- `STOPPED_OVERCROWDED`: Stopped due to overcrowding

## Parameter Groups

### Leaf Parameters
| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| `area` | 0.01 | m² | Individual leaf area |
| `photosynthesis_efficiency` | 0.3 | ratio | Efficiency of light conversion |
| `reflection_coefficient` | 0.3 | ratio | Light reflection factor |

### Branch Growth Parameters
| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| `growth_rate` | 0.1 | m/step | Branch elongation per time step |
| `max_length` | 1.0 | m | Maximum branch length |
| `branching_threshold` | 0.4 | m | Minimum length before branching |
| `max_generation` | 4 | count | Maximum branch generations |
| `node_spacing` | 0.2 | m | Distance between leaf nodes |
| `max_leaves_per_node` | 3 | count | Maximum leaves at each node |
| `min_branch_spacing` | 0.3 | m | Minimum distance between branches |

### Plant Parameters
| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| `area` | 3.0 | m² | Total plant growing area |
| `branch_area` | 0.1 | m² | Area occupied by each branch |

### Environmental Parameters
| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| `incident_light` | 1000.0 | μmol/m²/s | Default light intensity |
| `extinction_coeff` | 0.5 | ratio | Light extinction coefficient |

### Pruning Parameters
| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| `prune_ratio` | 0.2 | ratio | Fraction of branches to remove |

## Variable Relationships

### Growth Process Flow
1. **Plant Level**
   - `branches` → List of main branches
   - `photosynthesis_history` → Tracks total plant productivity

2. **Branch Level**
   - `start_pos` → Branch origin point
   - `angle` → Growth direction
   - `length` → Current branch length
   - `sub_branches` → Child branches
   - `leaves` → Dictionary of leaves by position
   - `status` → Current growth status

3. **Leaf Level**
   - `position` → Location on branch
   - `light_gain` → Photosynthetic output
   - `structure_complexity_factor` → Age-based efficiency

### Growth Control Hierarchy
- Plant area limits total branches
- Branch generation limits sub-branching
- Space constraints affect branch status
- Node spacing determines leaf positions
- Overcrowding checks influence growth

### Photosynthesis Calculation Chain
1. Leaf light interception
2. Individual leaf photosynthesis
3. Branch total calculation
4. Plant-level aggregation

## Simulation Parameters
| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| `steps` | 150 | count | Simulation duration |
| `random_seed` | [42, 123, 456] | - | Random number seeds |

## Visualization
- Left subplot: Plant structure with color-coded branch status
- Right subplot: Photosynthesis rate over time
- Statistics display: Branch counts, nodes, and average age
