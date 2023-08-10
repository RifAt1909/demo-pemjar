import socket
import threading
import os

HOST = '10.217.21.142'
PORT = 12345

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            print(data.decode("utf-8"))
        except:
            break

def send_file(client_socket, file_path, recipient):
    file_type = file_path.split(".")[-1].lower()
    message = f"!file {file_type} {recipient}"
    client_socket.send(message.encode("utf-8"))

    file_size = os.path.getsize(file_path)
    # Send the file size as part of the header
    file_header = f"{file_size}\n"
    client_socket.send(file_header.encode("utf-8"))

    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            client_socket.send(data)

    print(f"File {file_path} terkirim dengan sukses.")

def receive_file(client_socket, file_path):
    # Receive the file size from the header
    file_header = client_socket.recv(1024).decode("utf-8")
    file_size = int(file_header.strip())

    with open(file_path, "wb") as file:
        remaining_bytes = file_size
        while remaining_bytes > 0:
            data = client_socket.recv(min(remaining_bytes, 1024))
            if not data:
                break
            file.write(data)
            remaining_bytes -= len(data)

    print(f"File {file_path} diterima dengan sukses.")

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Input username dari klien
    username = input("Masukkan username Anda: ")
    client_socket.send(username.encode("utf-8"))

    # Input nama grup dari klien
    groupname = input("Masukkan nama grup Anda: ")
    client_socket.send(groupname.encode("utf-8"))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        print("\nMenu Opsi:")
        print("1. Kirim Pesan Unicast")
        print("2. Kirim Pesan Multicast")
        print("3. Kirim Pesan Broadcast")
        print("4. Kirim File")
        print("5. Terima File")
        print("6. Keluar")

        choice = input("Masukkan pilihan (1/2/3/4/5/6): ")

        if choice == "1":
            recipient = input("Masukkan nama penerima: ")
            message = input("Masukkan pesan untuk unicast: ")
            full_message = f"@{recipient} {message}"
        elif choice == "2":
            group = input("Masukkan nama grup: ")
            message = input("Masukkan pesan untuk multicast: ")
            full_message = f"${group} {message}"
        elif choice == "3":
            message = input("Masukkan pesan untuk broadcast: ")
            full_message = f"*Broadcast {message}"
        elif choice == "4":
            file_path = input("Masukkan path file yang akan dikirim: ")
            send_to = input("Masukkan nama penerima file: ")

            # Kirim pesan ke server untuk meminta pengiriman file ke klien tujuan
            full_message = f"!file {send_to} {file_path}"
            client_socket.send(full_message.encode("utf-8"))
            continue
        elif choice == "5":
            file_name = input("Masukkan nama file yang akan diterima: ")
            receive_file(client_socket, file_name)
            continue
        elif choice == "6":
            full_message = "exit"
        else:
            print("Pilihan tidak valid. Silakan pilih opsi yang benar.")
            continue

        client_socket.send(full_message.encode("utf-8"))

        if choice == "6":
            break

    client_socket.close()

if __name__ == "__main__":
    main()
