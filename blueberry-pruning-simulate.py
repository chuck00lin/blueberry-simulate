import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict
import math
import os
from enum import Enum

class BranchStatus(Enum):
    GROWING = 'growing'
    STOPPED_MAX_LENGTH = 'max_length'
    STOPPED_SPACE_CONSTRAINT = 'space_constraint'
    STOPPED_MAX_GENERATION = 'max_generation'
    STOPPED_OVERCROWDED = 'overcrowded'

class Leaf:
    def __init__(self, position: tuple, area: float = 0.01):
        self.position = position
        self.area = area
        self.light_gain = 0.0
        self.photosynthesis_efficiency = 0.3
        self.structure_complexity_factor = 1.0
        self.reflection_coefficient = 0.3

    def calculate_light_gain(self, incident_light: float, extinction_coeff: float, total_lai: float):
        self.light_gain = (incident_light * (1 - self.reflection_coefficient) * 
                          (1 - math.exp(-extinction_coeff * 1)) * 
                          self.photosynthesis_efficiency * 
                          self.structure_complexity_factor)
        return self.light_gain

class Branch:
    def __init__(self, start_pos: tuple, angle: float, growth_rate: float = 0.1, 
                 generation: int = 0, parent=None, plant=None):
        self.start_pos = start_pos
        self.angle = angle
        self.length = 0.0
        self.max_length = 1.0
        self.leaves: Dict[float, List[Leaf]] = {}
        self.age = 0
        self.structure_complexity = 0.0
        self.growth_rate = growth_rate
        self.sub_branches: List[Branch] = []
        self.generation = generation
        self.parent = parent
        self.plant = plant
        self.branching_threshold = 0.4
        self.max_generation = 4
        self.node_spacing = 0.2
        self.max_leaves_per_node = 3
        self.status = BranchStatus.GROWING
        self.last_branch_length = 0.0
        self.min_branch_spacing = 0.3
        
    def is_overcrowded(self, pos: tuple) -> bool:
        """Check if a position is overcrowded using directional analysis"""
        nearby = self.get_nearby_branches(pos, radius=0.3)
        if len(nearby) < 2:
            return False
            
        # Count branches in different sectors around the position
        sectors = {i: 0 for i in range(4)}  # Divide space into 4 sectors
        for branch in nearby:
            branch_pos = branch.get_end_pos()
            dx = branch_pos[0] - pos[0]
            dy = branch_pos[1] - pos[1]
            angle = math.atan2(dy, dx)
            sector = int((angle + math.pi) / (math.pi/2)) % 4
            sectors[sector] += 1
            
        # Position is overcrowded if any sector has too many branches
        return max(sectors.values()) >= 2
        
    def update_status(self):
        if self.length >= self.max_length:
            self.status = BranchStatus.STOPPED_MAX_LENGTH
        elif self.generation >= self.max_generation:
            self.status = BranchStatus.STOPPED_MAX_GENERATION
        elif self.is_overcrowded(self.get_end_pos()):
            self.status = BranchStatus.STOPPED_OVERCROWDED
        
    def get_branch_color(self):
        color_map = {
            BranchStatus.GROWING: 'blue',
            BranchStatus.STOPPED_MAX_LENGTH: 'brown',
            BranchStatus.STOPPED_SPACE_CONSTRAINT: 'red',
            BranchStatus.STOPPED_MAX_GENERATION: 'purple',
            BranchStatus.STOPPED_OVERCROWDED: 'orange'
        }
        return color_map[self.status]
        
    def can_branch(self) -> bool:
        # Basic conditions for branching
        if not (self.length >= self.branching_threshold and 
                self.generation < self.max_generation and 
                len(self.sub_branches) < 2 and  # Reduce max sub-branches to 2
                self.status == BranchStatus.GROWING):
            return False
            
        # Check if enough length has grown since last branching
        if self.length - self.last_branch_length < self.min_branch_spacing:
            return False
            
        # Check space constraints
        end_pos = self.get_end_pos()
        if self.is_overcrowded(end_pos):
            self.status = BranchStatus.STOPPED_SPACE_CONSTRAINT
            return False
            
        return True
        
    def add_sub_branch(self):
        if not self.can_branch():
            return
            
        # Calculate branching angles based on parent direction and available space
        base_angle = self.angle
        if len(self.sub_branches) == 0:
            # First sub-branch: try to grow upward when possible
            if -math.pi/2 <= base_angle <= math.pi/2:
                new_angle = base_angle + math.pi/4  # Grow upward-ish
            else:
                new_angle = base_angle - math.pi/4  # Grow upward-ish
        else:
            # Second sub-branch: opposite side of first
            first_branch_angle = self.sub_branches[0].angle
            angle_diff = (first_branch_angle - base_angle)
            new_angle = base_angle - angle_diff  # Symmetric branching
            
        # Add some natural variation
        new_angle += np.random.uniform(-0.1, 0.1)
        
        new_branch = Branch(
            start_pos=self.get_end_pos(),
            angle=new_angle,
            growth_rate=self.growth_rate * 0.9,
            generation=self.generation + 1,
            parent=self,
            plant=self.plant
        )
        self.sub_branches.append(new_branch)
        self.last_branch_length = self.length
        
    def add_leaves_at_node(self, node_pos: tuple, node_length: float):
        if node_length not in self.leaves:
            self.leaves[node_length] = []
        
        if len(self.leaves[node_length]) < self.max_leaves_per_node:
            # Add leaf at node with slight random offset
            offset_angle = np.random.uniform(0, 2 * math.pi)
            offset_dist = 0.05  # Small offset from branch
            leaf_pos = (
                node_pos[0] + offset_dist * math.cos(offset_angle),
                node_pos[1] + offset_dist * math.sin(offset_angle)
            )
            self.leaves[node_length].append(Leaf(leaf_pos))
        
    def grow(self):
        if self.status == BranchStatus.GROWING:
            if self.length < self.max_length:
                old_length = self.length
                self.length += self.growth_rate
                self.age += 1
                self.structure_complexity = max(0.5,1-self.age * 0.01)
                
                # Add leaves at nodes
                current_node = math.floor(old_length / self.node_spacing) * self.node_spacing
                while current_node <= self.length:
                    if current_node >= 0:
                        node_pos = self.get_position_at_length(current_node)
                        self.add_leaves_at_node(node_pos, current_node)
                    current_node += self.node_spacing
                
                # Increased chance of branching and check more frequently
                if np.random.random() < 0.8 and self.can_branch():  # 20% chance
                    self.add_sub_branch()
                
                # Update status after growth
                self.update_status()
        
        # Grow sub-branches regardless of this branch's status
        for sub_branch in self.sub_branches:
            sub_branch.grow()
    
    def get_position_at_length(self, length: float) -> tuple:
        """Get position at specified length along branch"""
        x = self.start_pos[0] + length * math.cos(self.angle)
        y = self.start_pos[1] + length * math.sin(self.angle)
        return (x, y)
    
    def get_end_pos(self):
        return self.get_position_at_length(self.length)
    
    def draw(self, plt):
        """Recursively draw this branch and all sub-branches"""
        end_pos = self.get_end_pos()
        # Draw branch with color indicating status
        plt.plot([self.start_pos[0], end_pos[0]], 
                [self.start_pos[1], end_pos[1]], 
                color=self.get_branch_color(),
                linewidth=max(0.5, 2 - self.generation * 0.5))
        
        # Draw leaves at nodes
        for node_length, leaves in self.leaves.items():
            for leaf in leaves:
                plt.plot(leaf.position[0], leaf.position[1], 'go', markersize=3)
        
        # Draw sub-branches
        for sub_branch in self.sub_branches:
            sub_branch.draw(plt)

    def calculate_photosynthesis(self, incident_light: float = 1000.0, extinction_coeff: float = 0.5):
        total = 0.0
        # Calculate this branch's leaves
        all_leaves = [leaf for leaves in self.leaves.values() for leaf in leaves]
        if all_leaves:
            total_lai = sum(leaf.area for leaf in all_leaves)
            # LAI is not used now, we set it to 1 in calculate_light_gainl
            total += sum(leaf.calculate_light_gain(incident_light, extinction_coeff, total_lai) 
                        for leaf in all_leaves)
        
        # Add sub-branches' photosynthesis
        for sub_branch in self.sub_branches:
            total += sub_branch.calculate_photosynthesis(incident_light, extinction_coeff)
        
        return total

    def get_nearby_branches(self, pos: tuple, radius: float) -> List['Branch']:
        """Get all branches within radius of pos"""
        nearby = []
        if not self.plant:
            return nearby
            
        def check_branch(branch):
            if branch != self:
                branch_pos = branch.get_end_pos()
                dist = math.sqrt((pos[0] - branch_pos[0])**2 + (pos[1] - branch_pos[1])**2)
                if dist < radius:
                    nearby.append(branch)
            for sub in branch.sub_branches:
                check_branch(sub)
                
        for main_branch in self.plant.branches:
            check_branch(main_branch)
        return nearby

    def get_all_sub_branches(self):
        """
        Return a list of all this branch's sub-branches (recursively).
        This excludes 'self' if you only want the true sub-branches.
        """
        branches = []
        for sb in self.sub_branches:
            branches.append(sb)
            branches.extend(sb.get_all_sub_branches())
        return branches

    def recheck_status_after_pruning(self):
        """
        Re-check if this branch can resume growth now that some
        branches have been pruned.
        """
        from enum import Enum
        # Only re-check if the reason for stopping was space or overcrowding
        if self.status in [BranchStatus.STOPPED_SPACE_CONSTRAINT, BranchStatus.STOPPED_OVERCROWDED]:
            if not self.is_overcrowded(self.get_end_pos()):
                self.status = BranchStatus.GROWING
                # Reset growth-related parameters to allow continued growth
                self.length = min(self.length, self.max_length)  # Ensure within bounds
                self.last_branch_length = self.length  # Reset branching position

        # Re-check sub-branches as well
        for sb in self.sub_branches:
            sb.recheck_status_after_pruning()

