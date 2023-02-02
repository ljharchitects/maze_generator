# -*- coding:utf-8 -*-
try:
    from typing import List
except:
    pass
import random

import Rhino.Geometry as geo


class Maze:
    def __init__(self, w, d, h):
        # type: (int, int, int) -> None
        self.w = max(1, w)
        self.d = max(1, d)
        self.h = max(1, h)

        self.cells = []  # type: List[List[List[Cell]]]
        self.walls = []
        self.wall_breps = []

    def build(self):
        # 육면체 방에 해당하는 cell 생성
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

        # 각 방을 랜덤하게 연결하면서 벽체 삭제
        self._init_maze()

        # 미로 결과물에서 라이노 벽체 모델링 생성
        for h in self.cells:
            for d in h:
                for cell in d:
                    self._draw_wall(cell)

        # 겹쳐진 벽체 제거
        self.walls = list(set(self.walls))

        # 파일 저장
        self.wall_breps = self._export_result(self.walls)

    def _export_result(self, walls):
        # type: (List[WallFace]) -> List[geo.Brep]
        result = []
        for wall in walls:
            result.append(wall.brep)
        return result

    def _set_walls(self, cell, wall_face_list):
        # type: (Cell, List[WallFace]) -> None
        front = max(wall_face_list, key=lambda wall_face: wall_face.cen_pt.X)
        back = min(wall_face_list, key=lambda wall_face: wall_face.cen_pt.X)
        right = max(wall_face_list, key=lambda wall_face: wall_face.cen_pt.Y)
        left = min(wall_face_list, key=lambda wall_face: wall_face.cen_pt.Y)
        top = max(wall_face_list, key=lambda wall_face: wall_face.cen_pt.Z)
        bottom = min(wall_face_list, key=lambda wall_face: wall_face.cen_pt.Z)

        if "front" in cell.wall.sides:
            self.walls.append(front)
        if "back" in cell.wall.sides:
            self.walls.append(back)
        if "right" in cell.wall.sides:
            self.walls.append(right)
        if "left" in cell.wall.sides:
            self.walls.append(left)
        if "top" in cell.wall.sides:
            self.walls.append(top)
        if "bottom" in cell.wall.sides:
            self.walls.append(bottom)

    def _draw_wall(self, cell):
        # type: (Cell) -> None
        pos_pt = geo.Point3d(cell.x, cell.y, cell.z)
        interval = geo.Interval(0, 1)
        plane = geo.Plane(pos_pt, geo.Vector3d.ZAxis)
        box_faces = geo.Box(plane, interval, interval, interval).ToBrep().Faces
        wall_face_list = []  # type: List[WallFace]
        for face in box_faces:
            if not face:
                break
            wall_face = WallFace(face.PointAt(0.5, 0.5), face)
            wall_face_list.append(wall_face)

        self._set_walls(cell, wall_face_list)

    def _init_maze(self):
        # 시작 셀
        start_cell = self.cells[0][0][0]
        start_cell.wall.sides.remove("left")  # 시작 벽체 제거
        end_cell = self.cells[self.w - 1][self.d - 1][self.h - 1]
        end_cell.wall.sides.remove("right")  # 목적지 벽체 제거

        stack = [start_cell]

        while stack:
            current = stack[-1]  # type: Cell
            if not current.directions:
                stack.pop()
                continue
            current.is_visit = True
            direction = current.directions.pop()
            dir_x, dir_y, dir_z, wall = direction
            # print("Check Direction : {}".format([dir_x, dir_y, dir_z, wall]))
            if 0 <= dir_x < self.w and 0 <= dir_y < self.d and 0 <= dir_z < self.h:
                next_cell = self.cells[dir_x][dir_y][dir_z]
                if not next_cell.is_visit:
                    # print("Move to Direction  : {}".format([dir_x, dir_y, dir_z]))
                    current.wall.sides.remove(wall)
                    next_cell_wall = self._get_next_cell_wall(wall)
                    next_cell.wall.sides.remove(next_cell_wall)
                    stack.append(next_cell)
            #     else:
            #         print("Aleady Visited")
            # else:
            #     print("Wrong direction")

    def _get_next_cell_wall(self, prev_wall):
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

        self.wall = Wall()
        self.prev = None
        self.is_visit = False

        self.front_dir = [x + 1, y, z, self.wall.front]
        self.back_dir = [x - 1, y, z, self.wall.back]
        self.right_dir = [x, y + 1, z, self.wall.right]
        self.left_dir = [x, y - 1, z, self.wall.left]
        self.top_dir = [x, y, z + 1, self.wall.top]
        self.bottom_dir = [x, y, z - 1, self.wall.bottom]

        self.directions = [
            self.front_dir,
            self.back_dir,
            self.right_dir,
            self.left_dir,
            self.top_dir,
            self.bottom_dir,
        ]
        random.shuffle(self.directions)


class Wall:
    def __init__(self):
        self.front = "front"
        self.back = "back"
        self.right = "right"
        self.left = "left"
        self.top = "top"
        self.bottom = "bottom"

        self.sides = []
        self.sides.append(self.front)
        self.sides.append(self.back)
        self.sides.append(self.right)
        self.sides.append(self.left)
        self.sides.append(self.top)
        self.sides.append(self.bottom)


class WallFace:
    def __init__(self, cen_pt, face):
        # type: (geo.Point3d, geo.BrepFace) -> None
        self.cen_pt = cen_pt
        self.face = face
        self.brep = face.ToBrep()

    def __eq__(self, other):
        # type: (WallFace) -> bool
        return self.cen_pt.DistanceToSquared(other.cen_pt) < 0.01

    def __hash__(self):
        return hash(self.cen_pt)


maze = Maze(width, depth, height)
maze.build()
a = maze.wall_breps
