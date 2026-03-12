---
sidebar_position: 1
title: PhotoKit
---

# PhotoKit

## ¿Qué es PhotoKit?

PhotoKit es el framework de Apple que proporciona acceso directo a las fotos y vídeos gestionados por la aplicación Fotos en iOS, iPadOS, macOS y tvOS. A través de un conjunto robusto de APIs, permite a los desarrolladores leer, crear, modificar y eliminar assets (imágenes y vídeos), álbumes y colecciones del usuario sin necesidad de duplicar contenido ni gestionar almacenamiento propio. PhotoKit actúa como una capa de abstracción sobre la biblioteca de Fotos del sistema, garantizando que cualquier cambio realizado se refleje de forma consistente en todas las aplicaciones que acceden a dicha biblioteca.

Este framework reemplaza a la antigua `AssetsLibrary` (deprecada desde iOS 9) y ofrece un modelo de datos inmutable, seguro para hilos y orientado a rendimiento. Su arquitectura se basa en el concepto de **fetch results** perezosos, lo que significa que los objetos no se cargan completamente en memoria hasta que se necesitan, permitiendo trabajar con bibliotecas de miles o incluso cientos de miles de assets de forma eficiente.

PhotoKit es la elección adecuada cuando tu aplicación necesita interactuar con la biblioteca de Fotos del sistema: desde un simple selector de imágenes personalizado hasta un editor de fotos profesional, pasando por aplicaciones de respaldo en la nube, galerías personalizadas o herramientas de organización automatizada basadas en metadatos.

## Casos de uso principales

- **Galería de fotos personalizada**: Construir una interfaz propia para navegar, filtrar y visualizar las fotos y vídeos del usuario con un diseño adaptado a tu marca o funcionalidad específica.
- **Editor de imágenes y vídeos**: Aplicar filtros, recortes y ajustes sobre assets existentes y guardar los cambios de vuelta en la biblioteca de Fotos de forma no destructiva.
- **Respaldo y sincronización en la nube**: Acceder a todos los assets del dispositivo para subirlos a un servicio externo, detectando cambios incrementales mediante observadores de la biblioteca.
- **Organización inteligente de álbumes**: Crear, renombrar y eliminar álbumes programáticamente, así como añadir o eliminar assets de colecciones específicas.
- **Análisis de metadatos**: Leer información EXIF, ubicación GPS, fecha de captura y tipo de media para clasificar o buscar contenido de forma avanzada.
- **Widgets y extensiones**: Mostrar fotos recientes, recuerdos o álbumes seleccionados en widgets de la pantalla de inicio utilizando los datos de la biblioteca de Fotos.

## Instalación y configuración

PhotoKit forma parte del SDK del sistema, por lo que **no requiere instalación externa** mediante CocoaPods, SPM ni Carthage. Sin embargo, sí es necesario configurar los permisos adecuados.

### Permisos en Info.plist

Debes agregar las siguientes claves en tu archivo `Info.plist` según el nivel de acceso que necesites:

```xml
<!-- Permiso de lectura y escritura completo -->
<key>NSPhotoLibraryUsageDescription</key>
<string>Necesitamos acceder a tu biblioteca de fotos para mostrar y editar tus imágenes.</string>

<!-- Permiso solo para agregar fotos (sin lectura) -->
<key>NSPhotoLibraryAddUsageDescription</key>
<string>Necesitamos permiso para guardar fotos en tu biblioteca.</string>
```

### Import necesario

```swift
import Photos      // Modelo de datos y operaciones con la biblioteca
import PhotosUI    // Componentes de interfaz (PHPicker, etc.)
```

### Solicitar autorización programáticamente

```swift
PHPhotoLibrary.requestAuthorization(for: .readWrite) { status in
    switch status {
    case .authorized:
        print("Acceso completo concedido")
    case .limited:
        print("Acceso limitado a fotos seleccionadas")
    case .denied, .restricted:
        print("Acceso denegado o restringido")
    case .notDetermined:
        print("Aún no se ha solicitado permiso")
    @unknown default:
        break
    }
}
```

## Conceptos clave

### 1. PHAsset
Representa un único recurso multimedia (foto, vídeo, Live Photo, etc.) en la biblioteca de Fotos. Es un objeto inmutable que contiene metadatos como fecha de creación, ubicación, tipo de media, dimensiones y duración. No contiene los datos de la imagen directamente; para obtener los píxeles se debe usar un *image manager*.

### 2. PHAssetCollection y PHCollectionList
`PHAssetCollection` representa un grupo de assets, como un álbum, un momento o una carpeta inteligente del sistema (favoritos, capturas de pantalla, etc.). `PHCollectionList` es una colección de colecciones, permitiendo jerarquías como carpetas que contienen álbumes.

