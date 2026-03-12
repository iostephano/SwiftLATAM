---
sidebar_position: 1
title: Speech
---

# Speech

## ¿Qué es Speech?

**Speech** es el framework de Apple que proporciona capacidades de reconocimiento de voz (Speech-to-Text) en aplicaciones iOS, macOS, watchOS y tvOS. Utiliza las mismas tecnologías avanzadas de reconocimiento de habla que impulsan a Siri y el dictado del sistema, permitiendo a los desarrolladores convertir audio en texto de forma precisa y en tiempo real. El framework soporta más de 50 idiomas y dialectos, lo que lo convierte en una herramienta versátil para aplicaciones globales.

El framework Speech va mucho más allá de una simple transcripción. Ofrece información detallada sobre cada segmento reconocido, incluyendo niveles de confianza, transcripciones alternativas, marcas de tiempo y metadatos lingüísticos. Esto permite a los desarrolladores construir experiencias sofisticadas como comandos de voz, subtítulos en vivo, asistentes virtuales y herramientas de accesibilidad.

Es fundamental utilizar Speech cuando tu aplicación necesita interpretar lenguaje hablado, ya sea desde el micrófono en tiempo real o desde archivos de audio pregrabados. A diferencia de soluciones de terceros, Speech funciona con la infraestructura nativa de Apple, lo que garantiza mejor integración con el sistema operativo, mayor privacidad del usuario y la posibilidad de procesamiento on-device a partir de iOS 13, eliminando la dependencia de una conexión a Internet en muchos escenarios.

## Casos de uso principales

- **Dictado de texto en aplicaciones de notas o mensajería**: Permite a los usuarios redactar texto mediante voz, ideal para apps de productividad, editores de texto o plataformas de comunicación donde escribir puede ser incómodo o lento.

- **Comandos de voz para control de la interfaz**: Implementar navegación y acciones dentro de la app usando instrucciones habladas, como "siguiente página", "guardar documento" o "reproducir canción", mejorando drásticamente la accesibilidad.

- **Subtítulos en tiempo real para videollamadas o streaming**: Generar transcripciones en vivo durante conferencias, clases online o transmisiones en directo, haciendo el contenido accesible para personas con discapacidad auditiva.

- **Transcripción de grabaciones de audio**: Convertir entrevistas, podcasts, reuniones grabadas o notas de voz en texto editable, facilitando la búsqueda y organización de contenido.

- **Aplicaciones educativas de aprendizaje de idiomas**: Evaluar la pronunciación de los estudiantes comparando el texto reconocido con el texto esperado, utilizando los niveles de confianza para medir la precisión.

- **Herramientas de accesibilidad personalizadas**: Crear interfaces adaptadas para usuarios con movilidad reducida que dependen de la voz como método principal de interacción con sus dispositivos.

## Instalación y configuración

### Agregar el framework al proyecto

Speech es un framework nativo de Apple, por lo que no requiere instalación mediante gestores de paquetes. Simplemente importa el módulo en los archivos donde lo necesites:

```swift
import Speech
```

### Permisos requeridos en Info.plist

El framework Speech requiere **dos permisos** críticos que deben declararse en el archivo `Info.plist`. Sin ellos, la app se cerrará de forma inmediata al intentar acceder al reconocimiento de voz o al micrófono:

```xml
<!-- Permiso para reconocimiento de voz -->
<key>NSSpeechRecognitionUsageDescription</key>
<string>Esta app necesita acceso al reconocimiento de voz para transcribir tu audio a texto.</string>

<!-- Permiso para acceder al micrófono (solo si usas reconocimiento en tiempo real) -->
<key>NSMicrophoneUsageDescription</key>
<string>Esta app necesita acceso al micrófono para escuchar y transcribir tu voz en tiempo real.</string>
```

### Verificar disponibilidad y solicitar autorización

Antes de usar cualquier funcionalidad del framework, es obligatorio solicitar autorización al usuario:

```swift
import Speech

func solicitarPermisos() {
    SFSpeechRecognizer.requestAuthorization { estado in
        DispatchQueue.main.async {
            switch estado {
            case .authorized:
                print("Reconocimiento de voz autorizado")
            case .denied:
                print("El usuario denegó el acceso")
            case .restricted:
                print("Reconocimiento de voz restringido en este dispositivo")
            case .notDetermined:
                print("Permiso aún no determinado")
            @unknown default:
                print("Estado desconocido")
            }
        }
    }
}
```

### Compatibilidad

| Plataforma | Versión mínima |
|------------|---------------|
| iOS        | 10.0+         |
| macOS      | 10.15+        |
| watchOS    | (limitado)    |
| Reconocimiento on-device | iOS 13+ |

## Conceptos clave

### 1. SFSpeechRecognizer

