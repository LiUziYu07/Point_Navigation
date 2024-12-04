# 8 nodes
uuid2timestamp = {'016c53b3-0077-488c-b76f-c1b76e8ca019': '1728908147', 'e5bd8e0f-b268-4e6d-b4c1-e585fad3f85f': '1728908179', 'e3ff2e86-6818-4396-9a86-533b8d3e43f2': '1728908207', '012e09ff-e8e9-4cf4-b491-db201f92e56b': '1728908269', 'b025a50d-80e9-4250-83ef-9ff6f7728062': '1728908302', 'd3e4af0c-96ba-482b-b45c-793dce9f732e': '1728908336', '77d80b4d-f9a1-40ee-832e-3618e5aed50c': '1728908406', '2ffe2640-5ed2-43cd-b3e7-ac479b918ded': '1728908421', 'a2e768b3-935d-439a-8843-24eec2e106b9': '1728908463'}

coordinates = {"1728908147": (1.545, 3.119, 0),
               "1728908179": (1.4, 7.7071, 0),
               "1728908207": (1.4, 9.649, 0),
               "1728908269": (-2.529, 10.162, 0),
               "1728908302": (-2.538, 7.77, 0),
               "1728908336": (-2.322, 3.683, 0),
               "1728908406": (9.45, 3.041, 0),
               "1728908421": (7.629, 3.212, 0),
               "1728908463": (0, 0, 0)}

node_infos = {
    "1728908147": {
        "FRONT_CAMERA": "A long walkway with lots of chairs, a lighted computer in front of it, "
                        "and an alarm button on the left side of it.",
        "BACK_CAMERA": "A frame that resembles a door, the inner measurement of the door looks like an "
                       "office with people working. A wooden table and a metal table with a telephone on "
                       "the wooden table.",
        "LEFT_CAMERA": "A walkway with long tables and what appeared to be a whiteboard with writing on it "
                       "in the distance.",
        "RIGHT_CAMERA": "A long walkway with a trash can and a long table;There is a long corridor that "
                        "seems to go all the way to the main door, and there are areas to the left that are "
                        "enclosed by a red fence"
    },

    "1728908179": {
        "FRONT_CAMERA": "A walkway, flanked by tables and chairs, with what looks like a whiteboard with a "
                        "lot of things posted on it in the distance",
        "BACK_CAMERA": "There was a frame resembling a door in the distance, with what appeared to be "
                       "tables and chairs on either side, and a wooden table with something resembling a "
                       "telephone a long way off.",
        "LEFT_CAMERA": "A long table and a lot of chairs with computers on the table turned on.",
        "RIGHT_CAMERA": "A long table and lots of chairs"
    },

    "1728908207": {
        "FRONT_CAMERA": "A whiteboard with a lot of formulas written on it, a lot of paper taped to it, "
                        "and a computer on the table in front of it.",
        "BACK_CAMERA": "On either side were long tables, far away from the wooden ones in the distance.",
        "LEFT_CAMERA": "There was a table with a printer on it, a chair that seemed to be close by, "
                       "and a whiteboard with writing and paper near it.",
        "RIGHT_CAMERA": "Near the right side, which seemed to be blocked by a red wall, there were a lot "
                        "of chairs turned upside down and two tables"
    },

    "1728908269": {
        "FRONT_CAMERA": "Tables on both sides, printer on the table on the left, whiteboard in the near distance, "
                        "window in the far distance.",
        "BACK_CAMERA": "There are some host computers on the near table, and the far whiteboard seems to have "
                       "function images computerized and pasted on a lot of paper.",
        "LEFT_CAMERA": "The whiteboard near the whiteboard has a lot of formulas, images and symbols drawn on it and "
                       "a lot of paper taped to it. Printer on the table near by.",
        "RIGHT_CAMERA": "Nearby were tables and chairs, and the tables appeared to hold lab equipment. In the "
                        "distance there appears to be cabinets."
    },

    "1728908302": {
        "FRONT_CAMERA": "On the left is a table, to the right is a whiteboard with what appears to be a form drawn on "
                        "it, and in the distance are a table, chairs, and windows.",
        "BACK_CAMERA": "On either side are tables and chairs, and on the far table is a computer, next to which is a "
                       "whiteboard on which diagrams have been drawn and labeled.",
        "LEFT_CAMERA": "Printer on the table on the right, chair under the table.",
        "RIGHT_CAMERA": "The whiteboard in the center had so many tables drawn and written on it that it blocked the "
                        "table behind it."
    }
    ,

    "1728908336": {
        "FRONT_CAMERA": "There is a red FIRE HOST REEL in the front, a long walkway with cabinets and tables along "
                        "the walkway. There's a red button on a pillar on the left, and what looks like a gate in the"
                        " distance.",
        "BACK_CAMERA": "A long walkway with a whiteboard near it, flanked by tables.",
        "LEFT_CAMERA": "A red fire hose reel, two white boards, a table, and a walkway.",
        "RIGHT_CAMERA": "Nearby two chairs and a long table with a computer on it."
    },

    "1728908406": {"FRONT_CAMERA": "Nearby a cabinet, a fire extinguisher, blue boxes in the distance, long walkway "
                                   "in the distance",
                   "BACK_CAMERA": "Nearby is a model display case with what appears to be a drone, with the sitting "
                                  "position on the right and the gate in the distance",
                   "LEFT_CAMERA": "A fire extinguisher, a short walkway, blue boxes, a chair and a table in close "
                                  "proximity",
                   "RIGHT_CAMERA": "There was a table and two chairs and display cabinets and green netting"},

    "1728908421": {"FRONT_CAMERA": "Long walkway, some table and chairs, red wall and cabinet on the right",
                   "BACK_CAMERA": "Model Display case in the distance on the left, table and covered cabinet on the "
                                  "right",
                   "LEFT_CAMERA": "The box on the table says ROBOTS, the cabinet as well as the chair and table",
                   "RIGHT_CAMERA": "Fire extinguishers, cabinets and covered model display cases"},

    "1728908463": {"FRONT_CAMERA": "Covered door frames, wooden cabinets, many chairs, and windows",
                   "BACK_CAMERA": "A very large robot, two people working, clothes hanging from one of the chairs",
                   "LEFT_CAMERA": "A chair, fire extinguisher sign on the wall blocked fire extinguisher",
                   "RIGHT_CAMERA": "A table or cabinet with a computer and monitor on the table"},
}


def get_adjacency_matrix(edges):
    adjacency_matrix = [[False for _ in range(9)] for _ in range(9)]

    for edge in edges:
        i, j = edge
        adjacency_matrix[i][j] = True
        adjacency_matrix[j][i] = True  # Since it's an undirected graph

    return adjacency_matrix


edges = [(0, 1), (0, 5), (0, 7), (0, 8), (1, 2), (2, 3), (3, 4), (4, 5), (6, 7)]
connection_matrix = get_adjacency_matrix(edges)


example_instructions = ["go to the cabinet and try to find a stop sign and stop there.",
                        "go to the white bag and try to find a white board and stop it",
                        "go to the cabinet and try to find a blue garbagecan and stop there",
                        "go to the cabinet and try to find a green bag and get there after that you should find a basketball and stop there",
                        "go to the white bag and try to find a red garbagecan and stop there",]

if __name__ == "__main__":
    edges = [(0, 1), (0, 5), (0, 7), (0, 8), (1, 2), (2, 3), (3, 4), (4, 5), (6, 7)]
    print(get_adjacency_matrix(edges))
