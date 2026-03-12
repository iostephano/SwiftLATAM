---
sidebar_position: 1
title: CoreImage
---

# CoreImage

## ¿Qué es CoreImage?

CoreImage es el framework de procesamiento de imágenes de alto rendimiento de Apple, diseñado para aplicar filtros, efectos y transformaciones a imágenes de forma eficiente y en tiempo real. Internamente, CoreImage aprovecha la GPU (a través de Metal) o la CPU según convenga, optimizando automáticamente las cadenas de filtros mediante evaluación diferida (*lazy evaluation*). Esto significa que, sin importar cuántos filtros encadenes, CoreImage los compone en una sola operación optimizada antes de renderizar el resultado final.

Este framework incluye más de 200 filtros integrados organizados en categorías como desenfoque, distorsión, generación de patrones, corrección de color, composición y detección de rostros, entre otros. Cada filtro se representa mediante la clase `CIFilter`, que recibe parámetros de entrada y produce una imagen de salida (`CIImage`). Además, CoreImage permite crear filtros personalizados mediante kernels escritos en el **Core Image Kernel Language** o, desde iOS 15+, usando Metal Shading Language directamente.

CoreImage es la elección ideal cuando necesitas manipular imágenes en tiempo real (por ejemplo, en la cámara), aplicar efectos visuales en aplicaciones de edición fotográfica, generar códigos QR o de barras, o realizar detección de características en imágenes. Su integración nativa con UIKit, SwiftUI, AVFoundation y Metal lo convierte en una pieza central del ecosistema de procesamiento visual de Apple.

## Casos de uso principales

- **Edición fotográfica en tiempo real**: Ajustar brillo, contraste, saturación y temperatura de color de fotos del usuario con previsualización instantánea.
- **Filtros estilo Instagram/VSCO**: Encadenar múltiples filtros para crear *presets* de estilo fotográfico que se aplican de forma no destructiva.
- **Detección de rostros y características**: Identificar posiciones de rostros, ojos y bocas en imágenes para aplicar efectos localizados o validar selfies.
- **Generación de códigos QR y de barras**: Crear dinámicamente códigos QR personalizados (con colores y logos) para compartir enlaces, datos de contacto o información.
- **Procesamiento de video en tiempo real**: Aplicar filtros a cada fotograma capturado por la cámara del dispositivo, integrado con AVFoundation.
- **Corrección automática de imágenes**: Utilizar los *autoAdjustmentFilters* de `CIImage` para mejorar automáticamente la exposición, balance de blancos y reducción de ojos rojos.

## Instalación y configuración

### Agregar CoreImage al proyecto

CoreImage viene incluido en el SDK de iOS, macOS, tvOS y watchOS. No necesitas agregar dependencias externas ni paquetes de Swift Package Manager. Simplemente importa el framework en los archivos donde lo necesites:

```swift
import CoreImage
import CoreImage.CIFilterBuiltins // API type-safe para filtros (iOS 13+)
```

### Permisos en Info.plist

CoreImage por sí solo **no requiere permisos especiales**. Sin embargo, si lo combinas con otros frameworks, necesitarás:

| Permiso | Clave en Info.plist | Cuándo se necesita |
|---|---|---|
| Cámara | `NSCameraUsageDescription` | Al usar CoreImage con AVFoundation para captura en vivo |
| Biblioteca de fotos | `NSPhotoLibraryUsageDescription` | Al leer imágenes del carrete del usuario |
| Guardar fotos | `NSPhotoLibraryAddUsageDescription` | Al guardar imágenes procesadas en el carrete |

### Configuración del CIContext

El `CIContext` es el motor de renderizado. Créalo una sola vez y reutilízalo:

```swift
// Contexto basado en Metal (recomendado para máximo rendimiento)
let device = MTLCreateSystemDefaultDevice()!
let context = CIContext(mtlDevice: device)

// Contexto básico (suficiente para operaciones simples)
let contextBasico = CIContext(options: [
    .workingColorSpace: CGColorSpaceCreateDeviceRGB(),
    .highQualityDownsample: true
])
```

## Conceptos clave

### 1. CIImage — La imagen inmutable

`CIImage` no es un píxel buffer renderizado, sino una **receta** que describe cómo producir una imagen. Es inmutable y ligera. Puede crearse desde múltiples fuentes:

```swift
// Desde un UIImage
let ciImage = CIImage(image: uiImage)

// Desde datos
let ciImage = CIImage(data: imageData)

// Desde una URL de archivo
let ciImage = CIImage(contentsOf: fileURL)

// Desde un CVPixelBuffer (video en vivo)
let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
```

### 2. CIFilter — El procesador de efectos

