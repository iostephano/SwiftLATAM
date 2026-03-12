---
sidebar_position: 1
title: Network
---

# Network

## ¿Qué es Network?

**Network** (también conocido como `Network.framework`) es el framework moderno de Apple para establecer y gestionar conexiones de red a nivel de transporte. Introducido en iOS 12 y macOS 10.14, fue diseñado como el reemplazo directo de las antiguas APIs basadas en sockets BSD y las clases de `CFNetwork` de bajo nivel. A diferencia de `URLSession`, que opera a nivel de protocolo de aplicación (HTTP/HTTPS), Network framework trabaja directamente con los protocolos de transporte como **TCP**, **UDP**, **TLS** y **QUIC**, ofreciendo un control granular sobre las conexiones de red.

Este framework proporciona una arquitectura completamente asíncrona y orientada a eventos, que se integra de forma nativa con Grand Central Dispatch (GCD). Permite a los desarrolladores crear tanto clientes como servidores de red, monitorizar cambios en la conectividad del dispositivo, seleccionar interfaces de red específicas (Wi-Fi, celular, Ethernet) y gestionar la seguridad de las conexiones de forma declarativa. Es la herramienta ideal cuando necesitas ir más allá de las peticiones HTTP estándar.

Deberías usar Network framework cuando tu aplicación requiera comunicación en tiempo real mediante sockets (chats, juegos multijugador), cuando necesites implementar protocolos personalizados sobre TCP o UDP, cuando quieras monitorizar el estado de la red de forma eficiente con `NWPathMonitor`, o cuando necesites un control preciso sobre los parámetros de conexión como timeouts, interfaces preferidas o configuración TLS específica.

## Casos de uso principales

- **Chat en tiempo real**: Establecer conexiones TCP/UDP persistentes para enviar y recibir mensajes instantáneamente entre dispositivos, sin la sobrecarga del protocolo HTTP.

- **Monitorización del estado de red**: Detectar cambios en la conectividad del dispositivo (Wi-Fi, datos móviles, sin conexión) para adaptar el comportamiento de la aplicación en tiempo real utilizando `NWPathMonitor`.

- **Juegos multijugador locales o en red**: Crear conexiones de baja latencia mediante UDP para sincronizar el estado del juego entre jugadores con la mínima demora posible.

- **Protocolos personalizados**: Implementar protocolos de comunicación propietarios o estándar no HTTP (MQTT, protocolos industriales IoT, protocolos de domótica) sobre TCP o UDP.

- **Transferencia de archivos peer-to-peer**: Enviar archivos directamente entre dispositivos en la misma red local sin necesidad de un servidor intermediario, aprovechando Bonjour para el descubrimiento de servicios.

- **Servidores locales embebidos**: Crear un listener TCP dentro de la app que acepte conexiones entrantes, útil para depuración, streaming local o integración con dispositivos IoT.

## Instalación y configuración

### Agregar al proyecto

Network framework viene incluido de serie en el SDK de Apple. **No requiere instalación externa** ni dependencias adicionales mediante Swift Package Manager, CocoaPods o Carthage.

### Import necesario

```swift
import Network
```

### Permisos en Info.plist

Para la mayoría de operaciones de red estándar, no se necesitan permisos especiales. Sin embargo, hay escenarios que sí los requieren:

```xml
<!-- Necesario si usas Bonjour para descubrimiento de servicios locales -->
<key>NSBonjourServices</key>
<array>
    <string>_miservicio._tcp</string>
</array>

<!-- Necesario si accedes a la red local en iOS 14+ -->
<key>NSLocalNetworkUsageDescription</key>
<string>Esta app necesita acceder a la red local para descubrir dispositivos cercanos.</string>
```

### Capacidades del proyecto (Capabilities)

Si tu app actúa como servidor (usando `NWListener`), habilita en Xcode:

1. Ve a tu **Target** → **Signing & Capabilities**.
2. Si es una app macOS, habilita **App Sandbox** → **Incoming Connections (Server)** y **Outgoing Connections (Client)**.
3. Para iOS, generalmente no se necesitan capabilities adicionales más allá de los permisos del `Info.plist`.

### Compatibilidad

| Plataforma | Versión mínima |
|---|---|
| iOS | 12.0+ |
| macOS | 10.14+ |
| tvOS | 12.0+ |
| watchOS | 5.0+ |
| Mac Catalyst | 13.0+ |

## Conceptos clave

### 1. NWConnection

Es la clase central del framework. Representa una conexión bidireccional entre tu aplicación y un endpoint remoto. Puede configurarse para usar TCP, UDP, TLS o WebSocket. Cada conexión tiene un **ciclo de vida** con estados definidos: `setup` → `preparing` → `ready` → `failed`/`cancelled`. Toda la comunicación se realiza de forma asíncrona.

