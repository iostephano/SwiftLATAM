---
sidebar_position: 1
title: ImageIO
---

# ImageIO

## ¿Qué es ImageIO?

**ImageIO** es un framework de bajo nivel proporcionado por Apple que permite leer, escribir y manipular datos de imágenes en una amplia variedad de formatos. A diferencia de `UIImage` o `SwiftUI.Image`, que son abstracciones de alto nivel, ImageIO trabaja directamente con las fuentes de datos binarios de las imágenes, lo que otorga un control granular sobre metadatos (EXIF, IPTC, GPS), perfiles de color, miniaturas (thumbnails) y propiedades individuales de cada fotograma en imágenes animadas.

Este framework es la columna vertebral que subyace detrás de muchas operaciones de imagen en iOS, macOS, tvOS y watchOS. Cuando `UIImage` carga un JPEG o un PNG, internamente utiliza ImageIO para decodificar esos bytes. Al exponer esta capa directamente, Apple permite a los desarrolladores realizar tareas que serían imposibles o extremadamente ineficientes con las APIs de alto nivel: decodificación progresiva, generación de miniaturas sin cargar la imagen completa en memoria, lectura y escritura de metadatos EXIF, y conversión eficiente entre formatos.

Deberías considerar usar ImageIO cuando necesites rendimiento óptimo en la carga de imágenes, acceso directo a metadatos fotográficos, generación de miniaturas eficientes en memoria, soporte para formatos especializados (como HEIF, RAW, WebP en versiones recientes) o cuando trabajes con imágenes de gran resolución donde cargar el bitmap completo en memoria no sea viable.

## Casos de uso principales

- **Generación eficiente de miniaturas**: Crear thumbnails de imágenes de alta resolución sin necesidad de decodificar la imagen completa en memoria, ideal para galerías fotográficas y listas con cientos de imágenes.

- **Lectura y escritura de metadatos EXIF/GPS**: Extraer información como la fecha de captura, coordenadas GPS, modelo de cámara, apertura, ISO y velocidad de obturación de fotografías. También permite modificar o eliminar estos metadatos antes de compartir imágenes.

- **Decodificación progresiva de imágenes**: Cargar imágenes de forma incremental conforme los datos llegan desde la red, mostrando una versión parcial mientras la descarga continúa, mejorando drásticamente la experiencia del usuario.

- **Conversión entre formatos de imagen**: Transformar imágenes entre formatos como JPEG, PNG, HEIF, TIFF y GIF de manera eficiente, controlando parámetros de compresión y calidad.

- **Procesamiento de imágenes RAW**: Trabajar con archivos RAW de cámaras profesionales, accediendo a la máxima información tonal disponible antes del procesamiento.

- **Manejo de imágenes animadas (GIF/APNG)**: Acceder a fotogramas individuales de imágenes animadas, controlar tiempos de delay entre frames y crear nuevas animaciones desde código.

## Instalación y configuración

ImageIO es un framework del sistema incluido en todas las plataformas Apple, por lo que **no requiere instalación adicional** mediante Swift Package Manager, CocoaPods ni Carthage.

### Import necesario

```swift
import ImageIO
// Frecuentemente se usa junto con estos frameworks complementarios:
import CoreGraphics    // Para CGImage, CGColorSpace, etc.
import UniformTypeIdentifiers // Para tipos UTI modernos (iOS 14+)
import MobileCoreServices // Para tipos UTI legacy (kUTTypeJPEG, etc.)
```

### Permisos en Info.plist

ImageIO en sí mismo no requiere permisos especiales. Sin embargo, dependiendo de **dónde obtengas las imágenes**, podrías necesitar:

```xml
<!-- Si accedes a la biblioteca de fotos -->
<key>NSPhotoLibraryUsageDescription</key>
<string>Necesitamos acceder a tus fotos para mostrar la galería</string>

<!-- Si accedes a la ubicación embebida en metadatos GPS -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>Usamos la ubicación para etiquetar tus fotos</string>
```

### Compatibilidad de plataformas

| Plataforma | Versión mínima |
|-----------|---------------|
| iOS | 4.0+ |
| macOS | 10.4+ |
| tvOS | 9.0+ |
| watchOS | 2.0+ |
| visionOS | 1.0+ |

## Conceptos clave

### 1. CGImageSource — La fuente de imagen

`CGImageSource` es el objeto fundamental para **leer** imágenes. Representa una fuente de datos de imagen (un archivo, un `Data`, una URL) y proporciona acceso a las imágenes contenidas, sus propiedades y metadatos. Una sola fuente puede contener múltiples imágenes (como en un GIF animado o un archivo TIFF multi-página).

