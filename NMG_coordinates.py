import tkinter as tk
from PIL import Image, ImageTk
import cv2
import math as math
path = "C:/Users/20192478/Desktop/bep image analysis/microscope_images/Example_images/laatsteoni.png"
mm_per_pixel = 0.001075
threshold_start = 95
threshold_end = 255
centerx = 'x'
centery =  'y'
cell_coordinates_mm_oni = []
class ImageApp:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Image Viewer")

        # Load and display the image
        self.image = Image.open(image_path)
        self.tk_image = ImageTk.PhotoImage(self.image)

        # Create a canvas with scrollbars
        
        self.canvas = tk.Canvas(root, width=10, height=10, scrollregion=(0, 0, self.image.width, self.image.height))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbars
        self.scrollbar_x = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scrollbar_y = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure canvas to use scrollbars
        self.canvas.config(xscrollcommand=self.scrollbar_x.set, yscrollcommand=self.scrollbar_y.set)

        # Display coordinates
        self.coordinates_label = tk.Label(root, text="")
        self.coordinates_label.pack()

        # Calculate center coordinates
        self.image_center = (self.image.width // 2, self.image.height // 2)

        # List to store clicked relative coordinates
        self.clicked_coordinates = []

        # Bind mouse motion event to update coordinates
        self.canvas.bind("<Motion>", self.update_coordinates)

        # Bind mouse click event to save relative coordinates and display a 2x2 pixel square marker
        self.canvas.bind("<Button-1>", self.save_coordinates)

        # Add a "Detect Cells" button
        self.detect_button = tk.Button(root, text="Detect Cells", command=self.detect_cells)
        self.detect_button.pack(side=tk.TOP, padx=10, pady=10)

        self.start_coordinates_label = tk.Label(root, text="Coordinate startpoint (x,y)")
        self.start_coordinates_label.pack()

        self.start_coordinatex = tk.Entry(root,textvariable=centerx, width = 3 )
        self.start_coordinatex.pack()

        self.start_coordinatey = tk.Entry(root,textvariable=centery,width = 3 )
        self.start_coordinatey.pack()


    def update_coordinates(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        startx = self.start_coordinatex.get()
        starty = self.start_coordinatey.get()
        # Calculate relative coordinates
        rel_x = x - self.image_center[0] 
        rel_y = self.image_center[1] - y 
        
         ## rotate the image 45 degree clockwise
        rel_x_rotated = rel_x*math.cos(math.radians(45)) + rel_y*math.sin(math.radians(45))
        rel_y_rotated = -rel_x*math.sin(math.radians(45)) + rel_y*math.cos(math.radians(45))

         ## go to startposition in scan
        rel_x_start = rel_x_rotated + float(startx)/mm_per_pixel
        rel_y_start = rel_y_rotated + float(starty)/mm_per_pixel
        
        ## mirror in x
        rel_x_mirrored = -rel_x_start   
        rel_y_mirrored = rel_y_start
       
         

        xoni = rel_x_mirrored * mm_per_pixel
        yoni = rel_y_mirrored * mm_per_pixel
      

        # Update coordinates label
        self.coordinates_label.config(text=f"Coordinates ONI (mm) : ({round(xoni,2)},{round(yoni,2)})")
        #"Center Coordinates: ({round(rel_x_mm,2)}, {round(rel_y_mm,2)}) 
    def save_coordinates(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        startx = self.start_coordinatex.get()
        starty = self.start_coordinatey.get()
        # Calculate relative coordinates
        rel_x = x - self.image_center[0] 
        rel_y = self.image_center[1] - y 
       
        
       
         ## rotate the image 45 degree clockwise
        rel_x_rotated = rel_x*math.cos(math.radians(45)) + rel_y*math.sin(math.radians(45))
        rel_y_rotated = -rel_x*math.sin(math.radians(45)) + rel_y*math.cos(math.radians(45))

         ## go to startposition in scan
        rel_x_start = rel_x_rotated + float(startx)/mm_per_pixel
        rel_y_start = rel_y_rotated + float(starty)/mm_per_pixel
        
        ## mirror in x and y
        rel_x_mirrored =  -rel_x_start   
        rel_y_mirrored = rel_y_start
       
         

        xoni = rel_x_mirrored * mm_per_pixel
        yoni = rel_y_mirrored * mm_per_pixel
        
        
       
        cell_coordinates_mm_oni.append((round(xoni,4),round(yoni,4)))

        print('oni : ', cell_coordinates_mm_oni)
        

        # Save clicked relative coordinates
        self.clicked_coordinates.append((rel_x, rel_y))
        #print(f"Clicked Relative Coordinates: {self.clicked_coordinates}")
        
        # Display a 2x2 pixel square marker at the clicked position on the Canvas widget
        marker_size = 4  # Set to 1 for a 2x2 pixel square
        self.marker = self.canvas.create_rectangle(x - marker_size // 2, y - marker_size // 2,x + marker_size // 2, y + marker_size // 2, outline="red", fill="red")

    def detect_cells(self):
        # Add your code here to detect cells
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

        # Example: Thresholding
        ret, binary_image = cv2.threshold(image, threshold_start, threshold_end, cv2.THRESH_BINARY)

        # Find contours (cells)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Extract coordinates of cell centroids relative to the center
        cell_coordinates_mm_oni =[]
        cell_coordinates_mm = []
        cell_coordinates = []
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cell_coordinates.append((cX, cY))
                cv2.circle(image, (cX, cY), 3, ((0, 0, 255)), -1)  # (0, 255, 0) is the color (green), -1 indicates filled circle


                
                
                startx = self.start_coordinatex.get()
                starty = self.start_coordinatey.get()
                # Calculate relative coordinates
                rel_x = cX - self.image_center[0] 
                rel_y = self.image_center[1] - cY 

                
                 ## go to startposition in scan
                rel_x_rot_pos = rel_x_rotated + float(startx)/mm_per_pixel
                rel_y_rot_pos = rel_y_rotated + float(starty)/mm_per_pixel
                
                ## mirror in x and y
                rel_x_mirrored = -rel_x_rot_pos   
                rel_y_mirrored = -rel_y_rot_pos
            
                ## rotate the image 45 degree clockwise
                rel_x_rotated = rel_x*math.cos(45) + rel_y*math.sin(45)
                rel_y_rotated = -rel_x*math.sin(45 + rel_y*math.cos(45))


                xoni = rel_x_mirrored * mm_per_pixel
                yoni = rel_y_mirrored * mm_per_pixel

               
                cell_coordinates_mm_oni.append((round(xoni,4),round(yoni,4)))



                

        print('Cell Coordinates on Oni : ', len(cell_coordinates_mm_oni))

        ## cell coordinates in image

       

        ## cell coordinates on oni
        

        
        

        cv2.imshow("cell detection result", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        
def main():
    image_path = path
    root = tk.Tk()
    app = ImageApp(root, image_path)
    root.mainloop()
    

if __name__ == "__main__":
    main()
