---
sidebar_position: 1
title: Photos
---

# Photos

## ¿Qué es Photos?

Photos es el framework de Apple que proporciona acceso directo a la biblioteca de fotos y vídeos gestionada por la aplicación Fotos del sistema. A través de sus API, los desarrolladores pueden consultar, crear, editar y eliminar recursos multimedia (fotos, vídeos, Live Photos, etc.), así como trabajar con álbumes, momentos y colecciones inteligentes. El framework actúa como una capa de abstracción sobre la base de datos de medios del dispositivo, garantizando la coherencia de los datos y respetando los permisos de privacidad del usuario.

Este framework es fundamental para cualquier aplicación que necesite interactuar con la galería del usuario más allá de lo que ofrece el simple `UIImagePickerController` o `PHPickerViewController`. Permite operaciones complejas como la observación de cambios en tiempo real, la solicitud de imágenes con distintas calidades y tamaños, la edición no destructiva de recursos, y la gestión programática de álbumes personalizados.

Photos está disponible desde iOS 8, macOS 10.13, tvOS 10 y Mac Catalyst 13, y ha evolucionado significativamente a lo largo de los años. En versiones recientes de iOS, Apple ha introducido niveles de acceso limitado (`PHAccessLevel.limited`) que permiten al usuario compartir solo un subconjunto de sus fotos, lo que exige a los desarrolladores adaptar sus flujos de trabajo para respetar estas restricciones de privacidad.

## Casos de uso principales

- **Galería de fotos personalizada**: Construir una interfaz propia para navegar las fotos y vídeos del usuario con diseño personalizado, filtros por fecha, tipo de medio o ubicación, reemplazando el picker estándar del sistema.

- **Editor de imágenes**: Aplicar filtros, recortes y ajustes sobre fotos existentes usando edición no destructiva. Los cambios se guardan en la biblioteca de Fotos y el usuario puede revertirlos desde la app nativa.

- **Copia de seguridad y sincronización**: Leer todos los recursos multimedia del dispositivo para subirlos a un servicio en la nube, detectando nuevas fotos mediante observadores de cambios (`PHPhotoLibraryChangeObserver`).

- **Selección masiva de medios**: Permitir que el usuario seleccione múltiples fotos o vídeos para compartir, adjuntar a un mensaje o procesar por lotes, con control total sobre la experiencia de usuario.

- **Creación de álbumes automáticos**: Organizar fotos programáticamente en álbumes personalizados basados en criterios como ubicación, fecha, etiquetas de Machine Learning u otros metadatos.

- **Widgets y extensiones**: Acceder a fotos recientes o favoritas para mostrarlas en widgets de pantalla de inicio, complicaciones de watchOS o extensiones de compartir.

## Instalación y configuración

### Agregar el framework al proyecto

Photos forma parte del SDK del sistema, por lo que no se requiere instalación adicional mediante SPM, CocoaPods o Carthage. Simplemente importa el módulo en los archivos donde lo necesites:

```swift
import Photos
import PhotosUI // Para componentes de interfaz como PHPickerViewController
```

### Permisos en Info.plist

El acceso a la biblioteca de fotos requiere permisos explícitos del usuario. Debes agregar las siguientes claves a tu archivo `Info.plist`:

```xml
<!-- Permiso de lectura y escritura completo -->
<key>NSPhotoLibraryUsageDescription</key>
<string>Necesitamos acceso a tu biblioteca de fotos para mostrar y gestionar tus imágenes.</string>

<!-- Permiso solo para agregar fotos (sin lectura) -->
<key>NSPhotoLibraryAddUsageDescription</key>
<string>Necesitamos permiso para guardar fotos en tu biblioteca.</string>
```

### Solicitar autorización en código

```swift
import Photos

// Solicitar acceso con nivel específico (iOS 14+)
PHPhotoLibrary.requestAuthorization(for: .readWrite) { status in
    switch status {
    case .authorized:
        print("Acceso completo concedido")
    case .limited:
        print("Acceso limitado: el usuario seleccionó fotos específicas")
    case .denied, .restricted:
        print("Acceso denegado o restringido")
    case .notDetermined:
        print("Aún no se ha solicitado el permiso")
    @unknown default:
        break
    }
}
```

## Conceptos clave

### 1. PHAsset

Es la representación de un recurso multimedia individual (foto, vídeo, Live Photo, etc.) en la biblioteca. Contiene metadatos como fecha de creación, ubicación, dimensiones, tipo de medio y si es favorito. **No contiene los datos de imagen en sí**, sino que actúa como referencia para solicitarlos posteriormente.

### 2. PHAssetCollection y PHCollectionList

