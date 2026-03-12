---
sidebar_position: 1
title: AVFoundation
---

# AVFoundation

## ¿Qué es AVFoundation?

AVFoundation es el framework multimedia principal de Apple que proporciona una interfaz completa en Objective-C y Swift para trabajar con medios audiovisuales basados en el tiempo. Es el pilar fundamental sobre el que se construyen las capacidades de reproducción, captura, edición y procesamiento de audio y video en todas las plataformas Apple: iOS, macOS, tvOS, watchOS y visionOS. Se sitúa como una capa intermedia entre los frameworks de alto nivel (como AVKit, que ofrece controles de UI prediseñados) y los frameworks de bajo nivel (como Core Audio y Core Media, que operan directamente con buffers y muestras de datos).

Este framework es extraordinariamente amplio y cubre desde la reproducción simple de un archivo de audio hasta la composición multicapa de video con efectos en tiempo real. Permite a los desarrolladores inspeccionar, crear, editar y recodificar archivos multimedia, así como capturar flujos de audio y video directamente desde los dispositivos de hardware del equipo. Su arquitectura está diseñada para operar de forma asíncrona y eficiente, aprovechando al máximo el hardware disponible para garantizar un rendimiento fluido incluso en escenarios de alta demanda.

Deberías considerar AVFoundation cuando necesites un control granular sobre la experiencia multimedia que los componentes de alto nivel como `AVKit` o `VideoPlayer` de SwiftUI no te proporcionan. Por ejemplo, si necesitas aplicar filtros en tiempo real al video de la cámara, mezclar múltiples pistas de audio, generar miniaturas de video de forma programática, implementar un reproductor personalizado con controles propios o construir una experiencia de captura de cámara totalmente a medida, AVFoundation es tu herramienta.

## Casos de uso principales

- **Reproductor de audio/video personalizado**: Construir un reproductor multimedia con controles de interfaz propios, soporte para listas de reproducción, velocidad de reproducción variable y manejo de interrupciones de audio (llamadas, alarmas).

- **Captura de cámara y micrófono**: Implementar experiencias de cámara personalizadas con controles manuales de enfoque, exposición, balance de blancos, y captura de fotos y video con configuraciones avanzadas (HDR, formatos RAW, ProRes).

- **Edición y composición de video**: Combinar múltiples clips de video, superponer textos o imágenes (watermarks), añadir transiciones, mezclar pistas de audio y exportar el resultado final en diferentes formatos y calidades.

- **Procesamiento de audio en tiempo real**: Capturar audio del micrófono para análisis en tiempo real (detección de niveles, visualizadores), aplicar efectos de audio o implementar funcionalidades como grabación de notas de voz con medidores de nivel.

- **Generación de miniaturas y metadatos**: Extraer fotogramas específicos de archivos de video para mostrar previsualizaciones, leer metadatos embebidos (artista, álbum, duración, artwork) y manipular assets multimedia sin necesidad de reproducirlos.

- **Streaming y contenido en vivo**: Reproducir contenido HLS (HTTP Live Streaming), gestionar streams adaptativos con diferentes calidades y manejar contenido protegido con DRM mediante FairPlay Streaming.

## Instalación y configuración

### Agregar el framework al proyecto

AVFoundation es un framework del sistema incluido en el SDK de Apple, por lo que **no requiere instalación mediante gestores de paquetes**. Solo necesitas importarlo en los archivos donde lo utilices:

```swift
import AVFoundation
```

En la mayoría de los proyectos modernos con Xcode, el enlace con el framework se realiza automáticamente. Sin embargo, si trabajas con un proyecto que requiere enlace manual, puedes añadirlo desde:

> **Project → Target → General → Frameworks, Libraries, and Embedded Content → + → AVFoundation.framework**

### Frameworks complementarios comunes

Dependiendo de tu caso de uso, es probable que necesites importar frameworks adicionales:

```swift
import AVFoundation   // Framework principal multimedia
import AVKit          // Controles de UI para reproducción (AVPlayerViewController, VideoPlayer)
import CoreMedia      // Tipos de bajo nivel (CMTime, CMSampleBuffer)
import CoreImage      // Filtros y procesamiento de imagen en tiempo real
import Photos         // Acceso a la fototeca del usuario
```

### Permisos en Info.plist

AVFoundation interactúa directamente con hardware sensible del dispositivo. **Es obligatorio** declarar las descripciones de uso correspondientes en `Info.plist`, o la aplicación se cerrará de forma inmediata al intentar acceder al recurso:

