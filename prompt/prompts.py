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

When you try to go to the landmark, please capture the surrounding first. When taking pictures of your surroundings, 
you will only use one camera at a time, so you need to give rotate_degree, The rotation angle should be selected in 
order 0, 90, 180, 270, 360.

pipeline of the system
---

**STEP 1**: **surrounding_capture**  
1.1 Perform `surrounding_capture` at `cur_pose + 0°`.
   - **depth_estimate**: Immediately attempt to detect the landmark specified in the task description. If the target landmark is detected, calculate the depth (distance) between the LiDAR and the landmark. If a target landmark is found, retrieve its location on the map and proceed directly to **STEP 3**.

1.2 Rotate to `cur_pose + 90°` and perform `surrounding_capture`.
   - **depth_estimate**: Repeat the detection and depth calculation. If the target is detected, proceed directly to **STEP 3**.

1.3 Rotate to `cur_pose + 180°` and perform `surrounding_capture`.
   - **depth_estimate**: Perform the detection and depth calculation again. If the target is detected, proceed directly to **STEP 3**.

1.4 Rotate to `cur_pose + 270°` and perform `surrounding_capture`.
   - **depth_estimate**: Check for landmarks and calculate depth. If the target is detected, proceed directly to **STEP 3**.

**STEP 2**: **Final Check at 360° (if needed)**  
If no landmark is detected in steps 1.1 to 1.4, perform a final capture at `cur_pose + 360°` to confirm.

**STEP 3**: **viewpoint_get**  
Using the system’s map and past trajectory, find the closest connected viewpoint ID relative to the current viewpoint, suitable for further navigation.

**STEP 4**: **Navigate to viewpoint**  
Navigate to the identified viewpoint from **STEP 3**.

---

"""

NavPoint_simple_prompt = ''' Instruct: Starting from viewpoint(0915e34d-80cb-4a0a-808a-8c9793e052d2), go out to the door and turn left, forward to the whiteboard and stop at the it.
> think: To follow the instructions, I should take photos to understand surroundings to find a door
OK.
> Tool calls: detect_surroundings()
I have scan the surroundings and get photos at the viewpoint(0915e34d-80cb-4a0a-808a-8c9793e052d2)
> think: Now, I need to find the door and get its depth.
OK.
> Tool calls: depth_estimate('door')
The depth is 5m away, and the coordinates of the door in the world coordinate is about x=1.5, y=1.5. The door is appear in the first image. So I do not need to rotate to correct my pose. I need to find the next optimum viewpoints.
> Tool calls: find_viewpoint(0915e34d-80cb-4a0a-808a-8c9793e052d2, 1.5, 1.23)
The proper viewpoint is xvcbbgfdgf1.
> Tool calls: navigate(lknvm1sffdh, lknvm1sffdh, NO_CHANGED_POSE)
You are arrive at (lknvm1sffdh) with current pose.
> think: Okay, I have found a door in the first photo, so do not need to rotate and the door is about 2.5 meters away, the coordinates of the door in the world coordinate is about x=1.5, y=1.23.
OK.

> think: Okay. I should go there.
OK.
> Tool calls: navigate(lknvm1sffdh, xvcbbgfdgf1, NO_CHANGED_POSE)
You are arrive at (xvcbbgfdgf1) with current pose.
> think: Okay, after go out of the door, I need to turn left.
OK.
> Tool calls: navigate(xvcbbgfdgf1, xvcbbgfdgf1, TURN_LEFT, 90) 
you are arrive at (xvcbbgfdgf1) meanwhile turn left 90 degrees.
> think: I have turned right, now I need to detect surroundings to find a whiteboard.
Ok.
> Tool calls: detect_surroundings(whiteboard)
There is a whiteboard in the fourth photo, so I need to rotate 90 to right. And the door is about 3 meters away, the coordinates of the door in the world coordinate is about x=-3.7 , y=4.
> think: I need to get back to the pose I had when I took the fourth picture, I need to turn left 90 degree.
OK.
> Tool calls: navigate(xvcbbgfdgf1, xvcbbgfdgf1, TURN_LEFT, 90)
You are arrive at (xvcbbgfdgf1) meanwhile turn left 90 degrees.
> think: okay, I have found the whiteboard, and the door is about 3 meters away, the coordinates of the door in the world coordinate is about x=-3.7 , y=4.
OK.
> think Okay, now I need to find the closet viewpoint.
OK.
> Tool calls: find_viewpoint(xvcbbgfdgf1, 3.7, 4)
The proper viewpoint is xcbvn1.
> think: Okay. I should go there.
OK.
> Tool calls: navigate(xvcbbgfdgf1, xcbvn1, no_changed_pose)
You are arrive at (xcbvn1) with current pose.
> think: Okay, I have already been near the whiteboard. Lets me think whether I am close enough.
OK.
> Tool calls: detect_surroundings(whiteboard) 
There is a whiteboard in the first photo, and the depth of the white board is 0.5m. he coordinates of the door in the world coordinate is about x=-3.7 , y=4.
> think: Okay, I am close enough. Task Completed.
OK.
'''