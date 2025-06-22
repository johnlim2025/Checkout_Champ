import flet as ft
import keyboard
import threading
from queue import Queue
import time
import multiprocessing
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from CV import webcam_to_app as wc
import mysql.connector
import cv2
from flet import Image
from PIL import Image as PILImage
import io
import base64
import serial
texts = {}
barcode_to_item = {}
count = [0]
top_weight = [0]
last_scan = None
recent_item_scanned_flag = True
curr_detections = [] # list of item name to count seen by the CV model
scanned_items = {} # dict of item name to count scanned by the barcode scanner
in_scale_area = []
items_weight = {}
mydb = mysql.connector.connect(
        host="10.105.131.198",
        user="root",
        port = 3306,
        passwd="checkoutchamp",
        database="checkout"
    )
mycursor = mydb.cursor()

def main(page: ft.Page):
    theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.theme = theme

    def get_basket_summary():
        temp_dict = {}
        total_price = 0
        total_expected_weight = 0
        total_actual_weight = 0
        print(texts)
        for name in texts.keys():
            cur = texts[name]
            quantity = int(cur[1].value)
            sql = "SELECT item_price, price_flag, item_weight FROM items WHERE item_name = %s"
            mycursor.execute(sql, (name,))
            res = mycursor.fetchone()
            print("res", res)
            price = None
            price = res[0] 
            if res[1] == 1:
                temp_dict[name] = (sum(items_weight[name]), price, res[1])
                total_price += price * sum(items_weight[name])
                total_actual_weight += sum(items_weight[name])
                total_expected_weight += sum(items_weight[name])
            else:
                temp_dict[name] = (quantity, price, res[1])
                total_price += (price * quantity)
                total_actual_weight += res[2] * quantity
                total_expected_weight += res[2] * quantity
        
        return temp_dict, total_price, total_actual_weight, total_expected_weight
    
    def create_basket_listview():
        item_dict, total_price, total_actual_weight, total_expected_weight = get_basket_summary()
        basket_list = []

        # Create the ListView for the basket items and their quantities (this will be scrollable)
        items_list = []
        for name in item_dict.keys():
            quantity = item_dict[name][0]
            price = item_dict[name][1]
            flag = item_dict[name][2]

            if flag == 0:
                items_list.append(
                    ft.Row(
                        controls=[
                            ft.Text(f"{name}", size=12),
                            ft.Text(f"Unit Price: ${price:.2f}", size=12),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                )
                items_list.append(
                    ft.Row(
                        controls=[
                            ft.Text(f"  Quantity: {quantity}", size=10),
                        ],
                        alignment=ft.MainAxisAlignment.START
                    )
                )
            else:
                items_list.append(
                    ft.Row(
                        controls=[
                            ft.Text(f"{name}", size=12),
                            ft.Text(f"Unit Price: ${price:.2f}/lb", size=12),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                )
                items_list.append(
                    ft.Row(
                        controls=[
                            ft.Text(f"  Weight: {quantity}", size=10),
                        ],
                        alignment=ft.MainAxisAlignment.START
                    )
                )


        # Wrap the items in a ListView to make it scrollable
        scrollable_items_list = ft.ListView(controls=items_list, expand=1)

        # Add the scrollable items list to the basket list
        basket_list.append(scrollable_items_list)

        # Add total price at the bottom of the ListView
        basket_list.append(
            ft.Row(
                controls=[
                    ft.Text("Total Price:", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"${total_price:.2f}", size=20, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        return ft.Column(controls=basket_list), total_expected_weight

    def listen_for_barcode():
        barcode = ""
        while True:
            events = keyboard.record(until="enter")  # Capture all input until Enter
            barcode = "".join(event.name for event in events if event.event_type == "down" and event.name != "enter")
            if barcode:  # Ensure barcode is not empty
                print(f"Scanned barcode: {barcode}")
                sql = "SELECT * FROM items WHERE barcode_id = %s"
                mycursor.execute(sql, (barcode,))
                res = mycursor.fetchone()
                if res != None:
                    item_name = res[1]
                    # If item is already in texts, update its value
                    if item_name in texts:
                        cur = texts[item_name]
                        current_value = int(cur[1].value)
                        new_value = current_value + 1
                        update_text_widget(item_name, str(new_value))
                    else:
                        add_item_to_container(item_name, "1", ft.Colors.BLACK)
                            
                    print(f"Processed barcode: {barcode} for item: {item_name}")
                else:
                    print(f"Barcode not found: {barcode}")
                    popup = ft.AlertDialog(
                        content=ft.Text("Barcode Not Found in Database! Please Contact Manager"),
                        actions=[ft.TextButton("OK", on_click=lambda e: close_popup(popup))],
                        modal=True
                    )
                    page.open(popup)



    # Function to open the popup with the basket summary
    def show_basket_summary_popup():
        # Create the ListView for the basket items
        basket_listview, total_expected_weight = create_basket_listview()
    
        threshold = 0.1 * total_expected_weight
        actual_weight = read_bot_weight()
        weight =  float(actual_weight[:len(actual_weight) - 1])
        print(total_expected_weight)
        print(weight)


        if not (total_expected_weight - threshold <  weight < total_expected_weight + threshold):
            popup = ft.AlertDialog(
                title=ft.Text("Warning"),
                content=ft.Text(f"actual weight not within the threshold: expected - {total_expected_weight - threshold:.2f} ~ {total_expected_weight + threshold:.2f} actual - {weight:.2f}"),
                actions=[ft.TextButton("OK", on_click=lambda e: close_popup(popup))],
                modal=True
            )
            page.open(popup)
        else:
            # Create the popup to show the basket summary
            popup = ft.AlertDialog(
                title=ft.Text("Basket Summary"),
                content=basket_listview,
                actions=[
                    ft.TextButton("Close", on_click=lambda e: page.close(popup))
                ],
                modal=True
            )
            page.open(popup)
    
    def read_top_weight():
        while True:
            try:
                ser = serial.Serial('/dev/ttyUSB0', baudrate= 115200)
                line = ser.readline()
                decoded_line = line.decode('utf-8')
                break
            except:
                continue
        return decoded_line

    def read_bot_weight():
        while True:
            try:
                ser = serial.Serial('/dev/ttyUSB1', baudrate= 115200)
                line = ser.readline()
                decoded_line = line.decode('utf-8')
                break
            except:
                continue
        return decoded_line

    def start_scan():
        # Call the main function from the CV module when the scan button is clicked
        print("Starting webcam scan...")
        global curr_detections
        image, detection = wc.main(0)
        print(detection)
        
        if image is not None:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = PILImage.fromarray(image_rgb)

            # Convert PIL image to base64
            buffered = io.BytesIO()
            pil_image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            # Create base64 image source for Flet
            source = f"data:image/png;base64,{img_base64}"
            flet_image = Image(
                src=source,
                fit=ft.ImageFit.CONTAIN,  # Scale image to fit within bounds
                width=600,  # Set a reasonable width
                height=400,  # Set a reasonable height
            )
            count[0] += 1
            page.update()
        else:
            print("no image")

        if not detection:
            # no items
            container2_image.content = flet_image
            show_container(container2_image)
            change_button(container1_scan)
            text = "No Item Detected"
            popup = ft.AlertDialog(
                title=ft.Text("Warning"),
                content=ft.Text(text),
                actions=[ft.TextButton("OK", on_click=lambda e: close_popup(popup))],
                modal=True
            )
            page.open(popup)
        else:
            container2_image.content = flet_image
            show_container(container2_image)
            change_button(container1_scan)
            curr_detections = detection
            unique_items = set(curr_detections)
            # weighing multiple classes
            if len(unique_items) > 1:
                text = f"Please only weigh one type of item at a time. Currently weighing {unique_items}"
                popup = ft.AlertDialog(
                    title=ft.Text("Warning"),
                    content=ft.Text(text),
                    actions=[ft.TextButton("OK", on_click=lambda e: close_popup(popup))],
                    modal=True
                )
                page.open(popup)
            # this is the base case
            else:
                # get the weight of the item
                top_weight[0] = read_top_weight()
                weight = top_weight[0]

                if detection[0] not in items_weight: 
                    items_weight[detection[0]] = []

                text = ft.Text(f"Weight: {weight[:len(weight) - 1]}lb", color = ft.Colors.GREY_400, size = 30)
                col = ft.Column(
                    controls=[flet_image, text],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,  # Add space between elements
                    expand=True  # Make the column expand to fill the container
                )
                


                container2_image.content = col
                show_container(container2_image)
                change_button(container1_scan)


        page.update()
        print("scan complete")

    def close_popup(popup):
        page.close(popup)
        homepage()

    def update_cart_from_detections():
        items_weight[curr_detections[0]].append(float(top_weight[0][:len(top_weight[0]) - 1]))
        for item in curr_detections:
            if item in texts:
                cur = texts[item]
                current_value = int(cur[1].value)
                new_value = current_value + 1
                update_text_widget(item, str(new_value))
            else:
                add_item_to_container(item, "1", ft.Colors.BLACK)
        page.update()
        homepage()
    

    def update_scanned_items(item_name):
        if item_name in scanned_items:
            scanned_items[item_name] += 1
        else:
            scanned_items[item_name] = 1

    # Function to add items to the ListView in the second container
    def add_item_to_container(left_text, right_text, text_color):
        global scanned_items
        
        left_text_widget = ft.Text(left_text, color=text_color, size=30, expand=True)
        right_text_widget = ft.Text(right_text, color=text_color, size=30, text_align=ft.TextAlign.RIGHT)
        texts[left_text] = (left_text_widget, right_text_widget)

        popup_holder = [None]
        
        def close_popup():
            page.close(popup_holder[0])

        def decrement_item_value(item_name, amount):
            print(item_name)
            print(amount)
            for i in range(amount):
                if item_name in items_weight:
                    items_weight[item_name].pop()
            if item_name in texts:
                cur = texts[item_name]
                current_value = int(cur[1].value)
   
                if current_value >= 1:
                    new_value = current_value - amount
                    update_text_widget(item_name, str(new_value))
                    current_value = int(cur[1].value)
                if current_value <= 0:
                    container_to_remove = None
                    for container in list_view_basket.controls:
                        if container.content.controls[0] == cur[0]:
                            container_to_remove = container
                            break
                    
                    if container_to_remove:
                        list_view_basket.controls.remove(container_to_remove)
                        del texts[item_name]
                        list_view_basket.update()
            close_popup()
            page.update()
        
        def open_popup(item_name):
            cur = texts[item_name]
            max_value = int(cur[1].value)
            decrement_slider = ft.Slider(
                min=1, max=max_value, divisions=max_value - 1,  # Ensure step-by-step selection
                value=1, label="{value}",  # Show selected value
            )   
        
            popup = ft.AlertDialog(
                title=ft.Text(f"Remove {left_text}"),
                content=ft.Column([
                    ft.Text(f"Current quantity: {max_value}"),
                    decrement_slider,
                ], spacing=10),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_popup()),
                    ft.TextButton("Confirm", on_click=lambda e: decrement_item_value(left_text, int(decrement_slider.value)))
                ],
                modal=True
            )
            page.open(popup)
            popup_holder[0] = popup

        
        new_item = ft.Container(
            content=ft.Row(
                controls=[
                    left_text_widget,
                    right_text_widget
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            margin=ft.margin.symmetric(horizontal=10, vertical=10),  # Add horizontal and vertical margin
            expand=True,  # Make the container expand to fill the available space
            border=ft.border.all(1, ft.Colors.GREY_400),  # Add a border
            border_radius=10,  # Add rounded corners
            bgcolor=ft.Colors.GREY_400,
            on_click=lambda e: open_popup(left_text)
        )


        list_view_basket.controls.append(new_item)

        if container_placeholder.content == container2_basket:
            list_view_basket.update()
        else:
            page.update()
            
            

    def update_text_widget(old_text, new_text):
        if old_text in texts:
            cur = texts[old_text]
            cur[1].value = new_text
            #cur[1].update()
        page.update()

    def show_container(container):
        container_placeholder.content = container
        page.update()
    
    def change_button(container):
        button_placeholder.content = container
        page.update()
    
    def homepage():
        container_placeholder.content = container2_basket
        button_placeholder.content = container1
        page.update()


    buyButton = ft.IconButton(
        icon=ft.Icons.SHOPPING_CART_CHECKOUT_ROUNDED, 
        icon_size=25, 
        icon_color=ft.Colors.ON_PRIMARY, 
        bgcolor=ft.Colors.GREY_300,
        on_click=lambda e: show_basket_summary_popup()
    )

    confirmButton = ft.IconButton(
        icon=ft.Icons.CHECK, 
        icon_size=25, 
        icon_color=ft.Colors.ON_PRIMARY, 
        bgcolor=ft.Colors.GREY_300,
        on_click=lambda e: update_cart_from_detections()
    )

    scanButton = ft.IconButton(
        icon=ft.Icons.PHOTO_CAMERA, 
        icon_size=25, 
        icon_color=ft.Colors.ON_PRIMARY, 
        bgcolor=ft.Colors.GREY_300,
        on_click=lambda e: start_scan()
    )

    denyButton = ft.IconButton(
        icon=ft.Icons.DELETE, 
        icon_size=25, 
        icon_color=ft.Colors.ON_PRIMARY, 
        bgcolor=ft.Colors.GREY_300,
        on_click=lambda e: homepage()
    )

    # Create a row to hold the buttons and evenly space them
    button_row = ft.Row(
        controls=[scanButton, buyButton],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Space between the buttons
    )

    button_row_scan = ft.Row(
        controls=[confirmButton, denyButton],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Space between the buttons
    )

    # Create the first container
    container1 = ft.Container(
        content=button_row,
        border=ft.border.all(1, ft.Colors.ON_PRIMARY_CONTAINER),
        border_radius=10,
        padding=ft.padding.symmetric(15, 30),
        margin=ft.margin.symmetric(horizontal=10, vertical=0),
        bgcolor=ft.Colors.ON_PRIMARY_CONTAINER
    )

    container1_scan = ft.Container(
        content=button_row_scan,
        border=ft.border.all(1, ft.Colors.ON_PRIMARY_CONTAINER),
        border_radius=10,
        padding=ft.padding.symmetric(15, 30),
        margin=ft.margin.symmetric(horizontal=10, vertical=0),
        bgcolor=ft.Colors.ON_PRIMARY_CONTAINER
    )

    container2_image = ft.Container(
        content=ft.Text("placeholder"),
        border=ft.border.all(1, ft.Colors.ON_PRIMARY_CONTAINER),
        border_radius=10,
        bgcolor=ft.Colors.ON_PRIMARY_CONTAINER,
        padding=ft.padding.symmetric(15, 30),
        margin=ft.margin.symmetric(horizontal=20, vertical=0),
        expand=True,
        alignment=ft.alignment.center,
    )

    # Create the second container with a fixed size and a ListView to hold the items
    list_view_basket = ft.ListView(expand=True)
    container2_basket = ft.Container(
        content=list_view_basket,
        border=ft.border.all(1, ft.Colors.ON_PRIMARY_CONTAINER),
        border_radius=10,
        padding=10,
        margin=ft.margin.symmetric(horizontal =20, vertical=0),
        bgcolor=ft.Colors.ON_PRIMARY_CONTAINER,
        expand=True
    )

    # Add both containers to a column with flex properties
    container_placeholder = ft.Container(content=container2_basket, expand=True)
    button_placeholder = ft.Container(content=container1, margin = 10)
    page.add(
        ft.Column(
            controls=[
                container_placeholder,
                button_placeholder,
            ],
            expand=True  # Make the column expand to fill the page
        )
    )

    warning_container = ft.Container(
        content=ft.Column([
            ft.Text("", size=30, color=ft.colors.RED, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        border=ft.border.all(3, ft.colors.RED),
        border_radius=10,
        padding=20,
        margin=ft.margin.symmetric(horizontal=20, vertical=20),
        bgcolor=ft.colors.RED_50,
        alignment=ft.alignment.center,
        expand=True
    )
    

    # Start the barcode listener in a separate thread
    threading.Thread(target=listen_for_barcode, daemon=True).start()

    page.update()

if __name__ == "__main__":
    ft.app(main, assets_dir="assets") 


   