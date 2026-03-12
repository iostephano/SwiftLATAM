---
sidebar_position: 1
title: Vision
---

# Vision

## ¿Qué es Vision?

Vision es el framework de Apple diseñado para aplicar técnicas de visión por computadora a imágenes y vídeo de manera eficiente y sencilla. Introducido en iOS 11 y expandido significativamente en versiones posteriores, Vision abstrae la complejidad del procesamiento de imágenes y el aprendizaje automático, ofreciendo APIs de alto nivel para tareas como detección de rostros, reconocimiento de texto, clasificación de imágenes, seguimiento de objetos y análisis de poses corporales, entre muchas otras.

Este framework opera sobre un sistema de **solicitudes y observaciones** (*requests* y *observations*): el desarrollador crea una solicitud específica indicando qué desea detectar o analizar, la ejecuta contra una imagen o secuencia de vídeo, y recibe observaciones estructuradas con los resultados. Internamente, Vision aprovecha Core ML, Metal y el Neural Engine del dispositivo para ejecutar modelos de aprendizaje automático optimizados, sin que el desarrollador necesite conocer los detalles de implementación.

Vision es ideal cuando necesitas extraer información semántica de contenido visual: desde escanear documentos y leer texto en tiempo real, hasta construir experiencias de realidad aumentada basadas en el reconocimiento de manos o poses corporales. Su integración nativa con el ecosistema Apple garantiza rendimiento óptimo en todos los dispositivos, desde iPhone y iPad hasta Mac y Apple Vision Pro.

## Casos de uso principales

- **Reconocimiento óptico de caracteres (OCR):** Extraer texto de imágenes, escanear documentos, leer tarjetas de visita, matrículas o señales de tráfico en tiempo real mediante `VNRecognizeTextRequest`.

- **Detección y reconocimiento facial:** Identificar rostros en imágenes, detectar puntos de referencia faciales (ojos, nariz, boca) y analizar expresiones. Útil para apps de fotografía, filtros y autenticación visual.

- **Clasificación de imágenes:** Categorizar el contenido de una imagen usando modelos integrados o modelos Core ML personalizados. Ideal para organizar galerías fotográficas o sistemas de etiquetado automático.

- **Detección de poses corporales y manos:** Analizar la postura del cuerpo humano o la posición de las manos para aplicaciones de fitness, lenguaje de señas, control gestual o realidad aumentada.

- **Seguimiento de objetos en vídeo:** Rastrear objetos en movimiento cuadro a cuadro en secuencias de vídeo, útil para análisis deportivo, vigilancia inteligente o experiencias interactivas.

- **Detección de códigos de barras y QR:** Identificar y decodificar múltiples formatos de códigos de barras y códigos QR presentes en una imagen o flujo de cámara.

## Instalación y configuración

### Agregar el framework al proyecto

Vision es un framework nativo de Apple incluido en el SDK de iOS, macOS, tvOS y visionOS. **No requiere instalación mediante gestores de paquetes.** Simplemente importa el módulo en los archivos donde lo necesites:

```swift
import Vision
```

### Permisos en Info.plist

Vision por sí mismo no requiere permisos especiales. Sin embargo, si capturas imágenes desde la cámara o accedes a la biblioteca de fotos, necesitarás declarar los permisos correspondientes:

```xml
<!-- Acceso a la cámara -->
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceso a la cámara para analizar imágenes en tiempo real.</string>

<!-- Acceso a la biblioteca de fotos -->
<key>NSPhotoLibraryUsageDescription</key>
<string>Necesitamos acceso a tus fotos para procesar imágenes.</string>
```

### Compatibilidad

| Plataforma | Versión mínima |
|---|---|
| iOS | 11.0+ |
| macOS | 10.13+ |
| tvOS | 11.0+ |
| visionOS | 1.0+ |

> **Nota:** Algunas APIs como `VNRecognizeTextRequest` requieren iOS 13+ y las APIs revisadas de Vision (Swift moderno con async/await) están disponibles a partir de iOS 17+/macOS 14+.

## Conceptos clave

### 1. VNRequest (Solicitud)

Es la clase base para todas las solicitudes de análisis. Cada tipo de análisis tiene su propia subclase: `VNDetectFaceRectanglesRequest`, `VNRecognizeTextRequest`, `VNClassifyImageRequest`, etc. Una solicitud define **qué** quieres detectar o analizar.

```swift
// Ejemplo: crear una solicitud de detección de rostros
let faceRequest = VNDetectFaceRectanglesRequest()
```

### 2. VNImageRequestHandler (Manejador de solicitudes)

