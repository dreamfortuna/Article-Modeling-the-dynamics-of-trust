import expyriment
import random
import time
import mediadecoder
from expyriment import design, control, stimuli, io, misc
import os

# Developer mode (optional)
#expyriment.control.set_develop_mode(True)

random.seed(42)

# Create an experiment
exp = expyriment.design.Experiment(name="Trust Experiment")
expyriment.control.initialize(exp)

# Stimulus screen
screen = stimuli.BlankScreen()



# Define a global variable to store the total reward
total_reward = 0
experiment_count = 0
N_TRIALS = 80  # Number of experiment trials

# Add output data variables (optional)
exp.add_data_variable_names(['trial', 'task_difficulty', 'self_correctness', 'AI_correctness', 'trust', 'RT', 'trust_level', 'reward', 'self_difficulty'])

def show_video(video_path):
    """
    Function to present a video and wait for it to finish.
    Play the first video
    """
    video_stimulus = stimuli.Video(video_path)
    video_stimulus.preload()  # Preload the video
    video_stimulus.play()  # Play the video
    video_stimulus.present()  # Play the video
    video_stimulus.wait_end()

def create_buttons(rows, columns, button_size, text_size, colors, n):
    "Create buttons arranged by rows and columns"
    "Inputs: button rows, columns, button size, text size, colors (a list of colors), and total button count n"
    "Returns: generated buttons"
    screen = stimuli.BlankScreen()
    buttons = []
    count = 0
    for i in range(rows):
        for j in range(columns):
            if count >= n:
                break
            button = stimuli.Rectangle(button_size, position=(j*100, i*100), colour=colors[i*columns+j])
            buttons.append(button)
            count += 1
    numbers = [stimuli.TextLine(text=str(i), position=button.position, text_size=30,
                                text_colour=expyriment.misc.constants.C_WHITE) for i, button in enumerate(buttons)]

    for button, number in zip(buttons, numbers):
        button.plot(number)
    # Display buttons

    screen.present()
    #Return the button value selected by mouse click
    mouse = io.Mouse()
    while True:
        clicked_button, clicked_position, clicked_time = mouse.wait_press()
        for i, button in enumerate(buttons):
            if button.overlapping_with_position(clicked_position):
                return i

    return buttons, i

def show_prelude_message(video_path):
    "Show the instruction page before video playback"

    # Get the filename from the video path
    filename = os.path.basename(video_path)  # Get the filename, including extension
    video_number = filename.split('.')[0]  # Split on '.' and take the first part, i.e., the numeric part of the filename

    # Define the mapping between video IDs and instruction messages
    message_mapping = {
        "1": "Avoid obstacles and drive straight through the intersection.",
        "2": "Avoid obstacles and drive straight through the intersection.",
        "3": "Avoid obstacles and turn left at the intersection.",
        "4": "Avoid obstacles and turn left at the intersection.",
        "5": "Avoid obstacles and turn left at the intersection."
        # Additional video paths and corresponding instructions can be added here
    }

    # Get the instruction message from the video ID
    message = message_mapping.get(video_number, "Unknown task")

    screen = stimuli.BlankScreen()

    # Create the instruction text
    Text = expyriment.stimuli.TextLine(text=message, position=(0, 100), text_size=50, text_colour=expyriment.misc.constants.C_WHITE)
    Text.preload()
    Text.plot(screen)

    # Create the confirmation button
    button_ok = stimuli.Rectangle((100, 100), position=(0, -50), colour=(0, 255, 0))
    Text_ok = stimuli.TextLine(text="OK", position=button_ok.position, text_size=40, text_colour=expyriment.misc.constants.C_WHITE)
    # Draw the button and text separately
    button_ok.plot(screen)
    Text_ok.plot(screen)

    screen.present()  # Present the page

    # Wait for mouse click on the confirmation button
    mouse = io.Mouse()
    while True:
        clicked_button, clicked_position, clicked_time = mouse.wait_press()
        if button_ok.overlapping_with_position(clicked_position):
            screen.clear_surface()  # Clear the page
            break  # Exit the loop and continue to the next experiment step

