import sys
import os
import zipfile
import base64
import subprocess
import shutil

def create_secure_archive_script(password):
    """archive_secure.py dosyasını oluşturur ve verilen şifreyi kullanır."""
    encoded_password = base64.b64encode(password.encode('utf-8')).decode('utf-8')
    
    secure_archive_content = f"""
import os
import zipfile
import base64
import subprocess
from datetime import datetime
import sys

# Parolayı base64 ile encode edilmiş olarak saklıyoruz
encoded_password = b'{encoded_password}'

# Parolayı decode ederek asıl değeri elde ediyoruz
password = base64.b64decode(encoded_password).decode('utf-8')

def zip_directory(source_folder, zip_filename):
    \"\"\"Klasörü zip formatında arşivler.\"\"\"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), source_folder))

def encrypt_file(zip_filename, encrypted_filename, password):
    \"\"\"Zip dosyasını AES-256-CBC algoritması ile şifreler.\"\"\"
    try:
        subprocess.run([
            'openssl', 'enc', '-aes-256-cbc', '-salt', '-pbkdf2', '-iter', '100000',
            '-in', zip_filename, '-out', encrypted_filename, '-k', password
        ], check=True)
        print(f"Dosya şifrelendi: {{encrypted_filename}}")
    except subprocess.CalledProcessError as e:
        print(f"Hata oluştu: {{e}}")

def main():
    if len(sys.argv) != 2:
        print("Kullanım: archive_secure <kaynak_klasor>")
        sys.exit(1)

    source_folder = sys.argv[1]
    zip_filename = 'temp.zip'  # Geçici zip dosyası

    # Çıktı dosyası formatı: ChargePackAC_Firmware_v1.0_<TARIH>.fwenc
    today = datetime.now().strftime('%Y%m%d')  # Güncel tarihi alıyoruz
    encrypted_filename = f'ChargePackAC_Firmware_v1.0_{{today}}.fwenc'

    # Klasörü zipleyip şifreliyoruz
    print("Klasör zipleniyor...")
    zip_directory(source_folder, zip_filename)
    
    print("Dosya şifreleniyor...")
    encrypt_file(zip_filename, encrypted_filename, password)

    # Orijinal zip dosyasını siliyoruz
    os.remove(zip_filename)
    print(f"Orijinal zip dosyası silindi: {{zip_filename}}")

if __name__ == "__main__":
    main()
"""

    # archive_secure.py dosyasını oluşturuyoruz
    with open('archive_secure.py', 'w') as f:
        f.write(secure_archive_content)
    print("archive_secure.py dosyası oluşturuldu.")

def create_secure_unarchive_script(password):
    """unarchive_secure.py dosyasını oluşturur ve verilen şifreyi kullanır."""
    encoded_password = base64.b64encode(password.encode('utf-8')).decode('utf-8')
    
    secure_unarchive_content = f"""
import sys
import os
import base64
import subprocess
import zipfile

# Parolayı base64 ile encode edilmiş olarak saklıyoruz
encoded_password = b'{encoded_password}'

# Parolayı decode ederek asıl değeri elde ediyoruz
password = base64.b64decode(encoded_password).decode('utf-8')

def decrypt_file(encrypted_filename, zip_filename, password):
    \"\"\"Şifreli dosyayı AES-256-CBC algoritması ile çözer.\"\"\"
    try:
        subprocess.run([
            'openssl', 'enc', '-d', '-aes-256-cbc', '-pbkdf2', '-iter', '100000',
            '-in', encrypted_filename, '-out', zip_filename, '-k', password
        ], check=True)
        print(f"Dosya şifresi çözüldü: {{zip_filename}}")
    except subprocess.CalledProcessError as e:
        print(f"Şifre çözme sırasında hata oluştu: {{e}}")

def unzip_file(zip_filename, output_folder):
    \"\"\"Zip dosyasını belirtilen klasöre açar.\"\"\"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # Çıkış klasörü yoksa oluşturulur

    try:
        with zipfile.ZipFile(zip_filename, 'r') as zipf:
            # Dosyaları temp klasörü olmadan direkt çıkartıyoruz
            for member in zipf.namelist():
                zipf.extract(member, output_folder)
        print(f"Zip dosyası açıldı: {{output_folder}}")
    except Exception as e:
        print(f"Zip dosyası açılırken hata oluştu: {{e}}")

def main():
    if len(sys.argv) != 3:
        print("Kullanım: unarchive_secure <şifreli_dosya_yolu> <çıkış_klasör_yolu>")
        sys.exit(1)

    encrypted_filename = sys.argv[1]
    output_folder = sys.argv[2]

    # Çıkış yolunun bir klasör olduğundan emin olun
    if not os.path.isdir(output_folder):
        print(f"Çıkış klasörü geçerli değil veya mevcut değil: {{output_folder}}. Klasör oluşturuluyor...")
        os.makedirs(output_folder, exist_ok=True)

    zip_filename = os.path.join(os.path.dirname(encrypted_filename), 'temp.zip')

    # Şifreli dosyayı çözüp açıyoruz
    print("Dosya şifresi çözülüyor...")
    decrypt_file(encrypted_filename, zip_filename, password)
    
    print("Zip dosyası açılıyor...")
    unzip_file(zip_filename, output_folder)

    # Şifre çözülmüş zip dosyasını siliyoruz
    os.remove(zip_filename)
    print(f"Çözülmüş zip dosyası silindi: {{zip_filename}}")

if __name__ == "__main__":
    main()
"""

    # unarchive_secure.py dosyasını oluşturuyoruz
    with open('unarchive_secure.py', 'w') as f:
        f.write(secure_unarchive_content)
    print("unarchive_secure.py dosyası oluşturuldu.")

