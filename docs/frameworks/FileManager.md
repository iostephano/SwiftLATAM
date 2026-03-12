---
sidebar_position: 1
title: FileManager
---

# FileManager

## ¿Qué es FileManager?

`FileManager` es la clase fundamental del framework **Foundation** de Apple que proporciona una interfaz centralizada para interactuar con el sistema de archivos del dispositivo. A través de ella, los desarrolladores pueden crear, leer, copiar, mover y eliminar archivos y directorios, así como inspeccionar sus atributos (tamaño, fecha de modificación, permisos, etc.). Es el punto de entrada principal para cualquier operación de persistencia basada en archivos dentro del ecosistema Apple.

En iOS, cada aplicación vive dentro de su propio **sandbox**, un contenedor aislado que limita el acceso al sistema de archivos exclusivamente a los directorios asignados a dicha app. `FileManager` permite navegar de forma segura por estos directorios —`Documents`, `Library`, `tmp`, `Caches`—, garantizando que las operaciones respeten las políticas de seguridad del sistema operativo. Esto es crucial tanto para proteger los datos del usuario como para cumplir con los requisitos de la App Store.

Deberías usar `FileManager` siempre que necesites almacenar archivos que no encajan en bases de datos estructuradas: imágenes descargadas, documentos PDF, archivos JSON de configuración, cachés de contenido multimedia, archivos temporales de procesamiento o cualquier tipo de dato binario. Aunque existen alternativas como Core Data, SwiftData o UserDefaults para ciertos escenarios, `FileManager` ofrece el control más granular y directo sobre el sistema de archivos.

---

## Casos de uso principales

1. **Almacenamiento de imágenes y multimedia**: Guardar fotos capturadas por la cámara, thumbnails generados, vídeos descargados o archivos de audio para reproducción offline. Es el enfoque estándar cuando los binarios son demasiado grandes para bases de datos.

2. **Gestión de caché de red**: Almacenar respuestas de API, imágenes de perfil o recursos estáticos en el directorio `Caches` para reducir llamadas de red y mejorar la experiencia offline, con la posibilidad de que el sistema los elimine si necesita espacio.

3. **Exportación e importación de documentos**: Crear archivos PDF, CSV, JSON u otros formatos que el usuario puede compartir a través de `UIActivityViewController`, AirDrop o guardar en la app Archivos mediante `UIDocumentPickerViewController`.

4. **Persistencia de configuración compleja**: Cuando la configuración de la app supera lo que `UserDefaults` maneja cómodamente (archivos JSON grandes, esquemas de configuración anidados), `FileManager` permite serializar y deserializar estructuras complejas.

5. **Descargas en segundo plano**: Gestionar archivos descargados por `URLSession` con tareas de background, moviéndolos desde ubicaciones temporales a directorios permanentes una vez completada la transferencia.

6. **Migración y mantenimiento de datos**: Limpiar archivos obsoletos entre versiones de la app, reorganizar estructuras de directorios tras actualizaciones o calcular el espacio en disco utilizado por la aplicación.

---

## Instalación y configuración

### Importación

`FileManager` forma parte de **Foundation**, que se importa automáticamente en la mayoría de los proyectos. No necesitas agregar ninguna dependencia adicional:

```swift
import Foundation
```

### Permisos en Info.plist

Para operaciones dentro del sandbox de la app, **no se necesitan permisos adicionales**. Sin embargo, existen escenarios donde sí se requieren:

| Escenario | Clave en Info.plist |
|---|---|
| Acceder a la galería de fotos | `NSPhotoLibraryUsageDescription` |
| Acceder a la carpeta de descargas (macOS) | `com.apple.security.files.downloads.read-write` |
| Acceso a carpetas del usuario (macOS) | `com.apple.security.files.user-selected.read-write` |
| Documentos en iCloud | Activar la capability **iCloud Documents** |

### Configuración de App Groups (para compartir archivos entre apps/extensiones)

Si necesitas compartir archivos entre tu app principal y una extensión (widget, notification service, etc.):

1. Ve a tu target → **Signing & Capabilities** → **+ Capability** → **App Groups**.
2. Crea un grupo con formato `group.com.tuempresa.tuapp`.
3. Accede al contenedor compartido:

```swift
let sharedContainer = FileManager.default.containerURL(
    forSecurityApplicationGroupIdentifier: "group.com.tuempresa.tuapp"
)
```

---

## Conceptos clave

### 1. La instancia `default`

`FileManager` se utiliza habitualmente a través de su **singleton** `FileManager.default`. Esta instancia compartida es segura para operaciones individuales, pero si necesitas un delegado (`FileManagerDelegate`) para interceptar operaciones de copia, movimiento o eliminación, debes crear tu propia instancia con `FileManager()`.