Cada filtro es una unidad de procesamiento con parámetros de entrada y una imagen de salida. Desde iOS 13, la API *type-safe* con `CIFilter.BuiltIns` elimina la necesidad de usar strings propensos a errores:

```swift
// API moderna (type-safe)
let bloom = CIFilter.bloom()
bloom.inputImage = ciImage
bloom.intensity = 0.8
bloom.radius = 10.0
let resultado = bloom.outputImage

// API clásica (basada en strings)
let filtro = CIFilter(name: "CIBloom", parameters: [
    kCIInputImageKey: ciImage,
    "inputIntensity": 0.8,
    "inputRadius": 10.0
])
```

### 3. CIContext — El renderizador

El `CIContext` ejecuta la receta completa y produce píxeles reales. Es un objeto **costoso de crear**, por lo que debe inicializarse una vez y reutilizarse a lo largo de toda la aplicación:

```swift
let context = CIContext()

// Renderizar a CGImage
let cgImage = context.createCGImage(ciImage, from: ciImage.extent)

// Renderizar a datos JPEG
let jpegData = context.jpegRepresentation(of: ciImage,
                                           colorSpace: CGColorSpaceCreateDeviceRGB(),
                                           options: [:])
```

### 4. Encadenamiento de filtros (Filter Chain)

La verdadera potencia de CoreImage reside en encadenar múltiples filtros. Gracias a la evaluación diferida, CoreImage no renderiza cada paso intermedio, sino que fusiona internamente todas las operaciones en una sola pasada GPU:

```swift
let resultado = ciImage
    .applyingFilter("CIColorControls", parameters: [
        "inputSaturation": 1.2,
        "inputBrightness": 0.05
    ])
    .applyingFilter("CIGaussianBlur", parameters: [
        "inputRadius": 3.0
    ])
    .applyingFilter("CIVignette", parameters: [
        "inputIntensity": 0.8,
        "inputRadius": 2.0
    ])
```

### 5. CIDetector — Detección de características

CoreImage incluye detectores especializados para encontrar rostros, códigos QR, rectángulos y texto en imágenes:

```swift
let detector = CIDetector(ofType: CIDetectorTypeFace,
                           context: context,
                           options: [CIDetectorAccuracy: CIDetectorAccuracyHigh])

let features = detector?.features(in: ciImage) as? [CIFaceFeature] ?? []
for face in features {
    print("Rostro en: \(face.bounds)")
    if face.hasSmile { print("¡Está sonriendo!") }
}
```

### 6. Espacios de color (Color Spaces)

CoreImage trabaja internamente en un espacio de color lineal amplio. Es fundamental entender cómo los espacios de color afectan el resultado para evitar imágenes apagadas o sobresaturadas:

```swift
// Forzar espacio de color de trabajo
let context = CIContext(options: [
    .workingColorSpace: CGColorSpace(name: CGColorSpace.linearSRGB)!
])

// Convertir espacio de color de una imagen
let imagenConvertida = ciImage.matchedFromWorkingSpace(to: CGColorSpace(name: CGColorSpace.sRGB)!)
```

## Ejemplo básico

Este ejemplo aplica un filtro de sepia a una imagen y la convierte en `UIImage`:

```swift
import UIKit
import CoreImage
import CoreImage.CIFilterBuiltins

/// Aplica un efecto sepia clásico a una UIImage
func aplicarFiltroSepia(a imagen: UIImage, intensidad: Float = 0.8) -> UIImage? {
    // 1. Convertir UIImage a CIImage
    guard let ciImage = CIImage(image: imagen) else {
        print("Error: No se pudo crear CIImage desde UIImage")
        return nil
    }
    
    // 2. Crear y configurar el filtro de sepia (API type-safe)
    let filtroSepia = CIFilter.sepiaTone()
    filtroSepia.inputImage = ciImage
    filtroSepia.intensity = intensidad // 0.0 = sin efecto, 1.0 = máximo
    
    // 3. Obtener la imagen de salida (aún es una "receta", no píxeles)
    guard let imagenFiltrada = filtroSepia.outputImage else {
        print("Error: El filtro no produjo imagen de salida")
        return nil
    }
    
    // 4. Renderizar con CIContext para obtener píxeles reales
    let contexto = CIContext() // En producción, reutilizar esta instancia
    guard let cgImage = contexto.createCGImage(imagenFiltrada, from: imagenFiltrada.extent) else {
        print("Error: No se pudo renderizar CGImage")
        return nil
    }
    
    // 5. Convertir a UIImage manteniendo la orientación original
    return UIImage(cgImage: cgImage, scale: imagen.scale, orientation: imagen.imageOrientation)
}

// Uso:
// let imagenOriginal = UIImage(named: "paisaje")!
// let imagenSepia = aplicarFiltroSepia(a: imagenOriginal, intensidad: 0.7)
```