### 3. PHFetchResult
Es el contenedor que devuelven las operaciones de consulta (`fetch`). Se comporta de forma similar a un array, pero carga sus elementos de manera perezosa. Es seguro para hilos y puede contener `PHAsset`, `PHAssetCollection` u otros objetos del modelo.

### 4. PHImageManager y PHCachingImageManager
`PHImageManager` es el motor que convierte un `PHAsset` en una imagen renderizable (`UIImage` o `NSImage`). Se le puede solicitar diferentes tamaños, modos de entrega (rápida, de alta calidad, oportunista) y formatos. `PHCachingImageManager` es una subclase optimizada para precachear imágenes en escenarios de scroll intensivo, como una cuadrícula de fotos.

### 5. PHPhotoLibrary y cambios (PHAssetChangeRequest)
`PHPhotoLibrary.shared()` es el punto de entrada para realizar operaciones de escritura (crear, modificar, eliminar). Todas las mutaciones se encapsulan dentro de un bloque `performChanges(_:completionHandler:)` que garantiza atomicidad y consistencia. Dentro de ese bloque se usan objetos como `PHAssetChangeRequest` o `PHAssetCollectionChangeRequest`.

### 6. PHPhotoLibraryChangeObserver
Protocolo que permite observar cambios en la biblioteca de Fotos en tiempo real. Cuando el usuario agrega, edita o elimina fotos (incluso desde otra app), el observador recibe un objeto `PHChange` que describe exactamente qué ha cambiado, permitiendo actualizar la UI de forma eficiente.

## Ejemplo básico

```swift
import Photos
import UIKit

/// Ejemplo básico: obtener todas las fotos del usuario y cargar la más reciente
class BasicPhotoLoader {
    
    /// Solicita permisos y carga la foto más reciente de la biblioteca
    func loadMostRecentPhoto(completion: @escaping (UIImage?) -> Void) {
        // 1. Solicitar autorización
        PHPhotoLibrary.requestAuthorization(for: .readWrite) { status in
            guard status == .authorized || status == .limited else {
                print("❌ No se tiene acceso a la biblioteca de fotos")
                completion(nil)
                return
            }
            
            // 2. Configurar opciones de búsqueda: ordenar por fecha, solo la más reciente
            let fetchOptions = PHFetchOptions()
            fetchOptions.sortDescriptors = [
                NSSortDescriptor(key: "creationDate", ascending: false)
            ]
            fetchOptions.fetchLimit = 1 // Solo necesitamos una foto
            
            // 3. Realizar la consulta de assets de tipo imagen
            let fetchResult = PHAsset.fetchAssets(with: .image, options: fetchOptions)
            
            guard let asset = fetchResult.firstObject else {
                print("⚠️ No se encontraron fotos en la biblioteca")
                completion(nil)
                return
            }
            
            // 4. Solicitar la imagen al image manager
            let imageManager = PHImageManager.default()
            let targetSize = CGSize(width: 300, height: 300)
            let options = PHImageRequestOptions()
            options.deliveryMode = .highQualityFormat
            options.isSynchronous = false
            
            imageManager.requestImage(
                for: asset,
                targetSize: targetSize,
                contentMode: .aspectFill,
                options: options
            ) { image, info in
                // 5. Verificar que no sea una imagen degradada (thumbnail temporal)
                let isDegraded = (info?[PHImageResultIsDegradedKey] as? Bool) ?? false
                if !isDegraded {
                    completion(image)
                }
            }
        }
    }
}
```

## Ejemplo intermedio

