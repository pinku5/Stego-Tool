from PIL import Image
from colorama import Fore, init
import hashlib
import base64
import os

init(autoreset=True)

END_MARKER = "#####END#####"

def password_key(password):
    return hashlib.sha256(password.encode()).digest()

def encrypt_message(message, password):
    key = password_key(password)
    data = message.encode()

    encrypted = bytearray()
    for i in range(len(data)):
        encrypted.append(data[i] ^ key[i % len(key)])

    return base64.b64encode(encrypted).decode()

def decrypt_message(ciphertext, password):
    key = password_key(password)

    data = base64.b64decode(ciphertext)

    decrypted = bytearray()
    for i in range(len(data)):
        decrypted.append(data[i] ^ key[i % len(key)])

    return decrypted.decode()

def text_to_binary(text):
    return ''.join(format(ord(c), '08b') for c in text)

def binary_to_text(binary):
    result = ""
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            result += chr(int(byte, 2))
    return result

def capacity(path):
    img = Image.open(path)
    w, h = img.size
    return (w * h * 3) // 8

def hide_message():
    path = input("Image Path: ").strip()

    if not os.path.exists(path):
        print(Fore.RED + "Image not found!")
        return

    password = input("Password: ")
    message = input("Secret Message: ")

    img = Image.open(path)

    if img.mode != "RGB":
        img = img.convert("RGB")

    if img.format and img.format.upper() == "JPEG":
        png_path = os.path.splitext(path)[0] + "_converted.png"
        img.save(png_path, "PNG")
        path = png_path
        img = Image.open(path)
        print(Fore.YELLOW + f"JPEG converted: {png_path}")

    encrypted = encrypt_message(message, password)
    payload = encrypted + END_MARKER

    binary = text_to_binary(payload)

    max_bits = img.size[0] * img.size[1] * 3

    if len(binary) > max_bits:
        print(Fore.RED + "Message too large for image!")
        return

    pixels = img.load()
    index = 0

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b = pixels[x, y]

            if index < len(binary):
                r = (r & ~1) | int(binary[index])
                index += 1

            if index < len(binary):
                g = (g & ~1) | int(binary[index])
                index += 1

            if index < len(binary):
                b = (b & ~1) | int(binary[index])
                index += 1

            pixels[x, y] = (r, g, b)

            if index >= len(binary):
                break

        if index >= len(binary):
            break

    output = input("Output PNG Name: ").strip()

    if not output.endswith(".png"):
        output += ".png"

    img.save(output)

    print(Fore.GREEN + f"Saved: {output}")

def extract_message():
    path = input("Encoded Image Path: ").strip()

    if not os.path.exists(path):
        print(Fore.RED + "Image not found!")
        return

    password = input("Password: ")

    img = Image.open(path)

    if img.mode != "RGB":
        img = img.convert("RGB")

    pixels = img.load()

    binary = ""

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b = pixels[x, y]

            binary += str(r & 1)
            binary += str(g & 1)
            binary += str(b & 1)

    extracted = ""

    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]

        if len(byte) < 8:
            break

        extracted += chr(int(byte, 2))

        if END_MARKER in extracted:
            extracted = extracted.replace(END_MARKER, "")
            break

    try:
        message = decrypt_message(extracted, password)

        print(Fore.GREEN + "\nHidden Message:\n")
        print(message)

    except Exception:
        print(Fore.RED + "Wrong password or corrupted image!")

def image_info():
    path = input("Image Path: ").strip()

    if not os.path.exists(path):
        print(Fore.RED + "Image not found!")
        return

    img = Image.open(path)

    print(Fore.CYAN + f"\nFormat: {img.format}")
    print(Fore.CYAN + f"Resolution: {img.size[0]} x {img.size[1]}")
    print(Fore.CYAN + f"Approx Capacity: {capacity(path)} chars")

while True:
    print(Fore.MAGENTA + r'''
╔══════════════════════════════════╗
║      STEGO TOOL v1.0            ║
║ Hide & Extract Secret Messages  ║
╚══════════════════════════════════╝
''')

    print(Fore.CYAN + "[1] Hide Message")
    print(Fore.CYAN + "[2] Extract Message")
    print(Fore.CYAN + "[3] Image Info")
    print(Fore.CYAN + "[4] Capacity Checker")
    print(Fore.CYAN + "[5] Exit")

    choice = input("\nSelect: ")

    if choice == "1":
        hide_message()

    elif choice == "2":
        extract_message()

    elif choice == "3":
        image_info()

    elif choice == "4":
        path = input("Image Path: ")
        print(Fore.GREEN + f"Approx Capacity: {capacity(path)} characters")

    elif choice == "5":
        print(Fore.YELLOW + "Goodbye!")
        break

    else:
        print(Fore.RED + "Invalid choice!")
