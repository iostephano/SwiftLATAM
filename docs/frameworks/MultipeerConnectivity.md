---
sidebar_position: 1
title: MultipeerConnectivity
---

# MultipeerConnectivity

## ¿Qué es MultipeerConnectivity?

**MultipeerConnectivity** es un framework de Apple que permite la comunicación directa entre dispositivos cercanos sin necesidad de un servidor centralizado ni conexión a Internet. Utiliza una combinación de tecnologías como **Wi-Fi punto a punto**, **Bluetooth** y **redes locales** para descubrir dispositivos próximos y establecer sesiones de comunicación entre ellos. Fue introducido en iOS 7 y está disponible también en macOS y tvOS.

Este framework es especialmente útil cuando se necesita crear experiencias colaborativas o de intercambio de datos en entornos donde la conectividad a Internet no está garantizada. Piensa en un aula donde los estudiantes comparten archivos, un juego multijugador local en una cabaña sin señal, o una aplicación de campo donde los equipos sincronizan datos en tiempo real sin depender de infraestructura de red.

MultipeerConnectivity abstrae toda la complejidad de la comunicación de bajo nivel (sockets, protocolos de descubrimiento, emparejamiento Bluetooth) y expone una API de alto nivel basada en conceptos simples: **peers** (dispositivos participantes), **sessions** (conexiones activas), **advertisers** (dispositivos que se anuncian) y **browsers** (dispositivos que buscan otros). Esta abstracción permite que un desarrollador implemente comunicación peer-to-peer robusta en relativamente pocas líneas de código.

## Casos de uso principales

- **Juegos multijugador locales**: Permite que varios jugadores en la misma habitación se conecten y jueguen sin necesidad de Wi-Fi ni datos móviles. Ideal para juegos de mesa digitales, trivias grupales o juegos cooperativos.

- **Transferencia de archivos entre dispositivos**: Compartir fotos, documentos, contactos o cualquier tipo de archivo directamente entre iPhones, iPads o Macs cercanos, similar a como funciona AirDrop internamente.

- **Pizarras colaborativas en tiempo real**: Aplicaciones donde múltiples usuarios dibujan, escriben o interactúan sobre un lienzo compartido simultáneamente, viendo los cambios de los demás en tiempo real.

- **Chat offline**: Sistemas de mensajería que funcionan sin Internet, útiles en conferencias, eventos masivos o zonas rurales donde la cobertura es limitada o inexistente.

- **Sincronización de datos en campo**: Equipos de trabajo en terreno (investigadores, socorristas, técnicos) que necesitan compartir información recopilada sin depender de conectividad, sincronizando datos entre sus dispositivos al estar en proximidad.

- **Encuestas y votaciones en vivo**: Aplicaciones para aulas o reuniones donde un presentador envía preguntas y los asistentes responden desde sus dispositivos, todo procesado localmente sin servidor.

## Instalación y configuración

### Agregar el framework al proyecto

MultipeerConnectivity es un framework nativo de Apple incluido en el SDK de iOS, por lo que **no requiere instalación de dependencias externas** mediante CocoaPods, SPM u otro gestor. Solo necesitas importarlo en los archivos donde lo utilices:

```swift
import MultipeerConnectivity
```

### Configuración de Info.plist

Desde **iOS 14**, Apple requiere que declares el uso de la red local y servicios Bonjour en tu archivo `Info.plist`. Sin estas entradas, tu app no podrá descubrir ni anunciarse a otros dispositivos, y en muchos casos crasheará silenciosamente o simplemente no funcionará.

```xml
<!-- Descripción del uso de la red local (obligatorio iOS 14+) -->
<key>NSLocalNetworkUsageDescription</key>
<string>Esta app necesita acceso a la red local para descubrir y conectarse con dispositivos cercanos.</string>

<!-- Declaración del tipo de servicio Bonjour (obligatorio) -->
<key>NSBonjourServices</key>
<array>
    <string>_mi-servicio._tcp</string>
    <string>_mi-servicio._udp</string>
</array>
```

> ⚠️ **Importante**: El nombre del servicio Bonjour debe coincidir exactamente con el `serviceType` que utilices en tu código. Debe tener entre 1 y 15 caracteres, contener solo letras minúsculas ASCII, números y guiones, y no puede comenzar ni terminar con un guion.

### Permisos adicionales

- **Bluetooth**: En iOS 13+ se requiere `NSBluetoothAlwaysUsageDescription` si tu app puede utilizar Bluetooth para la conexión entre peers.

```xml
<key>NSBluetoothAlwaysUsageDescription</key>
<string>Esta app utiliza Bluetooth para conectarse con dispositivos cercanos.</string>
```

### Plataformas compatibles

| Plataforma | Versión mínima |
|------------|---------------|
| iOS        | 7.0+          |
| macOS      | 10.10+        |
| tvOS       | 10.0+         |
| visionOS   | 1.0+          |

