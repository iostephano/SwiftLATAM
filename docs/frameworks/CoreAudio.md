---
sidebar_position: 1
title: CoreAudio
---

# CoreAudio

## ¿Qué es CoreAudio?

CoreAudio es el framework de bajo nivel de Apple que constituye la base fundamental de toda la infraestructura de audio en iOS, macOS, tvOS y watchOS. Es la capa más cercana al hardware de audio del dispositivo y proporciona interfaces para capturar, procesar, mezclar y reproducir audio con una latencia mínima y un control granular sobre cada aspecto del flujo de audio. A diferencia de frameworks de más alto nivel como AVFoundation o AVFAudio, CoreAudio expone directamente los buffers de audio, los formatos de datos PCM y las unidades de procesamiento de señal.

Este framework es esencial cuando las abstracciones de alto nivel no son suficientes para los requisitos de una aplicación. Si necesitas procesamiento de audio en tiempo real, síntesis de sonido, efectos personalizados, enrutamiento complejo de señales o trabajar directamente con muestras de audio a nivel de sample, CoreAudio es la herramienta adecuada. Se compone de varias sub-APIs interrelacionadas: **Audio Units** (procesamiento modular de audio), **Audio Toolbox** (servicios de reproducción, grabación y conversión), **Audio Queue Services** (grabación y reproducción con buffers) y el propio **CoreAudio** base que define tipos de datos, estructuras y constantes compartidas.

CoreAudio utiliza predominantemente APIs en C por razones de rendimiento, lo que significa que trabajar con él desde Swift requiere familiaridad con punteros, callbacks y manejo manual de memoria en ciertos contextos. A pesar de su complejidad, dominar CoreAudio otorga un control sin precedentes sobre el audio del dispositivo y es la base sobre la que se construyen aplicaciones profesionales como DAWs móviles, sintetizadores, afinadores de instrumentos, aplicaciones de podcasting avanzadas y motores de audio para videojuegos.

## Casos de uso principales

- **Síntesis de audio en tiempo real**: Generar formas de onda (seno, cuadrada, sierra, etc.) directamente desde código para sintetizadores musicales, generadores de tonos o instrumentos virtuales, controlando frecuencia, amplitud y fase sample a sample.

- **Procesamiento de efectos de audio personalizados**: Implementar reverberación, delay, distorsión, ecualización paramétrica u otros efectos DSP que se aplican en tiempo real sobre una señal de entrada, algo común en apps de producción musical.

- **Grabación de audio de ultra baja latencia**: Capturar audio del micrófono con la mínima latencia posible, ideal para apps de monitoreo en vivo, afinadores cromáticos de instrumentos o sistemas de comunicación por voz en tiempo real.

- **Análisis espectral y visualización de audio**: Realizar FFT (Transformada Rápida de Fourier) sobre buffers de audio para obtener datos de frecuencia y generar espectrogramas, analizadores de espectro o medidores de nivel profesionales.

- **Enrutamiento de audio complejo**: Mezclar múltiples fuentes de audio simultáneamente, aplicar paneos estéreo independientes, controlar volúmenes individuales y dirigir señales a diferentes buses de salida dentro de un grafo de procesamiento de Audio Units.

- **Conversión de formatos de audio**: Transformar audio entre diferentes formatos (PCM, AAC, ALAC, MP3), tasas de muestreo, profundidades de bits y configuraciones de canales utilizando Audio Converter Services.

## Instalación y configuración

### Agregar el framework al proyecto

CoreAudio viene incluido en el SDK de Apple, por lo que no necesitas instalar dependencias externas. Solo necesitas importar los módulos correspondientes:

```swift
import CoreAudio       // Tipos base, estructuras y constantes fundamentales
import AudioToolbox    // Audio Queue Services, Audio Files, Audio Converter, Audio Units
import AVFoundation    // Configuración de sesión de audio (AVAudioSession)
```

### Configuración en Info.plist

Si tu app captura audio del micrófono, debes declarar el permiso correspondiente:

```xml
<key>NSMicrophoneUsageDescription</key>
<string>Esta app necesita acceso al micrófono para grabar y procesar audio en tiempo real.</string>
```

### Configuración de la sesión de audio

Antes de usar cualquier funcionalidad de CoreAudio, es imprescindible configurar la sesión de audio correctamente:

```swift
import AVFoundation

func configurarSesionDeAudio() {
    let sesion = AVAudioSession.sharedInstance()
    do {
        // .playAndRecord permite entrada y salida simultánea
        try sesion.setCategory(.playAndRecord, mode: .measurement, options: [.defaultToSpeaker, .allowBluetooth])

        // Solicitar un buffer pequeño para baja latencia (≈5.8ms a 44100 Hz)
        try sesion.setPreferredSampleRate(44100.0)
        try sesion.setPreferredIOBufferDuration(256.0 / 44100.0)

        try sesion.setActive(true)
        print("Sesión de audio configurada correctamente")
        print("Tasa de muestreo activa: \(sesion.sampleRate) Hz")
        print("Duración de buffer IO: \(sesion.ioBufferDuration * 1000) ms")
    } catch {
        print("Error configurando sesión de audio: \(error.localizedDescription)")
    }
}
```

