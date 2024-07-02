import re

def fix_svg_polygon_selector(selector: dict, rescale_factor: float = 1):
    # https://stackoverflow.com/questions/10717190/convert-svg-polygon-to-path
    if selector['type'] == 'SvgSelector':
        selector['value'] = selector['value'].replace('<polygon points="', '<path d="M')
        selector['value'] = selector['value'].replace('"/>', 'z"/>')
        selector['value'] = selector['value'].replace('" />', 'z" />')
    # rescale coordinates?
    if rescale_factor != 1.0:
        regex = r'"M([0-9,. ]+)z"'
        if matches := re.findall(regex, selector['value'], re.MULTILINE):
            coordinates = [ float(number)*rescale_factor for number in re.split(',| ', matches[0])]
            coordinates = [coordinates[i:i+2] for i in range(0,len(coordinates),2)]
            points = ' '.join([f"{point[0]},{point[1]}" for point in coordinates])
            selector['value'] = f'<svg><path d="M{points}z" /></svg>'

    return selector