def create_slider(text):
    "Create a slider for a 7-point Likert scale. Participants click a position on the slider, and the selected scale value is returned."
    # Create a window
    #Stimulus screen
    screen = stimuli.BlankScreen()
    #Create the slider stimulus using a Rectangle.
    square_size = (500, 15)
    square = stimuli.Rectangle(square_size, colour=(255, 255, 255),position=(0,0))
    square.preload()
    square.plot(screen)
    Text = expyriment.stimuli.TextLine(text=text,
                                       position=(0, 100),
                                       text_colour=expyriment.misc.constants.C_WHITE, text_size=50)
    Text.preload()
    Text.plot(screen)

    text_labels = ["1", "2", "3", "4",
                   "5","6","7"]
    # Calculate the x-coordinates of the left and right boundaries of the square
    left = square.position[0] - square_size[0] / 2
    right = square.position[0] + square_size[0] / 2
    # Create six small squares and place them above the square
    small_square_size = (4, 20)
    for i in range(7):
        x = left + (i) * square_size[0] / 6  # Calculate the x-coordinate of the small square
        y = square.position[1] + square_size[1] / 2 + small_square_size[1] / 2  # Calculate the y-coordinate of the small square
        small_square = stimuli.Rectangle(small_square_size, position=(x, y), colour=(255, 255, 255))
        small_square.preload()
        small_square.plot(screen)

        text = stimuli.TextLine(text_labels[i], position=(x, y - 70),text_size=40, text_colour=expyriment.misc.constants.C_WHITE)
        text.rotate(45)  # Set the rotation angle
        text.preload()
        text.plot(screen)

    screen.present()
    # Create the mouse object
    mouse = io.Mouse()


    while True:
        clicked_button, clicked_position, clicked_time = mouse.wait_press()
        if clicked_button is not None:
            if square.overlapping_with_position(clicked_position):
                x, y = clicked_position
                normalized_x = (x - left) / square_size[0]  # Convert the x-coordinate to a value from 0 to 1
                break
    screen.clear_surface()
    return normalized_x
def final_decision():
    "Present the final decision choice"


    screen = stimuli.BlankScreen()

    # Create an image stimulus object
    Text=expyriment.stimuli.TextLine(text=" Do you choose to trust the AI's choice? ",position=(0,100), text_size=50,text_colour=expyriment.misc.constants.C_WHITE)# Replace the image path with the actual image path
    Text.preload()
    Text.plot(screen)
    button_trust = stimuli.Rectangle((100,100), position=( -100 , -50), colour=(0,255,0))
    button_nottrust = stimuli.Rectangle((100,100), position=( 100 ,-50), colour=(255,0,0))
    Text_trust = stimuli.TextLine(text="Trust", position=button_trust.position, text_size=30,text_colour=expyriment.misc.constants.C_WHITE)
    Text_nottrust = stimuli.TextLine(text="Distrust", position=button_nottrust.position, text_size=30,text_colour=expyriment.misc.constants.C_WHITE)
    button_trust.plot(Text_trust)
    button_nottrust.plot(Text_nottrust)
    button_trust.plot(screen)
    button_nottrust.plot(screen)
    Text_trust.plot(screen)
    Text_nottrust.plot(screen)
    #picture_stimulus.preload()
    buttons=[button_nottrust,button_trust]
    Text_timer = stimuli.TextLine(text="Please make a decision within 3 seconds.", position=(0, 200), text_size=30, text_colour=(255, 255, 0))
    Text_timer.preload()
    Text_timer.plot(screen)
    screen.present()

    # Return the button value selected by mouse click
    mouse = io.Mouse()
    while True:
        clicked_button, clicked_position, clicked_time = mouse.wait_press()
        for i, button in enumerate(buttons):
            if button.overlapping_with_position(clicked_position):
                return i, clicked_time
            
            
def show_run_file_instruction(video_path):
    "Show the page prompting the user to run the specified file"
    
    # Get the filename from the video path
    filename = os.path.basename(video_path)  # Get the filename, including extension
    video_number = filename.split('.')[0]  # Split on '.' and take the first part, i.e., the numeric part of the filename
    
    screen = stimuli.BlankScreen()

    # Create the instruction text and display the video number
    Text = expyriment.stimuli.TextLine(text=f"Please run switch_steeringwheel_0{video_number} on the platform.", position=(0, 100), text_size=50,text_colour=expyriment.misc.constants.C_WHITE)
    Text.preload()
    Text.plot(screen)

    # Create the confirmation button
    button_ok = stimuli.Rectangle((100, 100), position=(0, -50), colour=(0, 255, 0))
    Text_ok = stimuli.TextLine(text="OK", position=button_ok.position, text_size=40, text_colour=expyriment.misc.constants.C_WHITE)
    # Draw the button and text separately
    button_ok.plot(screen)
    Text_ok.plot(screen)

    screen.present()  # Present the page

    # Wait for mouse click on the confirmation button
    mouse = io.Mouse()
    while True:
        clicked_button, clicked_position, clicked_time = mouse.wait_press()
        if button_ok.overlapping_with_position(clicked_position):
            screen.clear_surface()  # Clear the page
            break  # Exit the loop and continue to the next experiment step
            