`PHAssetCollection` representa un grupo de assets, como un álbum del usuario, un álbum inteligente del sistema (capturas de pantalla, selfies, panorámicas) o un momento. `PHCollectionList` es una colección de colecciones, útil para representar jerarquías como carpetas de álbumes o agrupaciones por año.

### 3. PHFetchResult

Es el objeto que devuelven las consultas al framework. Funciona de forma similar a un array pero con carga diferida (*lazy loading*): los objetos se recuperan de la base de datos solo cuando se acceden, lo que lo hace extremadamente eficiente incluso con bibliotecas de miles de fotos.

### 4. PHImageManager y PHCachingImageManager

`PHImageManager` es el servicio centralizado para solicitar imágenes y vídeos a partir de `PHAsset`. Permite especificar el tamaño deseado, el modo de entrega (rápido, de alta calidad o oportunista) y si se desea la versión original o editada. `PHCachingImageManager` es una subclase optimizada para precargar imágenes de múltiples assets, ideal para colecciones con scroll.

### 5. PHPhotoLibraryChangeObserver

Protocolo que permite observar cambios en la biblioteca de fotos en tiempo real. Cuando el usuario toma una nueva foto, elimina una imagen o edita un recurso desde otra app, tu aplicación recibe una notificación con los detalles incrementales del cambio para actualizar la interfaz eficientemente.

### 6. PHContentEditingInput / Output

Estos objetos son la base del sistema de edición no destructiva. `PHContentEditingInput` proporciona los datos originales del recurso, mientras que `PHContentEditingOutput` permite guardar los resultados de la edición junto con los datos de ajuste necesarios para que la edición pueda revertirse o modificarse posteriormente.

## Ejemplo básico

```swift
import Photos
import UIKit

/// Ejemplo básico: obtener todas las fotos del usuario ordenadas por fecha
class BasicPhotosFetcher {
    
    /// Solicita permisos y obtiene las últimas 20 fotos del carrete
    func fetchRecentPhotos(completion: @escaping ([UIImage]) -> Void) {
        // 1. Solicitar autorización
        PHPhotoLibrary.requestAuthorization(for: .readWrite) { status in
            guard status == .authorized || status == .limited else {
                print("No se tiene acceso a la biblioteca de fotos")
                completion([])
                return
            }
            
            // 2. Configurar las opciones de búsqueda
            let fetchOptions = PHFetchOptions()
            fetchOptions.sortDescriptors = [
                NSSortDescriptor(key: "creationDate", ascending: false)
            ]
            fetchOptions.fetchLimit = 20 // Limitar a 20 resultados
            
            // 3. Ejecutar la consulta para obtener solo imágenes
            let fetchResult = PHAsset.fetchAssets(
                with: .image,
                options: fetchOptions
            )
            
            // 4. Solicitar la imagen de cada asset
            let imageManager = PHImageManager.default()
            let requestOptions = PHImageRequestOptions()
            requestOptions.isSynchronous = true
            requestOptions.deliveryMode = .highQualityFormat
            requestOptions.resizeMode = .exact
            
            var images: [UIImage] = []
            let targetSize = CGSize(width: 300, height: 300)
            
            // 5. Iterar sobre los resultados
            fetchResult.enumerateObjects { asset, index, _ in
                imageManager.requestImage(
                    for: asset,
                    targetSize: targetSize,
                    contentMode: .aspectFill,
                    options: requestOptions
                ) { image, info in
                    if let image = image {
                        images.append(image)
                    }
                }
            }
            
            // 6. Devolver las imágenes en el hilo principal
            DispatchQueue.main.async {
                completion(images)
            }
        }
    }
}
```

## Ejemplo intermedio