### 2. Estructura del sandbox en iOS

Cada app tiene su propia estructura de directorios aislada:

```
AppContainer/
├── Documents/          → Datos del usuario (se respalda en iCloud)
├── Library/
│   ├── Caches/         → Datos temporales (NO se respalda, el sistema puede borrar)
│   ├── Preferences/    → UserDefaults (gestionado automáticamente)
│   └── Application Support/ → Datos de la app (se respalda en iCloud)
├── tmp/                → Archivos temporales (el sistema puede borrar en cualquier momento)
└── SystemData/         → Uso interno del sistema
```

### 3. URLs vs Paths

Apple recomienda encarecidamente usar **`URL`** en lugar de cadenas de texto (`String`) para representar rutas de archivos. Las URLs son más seguras, evitan problemas de codificación de caracteres y se integran mejor con las APIs modernas:

```swift
// ✅ Recomendado
let url = documentsURL.appendingPathComponent("datos.json")

// ❌ Evitar
let path = "/var/mobile/.../Documents/datos.json"
```

### 4. Operaciones síncronas

La mayoría de las operaciones de `FileManager` son **síncronas y bloqueantes**. Esto significa que si lees un archivo de 500 MB en el hilo principal, la interfaz se congelará. Siempre debes ejecutar operaciones pesadas en un hilo secundario usando `DispatchQueue`, `Task` o `OperationQueue`.

### 5. Atributos de archivos

Cada archivo y directorio posee un diccionario de atributos que incluye tamaño, fecha de creación, fecha de modificación, tipo (archivo regular, directorio, enlace simbólico), permisos, etc. Se accede con `attributesOfItem(atPath:)` y se modifican con `setAttributes(_:ofItemAtPath:)`.

### 6. Protección de datos (Data Protection)

iOS ofrece niveles de protección de archivos que determinan cuándo están accesibles:

- `.complete` → Solo cuando el dispositivo está desbloqueado.
- `.completeUnlessOpen` → Disponible si el archivo ya estaba abierto.
- `.completeUntilFirstUserAuthentication` → Disponible tras el primer desbloqueo (valor por defecto).
- `.none` → Siempre disponible.

---

## Ejemplo básico

Este ejemplo muestra las operaciones fundamentales: obtener directorios, escribir un archivo de texto y leerlo de vuelta.

```swift
import Foundation

// MARK: - Obtener el directorio Documents
let fileManager = FileManager.default

guard let documentsURL = fileManager.urls(
    for: .documentDirectory,
    in: .userDomainMask
).first else {
    fatalError("No se pudo acceder al directorio Documents")
}

print("📁 Documents: \(documentsURL.path)")

// MARK: - Escribir un archivo de texto
let archivoURL = documentsURL.appendingPathComponent("saludo.txt")
let contenido = "¡Hola desde FileManager!"

do {
    try contenido.write(to: archivoURL, atomically: true, encoding: .utf8)
    print("✅ Archivo escrito correctamente")
} catch {
    print("❌ Error al escribir: \(error.localizedDescription)")
}

// MARK: - Verificar si el archivo existe
if fileManager.fileExists(atPath: archivoURL.path) {
    print("📄 El archivo existe en: \(archivoURL.lastPathComponent)")
}

// MARK: - Leer el contenido del archivo
do {
    let textoLeido = try String(contentsOf: archivoURL, encoding: .utf8)
    print("📖 Contenido: \(textoLeido)")
} catch {
    print("❌ Error al leer: \(error.localizedDescription)")
}

// MARK: - Obtener atributos del archivo
do {
    let atributos = try fileManager.attributesOfItem(atPath: archivoURL.path)
    let tamaño = atributos[.size] as? Int64 ?? 0
    let fechaCreacion = atributos[.creationDate] as? Date ?? Date()
    print("📊 Tamaño: \(tamaño) bytes | Creado: \(fechaCreacion)")
} catch {
    print("❌ Error al obtener atributos: \(error.localizedDescription)")
}

// MARK: - Eliminar el archivo
do {
    try fileManager.removeItem(at: archivoURL)
    print("🗑️ Archivo eliminado correctamente")
} catch {
    print("❌ Error al eliminar: \(error.localizedDescription)")
}
```

---

## Ejemplo intermedio

Un servicio reutilizable para gestionar el almacenamiento de imágenes en caché con creación automática de directorios, listado de contenidos y cálculo de espacio usado.

