import logging
from logging.handlers import RotatingFileHandler

# Logger yapılandırması
def setup_logger(log_file="/root/sync_database.log", log_level=logging.INFO):
    """
    Logger yapılandırması.
    
    Args:
        log_file (str): Log dosyasının yolu.
        log_level (logging.level): Log seviyesini belirler.
    
    Returns:
        logger (logging.Logger): Yapılandırılmış logger objesi.
    """
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Dosya rotasyonu için RotatingFileHandler ayarlanması
    log_handler = RotatingFileHandler(log_file, maxBytes=1 * 1024 * 1024, backupCount=5)
    log_handler.setFormatter(log_formatter)

    # Ana logger oluşturulması
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(log_handler)

    # Konsol çıktısı için handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    return logger

# Logger'ı ayarla
logger = setup_logger()

def main():
    logger.info("Sync işlemi başladı.")
    # Burada senkronizasyon işlemleri yapılabilir
    logger.info("Sync işlemi başarıyla tamamlandı.")

if __name__ == "__main__":
    main()