Es el motor de ejecución para imágenes estáticas. Recibe una imagen (como `CGImage`, `CIImage`, `Data` o `URL`) y ejecuta una o más solicitudes contra ella. Se usa para análisis puntual de una sola imagen.

```swift
let handler = VNImageRequestHandler(cgImage: miImagen, options: [:])
try handler.perform([faceRequest])
```

### 3. VNSequenceRequestHandler (Manejador de secuencias)

Similar al anterior, pero diseñado para procesar secuencias de imágenes (vídeo). Mantiene estado entre cuadros, lo que permite operaciones como el seguimiento de objetos.

### 4. VNObservation (Observación)

Es la clase base para los resultados. Cada tipo de solicitud produce observaciones específicas: `VNFaceObservation`, `VNRecognizedTextObservation`, `VNClassificationObservation`, etc. Las observaciones incluyen un valor de confianza (`confidence`) entre 0 y 1.

### 5. Sistema de coordenadas normalizado

Vision utiliza un sistema de coordenadas **normalizado** donde el origen `(0, 0)` está en la esquina **inferior izquierda** y los valores van de 0 a 1. Esto difiere de UIKit (origen superior izquierdo) y de SwiftUI, por lo que es necesario convertir las coordenadas al sistema del framework de UI que estés usando.

### 6. Niveles de reconocimiento (Recognition Levels)

Para solicitudes como el reconocimiento de texto, puedes elegir entre `.fast` (rápido pero menos preciso) y `.accurate` (más lento pero con mayor precisión). Esta decisión afecta directamente al rendimiento y a la calidad de los resultados.

## Ejemplo básico

Este ejemplo muestra cómo detectar texto en una imagen estática de forma sencilla:

```swift
import Vision
import UIKit

/// Función que extrae todo el texto reconocido de una UIImage
func reconocerTexto(en imagen: UIImage) {
    // 1. Convertir UIImage a CGImage (requerido por Vision)
    guard let cgImage = imagen.cgImage else {
        print("Error: No se pudo obtener CGImage de la imagen proporcionada.")
        return
    }

    // 2. Crear la solicitud de reconocimiento de texto
    let solicitudTexto = VNRecognizeTextRequest { solicitud, error in
        // 5. Manejar errores
        if let error = error {
            print("Error durante el reconocimiento: \(error.localizedDescription)")
            return
        }

        // 6. Extraer las observaciones de texto reconocido
        guard let observaciones = solicitud.results as? [VNRecognizedTextObservation] else {
            print("No se encontraron resultados de texto.")
            return
        }

        // 7. Iterar sobre cada observación y obtener el texto con mayor confianza
        let textosReconocidos = observaciones.compactMap { observacion in
            observacion.topCandidates(1).first?.string
        }

        // 8. Imprimir el texto completo
        let textoCompleto = textosReconocidos.joined(separator: "\n")
        print("Texto reconocido:\n\(textoCompleto)")
    }

    // 3. Configurar el nivel de reconocimiento
    solicitudTexto.recognitionLevel = .accurate

    // 4. Especificar idiomas de reconocimiento (español e inglés)
    solicitudTexto.recognitionLanguages = ["es", "en"]

    // 4b. Crear el handler y ejecutar la solicitud
    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    do {
        try handler.perform([solicitudTexto])
    } catch {
        print("Error al ejecutar la solicitud: \(error.localizedDescription)")
    }
}
```

## Ejemplo intermedio

Este ejemplo implementa un detector de rostros que retorna las posiciones y puntos de referencia faciales, usando async/await y un diseño más estructurado:

```swift
import Vision
import UIKit

// MARK: - Modelo de resultado

/// Estructura que encapsula los datos de un rostro detectado
struct RostroDetectado {
    /// Rectángulo normalizado del rostro (coordenadas Vision: origen inferior-izquierda)
    let rectanguloNormalizado: CGRect
    /// Puntuación de confianza (0.0 - 1.0)
    let confianza: Float
    /// Puntos de referencia faciales (ojos, nariz, boca, etc.)
    let puntosReferencia: VNFaceLandmarks2D?

    /// Convierte el rectángulo normalizado de Vision al sistema de coordenadas de UIKit
    func rectanguloEnVista(tamañoVista: CGSize) -> CGRect {
        let x = rectanguloNormalizado.origin.x * tamañoVista.width
        // Invertir Y: Vision usa origen inferior-izquierda, UIKit superior-izquierda
        let y = (1 - rectanguloNormalizado.origin.y - rectanguloNormalizado.height) * tamañoVista.height
        let ancho = rectanguloNormalizado.width * tamañoVista.width
        let alto = rectanguloNormalizado.height * tamañoVista.height
        return CGRect(x: x, y: y, width: ancho, height: alto)
    }
}

// MARK: - Servicio de detección facial

/// Servicio reutilizable para detección de rostros
final class ServicioDeteccionFacial {

    /// Detecta rostros en una imagen de forma asíncrona
    /// - Parameter imagen: La UIImage a analizar
    /// - Returns: Array de rostros detectados con sus propiedades
    func detectarRostros(en imagen: UIImage) async throws -> [RostroDetectado] {
        guard let cgImage = imagen.cgImage else {
            throw ErrorVision.imagenInvalida
        }

        return try await withCheckedThrowingContinuation { continuation in
            // Crear solicitud con detección de puntos de referencia faciales
            let solicitud = VNDetectFaceLandmarksRequest { solicitud, error in
                if let error = error {
                    continuation.resume(throwing: error)
                    return
                }

                guard let observaciones = solicitud.results as? [VNFaceObservation] else {
                    continuation.resume(returning: [])
                    return
                }

                // Mapear observaciones a nuestro modelo
                let rostros = observaciones.map { observacion in
                    RostroDetectado(
                        rectanguloNormalizado: observacion.boundingBox,
                        confianza: observacion.confidence,
                        puntosReferencia: observacion.landmarks
                    )
                }

                continuation.resume(returning: rostros)
            }

            // Ejecutar en un hilo de fondo
            let handler = VNImageRequestHandler(cgImage: cgImage, orientation: .up, options: [:])
            do {
                try handler.perform([solicitud])
            } catch {
                continuation.resume(throwing: error)
            }
        }
    }
}

// MARK: - Errores personalizados

enum ErrorVision: LocalizedError {
    case imagenInvalida
    case sinResultados

    var errorDescription: String? {
        switch self {
        case .imagenInvalida:
            return "La imagen proporcionada no es válida o no se pudo procesar."
        case .sinResultados:
            return "No se obtuvieron resultados del análisis."
        }
    }
}

// MARK: - Uso del servicio

func ejemploUso() async {
    let servicio = ServicioDeteccionFacial()
    let imagenEjemplo = UIImage(named: "foto_grupo")!

    do {
        let rostros = try await servicio.detectarRostros(en: imagenEjemplo)
        print("Se detectaron \(rostros.count) rostro(s)")

        for (indice, rostro) in rostros.enumerated() {
            let confianzaPorcentaje = String(format: "%.1f%%", rostro.confianza * 100)
            print("  Rostro \(indice + 1): confianza \(confianzaPorcentaje)")

            // Verificar si se detectaron ojos
            if let ojoIzquierdo = rostro.puntosReferencia?.leftEye {
                print("    - Ojo izquierdo: \(ojoIzquierdo.pointCount) puntos")
            }
            if let ojoDerecho = rostro.puntosReferencia?.rightEye {
                print("    - Ojo derecho: \(ojoDerecho.pointCount) puntos")
            }
        }
    } catch {
        print("Error: \(error.localizedDescription)")
    }
}
```

## Ejemplo avanzado

Este ejemplo implementa un escáner de documentos con OCR en tiempo real usando la cámara, con arquitectura MVVM y SwiftUI:

```swift
import SwiftUI
import Vision
import AVFoundation
import Combine

// MARK: - Modelo

/// Representa un bloque de texto detectado con su posición
struct BloqueTexto: Identifiable {
    let id = UUID()
    let texto: String
    let confianza: Float
    let boundingBox: CGRect
}

/// Resultado completo del escaneo de un frame
struct ResultadoEscaneo {
    let bloques: [BloqueTexto]
    let textoCompleto: String
    let timestamp: Date

    static let vacio = ResultadoEscaneo(bloques: [], textoCompleto: "", timestamp: .now)
}

// MARK: - Servicio de OCR (capa de datos)

/// Protocolo para inyección de dependencias y testing
protocol ServicioOCR {
    func procesarFrame(_ sampleBuffer: CMSampleBuffer) async throws -> ResultadoEscaneo
}

/// Implementación concreta del servicio OCR usando Vision
final class ServicioOCRVision: ServicioOCR {
    private let idiomasReconocimiento: [String]
    private let nivelReconocimiento: VNRequestTextRecognitionLevel
    private let correccionIdioma: Bool

    init(
        idiomas: [String] = ["es", "en"],
        nivel: VNRequestTextRecognitionLevel = .accurate,
        correccionIdioma: Bool = true
    ) {
        self.idiomasReconocimiento = idiomas
        self.nivelReconocimiento = nivel
        self.correccionIdioma = correccionIdioma
    }

    func procesarFrame(_ sampleBuffer: CMSampleBuffer) async throws -> ResultadoEscaneo {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else {
            throw ErrorVision.imagenInvalida
        }

        return try await withCheckedThrowing