def self_drive():
    "Present the final decision choice"
    screen = stimuli.BlankScreen()
    # Create an image stimulus object
    Text=expyriment.stimuli.TextLine(text=" Did you success ? ",position=(0,100), text_size=50,text_colour=expyriment.misc.constants.C_WHITE)
    Text.preload()
    Text.plot(screen)
    button_trust = stimuli.Rectangle((100,100), position=( -100 , -50), colour=(0,255,0))
    button_nottrust = stimuli.Rectangle((100,100), position=( 100 ,-50), colour=(255,0,0))
    Text_trust = stimuli.TextLine(text="Success", position=button_trust.position, text_size=25,text_colour=expyriment.misc.constants.C_WHITE)
    Text_nottrust = stimuli.TextLine(text="Fail", position=button_nottrust.position, text_size=30,text_colour=expyriment.misc.constants.C_WHITE)
    button_trust.plot(Text_trust)
    button_nottrust.plot(Text_nottrust)
    button_trust.plot(screen)
    button_nottrust.plot(screen)
    Text_trust.plot(screen)
    Text_nottrust.plot(screen)
    #picture_stimulus.preload()
    buttons=[button_nottrust,button_trust]
    screen.present()

    #Return the button value selected by mouse click
    mouse = io.Mouse()
    while True:
        clicked_button, clicked_position, clicked_time = mouse.wait_press()
        for i, button in enumerate(buttons):
            if button.overlapping_with_position(clicked_position):
                return i
            
            
def present_ai_result(probability):
    """
    Present "AI is correct" or "AI is not correct" according to the given probability
    
    :param probability: Probability that the AI is correct (between 0.0 and 1.0)
    :return: int, Indicates whether the AI is correct (1 for correct, 0 for incorrect)
    """
    screen = stimuli.BlankScreen()
    
    # Determine the displayed content according to the probability
    if random.random() < probability:
        result_text = "AI can successfully avoid obstacles in this round."
        result = 1
    else:
        result_text = "AI can't successfully avoid obstacles in this round."
        result = 0
    
    # Create the text stimulus object
    result_stimulus = stimuli.TextLine(text=result_text, position=(0, 100), text_size=50, text_colour=expyriment.misc.constants.C_WHITE)
    result_stimulus.preload()
    result_stimulus.plot(screen)
    
    # Create the confirmation button
    button_ok = stimuli.Rectangle((100, 100), position=(0, -50), colour=(0, 255, 0))
    Text_ok = stimuli.TextLine(text="OK", position=button_ok.position, text_size=40, text_colour=expyriment.misc.constants.C_WHITE)
    # Draw the button and text separately
    button_ok.plot(screen)
    Text_ok.plot(screen)

    screen.present()  # Present the page

    # Wait for mouse click on the confirmation button
    mouse = io.Mouse()
    while True:
        clicked_button, clicked_position, clicked_time = mouse.wait_press()
        if button_ok.overlapping_with_position(clicked_position):
            screen.clear_surface()  # Clear the page
            break  # Exit the loop and continue to the next experiment step
            
    # Return whether the AI is correct
    return result
    
            