### Capacidades del proyecto (Entitlements)

Para apps que usen Audio Units inter-app o extensiones de Audio Unit, activa en **Signing & Capabilities**:

- **Background Modes → Audio, AirPlay, and Picture in Picture** (para reproducción/grabación en segundo plano)
- **Inter-App Audio** (si corresponde, aunque está deprecado a favor de AUv3)

## Conceptos clave

### 1. AudioStreamBasicDescription (ASBD)

Es la estructura más importante de CoreAudio. Define completamente el formato de un flujo de audio: tasa de muestreo, número de canales, bits por muestra, bytes por frame, si es entrelazado o no, formato de datos (PCM lineal, flotante, entero). Toda operación en CoreAudio comienza definiendo un ASBD correcto.

```swift
var formatoAudio = AudioStreamBasicDescription(
    mSampleRate: 44100.0,                              // 44.1 kHz
    mFormatID: kAudioFormatLinearPCM,                  // PCM lineal sin compresión
    mFormatFlags: kAudioFormatFlagIsFloat | kAudioFormatFlagIsPacked | kAudioFormatFlagIsNonInterleaved,
    mBytesPerPacket: 4,                                // 4 bytes (Float32)
    mFramesPerPacket: 1,                               // Siempre 1 para PCM
    mBytesPerFrame: 4,                                 // 4 bytes por frame por canal
    mChannelsPerFrame: 2,                              // Estéreo
    mBitsPerChannel: 32,                               // 32 bits (Float32)
    mReserved: 0
)
```

### 2. Audio Units (AUAudioUnit)

Son los bloques modulares de procesamiento de audio. Cada Audio Unit recibe buffers de entrada, los procesa y produce buffers de salida. Existen tipos predefinidos: generadores (sintetizadores), efectos (reverb, delay), mezcladores (mixer), entrada/salida (RemoteIO) y conversores. Se pueden encadenar formando un grafo de procesamiento.

### 3. Audio Queue Services

Proporcionan una forma relativamente sencilla de grabar y reproducir audio mediante un sistema de buffers encolados. Tú proporcionas buffers vacíos para grabación (que CoreAudio llena) o buffers llenos para reproducción (que CoreAudio consume). Es el punto intermedio entre AVFoundation y Audio Units en cuanto a complejidad y control.

### 4. Render Callback

Es el corazón del procesamiento en tiempo real. Es una función C que CoreAudio invoca en un hilo de alta prioridad cada vez que necesita un nuevo bloque de muestras de audio. Dentro de este callback hay restricciones estrictas: no se puede alocar memoria, no se puede usar Objective-C, no se pueden hacer operaciones de I/O ni bloquear. Todo debe ser determinístico y ultrarrápido.

### 5. AudioBufferList

Estructura que contiene uno o más `AudioBuffer`, cada uno representando un canal de audio (en formato no entrelazado) o todos los canales entrelazados. Es el contenedor que se pasa entre Audio Units y dentro de los render callbacks para transportar las muestras de audio reales.

### 6. Audio Component Description

Identifica de manera única un tipo de Audio Unit mediante cuatro campos: tipo (efecto, generador, mixer, I/O), subtipo (reverb, delay, etc.), fabricante (Apple u otro) y flags. Se usa para buscar, instanciar y registrar Audio Units en el sistema.

## Ejemplo básico

Este ejemplo genera un tono sinusoidal puro usando Audio Queue Services:

```swift
import AudioToolbox
import AVFoundation

/// Generador simple de tono sinusoidal usando Audio Queue Services
class GeneradorDeTono {

    // MARK: - Propiedades

    private var colaDeAudio: AudioQueueRef?
    private var frecuencia: Double = 440.0        // La4 (A4) - nota de referencia
    private var amplitud: Double = 0.25            // Volumen (0.0 a 1.0)
    private var tasaDeMuestreo: Double = 44100.0
    private var faseActual: Double = 0.0           // Fase del oscilador

    // MARK: - Estructura de contexto para el callback

    /// Estructura que pasamos al callback para acceder al estado del generador
    struct ContextoDelCallback {
        var frecuencia: Double
        var amplitud: Double
        var tasaDeMuestreo: Double
        var faseActual: Double
    }

    private var contexto: ContextoDelCallback!

    // MARK: - Inicialización

    init(frecuencia: Double = 440.0, amplitud: Double = 0.25) {
        self.frecuencia = frecuencia
        self.amplitud = amplitud
        self.contexto = ContextoDelCallback(
            frecuencia: frecuencia,
            amplitud: amplitud,
            tasaDeMuestreo: tasaDeMuestreo,
            faseActual: 0.0
        )
    }

    // MARK: - Métodos públicos

    func iniciar() {
        // 1. Definir formato de audio: PCM flotante de 32 bits, mono
        var formato = AudioStreamBasicDescription(
            mSampleRate: tasaDeMuestreo,
            mFormatID: kAudioFormatLinearPCM,
            mFormatFlags: kAudioFormatFlagIsFloat | kAudioFormatFlagIsPacked,
            mBytesPerPacket: 4,
            mFramesPerPacket: 1,
            mBytesPerFrame: 4,
            mChannelsPerFrame: 1,    // Mono
            mBitsPerChannel: 32,
            mReserved: 0
        )

        // 2. Crear la cola de audio con el callback de reproducción
        let estado = AudioQueueNewOutput(
            &formato,
            callbackDeReproduccion,    // Función callback
            &contexto,                  // Datos de usuario (puntero al contexto)
            nil,                        // Run loop (nil = interno)
            nil,                        // Modo del run loop
            0,                          // Flags reservados
            &colaDeAudio
        )

        guard estado == noErr, let cola = colaDeAudio else {
            print("Error al crear la cola de audio: \(estado)")
            return
        }

        // 3. Crear y encolar 3 buffers (triple buffering para continuidad)
        let tamanoDeBuffer: UInt32 = 1024 * 4  // 1024 frames × 4 bytes
        for _ in 0..<3 {
            var buffer: AudioQueueBufferRef?
            AudioQueueAllocateBuffer(cola, tamanoDeBuffer, &buffer)
            if let buffer = buffer {
                // Llenar el buffer inicialmente con silencio
                buffer.pointee.mAudioDataByteSize = tamanoDeBuffer
                memset(buffer.pointee.mAudioData, 0, Int(tamanoDeBuffer))
                // Encolar para que el callback los llene
                callbackDeReproduccion(&contexto, cola, buffer)
            }
        }

        // 4. Iniciar reproducción
        AudioQueueStart(cola, nil)
        print("🔊 Tono de \(frecuencia) Hz iniciado")
    }

    func detener() {
        guard let cola = colaDeAudio else { return }
        AudioQueueStop(cola, true)
        AudioQueueDispose(cola, true)
        colaDeAudio = nil
        print("🔇 Tono detenido")
    }
}

// MARK: - Callback de reproducción (función C global)

/// Esta función es invocada por CoreAudio cada vez que necesita más muestras
private let callbackDeReproduccion: AudioQueueOutputCallback = {
    datoDeUsuario, cola, buffer in

    guard let contexto = datoDeUsuario?.assumingMemoryBound(
        to: GeneradorDeTono.ContextoDelCallback.self
    ) else { return }

    let numeroDeFrames = Int(buffer.pointee.mAudioDataByteSize) / MemoryLayout<Float32>.size
    let muestras = buffer.pointee.mAudioData.assumingMemoryBound(to: Float32.self)

    // Calcular el incremento de fase por muestra
    let incrementoDeFase = 2.0 * Double.pi * contexto.pointee.frecuencia / contexto.pointee.tasaDeMuestreo

    // Generar onda sinusoidal muestra por muestra
    for i in 0..<numeroDeFrames {
        muestras[i] = Float32(sin(contexto.pointee.faseActual) * contexto.pointee.amplitud)
        contexto.pointee.faseActual += incrementoDeFase

        // Mantener la fase en rango [0, 2π) para evitar pérdida de precisión
        if contexto.pointee.faseActual >= 2.0 * Double.pi {
            contexto.pointee.faseActual -= 2.0 * Double.pi
        }
    }

    // Re-encolar el buffer para mantener la reproducción continua
    AudioQueueEnqueueBuffer(cola, buffer, 0, nil)
}

// MARK: - Uso

// let generador = GeneradorDeTono(frecuencia: 440.0, amplitud: 0.3)
// generador.iniciar()
// ... después de un tiempo ...
// generador.detener()
```

## Ejemplo intermedio

Este ejemplo implementa un grabador de audio con medición de niveles en tiempo real usando Audio Queue Services:

```swift
import AudioToolbox
import AVFoundation
import Combine

/// Grabador de audio con monitoreo de niveles en tiempo real
class GrabadorDeAudioConNiveles: ObservableObject {

    // MARK: - Propiedades publicadas (para SwiftUI)

    @Published var estaGrabando = false
    @Published var nivelActualDB: Float = -160.0   // Nivel en decibelios
    @Published var nivelNormalizado: Float = 0.0     // Nivel normalizado 0.0 - 1.0
    @Published var duracionGrabada: TimeInterval = 0.0

    // MARK: - Propiedades privadas

    private var colaDeGrabacion