class Blueberry:
    def __init__(self, area: float = 3.0, branch_area: float = 0.1):
        self.area = area
        self.branches: List[Branch] = []
        self.branch_area = branch_area
        self.center_pos = (0, 0)
        self.photosynthesis_history = []
        
    def can_add_branch(self) -> bool:
        # Count total branches including sub-branches
        def count_all_branches(branch):
            count = 1
            for sub in branch.sub_branches:
                count += count_all_branches(sub)
            return count
            
        total_branches = sum(count_all_branches(b) for b in self.branches)
        return total_branches * self.branch_area < self.area
    
    def add_branch(self):
        if self.can_add_branch():
            # Check for space around the center
            existing_angles = [b.angle for b in self.branches]
            for _ in range(10):  # Try 10 times to find a good angle
                angle = np.random.uniform(0, 2 * math.pi)
                # Check if angle is far enough from existing branches
                if all(abs(angle - existing) > math.pi/6 for existing in existing_angles):
                    new_branch = Branch(self.center_pos, angle, plant=self)
                    self.branches.append(new_branch)
                    break
    
    def grow(self):
        # Grow existing branches
        for branch in self.branches:
            branch.grow()
        
        # Try to add new main branch
        if np.random.random() < 0.1:
            self.add_branch()
        
        # Calculate total photosynthesis
        total_photosynthesis = sum(branch.calculate_photosynthesis() for branch in self.branches)
        self.photosynthesis_history.append(total_photosynthesis)
    
    def get_statistics(self):
        """Calculate various statistics about the plant"""
        total_branches = 0
        total_nodes = 0
        total_age = 0
        
        def process_branch(branch):
            nonlocal total_branches, total_nodes, total_age
            total_branches += 1
            total_age += branch.age
            # Count nodes (based on node_spacing)
            total_nodes += len(branch.leaves)
            
            for sub_branch in branch.sub_branches:
                process_branch(sub_branch)
        
        for branch in self.branches:
            process_branch(branch)
            
        avg_age = total_age / total_branches if total_branches > 0 else 0
        
        return {
            'total_branches': total_branches,
            'total_nodes': total_nodes,
            'average_age': avg_age
        }

    def visualize(self, step: int):
        # Clear console
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Get statistics
        stats = self.get_statistics()
        
        print(f"Step: {step}")
        print(f"Number of main branches: {len(self.branches)}")
        print(f"Total branches: {stats['total_branches']}")
        print(f"Total nodes: {stats['total_nodes']}")
        print(f"Average branch age: {stats['average_age']:.2f}")
        if self.photosynthesis_history:
            print(f"Total photosynthesis: {self.photosynthesis_history[-1]:.2f}")
        
        plt.clf()
        
        # Plant structure subplot
        plt.subplot(1, 2, 1)
        circle = plt.Circle(self.center_pos, math.sqrt(self.area/np.pi), 
                          fill=False, color='green', linestyle='--')
        plt.gca().add_patch(circle)
        
        # Draw all branches recursively
        for branch in self.branches:
            branch.draw(plt)
        
        plt.axis('equal')
        plt.xlim(-2, 2)
        plt.ylim(-2, 2)
        plt.title('Blueberry Plant Structure')
        
        # Photosynthesis history subplot
        plt.subplot(1, 2, 2)
        plt.plot(self.photosynthesis_history, 'g-')
        plt.title('Total Photosynthesis Over Time')
        plt.xlabel('Time Steps')
        plt.ylabel('Photosynthesis Rate')
        plt.grid(True)
        
        plt.tight_layout()
        plt.pause(0.1)

        # Add status counts to display
        status_counts = self.get_branch_status_counts()
        print("\nBranch Status Counts:")
        for status, count in status_counts.items():
            print(f"{status.value}: {count}")

    def count_overcrowded_branches(self) -> int:
        """Count the number of overcrowded branches"""
        count = 0
        for main_branch in self.branches:
            count += sum(1 for b in main_branch.get_all_sub_branches() 
                        if b.status == BranchStatus.STOPPED_OVERCROWDED)
        return count

    def prune(self, prune_ratio=0.2) -> dict:
        """
        Prune the plant focusing on space efficiency
        """
        all_sub_branches = []
        inefficient_branches = []
        
        # Gather all branches and analyze their space efficiency
        for main_branch in self.branches:
            sub_branches = main_branch.get_all_sub_branches()
            all_sub_branches.extend(sub_branches)
            
            for branch in sub_branches:
                # Calculate space efficiency score for each branch
                nearby_count = len(branch.get_nearby_branches(branch.get_end_pos(), radius=0.3))
                leaf_count = sum(len(leaves) for leaves in branch.leaves.values())
                
                # Lower score = less efficient use of space
                efficiency_score = leaf_count / (nearby_count + 1) if nearby_count > 0 else leaf_count
                
                # Add to inefficient list if score is low
                if efficiency_score < 0.5:  # Threshold can be adjusted
                    inefficient_branches.append((branch, efficiency_score))
        
        # Sort branches by efficiency score (least efficient first)
        inefficient_branches.sort(key=lambda x: x[1])
        
        # Calculate how many to prune
        to_prune_count = int(prune_ratio * len(all_sub_branches))
        branches_to_prune = [b[0] for b in inefficient_branches[:to_prune_count]]
        
        # Remove selected branches
        for branch in branches_to_prune:
            if branch.parent is not None and branch in branch.parent.sub_branches:
                branch.parent.sub_branches.remove(branch)
        
        # After pruning, re-check statuses
        for main_branch in self.branches:
            main_branch.recheck_status_after_pruning()
        
        return {
            "pruned_total": len(branches_to_prune),
            "pruned_inefficient": len(branches_to_prune)
        }

    def get_branch_status_counts(self):
        """Count branches in each status"""
        counts = {status: 0 for status in BranchStatus}
        
        def count_branch(branch):
            counts[branch.status] += 1
            for sb in branch.sub_branches:
                count_branch(sb)
        
        for main_branch in self.branches:
            count_branch(main_branch)
        
        return counts