```xml
<!-- Acceso a la cámara -->
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceso a la cámara para capturar fotos y video.</string>

<!-- Acceso al micrófono -->
<key>NSMicrophoneUsageDescription</key>
<string>Necesitamos acceso al micrófono para grabar audio en tus videos.</string>

<!-- Acceso a la fototeca (si vas a guardar contenido) -->
<key>NSPhotoLibraryUsageDescription</key>
<string>Necesitamos acceso a tu fototeca para guardar las fotos y videos capturados.</string>

<!-- Acceso a la biblioteca musical (si aplica) -->
<key>NSAppleMusicUsageDescription</key>
<string>Necesitamos acceso a tu biblioteca musical para reproducir tus canciones.</string>
```

### Solicitar permisos en tiempo de ejecución

```swift
import AVFoundation

// Verificar y solicitar permiso de cámara
func solicitarPermisoCamara() async -> Bool {
    let estado = AVCaptureDevice.authorizationStatus(for: .video)

    switch estado {
    case .authorized:
        return true
    case .notDetermined:
        return await AVCaptureDevice.requestAccess(for: .video)
    case .denied, .restricted:
        return false
    @unknown default:
        return false
    }
}

// Verificar y solicitar permiso de micrófono
func solicitarPermisoMicrofono() async -> Bool {
    let estado = AVCaptureDevice.authorizationStatus(for: .audio)

    switch estado {
    case .authorized:
        return true
    case .notDetermined:
        return await AVCaptureDevice.requestAccess(for: .audio)
    case .denied, .restricted:
        return false
    @unknown default:
        return false
    }
}
```

### Configuración de la sesión de audio

Para cualquier aplicación que reproduzca o capture audio, es fundamental configurar la categoría de la sesión de audio:

```swift
func configurarSesionDeAudio() {
    let sesion = AVAudioSession.sharedInstance()
    do {
        // .playback: Audio se reproduce incluso en modo silencio
        // .playAndRecord: Para apps que graban y reproducen simultáneamente
        try sesion.setCategory(.playback, mode: .moviePlayback, options: [])
        try sesion.setActive(true)
    } catch {
        print("Error al configurar la sesión de audio: \(error.localizedDescription)")
    }
}
```

## Conceptos clave

### 1. AVAsset y AVURLAsset

`AVAsset` es la representación abstracta e inmutable de un recurso multimedia basado en el tiempo. No representa un archivo específico, sino una colección de pistas (tracks) con propiedades como duración, metadatos y formato. `AVURLAsset` es su subclase concreta que se inicializa a partir de una URL local o remota. **Todas las propiedades de un asset se cargan de forma asíncrona** para evitar bloquear el hilo principal.

```swift
let url = URL(string: "https://ejemplo.com/video.mp4")!
let asset = AVURLAsset(url: url)

// Carga asíncrona de propiedades (API moderna con async/await)
let duracion = try await asset.load(.duration)
let pistas = try await asset.load(.tracks)
```

### 2. AVPlayer y AVPlayerItem

`AVPlayer` es el controlador de reproducción que gestiona el timing y el estado de la reproducción. `AVPlayerItem` es el modelo que envuelve un `AVAsset` para su reproducción, manteniendo el estado dinámico como la posición actual, los buffers cargados y el estado de carga. Un `AVPlayer` reproduce un solo `AVPlayerItem` a la vez, mientras que `AVQueuePlayer` (subclase) permite encadenar múltiples items.

```swift
let playerItem = AVPlayerItem(url: videoURL)
let player = AVPlayer(playerItem: playerItem)

// Observar el estado del item
playerItem.publisher(for: \.status)
    .sink { estado in
        switch estado {
        case .readyToPlay: print("Listo para reproducir")
        case .failed: print("Error: \(playerItem.error?.localizedDescription ?? "")")
        default: break
        }
    }
```

### 3. AVCaptureSession

`AVCaptureSession` es el objeto central que coordina el flujo de datos desde dispositivos de entrada (cámaras, micrófonos) hacia salidas (archivos de video, previsualizaciones en pantalla, procesamiento de datos). Se configura conectando inputs (`AVCaptureDeviceInput`) con outputs (`AVCaptureMovieFileOutput`, `AVCapturePhotoOutput`, `AVCaptureVideoDataOutput`) y se inicia/detiene de forma explícita.

### 4. CMTime

`CMTime` es la estructura de Core Media que AVFoundation utiliza para representar tiempos con precisión racional (numerador/denominador), evitando los errores de punto flotante. Es fundamental para seeking preciso, definir rangos de tiempo y programar observadores periódicos.

```swift
// 2.5 segundos representados con precisión
let tiempo = CMTime(seconds: 2.5, preferredTimescale: 600)

// Tiempo cero y tiempo inválido
let cero = CMTime.zero
let invalido = CMTime.invalid

// Aritmética de tiempos
let suma = CMTimeAdd(tiempo, CMTime(seconds: 1.0, preferredTimescale: 600))
```

### 5. AVComposition y AVMutableComposition

