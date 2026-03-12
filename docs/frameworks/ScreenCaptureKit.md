---
sidebar_position: 1
title: ScreenCaptureKit
---

# ScreenCaptureKit

## ¿Qué es ScreenCaptureKit?

ScreenCaptureKit es un framework de alto rendimiento introducido por Apple en **macOS 12.3 (Monterey)** que permite capturar contenido de pantalla de manera eficiente y granular. A diferencia de las APIs de captura de pantalla anteriores (como `CGWindowListCreateImage` o `AVCaptureScreenInput`), ScreenCaptureKit fue diseñado desde cero para ofrecer un control preciso sobre **qué contenido se captura**, permitiendo incluir o excluir ventanas, aplicaciones y hasta regiones específicas de la pantalla.

Este framework está optimizado para escenarios de alto rendimiento como streaming en vivo, grabación de pantalla y videoconferencias. Utiliza aceleración por hardware y entrega los frames a través de un sistema de callbacks asíncrono, lo que minimiza el impacto en el rendimiento del sistema. Además, se integra de forma nativa con **Core Media**, **Core Video** y **AVFoundation**, facilitando el procesamiento y la codificación del contenido capturado.

ScreenCaptureKit es la opción recomendada por Apple para cualquier aplicación de macOS que necesite capturar contenido de pantalla. Su arquitectura basada en filtros (`SCContentFilter`) permite escenarios sofisticados como capturar una sola ventana sin su sombra, excluir la propia aplicación de la captura o incluso capturar únicamente el audio del sistema. Es importante destacar que este framework **solo está disponible para macOS** y no tiene equivalente directo en iOS, iPadOS, tvOS o watchOS.

## Casos de uso principales

- **Grabación de pantalla**: Crear aplicaciones que graben la pantalla completa o ventanas específicas, similar a QuickTime Player o OBS Studio. ScreenCaptureKit permite capturar vídeo y audio del sistema simultáneamente.

- **Streaming en vivo**: Transmitir el contenido de la pantalla en tiempo real a plataformas como Twitch o YouTube. La baja latencia y la aceleración por hardware lo hacen ideal para este escenario.

- **Compartir pantalla en videollamadas**: Integrar la funcionalidad de compartir pantalla en aplicaciones de videoconferencia, permitiendo al usuario elegir qué pantalla, ventana o aplicación compartir.

- **Herramientas de captura de screenshots**: Crear utilidades de captura de pantalla avanzadas que permitan seleccionar regiones específicas, ventanas individuales o múltiples monitores.

- **Aplicaciones de accesibilidad y productividad**: Desarrollar herramientas que analicen el contenido de la pantalla para ofrecer funciones de accesibilidad, automatización o monitoreo de actividad.

- **Creación de contenido educativo**: Grabar tutoriales, demos de software o presentaciones con la posibilidad de excluir elementos sensibles (como notificaciones o ciertas ventanas) de la captura.

## Instalación y configuración

### Requisitos del sistema

- **macOS 12.3** (Monterey) o superior
- **Xcode 13.3** o superior
- Solo disponible para aplicaciones **macOS** (AppKit/SwiftUI para macOS)

### Agregar el framework al proyecto

ScreenCaptureKit viene incluido en el SDK de macOS, por lo que no necesitas agregar dependencias externas. Simplemente importa el módulo:

```swift
import ScreenCaptureKit
```

### Configuración de permisos

ScreenCaptureKit requiere el permiso de **Grabación de Pantalla** del sistema. Este permiso se solicita automáticamente la primera vez que se intenta capturar contenido, pero debes configurar correctamente tu aplicación:

#### 1. Entitlement de App Sandbox (si aplica)

Si tu aplicación usa App Sandbox, no necesitas un entitlement específico para ScreenCaptureKit, pero el sistema mostrará el diálogo de permisos al usuario.

#### 2. Info.plist

Agrega una descripción de uso para informar al usuario por qué tu app necesita acceso a la pantalla:

```xml
<key>NSScreenCaptureUsageDescription</key>
<string>Esta aplicación necesita acceso a la pantalla para grabar y compartir contenido.</string>
```

#### 3. Hardened Runtime

Si distribuyes tu aplicación fuera de la Mac App Store con Hardened Runtime habilitado, no necesitas deshabilitar protecciones adicionales, ya que ScreenCaptureKit gestiona los permisos a nivel de sistema.

#### 4. Verificar permisos programáticamente

A partir de macOS 15, puedes verificar y solicitar permisos de forma explícita:

```swift
import ScreenCaptureKit

// Verificar si hay acceso previo a la captura (macOS 15+)
// En versiones anteriores, el permiso se solicita al intentar
// obtener el contenido compartible por primera vez.
```

### Imports adicionales frecuentes