```swift
import Photos
import UIKit

/// Ejemplo intermedio: gestor completo de álbumes con observación de cambios
class PhotoLibraryManager: NSObject, PHPhotoLibraryChangeObserver {
    
    // MARK: - Propiedades
    
    /// Resultado de la consulta actual (se actualiza con cambios)
    private(set) var fetchResult: PHFetchResult<PHAsset>
    
    /// Cache manager para scroll eficiente en colecciones
    private let cachingManager = PHCachingImageManager()
    
    /// Closure que se ejecuta cuando la biblioteca cambia
    var onLibraryChange: ((_ changeDetails: PHFetchResultChangeDetails<PHAsset>) -> Void)?
    
    // MARK: - Inicialización
    
    override init() {
        // Configurar consulta inicial: todas las imágenes ordenadas por fecha
        let options = PHFetchOptions()
        options.sortDescriptors = [
            NSSortDescriptor(key: "creationDate", ascending: false)
        ]
        options.predicate = NSPredicate(
            format: "mediaType == %d", PHAssetMediaType.image.rawValue
        )
        
        self.fetchResult = PHAsset.fetchAssets(with: options)
        
        super.init()
        
        // Registrar observador de cambios en la biblioteca
        PHPhotoLibrary.shared().register(self)
    }
    
    deinit {
        // Siempre desregistrar el observador al destruir la instancia
        PHPhotoLibrary.shared().unregisterChangeObserver(self)
    }
    
    // MARK: - Obtener imágenes
    
    /// Solicita una imagen para un índice específico con calidad configurable
    func requestImage(
        at index: Int,
        targetSize: CGSize,
        completion: @escaping (UIImage?) -> Void
    ) {
        guard index < fetchResult.count else {
            completion(nil)
            return
        }
        
        let asset = fetchResult.object(at: index)
        
        let options = PHImageRequestOptions()
        options.isNetworkAccessAllowed = true // Permitir descarga de iCloud
        options.deliveryMode = .opportunistic // Primero baja calidad, luego alta
        
        // Indicador de progreso para descargas de iCloud
        options.progressHandler = { progress, error, _, _ in
            DispatchQueue.main.async {
                print("Descargando de iCloud: \(Int(progress * 100))%")
            }
        }
        
        cachingManager.requestImage(
            for: asset,
            targetSize: targetSize,
            contentMode: .aspectFill,
            options: options
        ) { image, info in
            let isDegraded = (info?[PHImageResultIsDegradedKey] as? Bool) ?? false
            // Solo devolver si no es la versión degradada o si es la única
            if !isDegraded {
                DispatchQueue.main.async {
                    completion(image)
                }
            }
        }
    }
    
    // MARK: - Gestión de álbumes
    
    /// Crea un nuevo álbum personalizado en la biblioteca
    func createAlbum(
        named title: String,
        completion: @escaping (Result<PHAssetCollection, Error>) -> Void
    ) {
        var albumPlaceholder: PHObjectPlaceholder?
        
        PHPhotoLibrary.shared().performChanges {
            // Crear la solicitud de cambio para un nuevo álbum
            let request = PHAssetCollectionChangeRequest
                .creationRequestForAssetCollection(withTitle: title)
            albumPlaceholder = request.placeholderForCreatedAssetCollection
        } completionHandler: { success, error in
            DispatchQueue.main.async {
                if let error = error {
                    completion(.failure(error))
                    return
                }
                
                guard let placeholder = albumPlaceholder else {
                    completion(.failure(PhotoError.albumCreationFailed))
                    return
                }
                
                // Obtener el álbum recién creado
                let albums = PHAssetCollection.fetchAssetCollections(
                    withLocalIdentifiers: [placeholder.localIdentifier],
                    options: nil
                )
                
                if let album = albums.firstObject {
                    completion(.success(album))
                } else {
                    completion(.failure(PhotoError.albumCreationFailed))
                }
            }
        }
    }
    
    /// Agrega un asset existente a un álbum
    func addAsset(
        _ asset: PHAsset,
        toAlbum album: PHAssetCollection,
        completion: @escaping (Bool) -> Void
    ) {
        PHPhotoLibrary.shared().performChanges {
            guard let changeRequest = PHAssetCollectionChangeRequest(
                for: album
            ) else { return }
            
            changeRequest.addAssets([asset] as NSFastEnumeration)
        } completionHandler: { success, error in
            DispatchQueue.main.async {
                if let error = error {
                    print("Error al agregar asset al álbum: \(error)")
                }
                completion(success)
            }
        }
    }
    
    /// Obtiene todos los álbumes del usuario
    func fetchUserAlbums() -> [PHAssetCollection] {
        let options = PHFetchOptions()
        options.sortDescriptors = [
            NSSortDescriptor(key: "localizedTitle", ascending: true)
        ]
        
        let albums = PHAssetCollection.fetchAssetCollections(
            with: .album,
            subtype: .albumRegular,
            options: options
        )
        
        var result: [PHAssetCollection] = []
        albums.enumerateObjects { collection, _, _ in
            result.append(collection)
        }
        
        return result
    }
    
    // MARK: - Guardar imágenes
    
    /// Guarda una UIImage en la biblioteca de fotos
    func saveImage(
        _ image: UIImage,
        completion: @escaping (Result<String, Error>) -> Void
    ) {
        var localIdentifier: String?
        
        PHPhotoLibrary.shared().performChanges {
            let request = PHAssetChangeRequest.creationRequestForAsset(
                from: image
            )
            localIdentifier = request.placeholderForCreatedAsset?
                .localIdentifier
        } completionHandler: { success, error in
            DispatchQueue.main.async {
                if let error = error {
                    completion(.failure(error))
                } else if let id = localIdentifier {
                    completion(.success(id))
                }
            }
        }
    }
    
    // MARK: - PHPhotoLibraryChangeObserver
    
    func photoLibraryDidChange(_ changeInstance: PHChange) {
        // Verificar si hay cambios que afecten nuestra consulta