```swift
import Photos
import UIKit

/// Ejemplo intermedio: gestión completa de una galería con caché,
/// creación de álbumes y observación de cambios
class PhotoGalleryManager: NSObject, PHPhotoLibraryChangeObserver {
    
    // MARK: - Propiedades
    
    /// Resultado de la consulta actual de assets
    private(set) var fetchResult: PHFetchResult<PHAsset>!
    
    /// Image manager con caché para scroll suave en colecciones
    private let cachingImageManager = PHCachingImageManager()
    
    /// Callback para notificar cambios a la UI
    var onLibraryDidChange: ((_ changeDetails: PHFetchResultChangeDetails<PHAsset>) -> Void)?
    
    // MARK: - Inicialización
    
    override init() {
        super.init()
        // Registrar como observador de cambios en la biblioteca
        PHPhotoLibrary.shared().register(self)
        // Cargar la consulta inicial
        loadAllPhotos()
    }
    
    deinit {
        PHPhotoLibrary.shared().unregisterChangeObserver(self)
    }
    
    // MARK: - Consultas
    
    /// Carga todas las fotos ordenadas por fecha de creación descendente
    func loadAllPhotos() {
        let options = PHFetchOptions()
        options.sortDescriptors = [
            NSSortDescriptor(key: "creationDate", ascending: false)
        ]
        // Filtrar solo imágenes (excluir vídeos, Live Photos compuestos, etc.)
        options.predicate = NSPredicate(
            format: "mediaType == %d", PHAssetMediaType.image.rawValue
        )
        fetchResult = PHAsset.fetchAssets(with: options)
    }
    
    /// Obtiene fotos de un rango de fechas específico
    func fetchPhotos(from startDate: Date, to endDate: Date) -> PHFetchResult<PHAsset> {
        let options = PHFetchOptions()
        options.predicate = NSPredicate(
            format: "creationDate >= %@ AND creationDate <= %@ AND mediaType == %d",
            startDate as NSDate,
            endDate as NSDate,
            PHAssetMediaType.image.rawValue
        )
        options.sortDescriptors = [
            NSSortDescriptor(key: "creationDate", ascending: true)
        ]
        return PHAsset.fetchAssets(with: options)
    }
    
    // MARK: - Carga de imágenes con caché
    
    /// Solicita una imagen de un asset con el tamaño deseado
    func requestImage(
        for asset: PHAsset,
        targetSize: CGSize,
        completion: @escaping (UIImage?) -> Void
    ) -> PHImageRequestID {
        let options = PHImageRequestOptions()
        options.deliveryMode = .opportunistic  // Entrega rápida primero, luego alta calidad
        options.isNetworkAccessAllowed = true  // Permitir descarga de iCloud
        options.progressHandler = { progress, error, stop, info in
            print("📥 Descargando de iCloud: \(Int(progress * 100))%")
        }
        
        return cachingImageManager.requestImage(
            for: asset,
            targetSize: targetSize,
            contentMode: .aspectFill,
            options: options
        ) { image, info in
            DispatchQueue.main.async {
                completion(image)
            }
        }
    }
    
    /// Precachear imágenes para un rango de assets (ideal para UICollectionView)
    func startCaching(assets: [PHAsset], targetSize: CGSize) {
        cachingImageManager.startCachingImages(
            for: assets,
            targetSize: targetSize,
            contentMode: .aspectFill,
            options: nil
        )
    }
    
    /// Detener el precacheo de un rango específico
    func stopCaching(assets: [PHAsset], targetSize: CGSize) {
        cachingImageManager.stopCachingImages(
            for: assets,
            targetSize: targetSize,
            contentMode: .aspectFill,
            options: nil
        )
    }
    
    // MARK: - Operaciones de escritura
    
    /// Crea un nuevo álbum con el nombre proporcionado
    func createAlbum(
        named title: String,
        completion: @escaping (Result<PHAssetCollection, Error>) -> Void
    ) {
        var placeholderIdentifier: String?
        
        PHPhotoLibrary.shared().performChanges {
            // Crear la solicitud de nuevo álbum
            let request = PHAssetCollectionChangeRequest.creationRequestForAssetCollection(
                withTitle: title
            )
            placeholderIdentifier = request.placeholderForCreatedAssetCollection.localIdentifier
        } completionHandler: { success, error in
            DispatchQueue.main.async {
                if let error = error {
                    completion(.failure(error))
                    return
                }
                
                guard let identifier = placeholderIdentifier else {
                    completion(.failure(NSError(
                        domain: "PhotoKit",
                        code: -1,
                        userInfo: [NSLocalizedDescriptionKey: "No se pudo obtener el identificador"]
                    )))
                    return
                }
                
                // Recuperar el álbum creado usando su identificador
                let collections = PHAssetCollection.fetchAssetCollections(
                    withLocalIdentifiers: [identifier],
                    options: nil
                )
                
                if let album = collections.firstObject {
                    completion(.success(album))
                }
            }
        }
    }
    
    /// Agrega un asset a un álbum existente
    func addAsset(_ asset: PHAsset, toAlbum album: PHAssetCollection,
                  completion: @escaping (Bool) -> Void) {
        PHPhotoLibrary.shared().performChanges {
            guard let request = PHAssetCollectionChangeRequest(for: album) else { return }
            request.addAssets([asset] as NSFastEnumeration)
        } completionHandler: { success, error in
            DispatchQueue.main.async {
                if let error = error {
                    print("❌ Error al agregar asset al álbum: \(error.localizedDescription)")
                }
                completion(success)
            }
        }
    }
    
    /// Elimina assets de la biblioteca (solicita confirmación al usuario)
    func deleteAssets(_ assets: [PHAsset], completion: @escaping (Bool) -> Void) {
        PHPhotoLibrary.shared().performChanges {
            PHAssetChangeRequest.deleteAssets(assets as NSFastEnumeration)
        } completionHandler: { success, error in
            DispatchQueue.main.async {
                completion(success)
            }
        }
    }
    
    // MARK: - PHPhotoLibraryChangeObserver
    
    /// Se invoca cuando la biblioteca de fotos cambia (desde cualquier app)
    func photoLibraryDidChange(_ changeInstance: PHChange) {
        guard let currentResult =