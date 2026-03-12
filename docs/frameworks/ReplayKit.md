---
sidebar_position: 1
title: ReplayKit
---

# ReplayKit

## ¿Qué es ReplayKit?

ReplayKit es un framework de Apple que permite a las aplicaciones iOS, macOS y tvOS grabar el contenido de la pantalla, capturar audio (tanto del micrófono como del sistema) y transmitir en vivo el contenido de la aplicación a servicios de broadcasting. Introducido en iOS 9, ha evolucionado significativamente hasta convertirse en una herramienta robusta para la creación de contenido multimedia directamente desde dispositivos Apple.

Este framework proporciona una API de alto nivel que abstrae toda la complejidad de la captura de pantalla, codificación de vídeo y gestión de buffers de audio. Los desarrolladores pueden integrar funcionalidades de grabación y streaming en sus aplicaciones con relativamente poco código, mientras que el sistema operativo se encarga de gestionar los recursos de hardware de manera eficiente, minimizando el impacto en el rendimiento y la batería del dispositivo.

ReplayKit es especialmente útil en aplicaciones de juegos, herramientas educativas, aplicaciones de productividad y cualquier contexto donde el usuario necesite capturar lo que sucede en pantalla. Desde iOS 12, el framework también soporta extensiones de broadcast que permiten transmitir contenido en vivo a plataformas como Twitch, YouTube Live u otros servicios personalizados, ampliando enormemente sus posibilidades de integración.

## Casos de uso principales

- **Grabación de partidas en juegos**: Los jugadores pueden grabar sus sesiones de juego para compartirlas en redes sociales o revisarlas posteriormente. Es el caso de uso más clásico y la razón original por la que se creó el framework.

- **Tutoriales y contenido educativo**: Aplicaciones educativas pueden permitir a profesores y alumnos grabar demostraciones paso a paso, presentaciones interactivas o resolución de ejercicios directamente desde la app.

- **Transmisión en vivo (Live Streaming)**: Mediante las extensiones de broadcast, las aplicaciones pueden transmitir contenido en tiempo real a plataformas de streaming, ideal para eSports, clases en línea o eventos en vivo.

- **Reporte de errores y soporte técnico**: Los usuarios pueden grabar la reproducción de un bug para enviar al equipo de desarrollo, proporcionando contexto visual mucho más útil que una descripción textual.

- **Creación de contenido para redes sociales**: Aplicaciones de diseño, dibujo o edición pueden permitir que los usuarios graben su proceso creativo para compartirlo en plataformas como Instagram, TikTok o YouTube.

- **Captura de pantalla a nivel de sistema**: Desde iOS 11, ReplayKit permite capturar no solo el contenido de la propia app, sino toda la pantalla del dispositivo mediante la extensión de grabación del sistema (Broadcast Upload Extension), habilitando aplicaciones tipo grabadora de pantalla general.

## Instalación y configuración

### Agregar el framework al proyecto

ReplayKit viene incluido en el SDK de iOS, por lo que no necesitas instalarlo mediante gestores de paquetes. Solo debes importarlo en los archivos donde lo necesites:

```swift
import ReplayKit
```

### Configuración en el proyecto de Xcode

Para funcionalidades básicas de grabación in-app no se requiere configuración adicional en `Info.plist`. Sin embargo, para ciertos escenarios avanzados necesitarás:

**1. Permisos de micrófono** (si capturas audio del micrófono):

Agrega la clave `NSMicrophoneUsageDescription` en tu archivo `Info.plist`:

```xml
<key>NSMicrophoneUsageDescription</key>
<string>La app necesita acceso al micrófono para grabar audio junto con el vídeo de pantalla.</string>
```

**2. Extensiones de Broadcast** (para streaming en vivo o grabación del sistema):

Ve a **File → New → Target** y selecciona:
- **Broadcast Upload Extension**: Para enviar contenido a un servicio de streaming.
- **Broadcast Setup UI Extension**: Para presentar una interfaz de configuración antes de iniciar la transmisión.

**3. App Groups** (para comunicación entre la app principal y las extensiones):

```xml
<key>com.apple.security.application-groups</key>
<array>
    <string>group.com.tuempresa.tuapp</string>
</array>
```

### Compatibilidad

| Plataforma | Versión mínima |
|-----------|---------------|
| iOS       | 9.0           |
| macOS     | 11.0          |
| tvOS      | 10.0          |
| Mac Catalyst | 13.0      |

## Conceptos clave

### 1. RPScreenRecorder

Es la clase central de ReplayKit. Proporciona un singleton (`RPScreenRecorder.shared()`) que gestiona el inicio, pausa y finalización de las grabaciones. También permite verificar si la grabación está disponible en el dispositivo actual y si se está grabando en ese momento.

