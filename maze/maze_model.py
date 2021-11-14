# -*- coding:utf-8 -*-
try:
    from typing import List
except:
    pass
import sys
import time
import random
import itertools

import Rhino.Geometry as geo

sys.setrecursionlimit(5000)


class Maze:
    def __init__(self, width, depth, height):
        # type: (int, int, int) -> None

        if width <= 0 or depth <= 0 or height <= 0:
            raise Exception("Input is Must bigger than 0")

        self.width = width
        self.depth = depth
        self.height = height

        self.cells = []  # type: List[Cell]
        self.walls = []

    def build(self):
        for w in range(self.width):
            d_list = []
            for d in range(self.depth):
                w_list = []
                for h in range(self.height):
                    cell = Cell(w, d, h)
                    w_list.append(cell)
                d_list.append(w_list)
            self.cells.append(d_list)

        self.compute_cell(None, self.cells[0][0][0])

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
        wall_set = set(cell.wall.walls)
        if "front" in wall_set:
            walls.append(front)
        if "back" in wall_set:
            walls.append(back)
        if "right" in wall_set:
            walls.append(right)
        if "left" in wall_set:
            walls.append(left)
        if "top" in wall_set:
            walls.append(top)
        if "bottom" in wall_set:
            walls.append(bottom)

        self.walls.extend(walls)

    def compute_cell(self, prev_cell, cell):
        # type: (Cell, Cell) -> None

        cell.prev = prev_cell
        cell.is_visit = True

        while True:
            if not cell.direction:
                break
            direction = cell.direction.pop()
            dir_x, dir_y, dir_z, wall = direction
            # print("Check Direction : {}".format([dir_x, dir_y, dir_z]))
            if (
                0 <= dir_x < self.width
                and 0 <= dir_y < self.depth
                and 0 <= dir_z < self.height
            ):
                next_cell = self.cells[dir_x][dir_y][dir_z]
                if not next_cell.is_visit:
                    # print("Move to Direction  : {}".format([dir_x, dir_y, dir_z]))
                    cell.wall.walls.remove(wall)
                    next_cell_wall = self._compute_next_cell_wall(wall)
                    # print("Candidate_wall : {}".format(next_cell_wall))
                    next_cell.wall.walls.remove(next_cell_wall)
                    self.compute_cell(cell, next_cell)
                # else:
            #         print("Aleady Visited")
            # else:
            #     print("Wrong Direction")

        # self.walls.extend(cell.wall.walls)

    def _compute_next_cell_wall(self, prev_wall):
        # type: (Cell, geo.Brep) -> None
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


