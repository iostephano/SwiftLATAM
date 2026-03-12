---
sidebar_position: 1
title: CoreML
---

# CoreML

## ¿Qué es CoreML?

CoreML es el framework de Apple diseñado para integrar modelos de aprendizaje automático (machine learning) directamente en aplicaciones iOS, macOS, watchOS y tvOS. Lanzado en 2017 con iOS 11, CoreML permite ejecutar inferencias de modelos entrenados de forma local en el dispositivo, sin necesidad de conexión a internet ni de enviar datos a servidores externos. Esto se traduce en mayor velocidad de respuesta, privacidad del usuario y funcionamiento offline.

El framework actúa como una capa de abstracción de alto nivel sobre tecnologías subyacentes como Accelerate, BNNS (Basic Neural Network Subroutines) y Metal Performance Shaders. CoreML optimiza automáticamente la ejecución del modelo seleccionando el hardware más adecuado disponible en el dispositivo: CPU, GPU o el Neural Engine de Apple. El desarrollador no necesita preocuparse por estos detalles de bajo nivel; simplemente integra el modelo compilado (`.mlmodel` o `.mlpackage`) y CoreML se encarga del resto.

CoreML es especialmente útil cuando necesitas incorporar capacidades inteligentes a tu aplicación — como clasificación de imágenes, detección de objetos, procesamiento de lenguaje natural, predicción de datos tabulares o generación de recomendaciones — sin depender de servicios en la nube. Apple proporciona herramientas complementarias como Create ML para entrenar modelos sin escribir código y `coremltools` (Python) para convertir modelos desde frameworks populares como TensorFlow, PyTorch y scikit-learn al formato `.mlmodel`.

## Casos de uso principales

- **Clasificación de imágenes**: Identificar el contenido de fotografías en tiempo real, como distinguir entre tipos de plantas, animales, alimentos o escenas. Aplicaciones de cámara inteligente y organización automática de fotos.

- **Detección de objetos**: Localizar y etiquetar múltiples objetos dentro de una imagen o fotograma de video. Útil en aplicaciones de realidad aumentada, seguridad industrial o accesibilidad.

- **Procesamiento de lenguaje natural (NLP)**: Análisis de sentimientos en reseñas, clasificación automática de textos, detección de spam o extracción de entidades. Se integra perfectamente con el framework `NaturalLanguage` de Apple.

- **Predicción de datos tabulares**: A partir de datos estructurados (edad, ubicación, historial de compras), predecir comportamientos futuros como probabilidad de cancelación de suscripción, precios estimados o recomendaciones personalizadas.

- **Reconocimiento de sonidos**: Clasificar audio en categorías como música, voz humana, ladridos de perro o sirenas. Ideal para aplicaciones de monitoreo ambiental o accesibilidad auditiva.

- **Segmentación de imágenes y estimación de pose**: Separar el fondo de una persona en video (efecto bokeh), detectar la posición de articulaciones del cuerpo humano para apps de fitness o rehabilitación.

## Instalación y configuración

CoreML viene integrado de forma nativa en el SDK de Apple, por lo que **no requiere instalación de dependencias externas** ni gestores de paquetes. Basta con importar el framework en los archivos donde lo necesites.

### Importación básica

```swift
import CoreML
```

### Agregar un modelo al proyecto

1. Obtén o entrena un modelo en formato `.mlmodel` o `.mlpackage`.
2. Arrastra el archivo del modelo directamente al navegador de archivos de Xcode.
3. Xcode compilará automáticamente el modelo y generará una clase Swift con la interfaz tipada correspondiente.
4. Verifica en **Build Phases → Compile Sources** que el modelo aparece listado.

### Permisos en Info.plist

CoreML en sí mismo **no requiere permisos especiales** en `Info.plist`. Sin embargo, si tu app captura imágenes de la cámara o accede a la galería de fotos para alimentar el modelo, necesitarás los permisos correspondientes:

```xml
<!-- Solo si usas la cámara -->
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceso a la cámara para analizar imágenes en tiempo real.</string>

<!-- Solo si accedes a la galería -->
<key>NSPhotoLibraryUsageDescription</key>
<string>Necesitamos acceso a tus fotos para clasificar imágenes.</string>

<!-- Solo si usas el micrófono para análisis de audio -->
<key>NSMicrophoneUsageDescription</key>
<string>Necesitamos acceso al micrófono para analizar sonidos.</string>
```

### Frameworks complementarios frecuentes

```swift
import CoreML
import Vision        // Para tareas de visión por computadora
import NaturalLanguage // Para tareas de procesamiento de texto
import SoundAnalysis   // Para clasificación de audio
import CoreImage       // Para preprocesamiento de imágenes
```