`AVComposition` es una subclase de `AVAsset` que permite combinar pistas de múltiples assets en una composición virtual. `AVMutableComposition` es su versión editable, utilizada para insertar, eliminar y reorganizar segmentos de audio y video de diferentes fuentes sin tocar los archivos originales. Es la base de cualquier flujo de edición de video.

### 6. AVAudioSession

`AVAudioSession` actúa como intermediario entre tu aplicación y el sistema de audio del dispositivo. Controla cómo tu app interactúa con otras apps que producen audio, si el audio se reproduce por altavoz o auriculares, y cómo responde a interrupciones (llamadas entrantes, alarmas de Siri). Configurarla correctamente es **absolutamente esencial** para una experiencia de audio profesional.

## Ejemplo básico

Este ejemplo muestra cómo crear un reproductor de audio simple que carga y reproduce un archivo desde una URL:

```swift
import AVFoundation

/// Reproductor de audio básico con funcionalidad esencial
class ReproductorDeAudioBasico {

    // MARK: - Propiedades

    /// El reproductor principal. Se mantiene como propiedad
    /// para evitar que ARC lo libere prematuramente.
    private var player: AVPlayer?

    /// Observador periódico para rastrear el progreso de reproducción
    private var observadorDeTiempo: Any?

    // MARK: - Configuración

    /// Configura la sesión de audio del sistema
    func configurar() {
        do {
            let sesion = AVAudioSession.sharedInstance()
            try sesion.setCategory(.playback, mode: .default)
            try sesion.setActive(true)
            print("✅ Sesión de audio configurada correctamente")
        } catch {
            print("❌ Error configurando sesión de audio: \(error)")
        }
    }

    // MARK: - Reproducción

    /// Carga y reproduce un archivo de audio desde una URL
    /// - Parameter url: URL local o remota del archivo de audio
    func reproducir(desde url: URL) {
        // Crear el item y el reproductor
        let item = AVPlayerItem(url: url)
        player = AVPlayer(playerItem: item)

        // Observar el progreso cada 0.5 segundos
        let intervalo = CMTime(seconds: 0.5, preferredTimescale: 600)
        observadorDeTiempo = player?.addPeriodicTimeObserver(
            forInterval: intervalo,
            queue: .main
        ) { tiempo in
            let segundos = CMTimeGetSeconds(tiempo)
            print("⏱️ Tiempo actual: \(String(format: "%.1f", segundos))s")
        }

        // Iniciar reproducción
        player?.play()
        print("▶️ Reproducción iniciada")
    }

    /// Pausa la reproducción actual
    func pausar() {
        player?.pause()
        print("⏸️ Reproducción pausada")
    }

    /// Reanuda la reproducción
    func reanudar() {
        player?.play()
        print("▶️ Reproducción reanudada")
    }

    /// Salta a una posición específica del audio
    /// - Parameter segundos: Posición en segundos a la que saltar
    func saltar(a segundos: Double) {
        let tiempo = CMTime(seconds: segundos, preferredTimescale: 600)
        player?.seek(to: tiempo) { completado in
            if completado {
                print("⏭️ Salto completado a \(segundos)s")
            }
        }
    }

    /// Detiene la reproducción y libera recursos
    func detener() {
        // Eliminar el observador periódico para evitar fugas de memoria
        if let observador = observadorDeTiempo {
            player?.removeTimeObserver(observador)
            observadorDeTiempo = nil
        }
        player?.pause()
        player = nil
        print("⏹️ Reproducción detenida y recursos liberados")
    }

    deinit {
        detener()
    }
}

// MARK: - Uso

let reproductor = ReproductorDeAudioBasico()
reproductor.configurar()

// Reproducir un archivo local del bundle
if let url = Bundle.main.url(forResource: "cancion", withExtension: "mp3") {
    reproductor.reproducir(desde: url)
}

// Reproducir desde una URL remota
// let urlRemota = URL(string: "https://ejemplo.com/audio.mp3")!
// reproductor.reproducir(desde: urlRemota)
```

## Ejemplo intermedio

Este ejemplo implementa un servicio completo de cámara personalizada capaz de capturar fotos con previsualización en tiempo real:

```swift
import AVFoundation
import UIKit

// MARK: - Protocolo delegado

/// Protocolo para comunicar eventos del servicio de cámara
protocol ServicioDeCamaraDelegado: AnyObject {
    func servicioDeCamara(_ servicio: ServicioDeCamara, capturoFoto imagen: UIImage)
    func servicioDeCamara(_ servicio: ServicioDeCamara, falloConError error: Error)
}

// MARK: - Errores personalizados

enum ErrorDeCamara: LocalizedError {
    case sinAcceso
    case dispositivoNoDisponible
    case configuracionFallida
    case capturaCancelada

    var errorDescription: String? {
        switch self {
        case .sinAcceso:
            return "No se tiene permiso para acceder a la c