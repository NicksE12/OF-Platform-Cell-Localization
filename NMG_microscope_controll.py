import tkinter as tk
import cv2
import uc2rest as uc2
import time
import threading
import math as calc

## initialize coordinates
x = 0
y = 0
movex = 0
movey = 0
img_count = 0
### Initialize the motors
serialport = "COM7"
if 'ESP32' not in locals():
    ESP32 = uc2.UC2Client(serialport=serialport)
_state = ESP32.state.get_state()
print(_state)

### Open camera
vid = cv2.VideoCapture(0) 
def show_webcam():
    while True:
        ret, frame = vid.read()

        if not ret:
            print("Error: Could not read a frame.")
            break
        
        height, width, _ = frame.shape
        center = (width // 2, height // 2)  # Calculate the center of the frame

        # Draw a dot in the center of the frame
        cv2.circle(frame, center, 70, (0, 0, 255), 0)  # The last argument -1 fills the circle
        cv2.circle(frame, center, 5, (0, 0, 255), -1)
        
        

        cv2.imshow("Openflexure Microscope, N.M.G.", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            vid.release()
            cv2.destroyAllWindows()
            break

### Control motor with keyboard
def move_left(pressed):
    if pressed:
        ESP32.motor.move_forever(speed=(0,10000,0,0), is_stop=False)

    else: 
        ESP32.motor.move_forever(speed=(0,10000,0,0), is_stop=True)
def move_right(pressed):
    if pressed:
        ESP32.motor.move_forever(speed=(0,-10000,0,0), is_stop=False)

    else: 
        ESP32.motor.move_forever(speed=(0,-10000,0,0), is_stop=True)
def move_up(pressed):
    if pressed:
        ESP32.motor.move_forever(speed=(10000,0,0,0), is_stop=False)

    else: 
        ESP32.motor.move_forever(speed=(10000,0,0,0), is_stop=True)
def move_down(pressed):
    if pressed:
        ESP32.motor.move_forever(speed=(-10000,0,0,0), is_stop=False)

    else: 
        ESP32.motor.move_forever(speed=(-10000,0,0,0), is_stop=True)
def move_in(pressed, zoomspeed= 20000):
    if pressed:
        ESP32.motor.move_forever(speed=(0,0,0,zoomspeed), is_stop=False)
    else: 
        ESP32.motor.move_forever(speed=(0,0,0,zoomspeed), is_stop=True)
def move_out(pressed, zoomspeed = 20000):
    if pressed:
        ESP32.motor.move_forever(speed=(0,0,0,-zoomspeed), is_stop=False)

    else: 
        ESP32.motor.move_forever(speed=(0,0,0,-zoomspeed), is_stop=True)

### Move stage by .. steps (input in mm)
def mm_to_steps(input):
    steps_in_mm = input
    steps_steps = steps_in_mm / 0.00004
    return steps_steps
def imgleft(pressed = False):
    global x, movex, movey
    if pressed == True:
        steps = mm_to_steps(nr_steps.get())
        ESP32.motor.move_xyza(steps=(-steps,steps,0,0), speed=(10000,10000,0,0), acceleration= (None,None,None,None), is_blocking=True)
        x = x - nr_steps.get()
        update_label()
        movex = movex - steps
        movey = movey + steps
        print(movex,movey)
def imgright(pressed = False):
    global x, movex, movey
    if pressed == True:
        steps = mm_to_steps(nr_steps.get())
        ESP32.motor.move_xyza(steps=(steps,-steps,0,0), speed=(10000,10000,0,0), acceleration= (None,None,None,None), is_blocking=True)
        x = x + nr_steps.get()
        update_label()
        movex = movex + steps
        movey = movey - steps
        print(movex,movey)
def imgup(pressed = False):
    global y, movex, movey
    if pressed == True:
        steps = mm_to_steps(nr_steps.get())
        ESP32.motor.move_xyza(steps=(-steps,-steps,0,0), speed=(10000,10000,0,0), acceleration= (None,None,None,None), is_blocking=True)
        y = y + nr_steps.get()
        update_label()
        movex = movex - steps
        movey = movey - steps    
        print(movex,movey)  
def imgdown(pressed = False):
    global y, movex, movey
    if pressed == True:
        steps = mm_to_steps(nr_steps.get())
        ESP32.motor.move_xyza(steps=(steps,steps,0,0), speed=(10000,10000,0,0), acceleration= (None,None,None,None), is_blocking=True)
        y = y - nr_steps.get()
        update_label()
        movex = movex + steps
        movey = movey + steps
        print(movex,movey)

### Microscope functionalities
def takepicture(pressed = False):
    if pressed == True:
        print("OKE HET WERKT!")
        global img_count
        
        ret, frame = vid.read() 
        
        

        #gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Display the resulting frame
        if img_count != 0:
            file_path = 'C:/Users/20192478/Desktop/bep image analysis/microscope_images/'+file_name.get()+'{}.jpg'.format(img_count)
        else:
            file_path = 'C:/Users/20192478/Desktop/bep image analysis/microscope_images/'+file_name.get()+'.jpg'

        cv2.imwrite(file_path, frame)
        print("Saved image as:", file_path)
        img_count += 1
def autozoom(pressed = False):
    if pressed == True:
        Startpoint = Startpoint_zoom_in.get()
        Difference = Difference_over_maxlaplacian.get()
        print('OKE DE MICROSCOOP ZOEKT NU AUTOMATISCH NAAR EEN SCHERP PUNT')
        print(Startpoint)
        print(Difference)

        ESP32.motor.move_z(steps= Startpoint, speed= 10000, is_blocking=True)
        print('zoomed out')
                
        time.sleep(0.2)
        maxlaplacian = 0
        ESP32.motor.move_forever(speed=(0,0,0,-10000), is_stop=False)
        print('fast zoom search')
        while True:
            ret, frame = vid.read()
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray_frame, cv2.CV_64F).var()
            if laplacian > maxlaplacian :
                    maxlaplacian = laplacian
                        
            elif laplacian < maxlaplacian - Difference:
                print('max = ',maxlaplacian, '        current = ', laplacian)
                
                break
        ESP32.motor.move_forever(speed=(0,0,0,-10000), is_stop=True)
         
        print('done')
        time.sleep(0.3)
def scan(pressed = False, frame = 25000):
    global img_count
    if pressed == True:
        img_count = 1

        height = scan_height.get()
        width = scan_width.get()
        framex = frame *  (640/1120)
        framey = frame * (480/1120)

        print('OKE DE SCAN WERKT')
        print(height)
        print(width)
        if width%2 == 0:
            print("error: the width has to be an odd numer")
        elif height%2 == 0:
            print('error: the height has to be an odd number')
        else:
            print('ja')

            #### go to start point
            x_startpoint =  ((width-1)/2) * framey
            y_startpoint =  ((height-1)/2) * framex
            ESP32.motor.move_xyza(steps=(x_startpoint, y_startpoint,0,0), speed=(10000,10000,0,0), acceleration= (None,None,None,None), is_blocking=True)
    
            ### ACTUAL SCAN
            autozoom(pressed= True)
            takepicture(pressed = True)
            for i in range(width-1):
                    ESP32.motor.move_x(steps=-framex, speed= 10000, is_blocking=True)
                    autozoom(pressed= True)
                    takepicture(pressed = True)

            for j in range(int(((height-1)/2))):
                ESP32.motor.move_a(steps=-framey, speed= -10000, is_blocking=True)
                autozoom(pressed= True)
                takepicture(pressed = True)

                for i in range(width-1):
                    ESP32.motor.move_x(steps=framex, speed= 10000, is_blocking=True)
                    autozoom(pressed= True)
                    takepicture(pressed = True)
                
                ESP32.motor.move_a(steps=-framey, speed= -10000, is_blocking=True)
                autozoom(pressed= True)
                takepicture(pressed = True)

                for i in range(width-1):
                    ESP32.motor.move_x(steps=-framex, speed= 10000, is_blocking=True)
                    autozoom(pressed= True)
                    takepicture(pressed = True)
                
            ### go home
            
            ESP32.motor.move_xyza(steps=(x_startpoint, y_startpoint,0,0), speed=(10000,10000,0,0), acceleration= (None,None,None,None), is_blocking=True)
            img_count = 0

###  Coordinate system
def calibrate_homepoint(pressed = False):
    global x, y, movex, movey
    x=0
    y=0
    movex=0
    movey=0
    #ESP32.motor.move_xyza(steps=(95000,-95000,0,0), speed=(10000,10000,0,0), acceleration= (None,None,None,None), is_blocking=True)
    print('Calibrate')
    update_label()
def go_home(pressed = False):
    global x, y, movex, movey
    ESP32.motor.move_xyza(steps=(-movex,-movey,0,0), speed=(10000,10000,0,0), acceleration= (None,None,None,None), is_blocking=True)
    x = 0
    y = 0
    movex=0
    movey=0
    print("Home")
    update_label()

### Movement using arrow keys
def on_key(event):
    if event.keysym == "Left":
        move_left(True)
    elif event.keysym == "Right":
        move_right(True)
    elif event.keysym == "Up":
        move_up(True)
    elif event.keysym == "Down":
        move_down(True)
    elif event.keysym == "i":
        move_in(True)
    elif event.keysym == "o":
        move_out(True)
    elif event.keysym == 'q':
        root.destroy()
def on_key_release(event):
    if event.keysym == "Left":
        move_left(False)
    elif event.keysym == "Right":
        move_right(False)
    elif event.keysym == "Up":
        move_up(False)
    elif event.keysym == "Down":
        move_down(False)
    elif event.keysym == "i":
        move_in(False)
    elif event.keysym == "o":
        move_out(False)


### Threads (allows for displaying, computing calculation, and snapsave the camera the same time)

webcam_thread = threading.Thread(target=show_webcam, daemon=True)
webcam_thread.start()
takepicture_thread = threading.Thread(target=takepicture, daemon=True)
takepicture_thread.start()
autozoom_thread = threading.Thread(target=autozoom, daemon=True)
autozoom_thread.start()

### Tkinter GUI code and layout
root = tk.Tk()
root.title("Microscope Control")

def Picture_on_button_click():
    takepicture(True)  
def Scan_on_button_click():
    scan(True)
def Autozoom_on_button_click():
    autozoom(True)
def imgup_on_button_click():
    imgup(True)
def imgdown_on_button_click():
    imgdown(True)
def imgright_on_button_click():
    imgright(True)
def imgleft_on_button_click():
    imgleft(True)
def Calibrate_homepoint_click():
    calibrate_homepoint(True)
def go_home_click():
    go_home(True)
def update_label():
    label_coordinates.config(text=f"Coordinates: ({x}, {y})")

# Variables to store the values entered in the text entries
Startpoint_zoom_in = tk.IntVar()
Difference_over_maxlaplacian = tk.IntVar()
Startpoint_zoom_in.set(5000)
Difference_over_maxlaplacian.set(10)
scan_height = tk.IntVar()
scan_width = tk.IntVar()
scan_height.set(2)
scan_width.set(2)
nr_steps = tk.DoubleVar()
nr_steps.set(0)
file_name = tk.StringVar()

# Labels
label_movement_instruction = tk.Label(root, text="Use arrow keys to move the sample. \n Press 'i' to zoom in and 'o' to zoom out\n\n Press 'q' to leave")
label_movement_instruction.grid(row=0, column=0, columnspan=3, pady=(10, 0))

label_startpoint_zoom_in = tk.Label(root, text="Startpoint Zoom In:")
label_startpoint_zoom_in.grid(row=1, column=0, sticky=tk.E, padx=10, pady=(20, 0))

label_difference_over_maxlaplacian = tk.Label(root, text="Diff Max Laplacian:")
label_difference_over_maxlaplacian.grid(row=2, column=0, sticky=tk.E, padx=10)

label_scan_height = tk.Label(root, text="Scan Height:")
label_scan_height.grid(row=3, column=0, sticky=tk.E, padx=10, pady=(20, 0))

label_scan_width = tk.Label(root, text="Scan Width:")
label_scan_width.grid(row=4, column=0, sticky=tk.E, padx=10)

label_coordinates = tk.Label(root, text=f"Coordinates (mm)): ({x}, {y})")
label_coordinates.grid(row = 9, column = 1, pady=20)

label_filename = tk.Label(root, text="Save file as : ")
label_filename.grid(row = 13, column = 0, padx =10)

# Entry Widgets
entry_startpoint_zoom_in = tk.Entry(root, textvariable=Startpoint_zoom_in)
entry_startpoint_zoom_in.grid(row=1, column=1, padx=10, pady=(20, 0))

entry_difference_over_maxlaplacian = tk.Entry(root, textvariable=Difference_over_maxlaplacian)
entry_difference_over_maxlaplacian.grid(row=2, column=1, padx=10)

entry_scan_height = tk.Entry(root, textvariable=scan_height)
entry_scan_height.grid(row=3, column=1, padx=10, pady=(20, 0))

entry_scan_width = tk.Entry(root, textvariable=scan_width)
entry_scan_width.grid(row=4, column=1, padx=10)

entry_nr_steps = tk.Entry(root, textvariable=nr_steps)
entry_nr_steps.grid(row=7, column=1, padx=10, pady=20)

entry_name = tk.Entry(root, textvariable = file_name)
entry_name.grid(row = 13, column = 1)

# Buttons
button_autozoom = tk.Button(root, text="Autozoom", command=Autozoom_on_button_click)
button_autozoom.grid(row=1, column=2, rowspan=2, pady=10, padx=10)

button_scan = tk.Button(root, text="Scan", command=Scan_on_button_click)
button_scan.grid(row=3, column=2, rowspan=2, pady=10, padx=10)

btn_up = tk.Button(root, text="Up (+y)", command=imgup_on_button_click)
btn_up.grid(row=6, column=1, pady=10)

btn_down = tk.Button(root, text="Down (-y)", command=imgdown_on_button_click)
btn_down.grid(row=8, column=1, pady=10)

btn_right = tk.Button(root, text="Right (+x)", command=imgright_on_button_click)
btn_right.grid(row=7, column=2, pady=10)

btn_left = tk.Button(root, text="Left (-x)", command=imgleft_on_button_click)
btn_left.grid(row=7, column=0, pady=10)

button_take_picture = tk.Button(root, text="Take a Picture", command=Picture_on_button_click)
button_take_picture.grid(row=13, column=2, padx=10, pady=10)

button_callibrate = tk.Button(root, text ="Calibrate", command=Calibrate_homepoint_click)
button_callibrate.grid(row = 9, column = 0, padx = 10, pady=10)

button_callibrate = tk.Button(root, text ="go to homepoint", command=go_home_click)
button_callibrate.grid(row = 9, column = 2, padx = 10, pady=10)

root.bind("<KeyPress>", on_key)
root.bind("<KeyRelease>", on_key_release)
root.mainloop()

vid.release()
cv2.destroyAllWindows()