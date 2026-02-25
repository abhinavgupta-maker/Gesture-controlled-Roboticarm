import serial
import struct

# Initialize serial
ser = serial.Serial('COM4', 115200)


def send_arm_data(a1, a2, a3, claw):
    # 'B' = unsigned char (1 byte, 0-255)
    # Header (0xAA) + 3 Angles + 1 Claw State + 1 Checksum
    header = 0xAA

    # Simple Checksum: Sum of angles % 256
    checksum = (a1 + a2 + a3 + claw) % 256

    # Pack into a 6-byte binary string
    packet = struct.pack('BBBBBB', header, a1, a2, a3, claw, checksum)

    ser.write(packet)