def compile_script(script_name, binary_name):
    """Belirtilen scripti PyInstaller ile binary dosyaya derler."""
    try:
        # PyInstaller kullanarak scripti derliyoruz
        subprocess.run(['pyinstaller', '--onefile', '--noconsole', script_name], check=True)
        print(f"{script_name} başarıyla {binary_name} olarak derlendi.")
    except subprocess.CalledProcessError as e:
        print(f"{script_name} derleme sırasında hata oluştu: {e}")

def move_binary(binary_name):
    """Derlenen binary dosyasını dist klasöründen /bin dizinine taşır. /bin'e taşıma başarısız olursa mevcut dizine kopyalar."""
    binary_path = os.path.join('dist', binary_name)
    target_path = os.path.join('/bin', binary_name)
    fallback_path = os.path.join('.', binary_name)  # Eğer /bin'e taşıma başarısız olursa bu yola kopyalanacak

    if os.path.exists(binary_path):
        try:
            # /bin dizinine taşımayı dener
            shutil.move(binary_path, target_path)
            print(f"Çalıştırılabilir dosya /bin klasörüne taşındı: {target_path}")
        except PermissionError:
            # Eğer taşıma başarısız olursa mevcut dizine kopyalar
            shutil.move(binary_path, fallback_path)
            print(f"Taşıma başarısız oldu, çalıştırılabilir dosya mevcut dizine kopyalandı: {fallback_path}")
    else:
        print(f"{binary_name} çalıştırılabilir dosya bulunamadı, taşıma işlemi başarısız.")


def clean_up():
    """Derleme sonrası yalnızca PyInstaller tarafından oluşturulan geçici dosyaları temizler."""
    files_to_remove = ['archive_secure.spec', 'unarchive_secure.spec', 'archive_secure.py', 'unarchive_secure.py']
    directories_to_remove = ['build', 'dist']

    # Sadece derleme ile ilgili dosyaları temizle, proje dosyalarına dokunma
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
    
    for directory in directories_to_remove:
        if os.path.exists(directory):
            shutil.rmtree(directory)

    print("Geçici derleme dosyaları temizlendi.")

def main():
    if len(sys.argv) != 2:
        print("Kullanım: python3 create_secure_script.py <şifre>")
        sys.exit(1)
    
    password = sys.argv[1]
    create_secure_archive_script(password)
    create_secure_unarchive_script(password)
    compile_script('archive_secure.py', 'archive_secure')
    compile_script('unarchive_secure.py', 'unarchive_secure')
    move_binary('archive_secure')
    move_binary('unarchive_secure')
    clean_up()

if __name__ == "__main__":
    main()