### 2. RPPreviewViewController

Controlador de vista que el sistema proporciona al finalizar una grabación. Presenta una interfaz nativa donde el usuario puede previsualizar el vídeo grabado, editarlo (recortarlo) y compartirlo o guardarlo. Es la forma más sencilla de gestionar el resultado de una grabación sin necesidad de construir UI propia.

### 3. RPBroadcastActivityViewController

Controlador que presenta al usuario una lista de servicios de broadcast disponibles en el dispositivo. Permite seleccionar a qué plataforma de streaming desea transmitir y gestiona el flujo de autenticación y configuración del servicio seleccionado.

### 4. RPSystemBroadcastPickerView

Vista del sistema (disponible desde iOS 12) que muestra un botón nativo para iniciar o detener la grabación/transmisión a nivel de sistema. Es fundamental para aplicaciones que necesitan capturar contenido fuera de su propio sandbox.

### 5. Broadcast Upload Extension

Es un tipo de extensión de aplicación que procesa los datos de audio y vídeo capturados durante un broadcast. Recibe los sample buffers en tiempo real y los puede enviar a un servidor remoto. Opera en un proceso separado con su propio ciclo de vida.

### 6. Captura de Sample Buffers

Desde iOS 11, ReplayKit permite acceder directamente a los `CMSampleBuffer` de vídeo y audio, lo que habilita el procesamiento personalizado de los frames capturados: aplicar filtros, enviar a un servidor propio, guardar en formato personalizado, etc.

## Ejemplo básico

```swift
import UIKit
import ReplayKit

/// ViewController básico que demuestra la grabación de pantalla
/// usando RPScreenRecorder con la API más simple posible.
class GrabacionBasicaViewController: UIViewController {
    
    // Referencia al singleton del grabador de pantalla
    private let grabador = RPScreenRecorder.shared()
    
    // Botón para controlar la grabación
    private let botonGrabar: UIButton = {
        let boton = UIButton(type: .system)
        boton.setTitle("Iniciar Grabación", for: .normal)
        boton.titleLabel?.font = .systemFont(ofSize: 18, weight: .semibold)
        boton.translatesAutoresizingMaskIntoConstraints = false
        return boton
    }()
    
    // Indicador visual de que se está grabando
    private let indicadorGrabacion: UIView = {
        let vista = UIView()
        vista.backgroundColor = .red
        vista.layer.cornerRadius = 6
        vista.isHidden = true
        vista.translatesAutoresizingMaskIntoConstraints = false
        return vista
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        configurarUI()
        botonGrabar.addTarget(self, action: #selector(alternarGrabacion), for: .touchUpInside)
    }
    
    private func configurarUI() {
        view.backgroundColor = .systemBackground
        view.addSubview(botonGrabar)
        view.addSubview(indicadorGrabacion)
        
        NSLayoutConstraint.activate([
            botonGrabar.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            botonGrabar.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            indicadorGrabacion.widthAnchor.constraint(equalToConstant: 12),
            indicadorGrabacion.heightAnchor.constraint(equalToConstant: 12),
            indicadorGrabacion.trailingAnchor.constraint(equalTo: botonGrabar.leadingAnchor, constant: -8),
            indicadorGrabacion.centerYAnchor.constraint(equalTo: botonGrabar.centerYAnchor)
        ])
    }
    
    @objc private func alternarGrabacion() {
        if grabador.isRecording {
            detenerGrabacion()
        } else {
            iniciarGrabacion()
        }
    }
    
    private func iniciarGrabacion() {
        // Verificar que la grabación esté disponible en este dispositivo
        guard grabador.isAvailable else {
            mostrarAlerta(mensaje: "La grabación de pantalla no está disponible en este dispositivo.")
            return
        }
        
        // Iniciar la grabación con captura de micrófono habilitada
        grabador.isMicrophoneEnabled = true
        
        grabador.startRecording { [weak self] error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.mostrarAlerta(mensaje: "Error al iniciar: \(error.localizedDescription)")
                    return
                }
                // Actualizar la UI para reflejar que se está grabando
                self?.botonGrabar.setTitle("Detener Grabación", for: .normal)
                self?.indicadorGrabacion.isHidden = false
            }
        }
    }
    
    private func detenerGrabacion() {
        grabador.stopRecording { [weak self] previewController, error in
            DispatchQueue.main.async {
                // Restaurar la UI
                self?.botonGrabar.setTitle("Iniciar Grabación", for: .normal)
                self?.indicadorGrabacion.isHidden = true
                
                if let error = error {
                    self?.mostrarAlerta(mensaje: "Error al detener: \(error.localizedDescription)")
                    return
                }
                
                // Presentar el controlador de previsualización nativo
                if let preview = previewController {
                    preview.previewControllerDelegate = self
                    self?.present(preview, animated: true)
                }
            }
        }
    }
    
    private func mostrarAlerta(mensaje: String) {
        let alerta = UIAlertController(title: "ReplayKit", message: mensaje, preferredStyle: .alert)
        alerta.addAction(UIAlertAction(title: "OK", style: .default))
        present(alerta, animated: true)
    }
}

// MARK: - RPPreviewViewControllerDelegate
extension GrabacionBasicaViewController: RPPreviewViewControllerDelegate {
    
    /// Se llama cuando el usuario termina de interactuar con la previsualización
    func previewControllerDidFinish(_ previewController: RPPreviewViewController) {
        previewController.dismiss(animated: true)
    }
}
```