## Conceptos clave

### 1. MCPeerID — Identidad del dispositivo

Cada dispositivo participante se identifica mediante un `MCPeerID`. Este objeto encapsula un nombre visible (generalmente el nombre del dispositivo o del usuario) que se muestra a otros peers durante el descubrimiento. Es el fundamento de toda la comunicación: sin un `MCPeerID`, no puedes crear sesiones, anunciarte ni buscar otros dispositivos.

```swift
let miPeerID = MCPeerID(displayName: UIDevice.current.name)
```

### 2. MCSession — La sesión de comunicación

`MCSession` gestiona la conexión activa entre dos o más peers. Es el canal a través del cual fluyen todos los datos: mensajes, archivos y streams. Una sesión puede albergar hasta **8 peers conectados** simultáneamente (sin contar al peer local). Implementa el patrón delegado mediante `MCSessionDelegate` para notificar cambios de estado, recepción de datos y errores.

### 3. MCNearbyServiceAdvertiser — Anunciarse a otros

El advertiser hace que tu dispositivo sea **visible** para otros que estén buscando. Emite una señal con tu `serviceType` y opcionalmente un diccionario `discoveryInfo` con metadatos limitados (máximo ~400 bytes en total). Cuando otro peer quiere conectarse, el advertiser recibe una invitación que puede aceptar o rechazar.

### 4. MCNearbyServiceBrowser — Buscar dispositivos

El browser **escanea** activamente la red en busca de peers que estén anunciándose con un `serviceType` compatible. A medida que encuentra dispositivos, notifica a su delegado, permitiéndote presentar una lista al usuario o conectarte automáticamente. Es el complemento natural del advertiser.

### 5. MCBrowserViewController — Interfaz predeterminada

Apple proporciona un controlador de vista listo para usar que muestra los peers disponibles y permite al usuario seleccionar con cuáles conectarse. Es extremadamente útil para prototipos rápidos, aunque en aplicaciones de producción generalmente se prefiere una UI personalizada.

### 6. Tipos de envío de datos

MultipeerConnectivity ofrece tres mecanismos de transmisión:

- **`send(_:toPeers:with:)`**: Envía un objeto `Data` a uno o más peers. Soporta modo `.reliable` (garantiza entrega, como TCP) y `.unreliable` (más rápido, sin garantía, como UDP).
- **`sendResource(at:withName:toPeer:)`**: Envía archivos grandes de forma asíncrona con seguimiento de progreso mediante `Progress`.
- **`startStream(withName:toPeer:)`**: Abre un `OutputStream` para enviar datos de forma continua (ideal para audio o video en tiempo real).

## Ejemplo básico

Este ejemplo muestra la configuración mínima para descubrir peers y enviar un mensaje de texto:

```swift
import MultipeerConnectivity

// MARK: - Configuración básica de MultipeerConnectivity
class ConexionSimple: NSObject {
    
    // Tipo de servicio: identificador único para tu app (máx. 15 caracteres)
    private let tipoServicio = "mi-app-demo"
    
    // Identificador de este dispositivo en la red
    private let miPeerID = MCPeerID(displayName: UIDevice.current.name)
    
    // Sesión de comunicación
    private var sesion: MCSession
    
    // Componente que anuncia este dispositivo a otros
    private var advertiser: MCNearbyServiceAdvertiser
    
    // Componente que busca otros dispositivos
    private var browser: MCNearbyServiceBrowser
    
    override init() {
        // Crear la sesión con encriptación requerida
        self.sesion = MCSession(
            peer: miPeerID,
            securityIdentity: nil,
            encryptionPreference: .required
        )
        
        // Configurar el advertiser sin información adicional de descubrimiento
        self.advertiser = MCNearbyServiceAdvertiser(
            peer: miPeerID,
            discoveryInfo: nil,
            serviceType: tipoServicio
        )
        
        // Configurar el browser
        self.browser = MCNearbyServiceBrowser(
            peer: miPeerID,
            serviceType: tipoServicio
        )
        
        super.init()
        
        // Asignar delegados
        self.sesion.delegate = self
        self.advertiser.delegate = self
        self.browser.delegate = self
    }
    
    /// Inicia el descubrimiento y anuncio simultáneamente
    func iniciarConexion() {
        advertiser.startAdvertisingPeer()
        browser.startBrowsingForPeers()
        print("🔍 Buscando dispositivos cercanos...")
    }
    
    /// Detiene toda actividad de red
    func detenerConexion() {
        advertiser.stopAdvertisingPeer()
        browser.stopBrowsingForPeers()
        sesion.disconnect()
        print("🛑 Conexión detenida")
    }
    
    /// Envía un mensaje de texto a todos los peers conectados
    func enviarMensaje(_ texto: String) {
        // Verificar que hay peers conectados
        guard !sesion.connectedPeers.isEmpty else {
            print("⚠️ No hay peers conectados")
            return
        }
        
        // Convertir el texto a Data
        guard let datos = texto.data(using: .utf8) else { return }
        
        do {
            // Enviar de forma confiable a todos los peers
            try sesion.send(datos, toPeers: sesion.connectedPeers, with: .reliable)
            print("✅ Mensaje enviado: \(texto)")
        } catch {
            print("❌ Error al enviar: \(error.localizedDescription)")
        }
    }
}

// MARK: - MCSessionDelegate
extension ConexionSimple: MCSessionDelegate {
    
    /// Se llama cuando cambia el estado de conexión de un peer
    func session(_ session: MCSession, peer peerID: MCPeerID,
                 didChange state: MCSessionState) {
        switch state {
        case .notConnected:
            print("❌ Desconectado de: \(peerID.displayName)")
        case .connecting:
            print("⏳ Conectando con: \(peerID.displayName)")
        case .connected:
            print("✅ Conectado con: \(peerID.displayName)")
        @unknown default:
            print("⚠️ Estado desconocido")
        }
    }
    
    /// Se llama cuando se reciben datos de un peer
    func session(_ session: MCSession, didReceive data: Data,
                 fromPeer peerID: MCPeerID) {
        if let mensaje = String(data: data, encoding: .utf8) {
            print("📩 Mensaje de \(peerID.displayName): \(mensaje)")
        }
    }
    
    // Métodos requeridos del protocolo (implementación mínima)
    func session(_ session: MCSession,
                 didReceive stream: InputStream,
                 withName streamName: String,
                 fromPeer peerID: MCPeerID) {}
    
    func session(_ session: MCSession,
                 didStartReceivingResourceWithName resourceName: String,
                 fromPeer peerID: MCPeerID,
                 with progress: Progress) {}
    
    func session(_ session: MCSession,
                 didFinishReceivingResourceWithName resourceName: String,
                 fromPeer peerID: MCPeerID,
                 at localURL: URL?,
                 withError error: Error?) {}
}

// MARK: - MCNearbyServiceAdvertiserDelegate
extension ConexionSimple: MCNearbyServiceAdvertiserDelegate {
    
    /// Se llama cuando otro peer nos envía una invitación para conectarse
    func advertiser(_ advertiser: MCNearbyServiceAdvertiser,
                    didReceiveInvitationFromPeer peerID: MCPeerID,
                    withContext context: Data?,
                    invitationHandler: @escaping (Bool, MCSession?) -> Void) {
        // Aceptar automáticamente todas las invitaciones
        print("📨 Invitación recibida de: \(peerID.displayName)")
        invitationHandler(true, sesion)
    }
}

// MARK: - MCNearbyServiceBrowserDelegate
extension ConexionSimple: MCNearbyServiceBrowserDelegate {
    
    /// Se llama cuando se descubre un nuevo peer
    func browser(_ browser: MCNearbyServiceBrowser,
                 foundPeer peerID: MCPeerID,
                 withDiscoveryInfo info: [String: String]?) {
        print("🔍 Peer encontrado: \(peerID.displayName)")
        // Enviar invitación automáticamente con timeout de 30 segundos
        browser.invitePeer(peerID, to: sesion, withContext: nil, timeout: 30)
    }
    
    /// Se llama cuando un peer deja de estar disponible
    func browser(_ browser: MCNearbyServiceBrowser,
                 lostPeer peerID: MCPeerID) {
        print("👋 Peer perdido: \(peerID.displayName)")
    }
}
```

## Ejemplo intermedio

Un chat grupal funcional con serialización de mensajes usando `Codable`:

```swift
import MultipeerConnectivity
import Foundation

// MARK: - Modelo de mensaje serializable
struct MensajeChat: Codable, Identifiable {
    let id: UUID
    let remitente: String
    let contenido: String
    let timestamp: Date
    let tipo: TipoMensaje
    
    enum TipoMensaje: String, Codable {
        case texto
        case imagen
        case sistema // Mensajes como "X se ha unido"
    }
    
    init(remitente: String, contenido: String, tipo: TipoMensaje = .texto) {
        self.id = UUID()
        self.remitente = remitente
        self.contenido = contenido
        self.timestamp = Date()
        self.tipo = tipo
    }
}

// MARK: - Protocolo delegado personalizado
protocol ChatMultipeerDelegate: AnyObject {
    func chatDidReceiveMessage(_ mensaje: MensajeChat)
    func chatPeerDidChangeState(peerName: String, state: MCSessionState)
    func chatDidReceiveFile(nombre: String, localURL: URL, dePeer: String)
}

// MARK: - Servicio de chat multipeer
class ChatMultipeerService: NSObject {
    
    // MARK: - Propiedades
    private let ti