```swift
import Foundation
import UIKit

// MARK: - Servicio de caché de imágenes basado en FileManager

final class ImageCacheService {
    
    // MARK: - Propiedades
    
    static let shared = ImageCacheService()
    
    private let fileManager = FileManager.default
    private let cacheDirectoryName = "ImageCache"
    
    /// URL del directorio de caché personalizado
    private var cacheDirectoryURL: URL {
        let cachesURL = fileManager.urls(
            for: .cachesDirectory,
            in: .userDomainMask
        ).first!
        return cachesURL.appendingPathComponent(cacheDirectoryName)
    }
    
    // MARK: - Inicialización
    
    private init() {
        crearDirectorioCacheSiNoExiste()
    }
    
    // MARK: - Crear directorio de caché
    
    private func crearDirectorioCacheSiNoExiste() {
        guard !fileManager.fileExists(atPath: cacheDirectoryURL.path) else { return }
        
        do {
            // withIntermediateDirectories: true → crea directorios padres si no existen
            try fileManager.createDirectory(
                at: cacheDirectoryURL,
                withIntermediateDirectories: true,
                attributes: nil
            )
            print("📁 Directorio de caché creado: \(cacheDirectoryURL.lastPathComponent)")
        } catch {
            print("❌ Error al crear directorio de caché: \(error.localizedDescription)")
        }
    }
    
    // MARK: - Guardar imagen
    
    /// Guarda una UIImage en el directorio de caché con un identificador único
    /// - Parameters:
    ///   - image: La imagen a guardar
    ///   - identifier: Identificador único (por ejemplo, un hash de la URL de origen)
    ///   - compressionQuality: Calidad de compresión JPEG (0.0 a 1.0)
    /// - Returns: `true` si se guardó correctamente
    @discardableResult
    func guardarImagen(
        _ image: UIImage,
        identificador: String,
        calidadCompresion: CGFloat = 0.8
    ) -> Bool {
        let archivoURL = cacheDirectoryURL
            .appendingPathComponent(identificador)
            .appendingPathExtension("jpg")
        
        guard let data = image.jpegData(compressionQuality: calidadCompresion) else {
            print("❌ No se pudo convertir la imagen a datos JPEG")
            return false
        }
        
        do {
            try data.write(to: archivoURL, options: [.atomic])
            print("✅ Imagen guardada: \(archivoURL.lastPathComponent)")
            return true
        } catch {
            print("❌ Error al guardar imagen: \(error.localizedDescription)")
            return false
        }
    }
    
    // MARK: - Cargar imagen
    
    /// Recupera una imagen previamente almacenada en caché
    /// - Parameter identifier: El mismo identificador usado al guardar
    /// - Returns: La UIImage si existe, nil si no se encuentra
    func cargarImagen(identificador: String) -> UIImage? {
        let archivoURL = cacheDirectoryURL
            .appendingPathComponent(identificador)
            .appendingPathExtension("jpg")
        
        guard fileManager.fileExists(atPath: archivoURL.path) else {
            print("⚠️ Imagen no encontrada en caché: \(identificador)")
            return nil
        }
        
        do {
            let data = try Data(contentsOf: archivoURL)
            return UIImage(data: data)
        } catch {
            print("❌ Error al cargar imagen: \(error.localizedDescription)")
            return nil
        }
    }
    
    // MARK: - Listar imágenes en caché
    
    /// Devuelve los nombres de todos los archivos almacenados en el directorio de caché
    func listarImagenesEnCache() -> [String] {
        do {
            let contenidos = try fileManager.contentsOfDirectory(
                at: cacheDirectoryURL,
                includingPropertiesForKeys: [.fileSizeKey, .creationDateKey],
                options: [.skipsHiddenFiles] // Ignorar archivos como .DS_Store
            )
            return contenidos.map { $0.lastPathComponent }
        } catch {
            print("❌ Error al listar caché: \(error.localizedDescription)")
            return []
        }
    }
    
    // MARK: - Calcular tamaño del caché
    
    /// Calcula el tamaño total en bytes del directorio de caché
    func calcularTamañoCache() -> Int64 {
        do {
            let contenidos = try fileManager.contentsOfDirectory(
                at: cacheDirectoryURL,
                includingPropertiesForKeys: [.fileSizeKey],
                options: .skipsHiddenFiles
            )
            
            var tamañoTotal: Int64 = 0
            
            for archivoURL in contenidos {
                let atributos = try fileManager.attributesOfItem(atPath: archivoURL.path)
                tamañoTotal += atributos[.size] as? Int64 ?? 0
            }
            
            return tamañoTotal
        } catch {
            print("❌ Error al calcular tamaño: \(error.localizedDescription)")
            return 0
        }
    }
    
    /// Devuelve el tamaño del caché formateado para mostrar al usuario
    var tamañoCacheFormateado: String {
        let bytes = calcularTamañoCache()
        let formatter = ByteCountFormatter()
        formatter.allowedUnits =