```swift
import ScreenCaptureKit   // Framework principal
import CoreMedia          // CMSampleBuffer para procesar frames
import CoreVideo          // CVPixelBuffer para manipulación de píxeles
import AVFoundation       // Para codificación y escritura de archivos
import Combine            // Para patrones reactivos (opcional)
```

## Conceptos clave

### 1. SCShareableContent

Es el punto de entrada para descubrir qué contenido está disponible para capturar. Proporciona listas de **pantallas** (`SCDisplay`), **ventanas** (`SCWindow`) y **aplicaciones** (`SCRunningApplication`) actualmente visibles en el sistema. Se obtiene de forma asíncrona:

```swift
let content = try await SCShareableContent.excludingDesktopWindows(false,
                                                                     onScreenWindowsOnly: true)
// content.displays   -> [SCDisplay]
// content.windows    -> [SCWindow]
// content.applications -> [SCRunningApplication]
```

### 2. SCContentFilter

Define **qué** se va a capturar. Puedes crear filtros para capturar una pantalla completa (opcionalmente excluyendo ventanas o aplicaciones), una ventana individual, o combinaciones avanzadas. Es el corazón del sistema de filtrado:

```swift
// Capturar pantalla completa excluyendo ciertas apps
let filter = SCContentFilter(display: display,
                              excludingApplications: [miApp],
                              exceptingWindows: [])

// Capturar una sola ventana
let filter = SCContentFilter(desktopIndependentWindow: ventana)
```

### 3. SCStreamConfiguration

Controla **cómo** se realiza la captura: resolución, tasa de frames, formato de píxeles, captura de cursor, captura de audio y mucho más. Es donde se optimiza el rendimiento según las necesidades:

```swift
let config = SCStreamConfiguration()
config.width = 1920
config.height = 1080
config.minimumFrameInterval = CMTime(value: 1, timescale: 60) // 60 FPS
config.pixelFormat = kCVPixelFormatType_32BGRA
config.capturesAudio = true
config.showsCursor = true
```

### 4. SCStream

Es el objeto principal que gestiona la captura. Se inicializa con un filtro y una configuración, y se le agregan **salidas de stream** (objetos que conforman `SCStreamOutput`) para recibir los frames de vídeo y audio. Su ciclo de vida es: crear → agregar salidas → iniciar → (capturar) → detener.

### 5. SCStreamOutput (Protocolo)

Protocolo que deben implementar los objetos que reciben los datos capturados. Tiene un único método que entrega `CMSampleBuffer` con un tipo que indica si es vídeo (`.screen`) o audio (`.audio`):

```swift
func stream(_ stream: SCStream,
            didOutputSampleBuffer sampleBuffer: CMSampleBuffer,
            of type: SCStreamOutputType)
```

### 6. SCScreenshotManager (macOS 14+)

Introducido en macOS Sonoma, permite capturar **screenshots estáticos** de alta calidad sin necesidad de iniciar un stream completo. Es ideal para capturas puntuales.

## Ejemplo básico

Este ejemplo muestra cómo listar el contenido disponible y capturar un screenshot de la pantalla principal:

```swift
import ScreenCaptureKit
import CoreMedia

/// Ejemplo básico: Capturar un screenshot de la pantalla principal
class BasicScreenCapture {

    /// Obtiene el contenido disponible para captura y muestra
    /// información sobre pantallas y ventanas detectadas
    func listarContenidoDisponible() async throws {
        // Obtener todo el contenido compartible del sistema
        let content = try await SCShareableContent.excludingDesktopWindows(
            false,
            onScreenWindowsOnly: true
        )

        // Listar pantallas disponibles
        print("=== Pantallas disponibles ===")
        for display in content.displays {
            print("  - Display ID: \(display.displayID)")
            print("    Resolución: \(display.width) x \(display.height)")
        }

        // Listar ventanas visibles
        print("\n=== Ventanas visibles ===")
        for window in content.windows {
            let titulo = window.title ?? "Sin título"
            let app = window.owningApplication?.applicationName ?? "Desconocida"
            print("  - [\(app)] \(titulo)")
            print("    Frame: \(window.frame)")
        }

        // Listar aplicaciones en ejecución
        print("\n=== Aplicaciones en ejecución ===")
        for app in content.applications {
            print("  - \(app.applicationName) (PID: \(app.processID))")
            print("    Bundle: \(app.bundleIdentifier)")
        }
    }

    /// Captura un screenshot de la pantalla principal usando
    /// SCScreenshotManager (disponible en macOS 14+)
    @available(macOS 14.0, *)
    func capturarScreenshot() async throws -> CGImage? {
        // Obtener contenido disponible
        let content = try await SCShareableContent.excludingDesktopWindows(
            false,
            onScreenWindowsOnly: true
        )

        // Seleccionar la pantalla principal
        guard let pantallaPrincipal = content.displays.first else {
            print("Error: No se encontró ninguna pantalla")
            return nil
        }

        // Crear filtro para capturar la pantalla completa
        let filtro = SCContentFilter(
            display: pantallaPrincipal,
            excludingApplications: [],
            exceptingWindows: []
        )

        // Configurar la captura
        let configuracion = SCStreamConfiguration()
        configuracion.width = pantallaPrincipal.width * 2  // Retina
        configuracion.height = pantallaPrincipal.height * 2
        configuracion.showsCursor = true

        // Capturar el screenshot
        let imagen = try await SCScreenshotManager.captureImage(
            contentFilter: filtro,
            configuration: configuracion
        )

        print("Screenshot capturado: \(imagen.width) x \(imagen.height) píxeles")
        return imagen
    }
}
```

