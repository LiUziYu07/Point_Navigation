import uuid


def generate_action_space(coordinates, timestamp2uuid):
    viewpoints = {}
    for timestamp, coord in coordinates.items():
        viewpoints[str(timestamp2uuid[timestamp])] = coord
    return viewpoints