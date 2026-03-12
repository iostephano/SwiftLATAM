---
sidebar_position: 1
title: SoundAnalysis
---

# SoundAnalysis

## ¿Qué es SoundAnalysis?

**SoundAnalysis** es un framework de Apple que permite analizar flujos de audio para identificar y clasificar sonidos en tiempo real o a partir de archivos de audio pregrabados. Utiliza modelos de aprendizaje automático para reconocer más de 300 tipos de sonidos diferentes —desde ladridos de perros y sirenas hasta instrumentos musicales y voces humanas— gracias a su clasificador incorporado basado en la taxonomía de Apple.

Este framework se integra estrechamente con **Core ML**, lo que permite a los desarrolladores entrenar y utilizar sus propios modelos de clasificación de sonido personalizados mediante **Create ML**. De esta manera, es posible detectar sonidos específicos de un dominio particular, como maquinaria industrial, sonidos médicos o eventos acústicos propios de una aplicación.

SoundAnalysis es especialmente útil cuando se necesita construir aplicaciones de accesibilidad (alertas sonoras para personas con discapacidad auditiva), monitoreo ambiental, domótica inteligente, aplicaciones de salud o cualquier solución que requiera reaccionar ante eventos acústicos del entorno. Está disponible a partir de **iOS 13**, **macOS 10.15**, **tvOS 13** y **watchOS 7**.

## Casos de uso principales

- **Accesibilidad auditiva:** Detectar sonidos del hogar (timbre, alarma de incendio, llanto de bebé) y notificar al usuario mediante alertas visuales o hápticas. Esta es la base de la función "Reconocimiento de sonidos" integrada en iOS.

- **Monitoreo ambiental:** Aplicaciones que analizan el entorno acústico para detectar contaminación sonora, identificar especies de aves por su canto o monitorear ecosistemas naturales.

- **Salud y bienestar:** Detección de patrones de tos, ronquidos o eventos respiratorios durante el sueño para generar informes de salud o alertas tempranas.

- **Domótica y hogar inteligente:** Reconocer sonidos como el de una puerta cerrándose, cristales rompiéndose o electrodomésticos en funcionamiento para automatizar acciones en el hogar.

- **Aplicaciones musicales:** Identificar instrumentos musicales, clasificar géneros o detectar eventos rítmicos dentro de una pista de audio para herramientas de producción musical.

- **Seguridad y vigilancia:** Sistemas que detectan disparos, gritos o sonidos de impacto para activar protocolos de emergencia en espacios públicos o privados.

## Instalación y configuración

### Agregar el framework al proyecto

SoundAnalysis viene incluido en el SDK de Apple, por lo que no requiere dependencias externas. Solo necesitas importarlo:

```swift
import SoundAnalysis
import AVFoundation  // Necesario para captura de audio
import CoreML        // Solo si usas modelos personalizados
```

### Permisos en Info.plist

Para analizar audio en tiempo real desde el micrófono, debes solicitar permiso de acceso al micrófono. Agrega la siguiente clave en tu archivo `Info.plist`:

```xml
<key>NSMicrophoneUsageDescription</key>
<string>Necesitamos acceso al micrófono para analizar los sonidos del entorno.</string>
```

### Solicitar permiso en tiempo de ejecución

```swift
import AVFoundation

AVAudioSession.sharedInstance().requestRecordPermission { autorizado in
    if autorizado {
        print("Permiso de micrófono concedido")
    } else {
        print("Permiso de micrófono denegado")
    }
}
```

### Requisitos mínimos de despliegue

| Plataforma | Versión mínima |
|------------|---------------|
| iOS        | 13.0          |
| macOS      | 10.15         |
| tvOS       | 13.0          |
| watchOS    | 7.0           |

## Conceptos clave

### 1. SNAudioStreamAnalyzer

Es el motor principal de análisis para audio en tiempo real. Recibe buffers de audio provenientes de un `AVAudioEngine` y los procesa a través de las solicitudes de clasificación registradas. Cada buffer que alimentas al analizador es evaluado por todos los modelos activos simultáneamente.

### 2. SNAudioFileAnalyzer

Similar al anterior, pero diseñado para analizar archivos de audio completos. Acepta una URL al archivo y procesa el audio de principio a fin, emitiendo resultados de clasificación a medida que avanza.

### 3. SNClassifySoundRequest

Representa una solicitud de clasificación de sonido. Puede crearse con el clasificador integrado de Apple (`SNClassifierIdentifier.version1`) o con un modelo Core ML personalizado entrenado con Create ML. Es el objeto que registras en el analizador.

### 4. SNClassificationResult