## Conceptos clave

### 1. MLModel

Es la clase central de CoreML. Representa un modelo de machine learning compilado y listo para realizar predicciones. Cada archivo `.mlmodel` que agregas a Xcode genera automáticamente una clase Swift que encapsula un `MLModel` con interfaces tipadas para entrada y salida.

### 2. MLFeatureProvider

Protocolo que define cómo se proporcionan los datos de entrada al modelo y cómo se reciben los datos de salida. Tanto las entradas como las salidas del modelo se representan como conjuntos de *features* con nombre y tipo. Las clases autogeneradas por Xcode implementan este protocolo automáticamente.

### 3. MLModelConfiguration

Permite configurar opciones de ejecución del modelo antes de cargarlo, como forzar el uso de un procesador específico (CPU, GPU o Neural Engine) mediante la propiedad `computeUnits`. También permite especificar si se desea cargar el modelo de forma asíncrona.

### 4. Vision + CoreML (VNCoreMLRequest)

La combinación más potente para análisis de imágenes. El framework `Vision` actúa como intermediario para preprocesar imágenes (redimensionar, normalizar, ajustar orientación) antes de pasarlas al modelo CoreML. Esto simplifica enormemente el pipeline de visión por computadora.

### 5. MLMultiArray

Estructura de datos multidimensional utilizada por CoreML para representar tensores. Es el formato en que muchos modelos esperan recibir datos numéricos de entrada o devolver resultados. Similar a los arrays de NumPy en Python.

### 6. Modelos on-demand (MLModelCollection)

A partir de iOS 14, Apple permite alojar modelos en iCloud y descargarlos bajo demanda. Esto reduce significativamente el tamaño inicial de la app y permite actualizar modelos sin publicar una nueva versión en la App Store.

## Ejemplo básico

Este ejemplo muestra cómo cargar un modelo de clasificación de imágenes y realizar una predicción sencilla:

```swift
import CoreML
import UIKit

/// Ejemplo básico: clasificar una imagen usando un modelo CoreML
/// Se asume que el modelo "MobileNetV2" ya fue agregado al proyecto en Xcode
func clasificarImagen(imagen: UIImage) {
    do {
        // 1. Crear configuración del modelo
        let configuracion = MLModelConfiguration()
        configuracion.computeUnits = .all // Usar CPU, GPU y Neural Engine

        // 2. Instanciar el modelo (clase autogenerada por Xcode)
        let modelo = try MobileNetV2(configuration: configuracion)

        // 3. Convertir la UIImage al formato que espera el modelo
        //    MobileNetV2 espera un CVPixelBuffer de 224x224 píxeles
        guard let pixelBuffer = imagen.convertirAPixelBuffer(
            ancho: 224,
            alto: 224
        ) else {
            print("Error: No se pudo convertir la imagen a PixelBuffer")
            return
        }

        // 4. Crear el objeto de entrada tipado
        let entrada = MobileNetV2Input(image: pixelBuffer)

        // 5. Realizar la predicción
        let resultado = try modelo.prediction(input: entrada)

        // 6. Leer los resultados
        let etiqueta = resultado.classLabel
        let confianza = resultado.classLabelProbs[etiqueta] ?? 0.0

        print("Clasificación: \(etiqueta)")
        print("Confianza: \(String(format: "%.2f%%", confianza * 100))")

    } catch {
        print("Error al realizar la predicción: \(error.localizedDescription)")
    }
}

// MARK: - Extensión auxiliar para convertir UIImage a CVPixelBuffer
extension UIImage {
    func convertirAPixelBuffer(ancho: Int, alto: Int) -> CVPixelBuffer? {
        let atributos: [CFString: Any] = [
            kCVPixelBufferCGImageCompatibilityKey: true,
            kCVPixelBufferCGBitmapContextCompatibilityKey: true
        ]

        var pixelBuffer: CVPixelBuffer?
        let estado = CVPixelBufferCreate(
            kCFAllocatorDefault,
            ancho,
            alto,
            kCVPixelFormatType_32ARGB,
            atributos as CFDictionary,
            &pixelBuffer
        )

        guard estado == kCVReturnSuccess, let buffer = pixelBuffer else {
            return nil
        }

        CVPixelBufferLockBaseAddress(buffer, [])
        defer { CVPixelBufferUnlockBaseAddress(buffer, []) }

        guard let contexto = CGContext(
            data: CVPixelBufferGetBaseAddress(buffer),
            width: ancho,
            height: alto,
            bitsPerComponent: 8,
            bytesPerRow: CVPixelBufferGetBytesPerRow(buffer),
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
        ) else {
            return nil
        }

        contexto.draw(
            self.cgImage!,
            in: CGRect(x: 0, y: 0, width: ancho, height: alto)
        )

        return buffer
    }
}
```

