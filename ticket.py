import time
import hashlib
import qrcode
import os
class Ticket:
    def __init__(self, id, creation_time, start_location, destination,qr_code_file):
        self.id = id
        self.creation_time = creation_time
        self.start_location = start_location
        self.destination = destination
        self.qr_code_file = qr_code_file

    def is_valid(self):
        # Define your condition to check if the ticket is valid
        current_time = time.time()
        validity_duration = 3600  # 1 hour validity
        if current_time - self.creation_time <= validity_duration:
            return True
        else:
            del self
            return False

def generate_qr_code(hash_length=10, qr_code_file="qr_code.png"):
    # Generate a random hash
    random_string = str(hashlib.sha256(os.urandom(32)).hexdigest())[:hash_length]

    # Create the QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(random_string)
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white")

    # Save the QR code image to file
    qr_img.save(qr_code_file)
    print(f"QR code generated with hash: {random_string}")
    print(f"QR code saved to: {qr_code_file}")

# Example usage