def run_simulation(steps: int = 150, enable_pruning: bool = False, 
                  strategy: str = "fixed", random_seed: int = 42):
    """
    Run a single simulation with or without pruning.
    
    Args:
        steps: Number of simulation steps
        enable_pruning: Whether to enable pruning
        strategy: Pruning strategy
        random_seed: Seed for random number generation
    """
    # Set random seed for reproducibility
    np.random.seed(random_seed)
    
    plt.ion()
    plt.figure(figsize=(12, 5))
    plant = Blueberry()
    
    for step in range(steps):
        # Grow the plant
        plant.grow()

        if enable_pruning:
            if strategy == "fixed":
                if step in [50, 100, 150]:
                    plant.prune(prune_ratio=0.2)
                    
            elif strategy == "adaptive":
                overcrowded_count = plant.count_overcrowded_branches()
                if overcrowded_count > 10:
                    plant.prune(prune_ratio=0.2)
                    
            elif strategy == "progressive":
                if step == 50:
                    plant.prune(prune_ratio=0.1)
                elif step == 100:
                    plant.prune(prune_ratio=0.2)
                elif step == 150:
                    plant.prune(prune_ratio=0.3)
                    
            elif strategy == "regular_with_check":
                if step > 0 and step % 50 == 0:
                    overcrowded_count = plant.count_overcrowded_branches()
                    ratio = 0.1  # base ratio
                    if overcrowded_count > 20:
                        ratio = 0.3
                    elif overcrowded_count > 10:
                        ratio = 0.2
                    plant.prune(prune_ratio=ratio)
            elif strategy == "space_efficient":
                # Check space efficiency every 10 steps
                if step % 10 == 0:
                    # Calculate current space usage
                    total_branches = sum(1 for b in plant.branches 
                                      for sb in b.get_all_sub_branches())
                    area_used = total_branches * plant.branch_area
                    
                    # If space usage is inefficient, prune more
                    if area_used > plant.area * 0.8:  # 80% space threshold
                        plant.prune(prune_ratio=0.2)
                    elif area_used > plant.area * 0.6:  # 60% space threshold
                        plant.prune(prune_ratio=0.1)
        # Visualize
        plant.visualize(step)
    
    plt.ioff()
    return plant.photosynthesis_history

def compare_pruning_strategies(steps: int = 150, random_seed: int = 42):
    """
    Compare pruning vs non-pruning strategies using the same initial conditions.
    """
    # Run simulation without pruning
    no_pruning_history = run_simulation(steps=steps, enable_pruning=False, random_seed=random_seed, strategy="fixed")
    # Run simulation with fixed pruning
    pruning_history_fixed = run_simulation(steps=steps, enable_pruning=True, random_seed=random_seed, strategy="fixed")
    # Run simulation with pruning
    pruning_history_space_efficient = run_simulation(steps=steps, enable_pruning=True, random_seed=random_seed, strategy="space_efficient")
    
    # Plot comparison
    plt.figure(figsize=(10, 6))
    plt.plot(no_pruning_history, 'b-', label='No Pruning')
    plt.plot(pruning_history_fixed, 'r-', label='One Year Pruning')
    plt.plot(pruning_history_space_efficient, 'g-', label='Keep track efficiency')
    plt.title('Comparison of Pruning Strategies')
    plt.xlabel('Time Steps')
    plt.ylabel('Photosynthesis Rate')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Try different random seeds
    for seed in [42]: #[123,456]
        print(f"\nTrying seed: {seed}")
        compare_pruning_strategies(random_seed=seed)