## Ejemplo intermedio

```swift
import UIKit
import ReplayKit
import Photos

/// Servicio de grabación que captura sample buffers directamente,
/// permitiendo guardar el vídeo en el carrete de fotos sin pasar
/// por RPPreviewViewController.
class ServicioGrabacionPantalla: NSObject {
    
    // MARK: - Propiedades
    
    private let grabador = RPScreenRecorder.shared()
    private var escritorVideo: AVAssetWriter?
    private var entradaVideo: AVAssetWriterInput?
    private var entradaAudioApp: AVAssetWriterInput?
    private var entradaAudioMicrofono: AVAssetWriterInput?
    private var rutaArchivo: URL?
    private var escrituraIniciada = false
    
    /// Estado observable de la grabación
    var estaGrabando: Bool {
        return grabador.isRecording
    }
    
    // MARK: - Grabación con captura de buffers
    
    /// Inicia la grabación capturando los sample buffers individuales
    /// para tener control total sobre el archivo de salida.
    func iniciarGrabacion(completion: @escaping (Result<Void, Error>) -> Void) {
        guard grabador.isAvailable else {
            completion(.failure(ErrorGrabacion.noDisponible))
            return
        }
        
        // Configurar el archivo de salida
        let nombreArchivo = "grabacion_\(Date().timeIntervalSince1970).mp4"
        let directorio = FileManager.default.temporaryDirectory
        rutaArchivo = directorio.appendingPathComponent(nombreArchivo)
        
        guard let ruta = rutaArchivo else {
            completion(.failure(ErrorGrabacion.rutaInvalida))
            return
        }
        
        do {
            // Crear el escritor de vídeo
            escritorVideo = try AVAssetWriter(outputURL: ruta, fileType: .mp4)
            
            // Configurar la entrada de vídeo con códec H.264
            let ajustesVideo: [String: Any] = [
                AVVideoCodecKey: AVVideoCodecType.h264,
                AVVideoWidthKey: UIScreen.main.bounds.width * UIScreen.main.scale,
                AVVideoHeightKey: UIScreen.main.bounds.height * UIScreen.main.scale
            ]
            entradaVideo = AVAssetWriterInput(mediaType: .video, outputSettings: ajustesVideo)
            entradaVideo?.expectsMediaDataInRealTime = true
            
            // Configurar la entrada de audio de la aplicación
            let ajustesAudio: [String: Any] = [
                AVFormatIDKey: kAudioFormatMPEG4AAC,
                AVSampleRateKey: 44100,
                AVNumberOfChannelsKey: 2,
                AVEncoderBitRateKey: 128000
            ]
            entradaAudioApp = AVAssetWriterInput(mediaType: .audio, outputSettings: ajustesAudio)
            entradaAudioApp?.expectsMediaDataInRealTime = true
            
            entradaAudioMicrofono = AVAssetWriterInput(mediaType: .audio, outputSettings: ajustesAudio)
            entradaAudioMicrofono?.expectsMediaDataInRealTime = true
            
            // Agregar las entradas al escritor
            if let escritor = escritorVideo {
                if let video = entradaVideo, escritor.canAdd(video) {
                    escritor.add(video)
                }
                if let audioApp = entradaAudioApp, escritor.canAdd(audioApp) {
                    escritor.add(audioApp)
                }
                if let audioMic = entradaAudioMicrofono, escritor.canAdd(audioMic) {
                    escritor.add(audioMic)
                }
            }
            
            escrituraIniciada = false
            
        } catch {
            completion(.failure(error))
            return
        }
        
        // Activar micrófono
        grabador.isMicrophoneEnabled = true
        
        // Iniciar la captura con handler de sample buffers
        grabador.startCapture { [weak self] sampleBuffer, tipoBuffer, error in
            guard let self = self, error == nil else { return }
            
            // Asegurarse de que el escritor está en estado correcto
            guard let escritor = self.escritorVideo,
                  escritor.status != .failed else { return }
            
            // Iniciar la escritura con el