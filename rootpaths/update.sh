
NEW_SOFTWARE_DIR="/root/firmware"
SOFTWARE_DIR="/root/acApp"
BACKUP_DIR="/root/acApp_backup"

cp -r $SOFTWARE_DIR $BACKUP_DIR
rm -r $SOFTWARE_DIR
cp -r $NEW_SOFTWARE_DIR $SOFTWARE_DIR

rm -r /root/new_firmware.zip
rm -r $NEW_SOFTWARE_DIR

if systemctl restart acapp.service; then
    echo "Yazılım başarıyla güncellendi ve servis yeniden başlatıldı."
else
    echo "Hata: Servis yeniden başlatılamadı. Eski yazılıma geri dönülüyor..."
    # Yeni yazılımı kaldır
    rm -rf $SOFTWARE_DIR
    # Eski yazılımı geri yükle
    mv $BACKUP_DIR $SOFTWARE_DIR
    # Servisi eski yazılımla yeniden başlat
    if systemctl restart acapp.service; then
        echo "Eski yazılım başarıyla geri yüklendi ve servis yeniden başlatıldı."
    else
        echo "Kritik Hata: Servis eski yazılımla bile yeniden başlatılamadı. Manuel müdahale gerekebilir."
    fi
fi