```swift
// Una conexión es siempre hacia un endpoint con parámetros específicos
let connection = NWConnection(host: "api.ejemplo.com", port: 443, using: .tls)
```

### 2. NWListener

Actúa como un **servidor** que escucha conexiones entrantes en un puerto específico. Cuando un cliente se conecta, el listener genera una nueva `NWConnection` para manejar esa comunicación de forma independiente. Es esencial para crear servidores locales, servicios peer-to-peer o cualquier componente que deba aceptar conexiones.

### 3. NWPathMonitor

Es un observador reactivo del estado de conectividad del dispositivo. Informa continuamente sobre los cambios en la ruta de red: si hay conexión disponible, qué tipo de interfaz se está usando (Wi-Fi, celular, Ethernet, loopback), si la conexión es costosa (datos móviles) o restringida. Reemplaza eficazmente a `SCNetworkReachability`.

### 4. NWParameters

Define **cómo** se establece una conexión: qué protocolo de transporte usar, configuración TLS/DTLS, restricciones de interfaz, opciones de proxy y más. Es el objeto de configuración que se pasa tanto a `NWConnection` como a `NWListener`.

### 5. NWEndpoint

Representa el **destino** de una conexión. Puede ser una dirección host con puerto (`.hostPort`), un servicio Bonjour (`.service`), una URL (`.url`) o un endpoint Unix (`.unix`). Permite abstraer diferentes formas de identificar un destino de red.

### 6. NWProtocolOptions y la pila de protocolos

Network framework modela la red como una **pila de protocolos** configurable. Puedes apilar protocolos (por ejemplo, TLS sobre TCP) y configurar cada capa individualmente. Esto incluye opciones de TCP (como `noDelay`), configuraciones de TLS (certificados, versión mínima) y framing personalizado para protocolos propios.

## Ejemplo básico

Este ejemplo muestra cómo monitorizar el estado de la red, el caso de uso más común y sencillo de Network framework:

```swift
import Network

// MARK: - Monitor básico de conectividad de red

class NetworkMonitor {
    
    // Instancia del monitor de rutas de red
    private let monitor = NWPathMonitor()
    
    // Cola dedicada para recibir actualizaciones (nunca usar main queue)
    private let monitorQueue = DispatchQueue(label: "com.miapp.networkmonitor")
    
    // Estado actual de la conexión
    private(set) var isConnected: Bool = false
    
    // Tipo de conexión actual
    private(set) var connectionType: String = "Desconocida"
    
    /// Inicia el monitoreo de la red
    func startMonitoring() {
        // El handler se ejecuta cada vez que cambia el estado de la red
        monitor.pathUpdateHandler = { [weak self] path in
            guard let self = self else { return }
            
            // Verificar si hay conexión disponible
            self.isConnected = (path.status == .satisfied)
            
            // Determinar el tipo de interfaz activa
            if path.usesInterfaceType(.wifi) {
                self.connectionType = "Wi-Fi"
            } else if path.usesInterfaceType(.cellular) {
                self.connectionType = "Datos móviles"
            } else if path.usesInterfaceType(.wiredEthernet) {
                self.connectionType = "Ethernet"
            } else {
                self.connectionType = "Otra"
            }
            
            // Información adicional útil
            let isCostly = path.isExpensive    // true si es conexión de datos móviles
            let isLimited = path.isConstrained // true si modo de datos reducidos
            
            print("📡 Estado de red actualizado:")
            print("   Conectado: \(self.isConnected)")
            print("   Tipo: \(self.connectionType)")
            print("   Conexión costosa: \(isCostly)")
            print("   Conexión restringida: \(isLimited)")
        }
        
        // Iniciar el monitor en su cola dedicada
        monitor.start(queue: monitorQueue)
        print("🟢 Monitor de red iniciado")
    }
    
    /// Detiene el monitoreo de la red
    func stopMonitoring() {
        monitor.cancel()
        print("🔴 Monitor de red detenido")
    }
}

// --- Uso ---
let networkMonitor = NetworkMonitor()
networkMonitor.startMonitoring()

// Más adelante, cuando ya no se necesite:
// networkMonitor.stopMonitoring()
```

## Ejemplo intermedio

Este ejemplo implementa un **cliente TCP** que se conecta a un servidor, envía datos y recibe respuestas. Representa un caso real de comunicación con un servidor de chat o un servicio personalizado:

```swift
import Network

// MARK: - Cliente TCP reutilizable

class TCPClient {
    
    private var connection: NWConnection?
    private let queue = DispatchQueue(label: "com.miapp.tcpclient")
    
    // Callbacks para notificar al consumidor
    var onConnected: (() -> Void)?
    var onDataReceived: ((Data) -> Void)?
    var onError: ((Error) -> Void)?
    var onDisconnected: (() -> Void)?
    
    /// Establece conexión TCP con el servidor indicado
    /// - Parameters:
    ///   - host: Dirección del servidor (IP o dominio)
    ///   - port: Puerto del servidor
    ///   - useTLS: Si debe usar conexión segura TLS
    func connect(to host: String, port: UInt16, useTLS: Bool = false) {
        // Seleccionar parámetros según si queremos TLS o no
        let parameters: NWParameters = useTLS ? .tls : .tcp
        
        // Configurar opciones TCP específicas
        if let tcpOptions = parameters.defaultProtocolStack
            .transportProtocol as? NWProtocolTCP.Options {
            tcpOptions.noDelay = true                    // Desactivar algoritmo de Nagle
            tcpOptions.connectionTimeout = 10            // Timeout de 10 segundos
            tcpOptions.enableKeepalive = true            // Mantener conexión activa
            tcpOptions.keepaliveInterval = 30            // Ping cada 30 segundos
        }
        
        // Crear la conexión
        let nwHost = NWEndpoint.Host(host)
        let nwPort = NWEndpoint.Port(rawValue: port)!
        connection = NWConnection(host: nwHost, port: nwPort, using: parameters)
        
        // Observar cambios de estado de la conexión
        connection?.stateUpdateHandler = { [weak self] state in
            switch state {
            case .setup:
                print("⚙️ Configurando conexión...")
                
            case .preparing:
                print("🔄 Preparando conexión...")
                
            case .ready:
                print("✅ Conectado a \(host):\(port)")
                DispatchQueue.main.async {
                    self?.onConnected?()
                }
                // Iniciar la escucha de datos entrantes
                self?.receiveData()
                
            case .waiting(let error):
                print("⏳ Esperando conexión... Error: \(error.localizedDescription)")
                
            case .failed(let error):
                print("❌ Conexión fallida: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    self?.onError?(error)
                }
                // Limpiar la conexión fallida
                self?.connection = nil
                
            case .cancelled:
                print("🚫 Conexión cancelada")
                DispatchQueue.main.async {
                    self?.onDisconnected?()
                }
                self?.connection = nil
                
            @unknown default:
                break
            }
        }
        
        // Iniciar el proceso de conexión
        connection?.start(queue: queue)
    }
    
    /// Envía una cadena de texto al servidor
    /// - Parameter message: Texto a enviar
    func send(_ message: String) {
        guard let data = message.data(using: .utf8) else {
            print("⚠️ No se pudo codificar el mensaje")
            return
        }
        send(data: data)
    }
    
    /// Envía datos binarios al servidor
    /// - Parameter data: Datos a enviar
    func send(data: Data) {
        connection?.send(
            content: data,
            contentContext: .defaultMessage,
            isComplete: true,           // Indica que este envío es un mensaje completo
            completion: .contentProcessed { error in
                if let error = error {
                    print("❌ Error al enviar: \(error.localizedDescription)")
                } else {
                    print("📤 Datos enviados: \(data.count) bytes")
                }
            }
        )
    }
    
    /// Escucha datos entrantes de forma recursiva
    private func receiveData() {
        connection?.receive(
            minimumIncompleteLength: 1,     // Mínimo 1 byte para activar el callback
            maximumLength: 65536            // Máximo 64 KB por lectura
        ) { [weak self] content, contentContext, isComplete, error in
            
            // Procesar datos recibidos
            if let data = content, !data.isEmpty {
                print("📥 Datos recibidos: \(data.count) bytes")
                DispatchQueue.main.async {
                    self?.onDataReceived?(data)
                }
            }
            
            // Si hay error, notificar
            if let error = error {
                print("❌ Error al recibir: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    self?.onError?(error)
                }
                return
            }
            
            // Si isComplete es true y no hay más datos, el servidor cerró la conexión
            if isComplete {
                print("🔚 El servidor cerró la conexión")
                self?.disconnect()
                return
            }
            
            // Seguir escuchando más datos (patrón recursivo)
            self?.receiveData()
        }
    }
    
    /// Cierra la conexión de forma ordenada
    func disconnect() {
        connection?.cancel()
    }
}

// MARK: - Uso del cliente TCP

let client = TCPClient()

client.onConnected = {
    print("🎉 ¡Listo para enviar mensajes!")
    client.send("Hola servidor, soy un cliente iOS\n")
}

client.onDataReceived = { data in
    if let text = String(data