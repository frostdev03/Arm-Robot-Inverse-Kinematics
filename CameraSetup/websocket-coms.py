import websocket  # Tambahkan pustaka websocket-client

# Alamat IP ESP32 (ganti dengan IP ESP32 Anda)
ESP32_IP = "192.168.81.37"  # Sesuaikan dengan IP ESP32 Anda
ESP32_PORT = 81

def main():
    # URL WebSocket ESP32
    ws_url = f"ws://{ESP32_IP}:{ESP32_PORT}/"

    try:
        print(f"Menghubungkan ke WebSocket {ws_url}...")
        ws = websocket.create_connection(ws_url)
        print("Terhubung ke WebSocket.")

        # Loop untuk mengirim data dari input pengguna
        while True:
            # Meminta input dari pengguna
            message = input("Ketik pesan untuk dikirim (atau 'exit' untuk keluar): ")
            
            # Keluar jika pengguna mengetik 'exit'
            if message.lower() == "exit":
                print("Menutup koneksi...")
                break
            
            # Mengirim pesan ke ESP32
            print(f"Mengirim: {message}")
            ws.send(message)
        
        # Tutup koneksi
        ws.close()
        print("Koneksi WebSocket ditutup.")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
