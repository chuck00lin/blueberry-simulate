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
        self.photosynthesis_efficiency = 0.8
        self.structure_complexity_factor = 1.0

    def calculate_light_gain(self, incident_light: float, extinction_coeff: float, total_lai: float):
        self.light_gain = (incident_light * 
                          (1 - math.exp(-extinction_coeff * total_lai)) * 
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
                self.structure_complexity = min(1.0, self.age * 0.1)
                
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
    
    def visualize(self, step: int):
        # Clear console
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Step: {step}")
        print(f"Number of main branches: {len(self.branches)}")
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

def run_simulation(steps: int = 150):
    plt.ion()
    plt.figure(figsize=(12, 5))
    plant = Blueberry()
    
    for step in range(steps):
        plant.grow()
        plant.visualize(step)
    
    plt.ioff()
    plt.show()

if __name__ == "__main__":
    run_simulation()
