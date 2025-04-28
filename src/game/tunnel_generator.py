#?attr SERVER

import math
import random as r
from .random_num import get_random_num

#    MATEVŽ   veliko pomagal Deepseek

class TunnelGenerator:
    def __init__(self, seed):
        self.width = 1.5
        self.curvature = 0.6 
        self.seed = seed
        self.min_depth = 5
        

    def _center_point(self, region):
        """Calculate center of region"""
        avg_x = sum(p[0] for p in region) // len(region)
        avg_y = sum(p[1] for p in region) // len(region)
        return (avg_x, avg_y)
    
    def _distance(self, p1, p2):
        """Euclidean distance"""
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return math.sqrt(dx*dx + dy*dy)
    

    def _dig_circle(self, cave_data, center_x, center_y, radius):
        """Carve out a circular tunnel area with validation"""
        tiles_dug = 0
        for y in range(int(center_y-radius), int(center_y+radius)+1):
            for x in range(int(center_x-radius), int(center_x+radius)+1):
                if (0 <= y < len(cave_data) and 
                    0 <= x < len(cave_data[0])):
                    dx = x - center_x
                    dy = y - center_y
                    if dx*dx + dy*dy <= radius*radius:
                        cave_data[y][x] = (cave_data[y][x][0], True, True)
                        tiles_dug += 1


    def _dig_line(self, cave_data, x1, y1, x2, y2):
        """Dig tunnel segment with varying width"""
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        
        for i in range(steps+1):
            t = i/max(steps, 1)
            x = int(x1 + dx * t)
            y = int(y1 + dy * t)
            
            radius = self.width
            self._dig_circle(cave_data, x, y, radius)
    
    def _find_cave_regions(self, cave_data):
        """Find regions of the cave that are connected"""
        regions = []
        visited = set()
        
        for y in range(len(cave_data)):
            for x in range(len(cave_data[0])):
                if (x,y) not in visited and cave_data[y][x][1]:
                    # New region found
                    region = []
                    stack = [(x,y)]
                    
                    while stack:
                        cx, cy = stack.pop()
                        if (cx,cy) in visited:
                            continue
                            
                        visited.add((cx,cy))
                        region.append((cx,cy))
                        
                        # Check neighbors
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < len(cave_data[0]) and \
                               (0 <= ny < len(cave_data)) and \
                               cave_data[ny][nx][1]:
                                stack.append((nx,ny))
                    
                    if len(region) >= 2:
                        regions.append(region)
        return regions
        
    
    def _connect_regions(self, cave_data, regions, ground_levels):
        """Connect regions with tunnels"""
        centers = [self._center_point(region) for region in regions]

        depths = {index: ground_levels[center[0]] - center[1] for index, center in enumerate(centers)}

        connected = set()
        connected.add(0)


        max_iterations = len(regions) * 2
        iteration_count = 0

        while len(connected) < len(regions):
            iteration_count += 1
            if iteration_count > max_iterations:
                break

            closest = None
            min_dist = float('inf')

            for i in connected:
                for j in range(len(regions)):
                    if j not in connected:
                        dist = self._distance(centers[i], centers[j])
                        if dist < min_dist:
                            closest = (i, j)
                            min_dist = dist

            if closest:
                i, j = closest
                center_a, center_b = centers[i], centers[j]

                depth_a = depths[i]
                depth_b = depths[j]
       
                if depth_a < self.min_depth and depth_b < self.min_depth:
                    continue

                self._create_tunnel(cave_data, center_a, center_b)
                connected.add(j)
            else:
                break
                

    def generate_tunnels(self, cave_data, ground_levels):
        """Generate tunnels in the cave data"""
        regions = self._find_cave_regions(cave_data)
        
        if len(regions) < 2:
            return False
            
        # Connect regions
        self._connect_regions(cave_data, regions, ground_levels)
        return True            

    
    def _calculate_curve(self, start, end):
        """Create smooth curve between points"""
        points = []
        steps = 10
        
        # Add midpoint with random offset
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # Calculate direction
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            perp_x = -dy/length
            perp_y = dx/length
            
            # Apply curvature
            offset = (get_random_num(self.seed, (start,end) ) * 2 - 1) * length * self.curvature
            mid_x += perp_x * offset
            mid_y += perp_y * offset
        
        # Generate bezier curve points
        for i in range(steps+1):
            t = i/steps
            # Quadratic bezier
            x = (1-t)**2 * start[0] + 2*(1-t)*t * mid_x + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * mid_y + t**2 * end[1]
            points.append((int(x), int(y)))
        return points
    

    def _create_tunnel(self, cave_data, start, end):
        """Create a tunnel between two points"""

        path = self._calculate_curve(start, end)
        
        # Dig a long path
        for i in range(len(path)-1):
            x1, y1 = path[i]
            x2, y2 = path[i+1]
            self._dig_line(cave_data, x1, y1, x2, y2)