def feedback(feedback, trust, self_drive):
    """
    Generate the feedback stimulus and compute the corresponding score
    Inputs:
        - feedback: Whether the AI decision is correct (0 or 1)
        - trust: Whether the participant trusts the AI decision (0 or 1)
        - self_drive: Whether manual driving succeeds (0 or 1)
    Returns:
        - Reward score for the current trial
    """
    global total_reward, experiment_count  # Declare global variables
    experiment_count += 1  # Increment the trial counter on each function call
    
    screen = stimuli.BlankScreen()  # Create a stimulus screen
    button_reward_right = stimuli.Rectangle((100, 100), position=(0, 0), colour=(0, 255, 0))
    button_reward_wrong = stimuli.Rectangle((100, 100), position=(0, 0), colour=(255, 0, 0))
    
    # Generate reward feedback content and score for the current trial based on the conditions
    if trust == 1 and feedback == 1:
        reward = 20
        button_reward = button_reward_right
        feedback_text = "Congratulations! You are correct! This is your reward!"
    elif trust == 1 and feedback == 0:
        reward = -20
        button_reward = button_reward_wrong
        feedback_text = "Sorry! You are wrong! This is your loss!"
    elif trust == 0 and self_drive == 1:
        reward = 5
        button_reward = button_reward_right
        feedback_text = "Congratulations! You are correct! This is your reward!"
    elif trust == 0 and self_drive == 0:
        reward = -5
        button_reward = button_reward_wrong
        feedback_text = "Sorry! You are wrong! This is your loss!"
    
    # Update the total reward
    total_reward += reward
    
    # Reward feedback text
    feedback_stimulus = stimuli.TextLine(text=feedback_text, position=(0, 150), text_size=50,
                                         text_colour=expyriment.misc.constants.C_WHITE)
    # Display the current reward score
    reward_stimulus = stimuli.TextLine(text=str(reward), position=button_reward.position, text_size=40,
                                       text_colour=expyriment.misc.constants.C_WHITE)
    # Display the total reward score
    total_reward_text = f"Total Reward: {total_reward}"
    total_reward_stimulus = stimuli.TextLine(text=total_reward_text, position=(0, -150), text_size=50,
                                             text_colour=expyriment.misc.constants.C_WHITE)
    # Display the trial count
    experiment_count_text = f"Experiment: {experiment_count}"
    experiment_count_stimulus = stimuli.TextLine(text=experiment_count_text, position=(400, 500), text_size=50,
                                                 text_colour=(135, 206, 250))

    # Draw all elements on the screen
    feedback_stimulus.plot(screen)
    button_reward.plot(screen)
    reward_stimulus.plot(screen)
    total_reward_stimulus.plot(screen)
    experiment_count_stimulus.plot(screen)
    screen.present()
    
    # Return the result selected by mouse click
    mouse = io.Mouse()
    while True:
        clicked_button, clicked_position, clicked_time = mouse.wait_press()
        if button_reward.overlapping_with_position(clicked_position):
            return reward


    
VIDEO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mpg")
video_paths = [os.path.join(VIDEO_DIR, f"{difficulty}.mpg") for difficulty in range(1, 6)]
video_paths_1 = [os.path.join(VIDEO_DIR, "1.1.mpg"), os.path.join(VIDEO_DIR, "1.2.mpg")]  # Video paths for task difficulty 1: AI success and failure
video_paths_2 = [os.path.join(VIDEO_DIR, "2.1.mpg"), os.path.join(VIDEO_DIR, "2.2.mpg")]  # Video paths for task difficulty 2: AI success and failure
video_paths_3 = [os.path.join(VIDEO_DIR, "3.1.mpg"), os.path.join(VIDEO_DIR, "3.2.mpg")]  # Video paths for task difficulty 3: AI success and failure
video_paths_4 = [os.path.join(VIDEO_DIR, "4.1.mpg"), os.path.join(VIDEO_DIR, "4.2.mpg")]  # Video paths for task difficulty 4: AI success and failure
video_paths_5 = [os.path.join(VIDEO_DIR, "5.1.mpg"), os.path.join(VIDEO_DIR, "5.2.mpg")]  # Video paths for task difficulty 5: AI success and failure

# The first 40 trials include each video 8 times
video_sequence_first_half = [video_paths[0]] * 8 + [video_paths[1]] * 8 + [video_paths[2]] * 8 + [video_paths[3]] * 8 + [video_paths[4]] * 8
random.shuffle(video_sequence_first_half)

# The last 40 trials include each video 8 times
video_sequence_second_half = [video_paths[0]] * 8 + [video_paths[1]] * 8 + [video_paths[2]] * 8 + [video_paths[3]] * 8 + [video_paths[4]] * 8
random.shuffle(video_sequence_second_half)

# Combine the two parts
video_sequence = video_sequence_first_half + video_sequence_second_half


