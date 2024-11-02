import uuid


def generate_action_space(coordinates, timestamp2uuid):
    action_space = {"Turn left": 90, "Turn right": -90}
    viewpoints = generate_viewpoints(coordinates, timestamp2uuid)
    return action_space, viewpoints


def generate_viewpoints(coordinates, timestamp2uuid):
    viewpoints = {}
    for timestamp, coord in coordinates.items():
        viewpoints[str(timestamp2uuid[timestamp])] = coord
    return viewpoints