## Ejemplo intermedio

Este ejemplo muestra cómo iniciar un stream de captura continuo, recibir frames de vídeo y audio, y detener la captura:

```swift
import ScreenCaptureKit
import CoreMedia
import AVFoundation

/// Ejemplo intermedio: Stream de captura continuo con vídeo y audio
class ScreenRecorder: NSObject, SCStreamOutput, SCStreamDelegate {

    // MARK: - Propiedades

    private var stream: SCStream?
    private var isRecording = false

    /// Contador de frames recibidos para monitoreo
    private var frameCount: Int = 0
    private var audioSampleCount: Int = 0

    /// Callback opcional para procesar cada frame de vídeo
    var onVideoFrame: ((CMSampleBuffer) -> Void)?

    /// Callback opcional para procesar cada muestra de audio
    var onAudioSample: ((CMSampleBuffer) -> Void)?

    // MARK: - Configuración e inicio

    /// Inicia la captura de pantalla con la configuración especificada
    /// - Parameters:
    ///   - fps: Tasa de frames por segundo deseada (por defecto 30)
    ///   - capturaAudio: Indica si se debe capturar el audio del sistema
    ///   - excluirAppActual: Excluir la aplicación actual de la captura
    func iniciarCaptura(
        fps: Int = 30,
        capturaAudio: Bool = true,
        excluirAppActual: Bool = true
    ) async throws {
        // Evitar iniciar múltiples capturas
        guard !isRecording else {
            print("⚠️ La captura ya está en curso")
            return
        }

        // 1. Obtener contenido compartible
        let content = try await SCShareableContent.excludingDesktopWindows(
            false,
            onScreenWindowsOnly: true
        )

        guard let display = content.displays.first else {
            throw ScreenRecorderError.sinPantallaDisponible
        }

        // 2. Construir la lista de aplicaciones a excluir
        var appsExcluidas: [SCRunningApplication] = []
        if excluirAppActual {
            let bundleActual = Bundle.main.bundleIdentifier ?? ""
            appsExcluidas = content.applications.filter {
                $0.bundleIdentifier == bundleActual
            }
        }

        // 3. Crear el filtro de contenido
        let filtro = SCContentFilter(
            display: display,
            excludingApplications: appsExcluidas,
            exceptingWindows: []
        )

        // 4. Configurar los parámetros de captura
        let config = SCStreamConfiguration()
        config.width = display.width * 2               // Resolución Retina
        config.height = display.height * 2
        config.minimumFrameInterval = CMTime(
            value: 1,
            timescale: CMTimeScale(fps)
        )
        config.pixelFormat = kCVPixelFormatType_32BGRA  // Formato compatible con Metal/Core Image
        config.showsCursor = true                        // Incluir el cursor
        config.capturesAudio = capturaAudio              // Capturar audio del sistema
        config.sampleRate = 48000                        // Tasa de muestreo de audio
        config.channelCount = 2                          // Audio estéreo

        // Configuración de calidad (macOS 14+)
        if #available(macOS 14.0, *) {
            config.queueDepth = 8  // Tamaño del buffer de frames
        }

        // 5. Crear e iniciar el stream
        let nuevoStream = SCStream(
            filter: filtro,
            configuration: config,
            delegate: self
        )

        // Agregar salidas de vídeo y audio en colas dedicadas
        let colaVideo = DispatchQueue(
            label: "com.miapp.screencapture.video",
            qos: .userInteractive
        )
        let colaAudio = DispatchQueue(
            label: "com.miapp.screencapture.audio",
            qos: .userInteractive
        )

        try nuevoStream.addStreamOutput(
            self,
            type: .screen,
            sampleHandlerQueue: colaVideo
        )

        if capturaAudio {
            try nuevoStream.addStreamOutput(
                self,
                type: .audio,
                sampleHandlerQueue: colaAudio
            )
        }

        // Iniciar la captura
        try await nuevoStream.startCapture()

        self.stream = nuevoStream
        