# Preload all videos and save the video objects and durations
preloaded_videos = {}
video_durations = {}  # Dictionary storing video durations

for path in video_paths + video_paths_1 + video_paths_2 + video_paths_3 + video_paths_4 + video_paths_5:
    video_stimulus = expyriment.stimuli.Video(path)
    video_stimulus.preload()
    preloaded_videos[path] = video_stimulus
    video_durations[path] = video_stimulus.length  # Store the video duration
    
  
expyriment.control.start()  # Start the experiment


for i_trial in range(N_TRIALS):
    # Create a fixation cross stimulus
    center_point = expyriment.stimuli.FixCross(size=(20, 20), colour=expyriment.misc.constants.C_WHITE)

    # Display the fixation cross stimulus
    center_point.present()

    # Wait for the user key response
    exp.keyboard.wait()  # Wait for any key



    # Play the video stimulus
    video_path = video_sequence[i_trial]  # Video path
    video_duration_1 = video_durations[video_path]
    video_stimulus_1 = preloaded_videos[video_path]
    
    show_prelude_message(video_path)

    video_stimulus_1.play()
    video_stimulus_1.present()
    video_stimulus_1.wait_end()
    video_stimulus_1.stop()

    

    
    trust, clicked_time = final_decision()
    if trust == 0:
        show_run_file_instruction(video_path)

    self_dificulty = create_slider("How hard are you think in this task?")  # Participant-rated task difficulty
    trust_level = create_slider("How confident are you in AI's decision making?")  # Confidence in the participant decision
    #Ask whether the participant trusts the AI

    probabilities = [0.5, 0.5]  # 50% successful obstacle avoidance (.1.mpg), 50% failed obstacle avoidance (.2.mpg)
    
    # Play different videos based on the first video choice
    #Difficulty 1
    if video_path == video_paths[0]:
        task_dicifficulty = 1
        video_path_result = random.choices(video_paths_1, probabilities)[0] #Randomly choose success or failure
        if video_path_result == video_paths_1[0]:
            feedback_value = 1
        elif video_path_result == video_paths_1[1]:
            feedback_value  = 0
    #Difficulty 2
    elif video_path == video_paths[1]:
        task_dicifficulty = 2
        video_path_result =random.choices(video_paths_2, probabilities)[0]
        if video_path_result == video_paths_2[0]:
            feedback_value  = 1
        elif video_path_result == video_paths_2[1]:
            feedback_value  = 0
    #Difficulty 3
    elif video_path == video_paths[2]:
        task_dicifficulty = 3
        video_path_result =random.choices(video_paths_3, probabilities)[0]
        if video_path_result == video_paths_3[0]:
            feedback_value  = 1
        elif video_path_result == video_paths_3[1]:
            feedback_value  = 0
    #Difficulty 4
    elif video_path == video_paths[3]:
        task_dicifficulty = 4
        video_path_result =random.choices(video_paths_4, probabilities)[0]
        if video_path_result == video_paths_4[0]:
            feedback_value  = 1
        elif video_path_result == video_paths_4[1]:
            feedback_value  = 0    
    #Difficulty 5
    elif video_path == video_paths[4]:
        task_dicifficulty = 5
        video_path_result =random.choices(video_paths_5, probabilities)[0]
        if video_path_result == video_paths_5[0]:
            feedback_value  = 1
        elif video_path_result == video_paths_5[1]:
            feedback_value  = 0    
                    
    if trust == 1:
        video_stimulus_2 = preloaded_videos[video_path_result]
        video_duration_2 = video_durations[video_path_result]
        
        video_stimulus_2.play()
        video_stimulus_2.present()
        video_stimulus_2.wait_end()
        video_stimulus_2.stop()

        numbers = 0
        self_drive_value = 1 #When using automated driving, manual-driving success is set to 100%. Consider replacing this with an estimated individual ability probability.
    elif trust == 0:# If the participant does not trust the AI, do not play the video
        self_drive_value = self_drive()
        feedback_value = present_ai_result(0.5)


    reward = feedback(feedback_value,trust,self_drive_value)
    exp.data.add(
        [i_trial, task_dicifficulty, self_drive_value, feedback_value, trust, clicked_time, trust_level, reward, self_dificulty])

# End the experiment
expyriment.control.end()




