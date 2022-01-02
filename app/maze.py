# -*- coding:utf-8 -*-
try:
    from typing import List
except:
    pass
import random

try:
    import Rhino.Geometry as geo
except:
    geo = None


class Maze:
    def __init__(self, w, d, h):
        self.w = max(1, w)
        self.d = max(1, d)
        self.h = max(1, h)

        self.cells = []  # type: List[List[List[Cell]]]
        self.walls = []

    def build(self):
        # cell 생성
        column_list = []
        for x in range(self.w):
            row_list = []
            for y in range(self.d):
                height_list = []
                for z in range(self.h):
                    cell = Cell(x, y, z)
                    height_list.append(cell)
                row_list.append(height_list)
            column_list.append(row_list)
        self.cells = column_list

        self._init_maze()

        if geo:
            for h in self.cells:
                for d in h:
                    for cell in d:
                        self._draw_wall(cell)

    def _draw_wall(self, cell):
        # type: (Cell) -> None

        pos_pt = geo.Point3d(cell.x, cell.y, cell.z)
        interval = geo.Interval(0, 1)
        plane = geo.Plane(pos_pt, geo.Vector3d.ZAxis)
        box_faces = geo.Box(plane, interval, interval, interval).ToBrep().Faces
        pt_face_list = [
            [box_face.PointAt(0.5, 0.5), box_face] for box_face in box_faces
        ]
        front = sorted(pt_face_list, key=lambda pt_face: pt_face[0].X)[-1][1]
        back = sorted(pt_face_list, key=lambda pt_face: pt_face[0].X)[0][1]
        right = sorted(pt_face_list, key=lambda pt_face: pt_face[0].Y)[-1][1]
        left = sorted(pt_face_list, key=lambda pt_face: pt_face[0].Y)[0][1]
        top = sorted(pt_face_list, key=lambda pt_face: pt_face[0].Z)[-1][1]
        bottom = sorted(pt_face_list, key=lambda pt_face: pt_face[0].Z)[0][1]

        walls = []
        # wall_set = set(cell.wall.walls)
        if "front" in cell.wall.walls:
            walls.append(front)
        if "back" in cell.wall.walls:
            walls.append(back)
        if "right" in cell.wall.walls:
            walls.append(right)
        if "left" in cell.wall.walls:
            walls.append(left)
        if "top" in cell.wall.walls:
            walls.append(top)
        if "bottom" in cell.wall.walls:
            walls.append(bottom)

        self.walls.extend(walls)

    def _init_maze(self):
        stack = []
        stack.append(self.cells[0][0][0])

        while stack:
            current = stack[-1]  # type: Cell
            if not current.direction:
                stack.pop()
                continue
            current.is_visit = True
            direction = current.direction.pop()
            dir_x, dir_y, dir_z, wall = direction
            # print("Check Direction : {}".format([dir_x, dir_y, dir_z, wall]))
            if 0 <= dir_x < self.w and 0 <= dir_y < self.d and 0 <= dir_z < self.h:
                next_cell = self.cells[dir_x][dir_y][dir_z]
                if not next_cell.is_visit:
                    # print("Move to Direction  : {}".format([dir_x, dir_y, dir_z]))
                    current.wall.walls.remove(wall)
                    next_cell_wall = self._compute_next_cell_wall(wall)
                    next_cell.wall.walls.remove(next_cell_wall)
                    stack.append(next_cell)
            #     else:
            #         print("Aleady Visited")
            # else:
            #     print("Wrong direction")

    def _compute_next_cell_wall(self, prev_wall):
        if prev_wall == "front":
            candidate_wall = "back"
        elif prev_wall == "back":
            candidate_wall = "front"
        elif prev_wall == "right":
            candidate_wall = "left"
        elif prev_wall == "left":
            candidate_wall = "right"
        elif prev_wall == "top":
            candidate_wall = "bottom"
        elif prev_wall == "bottom":
            candidate_wall = "top"
        else:
            raise Exception("Check please!")

        return candidate_wall


class Cell:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        self.wall = Wall(self.x, self.y, self.z)
        self.prev = None
        self.is_visit = False

        self.front_dir = [x + 1, y, z, self.wall.front]
        self.back_dir = [x - 1, y, z, self.wall.back]
        self.right_dir = [x, y + 1, z, self.wall.right]
        self.left_dir = [x, y - 1, z, self.wall.left]
        self.top_dir = [x, y, z + 1, self.wall.top]
        self.bottom_dir = [x, y, z - 1, self.wall.bottom]

        self.direction = [
            self.front_dir,
            self.back_dir,
            self.right_dir,
            self.left_dir,
            self.top_dir,
            self.bottom_dir,
        ]
        random.shuffle(self.direction)

    def _compute_neighbors(self):

        pass

    def link(self):
        pass


class Wall:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        self.front = "front"
        self.back = "back"
        self.right = "right"
        self.left = "left"
        self.top = "top"
        self.bottom = "bottom"

        self.walls = []
        self.walls.append(self.front)
        self.walls.append(self.back)
        self.walls.append(self.right)
        self.walls.append(self.left)
        self.walls.append(self.top)
        self.walls.append(self.bottom)


if __name__ == "__main__":
    maze = Maze(10, 10, 10)
    maze.build()