Contiene los resultados de una clasificación individual. Incluye una colección de `SNClassification`, cada uno con un `identifier` (nombre del sonido) y un `confidence` (nivel de confianza entre 0.0 y 1.0). Los resultados están ordenados por confianza descendente.

### 5. SNResultsObserving

Protocolo que tu clase debe implementar para recibir los resultados del análisis. Define tres métodos: `request(_:didProduce:)` para resultados exitosos, `request(_:didFailWithError:)` para errores, y `requestDidComplete(_:)` cuando el análisis termina.

### 6. SNClassifierIdentifier

Identificador que referencia el clasificador de sonidos integrado de Apple. Este clasificador reconoce más de 300 categorías de sonido sin necesidad de un modelo externo. Apple lo actualiza entre versiones del sistema operativo.

## Ejemplo básico

Este ejemplo muestra cómo clasificar sonidos desde un archivo de audio utilizando el clasificador integrado de Apple:

```swift
import SoundAnalysis
import AVFoundation

// MARK: - Observador de resultados de clasificación
class ObservadorDeSonido: NSObject, SNResultsObserving {
    
    /// Se llama cada vez que el analizador produce un resultado
    func request(_ request: SNRequest, didProduce result: SNResult) {
        // Verificamos que el resultado sea de clasificación
        guard let clasificacion = result as? SNClassificationResult else { return }
        
        // Obtenemos la clasificación con mayor confianza
        guard let mejorResultado = clasificacion.classifications.first else { return }
        
        // Solo mostramos resultados con confianza mayor al 50%
        if mejorResultado.confidence > 0.5 {
            print("🔊 Sonido detectado: \(mejorResultado.identifier)")
            print("   Confianza: \(String(format: "%.1f", mejorResultado.confidence * 100))%")
            print("   Tiempo: \(clasificacion.timeRange)")
        }
    }
    
    /// Se llama cuando ocurre un error durante el análisis
    func request(_ request: SNRequest, didFailWithError error: Error) {
        print("❌ Error en el análisis: \(error.localizedDescription)")
    }
    
    /// Se llama cuando el análisis del archivo se completa
    func requestDidComplete(_ request: SNRequest) {
        print("✅ Análisis completado exitosamente")
    }
}

// MARK: - Función para analizar un archivo de audio
func analizarArchivoDeAudio(url: URL) {
    do {
        // Creamos el analizador de archivos de audio
        let analizador = try SNAudioFileAnalyzer(url: url)
        
        // Creamos la solicitud con el clasificador integrado de Apple
        let solicitud = try SNClassifySoundRequest(classifierIdentifier: .version1)
        
        // Configuramos la ventana de análisis (en segundos)
        solicitud.windowDuration = CMTimeMakeWithSeconds(1.5, preferredTimescale: 48_000)
        
        // Configuramos la superposición entre ventanas (50%)
        solicitud.overlapFactor = 0.5
        
        // Creamos el observador
        let observador = ObservadorDeSonido()
        
        // Registramos la solicitud con el observador
        try analizador.add(solicitud, withObserver: observador)
        
        // Iniciamos el análisis
        analizador.analyze()
        
    } catch {
        print("❌ No se pudo iniciar el análisis: \(error.localizedDescription)")
    }
}
```

## Ejemplo intermedio

Este ejemplo muestra cómo analizar sonidos en tiempo real desde el micrófono del dispositivo:

```swift
import SoundAnalysis
import AVFoundation

// MARK: - Clasificador de sonidos en tiempo real
class ClasificadorDeSonidosEnVivo: NSObject, SNResultsObserving {
    
    // Motor de audio para capturar desde el micrófono
    private let motorDeAudio = AVAudioEngine()
    
    // Analizador de flujo de audio en tiempo real
    private var analizadorDeStream: SNAudioStreamAnalyzer?
    
    // Cola dedicada para el análisis (evita bloquear el hilo principal)
    private let colaDeAnalisis = DispatchQueue(label: "com.app.analisisDeSonido")
    
    // Callback para notificar resultados
    var alDetectarSonido: ((String, Double) -> Void)?
    
    // MARK: - Iniciar análisis
    func iniciarAnalisis() {
        do {
            // Configuramos la sesión de audio
            let sesion = AVAudioSession.sharedInstance()
            try sesion.setCategory(.record, mode: .measurement)
            try sesion.setActive(true)
            
            // Obtenemos el formato del micrófono
            let nodoDeEntrada = motorDeAudio.inputNode
            let formatoDeGrabacion = nodoDeEntrada.outputFormat(forBus: 0)
            
            // Creamos el analizador con el formato de audio
            let analizador = SNAudioStreamAnalyzer(format: formatoDeGrabacion)
            self.analizadorDeStream = analizador
            
            // Creamos y configuramos la solicitud de clasificación
            let solicitud = try SNClassifySoundRequest(classifierIdentifier: .version1)
            solicitud.windowDuration = CMTimeMakeWithSeconds(1.0, preferredTimescale: 48_000)
            solicitud.overlapFactor = 0.5
            
            // Registramos la solicitud
            try analizador.add(solicitud, withObserver: self)
            
            // Instalamos un tap en el nodo de entrada para recibir buffers
            nodoDeEntrada.installTap(
                onBus: 0,
                bufferSize: 8192,
                format: formatoDeGrabacion
            ) { [weak self] buffer, tiempo in
                // Enviamos cada buffer al analizador en la cola dedicada
                self?.colaDeAnalisis.async {
                    analizador.analyze(buffer, atAudioFramePosition: tiempo.sampleTime)
                }
            }
            
            // Iniciamos el motor de audio
            try motorDeAudio.start()
            print("🎤 Análisis de sonido en tiempo real iniciado")
            
        } catch {
            print("❌ Error al iniciar el análisis: \(error.localizedDescription)")
        }
    }
    
    // MARK: - Detener análisis
    func detenerAnalisis() {
        motorDeAudio.inputNode.removeTap(onBus: 0)
        motorDeAudio.stop()
        analizadorDeStream?.completeAnalysis()
        analizadorDeStream = nil
        print("🛑 Análisis detenido")
    }
    
    // MARK: - SNResultsObserving
    func request(_ request: SNRequest, didProduce result: SNResult) {
        guard let clasificacion = result as? SNClassificationResult,
              let mejorResultado = clasificacion.classifications.first,
              mejorResultado.confidence > 0.6 else { return }
        
        // Notificamos en el hilo principal para actualizar la UI
        DispatchQueue.main.async { [weak self] in
            self?.alDetectarSonido?(
                mejorResultado.identifier,
                mejorResultado.confidence
            )
        }
    }
    
    func request(_ request: SNRequest, didFailWithError error: Error) {
        print("❌ Error: \(error.localizedDescription)")
    }
    
    func requestDidComplete(_ request: SNRequest) {
        print("✅ Análisis de stream completado")
    }
    
    deinit {
        detenerAnalisis()
    }
}

// MARK: - Uso del clasificador
let clasificador = ClasificadorDeSonidosEnVivo()

clasificador.alDetectarSonido = { sonido, confianza in
    print("🔊 \(sonido) — \(String(format: "%.0f", confianza * 100))%")
}

clasificador.iniciarAnalisis()
```

## Ejemplo avanzado

Este ejemplo implementa una arquitectura **MVVM** completa con **SwiftUI** y **Combine** para una aplicación de monitoreo de sonidos en el hogar:

```swift
import SwiftUI
import Combine
import SoundAnalysis
import AVFoundation

// MARK: - Modelo de datos
struct SonidoDetectado: Identifiable, Equatable {
    let id = UUID()
    let identificador: String
    let confianza: Double
    let fecha: Date
    let esAlerta: Bool
    
    /// Nombre legible en español para el sonido
    var nombreEnEspanol: String {
        let traducciones: [String: String] = [
            "dog_bark": "Ladrido de perro",
            "cat_meow": "Maullido de gato",
            "doorbell": "Timbre de puerta",
            "siren": "Sirena",
            "fire_alarm": "Alarma de incendio",
            "smoke_alarm": "Alarma de humo",
            "baby_crying": "Llanto de bebé",
            "glass_breaking": "Cristal rompiéndose",
            "knock": "Golpe en la puerta",
            "speech": "Voz humana",
            "music": "Música",
            "water_running": "Agua corriendo",
            "applause": "Aplausos",
            "laughter": "Risas",
            "coughing": "Tos",
            "car_horn": "Bocina de auto"
        ]
        return traducciones[identificador] ?? identificador.replacingOccurrences(of: "_", with: " ").capitalized
    }
    
    /// Emoji representativo del sonido
    var emoji: String {
        let emojis: [String: String] = [
            "dog_bark": "🐕", "cat_meow": "🐱", "doorbell": "🔔",
            "siren": "🚨", "fire_alarm": "🔥", "smoke_alarm": "💨",
            "baby_crying": "👶", "glass_breaking": "🪟", "knock": "🚪",
            "speech": "🗣️", "music": "🎵", "water_running": "🚿",
            "coughing": "😷", "car_horn": "🚗"
        ]
        return emojis[identificador] ?? "🔊"
    }
    
    /// Nivel de confianza formateado
    var confianzaFormateada: String {
        String(format: "%.0f%%", confianza * 100)