## Ejemplo intermedio

Este ejemplo utiliza el framework `Vision` junto con CoreML para clasificar imágenes de forma más robusta, manejando automáticamente el preprocesamiento:

```swift
import CoreML
import Vision
import UIKit

/// Servicio de clasificación de imágenes usando Vision + CoreML
class ServicioClasificacionImagenes {

    // MARK: - Propiedades

    /// Request de Vision configurado con el modelo CoreML
    private let requestClasificacion: VNCoreMLRequest

    /// Closure para notificar resultados
    var alObtenerResultados: (([ResultadoClasificacion]) -> Void)?

    /// Closure para notificar errores
    var alObtenerError: ((Error) -> Void)?

    // MARK: - Modelo de datos

    struct ResultadoClasificacion {
        let etiqueta: String
        let confianza: Float // Valor entre 0.0 y 1.0

        /// Confianza expresada como porcentaje legible
        var confianzaFormateada: String {
            String(format: "%.1f%%", confianza * 100)
        }
    }

    // MARK: - Inicialización

    init() throws {
        // Configurar el modelo para máximo rendimiento
        let configuracion = MLModelConfiguration()
        configuracion.computeUnits = .all

        // Cargar el modelo CoreML dentro de un contenedor de Vision
        let modeloCoreML = try MobileNetV2(configuration: configuracion)
        let modeloVision = try VNCoreMLModel(for: modeloCoreML.model)

        // Crear el request de Vision
        requestClasificacion = VNCoreMLRequest(model: modeloVision)

        // Configurar opciones de preprocesamiento
        // .centerCrop recorta la imagen al centro para mantener la proporción
        requestClasificacion.imageCropAndScaleOption = .centerCrop

        // Asignar el handler de completado
        requestClasificacion.completionHandler = { [weak self] request, error in
            self?.procesarResultados(request: request, error: error)
        }
    }

    // MARK: - Métodos públicos

    /// Clasifica una UIImage de forma asíncrona
    func clasificar(imagen: UIImage) {
        guard let ciImage = CIImage(image: imagen) else {
            alObtenerError?(ErrorClasificacion.imagenInvalida)
            return
        }

        // Obtener la orientación correcta de la imagen
        let orientacion = CGImagePropertyOrientation(rawValue:
            UInt32(imagen.imageOrientation.rawValue)) ?? .up

        // Ejecutar la clasificación en un hilo de fondo
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            let handler = VNImageRequestHandler(
                ciImage: ciImage,
                orientation: orientacion,
                options: [:]
            )

            do {
                try handler.perform([self.requestClasificacion])
            } catch {
                DispatchQueue.main.async {
                    self.alObtenerError?(error)
                }
            }
        }
    }

    /// Clasifica una imagen desde una URL de archivo local
    func clasificar(urlImagen: URL) {
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }

            let handler = VNImageRequestHandler(
                url: urlImagen,
                options: [:]
            )

            do {
                try handler.perform([self.requestClasificacion])
            } catch {
                DispatchQueue.main.async {
                    self.alObtenerError?(error)
                }
            }
        }
    }

    // MARK: - Procesamiento de resultados

    private func procesarResultados(request: VNRequest, error: Error?) {
        if let error = error {
            DispatchQueue.main.async { [weak self] in
                self?.alObtenerError?(error)
            }
            return
        }

        // Extraer las observaciones de clasificación
        guard let observaciones = request.results
                as? [VNClassificationObservation] else {
            DispatchQueue.main.async { [weak self] in
                self?.alObtenerError?(ErrorClasificacion.sinResultados)
            }
            return
        }

        // Filtrar resultados con confianza mayor al 5%
        // y tomar los 5 mejores
        let resultados = observaciones
            .filter { $0.confidence > 0.05 }
            .prefix(5)
            .map { observacion in
                ResultadoClasificacion(
                    etiqueta: observacion.identifier,
                    confianza: observacion.confidence
                )
            }

        DispatchQueue.main.async { [weak self] in
            self?.alObtenerResultados?(resultados)
        }
    }

    // MARK: - Errores personalizados

    enum ErrorClasificacion: LocalizedError {
        case imagenInvalida
        case sinResultados

        var errorDescription: String? {
            switch self {
            case .imagenInvalida:
                return "No se pudo procesar la imagen proporcionada."
            case .sinResultados:
                return "El modelo no devolvió resultados de clasificación."
            }
        }
    }
}

// MARK: - Ejemplo de uso

/*
 let servicio = try ServicioClasificacionImagenes()

 servicio.alObtenerResultados = { resultados in