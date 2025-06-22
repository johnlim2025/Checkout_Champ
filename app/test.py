import keyboard

while True:
    events = keyboard.record(until="enter")  # Capture all input until Enter

    barcode = "".join(event.name for event in events if event.event_type == "down" and event.name != "enter")

    print(f"Scanned Barcode: {barcode}")