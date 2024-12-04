intent_recognition_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a helpful AI 
assistant to help recognize the intention(Task, Dialogue) of the user only output these two intentions and output in 
json format. { \"intention\": \"{intention}\", \"content\": \"{
content}\"}<|eot_id|><|start_header_id|>user<|end_header_id|> What can you do for 
me?<|eot_id|><|start_header_id|>assistant<|end_header_id|> {\"intention\": \"Dialogue\", \"content\": \"What can you 
do for me\"}<|eot_id|><|start_header_id|>user<|end_header_id|> Follow my instructions to finish the task: go to the 
kitchen and stop at the fridge<|eot_id|><|start_header_id|>assistant<|end_header_id|> {\"intention\": \"Task\", 
\"content\": \"go to the kitchen and stop at the fridge\"}<|eot_id|><|start_header_id|>user<|end_header_id|>"""

SYSTEM_PRINCIPLE = """Here are some tips for you to finish point navigation. Note that only one action is output each 
time. In this case, landmark refers to a variety of objects such as cabinet, bag, etc. Try to extract the object from 
the instructions.

Remember all the objects in the instruction are landmarks.

Note that you can perform two tasks PointNav and ObjNav, when you perform PointNav there will be some viewpoints in 
the scene for you to navigate, and you need to find the most appropriate viewpoint; but when you perform ObjNav, 
you don't have these viewpoints, you will get the coordinate points of the objects on the radar, and then you need to 
utilize the Then you need to use the transform function to transform them into points on the map to perform navigation.

When the instructions require you to look for a variety of things, look for them piece by piece, do not ignore any one.

pipeline of the system (Do not ignore any steps)
---

STEP 1: **surrounding_detect**  
Using the surrounding_detect function to capture a photo and detect the landmark init. When you find it go to Step 2.

STEP 2: **viewpoint_get**  or **interestpoint_get**
For viewpoint_get, Using the system’s map and past trajectory, find the closest connected viewpoint ID relative to the current viewpoint, suitable for further navigation.
For interestpoint_get, Using the depth of the target object, find the closest connected coordinates on the map, suitable for further navigation.

**STEP 3**: **Navigate to viewpoint**  Note that you need to use coordinates on the map
Navigate to the identified viewpoint from **STEP 2**.

**STEP 4**: **surrounding_detect**
Double-check that you're close enough to the target.

"""

COT_PROMPT = """Here are some examples for you to get a better description of your task.
EXAMPLE INSTRUCTION 1: You are at point ajfklajslfka with pose 0, Your task is: go to the countertop and go to table and then stop at the fridge.
Your output should be: I am at ajfklajslfka with pose 0. To finish the task, I should go to the countertop and go to table. After I go to table, I should then go to  a fridge and stop at the it.
EXAMPLE INSTRUCTION 2: You are at point nvmnv12 with pose 120. Your task is: go to the desk and go to a computer and stop at the red wall.
Your output should be: I am at nvmnv12 with pose 120. To finish the task, I should go to the desk and go to  a computer. After I go to a computer, I should find a red wall and stop at the it.
"""

SUMMARY_PROMPT = """Here you need to summarize your past tool call records and task goals. I've omitted some of the content please focus on the landmark.
EXAMPLE INSTRUCTION 1: system: ALGORITHM PIPELINE. Your task: I am at ajfklajslfka with pose 0. To finish the task, I should go to the countertop and find a plastic bag. After I found the plastic bag, I should go there. Then I should find a fridge and get there. TOOL CALL MESSAGE. landmark countertop. Navigate vzxvz or 1.31 2.22
Your output should be: I am at vzxvzt or 1.31 2.22 with pose 90 and I have found and navigate to the countertop. Now I need to find a plastic bag. And then I need to find a fridge and stop at the it.
EXAMPLE INSTRUCTION 2: system: ALGORITHM PIPELINE. Your task: I am at nvmnv12 with pose 120. To finish the task, I should go to the desk and find a pen. After I found the pen, I should find a red wall and stop at the it. TOOL CALL MESSAGE. landmark countertop. Navigate cvbxnbm or 1.26 2.45
Your output should be: I am at cvbxnbm or 1.26 2.45 and I have found and navigate to the desk. After I found the pen, I should find a red wall and stop at the it.
"""