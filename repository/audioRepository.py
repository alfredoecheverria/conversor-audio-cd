from pymongo import MongoClient
import gridfs
from datetime import datetime
import os
class AudioRepository:

    def __init__(self, uri="mongodb://localhost:27017/", db_name="Prueba"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.fs = gridfs.GridFS(self.db)
        self.coleccion = self.db["audios"]


    def guardar_audio(self, path_archivo: str, tamanio:str = None,  dispositivo: str = None) -> str:
    

        metadata = {
            "fecha_guardado": datetime.now(),
            "dispositivo_de_grabacion": dispositivo or "desconocido",
            "size_kb":tamanio
        }

        nombre = path_archivo.split("\\")[-1]
        with open(path_archivo, "rb") as f:
            file_id = self.fs.put(f, filename=nombre, **(metadata or {}))
            self.coleccion.insert_one({
                "nombre": nombre,
                "file_id": file_id,
                "metadata": metadata or {}
            })
            return str(file_id)
        
    def listar_audios(self):
            return list(self.coleccion.find({}, {"_id": 0}))
    
    def obtener_audio_por_nombre(self, nombre: str, destino: str) -> bool:
        archivo = self.fs.find_one({"filename": nombre})
        if archivo:
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            with open(destino, "wb") as f:
                f.write(archivo.read())
            return True
        return False

