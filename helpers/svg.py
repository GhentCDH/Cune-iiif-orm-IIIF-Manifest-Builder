import re

type Coordinate = float
type Coordinates = list[float]

type Point = tuple[Coordinate, Coordinate]
type Points = list[Point]

def polygon_to_points(svg: str) -> Points:
    points = None
    regex = r'points="([0-9,. ]+)"'
    if matches := re.findall(regex, svg, re.MULTILINE):
        coordinates = [float(number) for number in re.split(',| ', matches[0])]
        points = [(coordinates[i], coordinates[i+1]) for i in range(0,len(coordinates),2)]
    return points

def path_to_points(svg: str) -> Points:
    points = None
    regex = r'"M([0-9,. ]+)z"'
    if matches := re.findall(regex, svg, re.MULTILINE):
        coordinates = [float(number) for number in re.split(',| ', matches[0])]
        points = [Point(coordinates[i], coordinates[i+1]) for i in range(0,len(coordinates),2)]
    return points

def rescale_points(points: Points, rescale_factor: float) -> Points:
    return [(point[0] * rescale_factor, point[1] * rescale_factor) for point in points]

def points_to_polygon(points: Points) -> str:
    svg_points = ' '.join([f"{point[0]:.2f},{point[1]:.2f}" for point in points])
    svg = f'<svg><polygon points="{svg_points}" /></svg>'
    return svg

def points_to_path(points: Points) -> str:
    svg_points = ' '.join([f"{point[0]:.2f},{point[1]:.2f}" for point in points])
    svg = f'<svg><path d="M{svg_points}z" /></svg>'
    return svg

def polygon_to_path(svg: str, rescale_factor: float = 1):
    points = polygon_to_points(svg)
    if rescale_factor != 1:
        points = rescale_points(points, rescale_factor)
    return points_to_path(points)
