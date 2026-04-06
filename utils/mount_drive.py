# from google.colab import drive
# import os

# def mount_google_drive():
#     """Montage de Google Drive"""
#     drive.mount('/content/drive')

#     # Vérification
#     print("\n📁 Dossiers disponibles dans Drive :")
#     for item in os.listdir('/content/drive/MyDrive'):
#         print(f"  - {item}")

from google.colab import drive

def mount_google_drive(mount_point='/content/drive', force_remount=False):
    """Monte Google Drive"""
    try:
        import os
        if os.path.exists(mount_point) and not force_remount:
            if os.path.exists(os.path.join(mount_point, 'MyDrive')):
                print(f"✅ Drive déjà monté sur {mount_point}")
                return True
        
        drive.mount(mount_point, force_remount=force_remount)
        print(f"✅ Google Drive monté sur {mount_point}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False