import MetaTrader5 as mt5

# Informasi akun MT5
account = 272055372         
password = "@Oskar2704"  
server = "Exness-MT5Trial14"    

# Inisialisasi koneksi MT5
if not mt5.initialize(login=account, password=password, server=server):
    print("Gagal connect ke MT5")
    mt5.shutdown()
else:
    print("Berhasil connect ke MT5")