```swift
// Crear una fuente desde una URL de archivo
let source = CGImageSourceCreateWithURL(fileURL as CFURL, nil)

// Crear una fuente desde datos en memoria
let source = CGImageSourceCreateWithData(imageData as CFData, nil)
```

### 2. CGImageDestination — El destino de imagen

`CGImageDestination` es el complemento de `CGImageSource` y se utiliza para **escribir** imágenes. Permite crear archivos de imagen especificando el formato de salida, la cantidad de imágenes, la calidad de compresión y los metadatos asociados.

```swift
// Crear un destino que escribe en una URL
let destination = CGImageDestinationCreateWithURL(
    outputURL as CFURL,
    "public.jpeg" as CFString,
    1,    // cantidad de imágenes
    nil
)
```

### 3. Propiedades y metadatos (Properties)

ImageIO modela los metadatos de imagen como diccionarios anidados de propiedades. Cada nivel tiene claves específicas definidas como constantes globales (`kCGImagePropertyExifDictionary`, `kCGImagePropertyGPSDictionary`, etc.). Estos diccionarios permiten acceder a información detallada sin decodificar los píxeles de la imagen.

### 4. Tipos UTI (Uniform Type Identifiers)

ImageIO identifica los formatos de imagen mediante UTIs. En iOS 14+ se recomienda usar `UTType` del framework `UniformTypeIdentifiers`, mientras que en versiones anteriores se usaban constantes como `kUTTypeJPEG` de `MobileCoreServices`.

### 5. Opciones de creación de thumbnails

Al generar miniaturas, ImageIO acepta un diccionario de opciones que controla el tamaño máximo, si se debe crear la miniatura desde la imagen completa o desde la miniatura embebida en el archivo, y si se debe respetar la orientación EXIF. Estas opciones son clave para optimizar rendimiento y memoria.

### 6. CGImageSource incremental

Para decodificación progresiva, ImageIO proporciona `CGImageSourceCreateIncremental`, que permite alimentar datos parciales y obtener imágenes parcialmente decodificadas. Es fundamental para cargas desde red.

## Ejemplo básico

Este ejemplo muestra cómo generar una miniatura eficiente desde un archivo de imagen local sin cargar la imagen completa en memoria:

```swift
import ImageIO
import UIKit

/// Genera una miniatura eficiente de una imagen ubicada en una URL local.
/// - Parameters:
///   - url: URL del archivo de imagen en disco
///   - maxPixelSize: Tamaño máximo en píxeles del lado más largo de la miniatura
/// - Returns: UIImage con la miniatura generada, o nil si falla
func generarMiniatura(desde url: URL, maxPixelSize: CGFloat = 300) -> UIImage? {
    // 1. Crear la fuente de imagen desde la URL
    guard let imageSource = CGImageSourceCreateWithURL(url as CFURL, nil) else {
        print("❌ No se pudo crear la fuente de imagen desde: \(url)")
        return nil
    }
    
    // 2. Definir opciones para la generación de miniatura
    let opciones: [CFString: Any] = [
        // Tamaño máximo del lado más largo
        kCGImageSourceThumbnailMaxPixelSize: maxPixelSize,
        // Crear la miniatura desde la imagen completa si no hay una embebida
        kCGImageSourceCreateThumbnailFromImageAlways: true,
        // Respetar la orientación EXIF
        kCGImageSourceCreateThumbnailWithTransform: true,
        // Permitir caché para mejorar rendimiento
        kCGImageSourceShouldCache: true
    ]
    
    // 3. Generar la miniatura como CGImage
    guard let thumbnailCG = CGImageSourceCreateThumbnailAtIndex(
        imageSource,
        0,  // Índice de la primera imagen
        opciones as CFDictionary
    ) else {
        print("❌ No se pudo generar la miniatura")
        return nil
    }
    
    // 4. Convertir a UIImage y devolver
    return UIImage(cgImage: thumbnailCG)
}

// --- Uso ---
// let url = Bundle.main.url(forResource: "foto_grande", withExtension: "jpg")!
// let miniatura = generarMiniatura(desde: url, maxPixelSize: 200)
```

## Ejemplo intermedio

Este ejemplo demuestra cómo leer metadatos EXIF y GPS de una fotografía, y cómo eliminar los datos de ubicación antes de compartirla:

```swift
import ImageIO
import CoreGraphics
import UniformTypeIdentifiers

// MARK: - Lectura de metadatos

/// Estructura que representa los metadatos relevantes de una fotografía
struct MetadatosFoto {
    let ancho: Int
    let alto: Int
    let formato: String
    let fechaCaptura: String?
    let modeloCamara: String?
    let iso: [Double]?
    let aperturaF: Double?
    let latitud: Double?
    let longitud: Double?
    let altitud: Double?
}

/// Extrae los metadatos completos de una imagen desde sus datos binarios.
/// - Parameter data: Datos binarios de la imagen
/// - Returns: Estructura con los metadatos extraídos
func extraerMetadatos(de data: Data) -> MetadatosFoto? {
    // 1. Crear la fuente desde los datos
    guard let source = CGImageSourceCreateWithData(data as CFData, nil) else {
        return nil
    }
    
    // 2. Obtener el tipo de imagen (formato)
    let tipoImagen = CGImageSourceGetType(source) as String? ?? "Desconocido"
    
    // 3. Obtener las propiedades de la imagen en el índice 0
    guard let propiedades = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
            as? [CFString: Any] else {
        return nil
    }
    
    // 4. Extraer dimensiones
    let ancho = propiedades[kCGImagePropertyPixelWidth] as? Int ?? 0
    let alto = propiedades[kCGImagePropertyPixelHeight] as? Int ?? 0
    
    // 5. Extraer datos EXIF
    let exif = propiedades[kCGImagePropertyExifDictionary] as? [CFString: Any]
    let fechaCaptura = exif?[kCGImagePropertyExifDateTimeOriginal] as? String
    let iso = exif?[kCGImagePropertyExifISOSpeedRatings] as? [Double]
    let apertura = exif?[kCGImagePropertyExifFNumber] as? Double
    
    // 6. Extraer datos TIFF (modelo de cámara)
    let tiff = propiedades[kCGImagePropertyTIFFDictionary] as? [CFString: Any]
    let modeloCamara = tiff?[kCGImagePropertyTIFFModel] as? String
    
    // 7. Extraer datos GPS
    let gps = propiedades[kCGImagePropertyGPSDictionary] as? [CFString: Any]
    let latitud = gps?[kCGImagePropertyGPSLatitude] as? Double
    let longitud = gps?[kCGImagePropertyGPSLongitude] as? Double
    let altitud = gps?[kCGImagePropertyGPSAltitude] as? Double
    
    return MetadatosFoto(
        ancho: ancho,
        alto: alto,
        formato: tipoImagen,
        fechaCaptura: fechaCaptura,
        modeloCamara: modeloCamara,
        iso: iso,
        aperturaF: apertura,
        latitud: latitud,
        longitud: longitud,
        altitud: altitud
    )
}

// MARK: - Eliminación de metadatos GPS (para privacidad)

/// Crea una copia de la imagen eliminando los datos de ubicación GPS.
/// Útil antes de compartir fotos en redes sociales.
/// - Parameter datosOriginales: Datos binarios de la imagen original
/// - Returns: Datos de la imagen sin información GPS
func eliminarMetadatosGPS(de datosOriginales: Data) -> Data? {
    guard let source = CGImageSourceCreateWithData(datosOriginales as CFData, nil),
          let tipo = CGImageSourceGetType(source) else {
        return nil
    }
    
    // Obtener las propiedades originales
    guard var propiedades = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
            as? [String: Any] else {
        return nil
    }
    
    // Eliminar el diccionario GPS completo
    propiedades[kCGImagePropertyGPSDictionary as String] = nil
    
    // Crear los datos de salida
    let datosSalida = NSMutableData()
    
    guard let destination = CGImageDestinationCreateWithData(
        datosSalida as CFMutableData,
        tipo,
        1,
        nil
    ) else {
        return nil
    }
    
    // Copiar la imagen con las propiedades modificadas
    CGImageDestinationAddImageFromSource(
        destination,
        source,
        0,
        propiedades as CFDictionary
    )
    
    // Finalizar la escritura
    guard CGImageDestinationFinalize(destination) else {
        return nil
    }
    
    return datosSalida as Data
}

// --- Uso ---
// if let data = try? Data(contentsOf: fotoURL) {
//     if let meta = extraerMetadatos(de: data) {
//         print("📷 Cámara: \(meta.modeloCamara ?? "N/A")")
//         print("📅 Fecha: \(meta.fechaCaptura ?? "N/A")")
//         print("📍 Ubicación: \(meta.latitud ?? 0), \(meta.longitud ?? 0)")
//     }
//     
//     let datosLimpios = eliminarMetadatosGPS(de: data)
//     // Compartir datosLimpios de forma segura
// }
```

## Ejemplo avanzado

Este ejemplo implementa un servicio completo de procesamiento de imágenes con arquitectura MVVM, incluyendo decodificación progresiva desde red, generación de miniaturas y conversión de formato:

```swift
import Foundation
import ImageIO
import UIKit
import Combine
import UniformTypeIdentifiers

// MARK: - Modelo

/// Representa una imagen procesada con sus metadatos y variantes
struct ImagenProcesada: Identifiable {
    let id = UUID()
    let imagenOriginal: CGImage
    