Es la clase central del framework. Representa el motor de reconocimiento de voz para un idioma específico. Se encarga de procesar las solicitudes de reconocimiento y devolver los resultados. Puedes inicializarlo con un `Locale` específico para definir el idioma objetivo:

```swift
let reconocedor = SFSpeechRecognizer(locale: Locale(identifier: "es-ES"))
```

Es importante verificar su propiedad `isAvailable` antes de usarlo, ya que la disponibilidad puede cambiar según la conectividad de red o restricciones del dispositivo. Puedes observar cambios implementando el protocolo `SFSpeechRecognizerDelegate`.

### 2. SFSpeechRecognitionRequest

Es la clase base abstracta para las solicitudes de reconocimiento. Tiene dos subclases concretas:

- **`SFSpeechURLRecognitionRequest`**: Para reconocer audio desde archivos pregrabados (URLs locales o remotas).
- **`SFSpeechAudioBufferRecognitionRequest`**: Para reconocimiento en tiempo real, alimentando buffers de audio progresivamente.

### 3. SFSpeechRecognitionTask

Representa una tarea de reconocimiento en curso. Permite monitorear el progreso, recibir resultados parciales y cancelar o finalizar la operación cuando sea necesario. Es el objeto que devuelve `SFSpeechRecognizer` al iniciar un reconocimiento.

### 4. SFSpeechRecognitionResult

Contiene el resultado del reconocimiento, incluyendo la **mejor transcripción** (`bestTranscription`) y un array de **transcripciones alternativas** ordenadas por nivel de confianza. Cada resultado tiene una propiedad `isFinal` que indica si el motor ha terminado de procesar el audio.

### 5. SFTranscription y SFTranscriptionSegment

`SFTranscription` contiene el texto completo reconocido y un array de `SFTranscriptionSegment`. Cada segmento representa una palabra o fragmento individual con propiedades como: texto reconocido, nivel de confianza (0.0 a 1.0), marca de tiempo, duración y transcripciones alternativas por segmento.

### 6. Reconocimiento On-Device vs. Servidor

A partir de iOS 13, Apple introdujo el reconocimiento on-device. Puedes forzar el procesamiento local estableciendo `requiresOnDeviceRecognition = true` en la solicitud. Esto ofrece mayor privacidad y funciona sin Internet, aunque la precisión puede ser ligeramente menor y no todos los idiomas están soportados en modo local.

## Ejemplo básico

Este ejemplo muestra cómo transcribir un archivo de audio pregrabado:

```swift
import Speech

class TranscriptorBasico {
    
    private let reconocedor: SFSpeechRecognizer?
    
    init() {
        // Inicializar reconocedor para español de España
        reconocedor = SFSpeechRecognizer(locale: Locale(identifier: "es-ES"))
    }
    
    /// Transcribe un archivo de audio ubicado en el bundle de la app
    func transcribirArchivo(nombreArchivo: String, extension ext: String) {
        // Verificar que el reconocedor está disponible
        guard let reconocedor = reconocedor, reconocedor.isAvailable else {
            print("El reconocedor de voz no está disponible")
            return
        }
        
        // Obtener la URL del archivo de audio
        guard let urlAudio = Bundle.main.url(forResource: nombreArchivo, withExtension: ext) else {
            print("No se encontró el archivo de audio: \(nombreArchivo).\(ext)")
            return
        }
        
        // Crear la solicitud de reconocimiento desde URL
        let solicitud = SFSpeechURLRecognitionRequest(url: urlAudio)
        
        // Opcional: solicitar solo procesamiento local (iOS 13+)
        solicitud.requiresOnDeviceRecognition = false
        
        // Iniciar el reconocimiento
        reconocedor.recognitionTask(with: solicitud) { resultado, error in
            // Verificar si hubo error
            if let error = error {
                print("Error en reconocimiento: \(error.localizedDescription)")
                return
            }
            
            // Procesar resultado
            guard let resultado = resultado else { return }
            
            // Imprimir la mejor transcripción
            print("Transcripción: \(resultado.bestTranscription.formattedString)")
            
            // Verificar si el resultado es definitivo
            if resultado.isFinal {
                print("--- Transcripción completada ---")
                
                // Mostrar nivel de confianza por segmento
                for segmento in resultado.bestTranscription.segments {
                    print("'\(segmento.substring)' - Confianza: \(segmento.confidence)")
                }
            }
        }
    }
}

// Uso:
// let transcriptor = TranscriptorBasico()
// transcriptor.transcribirArchivo(nombreArchivo: "entrevista", extension: "m4a")
```

## Ejemplo intermedio

Este ejemplo implementa reconocimiento de voz en tiempo real usando el micrófono del dispositivo con `AVAudioEngine`:

```swift
import Speech
import AVFoundation

class ReconocedorVozEnTiempoReal {
    
    // MARK: - Propiedades
    
    private let reconocedor: SFSpeechRecognizer?
    private let motorAudio = AVAudioEngine()
    private var solicitud: SFSpeechAudioBufferRecognitionRequest?
    private var tarea: SFSpeechRecognitionTask?
    
    /// Closure que se ejecuta cada vez que se recibe texto reconocido
    var alRecibirTexto: ((String, Bool) -> Void)?
    
    /// Indica si el reconocimiento está activo
    var estaEscuchando: Bool {
        return motorAudio.isRunning
    }
    
    init(idioma: String = "es-MX") {
        reconocedor = SFSpeechRecognizer(locale: Locale(identifier: idioma))
    }
    
    // MARK: - Métodos públicos
    
    /// Solicita todos los permisos necesarios
    func solicitarPermisos(completado: @escaping (Bool) -> Void) {
        var permisoVoz = false
        var permisoMicrofono = false
        
        let grupo = DispatchGroup()
        
        // Solicitar permiso de reconocimiento de voz
        grupo.enter()
        SFSpeechRecognizer.requestAuthorization { estado in
            permisoVoz = (estado == .authorized)
            grupo.leave()
        }
        
        // Solicitar permiso de micrófono
        grupo.enter()
        AVAudioSession.sharedInstance().requestRecordPermission { autorizado in
            permisoMicrofono = autorizado
            grupo.leave()
        }
        
        grupo.notify(queue: .main) {
            completado(permisoVoz && permisoMicrofono)
        }
    }
    
    /// Inicia el reconocimiento de voz en tiempo real
    func iniciarEscucha() throws {
        // Cancelar tarea previa si existe
        detenerEscucha()
        
        // Configurar la sesión de audio
        let sesionAudio = AVAudioSession.sharedInstance()
        try sesionAudio.setCategory(.record, mode: .measurement, options: .duckOthers)
        try sesionAudio.setActive(true, options: .notifyOthersOnDeactivation)
        
        // Crear nueva solicitud de reconocimiento
        solicitud = SFSpeechAudioBufferRecognitionRequest()
        
        guard let solicitud = solicitud else {
            throw NSError(domain: "Speech", code: -1,
                         userInfo: [NSLocalizedDescriptionKey: "No se pudo crear la solicitud"])
        }
        
        // Configurar para recibir resultados parciales
        solicitud.shouldReportPartialResults = true
        
        // Habilitar puntuación automática (iOS 16+)
        if #available(iOS 16, *) {
            solicitud.addsPunctuation = true
        }
        
        // Obtener el nodo de entrada de audio
        let nodoEntrada = motorAudio.inputNode
        let formatoGrabacion = nodoEntrada.outputFormat(forBus: 0)
        
        // Instalar un tap para capturar audio del micrófono
        nodoEntrada.installTap(onBus: 0, bufferSize: 1024, format: formatoGrabacion) {
            [weak self] buffer, _ in
            // Alimentar el buffer de audio a la solicitud de reconocimiento
            self?.solicitud?.append(buffer)
        }
        
        // Iniciar el motor de audio
        motorAudio.prepare()
        try motorAudio.start()
        
        // Iniciar la tarea de reconocimiento
        guard let reconocedor = reconocedor else {
            throw NSError(domain: "Speech", code: -2,
                         userInfo: [NSLocalizedDescriptionKey: "Reconocedor no disponible"])
        }
        
        tarea = reconocedor.recognitionTask(with: solicitud) { [weak self] resultado, error in
            var esFinal = false
            
            if let resultado = resultado {
                let texto = resultado.bestTranscription.formattedString
                esFinal = resultado.isFinal
                
                // Notificar el texto reconocido en el hilo principal
                DispatchQueue.main.async {
                    self?.alRecibirTexto?(texto, esFinal)
                }
            }
            
            // Si hay error o el resultado es final, detener
            if error != nil || esFinal {
                self?.detenerEscucha()
            }
        }
        
        print("Escuchando... Habla ahora.")
    }
    
    /// Detiene el reconocimiento de voz
    func detenerEscucha() {
        // Detener el motor de audio
        if motorAudio.isRunning {
            motorAudio.stop()
            motorAudio.inputNode.removeTap(onBus: 0)
        }
        
        // Finalizar la solicitud y la tarea
        solicitud?.endAudio()
        solicitud = nil
        
        tarea?.cancel()
        tarea = nil
    }
}

// MARK: - Uso del reconocedor

/*
let reconocedor = ReconocedorVozEnTiempoReal(idioma: "es-MX")

reconocedor.solicitarPermisos { autorizado in
    guard autorizado else {
        print("Permisos denegados")
        