## Ejemplo intermedio

Este ejemplo muestra cómo crear un generador de códigos QR personalizado con colores y logo central:

```swift
import UIKit
import CoreImage
import CoreImage.CIFilterBuiltins

/// Generador de códigos QR personalizados con colores y logo
class GeneradorQR {
    
    private let contexto = CIContext()
    
    /// Genera un código QR personalizado
    /// - Parameters:
    ///   - contenido: Texto o URL a codificar
    ///   - tamaño: Tamaño en puntos de la imagen resultante
    ///   - colorFrente: Color de los módulos del QR
    ///   - colorFondo: Color de fondo del QR
    ///   - logo: Imagen opcional para colocar en el centro
    /// - Returns: UIImage del código QR personalizado
    func generar(
        contenido: String,
        tamaño: CGFloat = 300,
        colorFrente: UIColor = .black,
        colorFondo: UIColor = .white,
        logo: UIImage? = nil
    ) -> UIImage? {
        
        // 1. Generar el QR base
        let generador = CIFilter.qrCodeGenerator()
        generador.message = Data(contenido.utf8)
        generador.correctionLevel = "H" // Alta corrección para permitir logo central
        
        guard let qrCIImage = generador.outputImage else { return nil }
        
        // 2. Aplicar colores personalizados usando CIFalseColor
        let filtroColor = CIFilter.falseColor()
        filtroColor.inputImage = qrCIImage
        filtroColor.color0 = CIColor(color: colorFrente) // Módulos oscuros
        filtroColor.color1 = CIColor(color: colorFondo)  // Fondo claro
        
        guard let qrColoreado = filtroColor.outputImage else { return nil }
        
        // 3. Escalar al tamaño deseado (el QR original es muy pequeño)
        let escala = tamaño / qrColoreado.extent.width
        let transformacion = CGAffineTransform(scaleX: escala, y: escala)
        let qrEscalado = qrColoreado.transformed(by: transformacion)
        
        // 4. Renderizar a CGImage
        guard let cgImage = contexto.createCGImage(qrEscalado, from: qrEscalado.extent) else {
            return nil
        }
        
        var imagenFinal = UIImage(cgImage: cgImage)
        
        // 5. Superponer logo si se proporcionó
        if let logo = logo {
            imagenFinal = superponerLogo(logo, sobre: imagenFinal, tamaño: tamaño)
        }
        
        return imagenFinal
    }
    
    /// Superpone un logo circular en el centro del código QR
    private func superponerLogo(_ logo: UIImage, sobre qr: UIImage, tamaño: CGFloat) -> UIImage {
        let tamañoLogo = tamaño * 0.25 // El logo ocupa el 25% del QR
        let renderer = UIGraphicsImageRenderer(size: CGSize(width: tamaño, height: tamaño))
        
        return renderer.image { ctx in
            // Dibujar el QR de fondo
            qr.draw(in: CGRect(origin: .zero, size: CGSize(width: tamaño, height: tamaño)))
            
            // Calcular posición centrada para el logo
            let origenLogo = CGPoint(
                x: (tamaño - tamañoLogo) / 2,
                y: (tamaño - tamañoLogo) / 2
            )
            let rectoLogo = CGRect(origin: origenLogo,
                                    size: CGSize(width: tamañoLogo, height: tamañoLogo))
            
            // Fondo blanco circular detrás del logo
            let padding: CGFloat = 4
            let rectoPadding = rectoLogo.insetBy(dx: -padding, dy: -padding)
            ctx.cgContext.setFillColor(UIColor.white.cgColor)
            ctx.cgContext.fillEllipse(in: rectoPadding)
            
            // Recortar en forma circular y dibujar el logo
            ctx.cgContext.addEllipse(in: rectoLogo)
            ctx.cgContext.clip()
            logo.draw(in: rectoLogo)
        }
    }
}

// Uso:
// let generador = GeneradorQR()
// let qrPersonalizado = generador.generar(
//     contenido: "https://miapp.com/perfil/12345",
//     tamaño: 300,
//     colorFrente: .systemIndigo,
//     colorFondo: .white,
//     logo: UIImage(named: "logo_app")
// )
```

## Ejemplo avanzado

Este ejemplo implementa un editor de fotos con arquitectura MVVM, procesamiento reactivo con Combine y vista en SwiftUI:

```swift
import SwiftUI
import Combine
import CoreImage
import CoreImage.CIFilterBuiltins

// MARK: - Modelo de datos

/// Representa los ajustes de edición de una imagen
struct AjustesImagen: Equatable {