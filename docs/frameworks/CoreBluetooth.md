---
sidebar_position: 1
title: CoreBluetooth
---

# CoreBluetooth

## ¿Qué es CoreBluetooth?

CoreBluetooth es el framework de Apple que permite a las aplicaciones iOS, macOS, watchOS y tvOS comunicarse con dispositivos que utilizan la tecnología **Bluetooth Low Energy (BLE)**, también conocida como Bluetooth 4.0 o Bluetooth Smart. Este framework proporciona las abstracciones necesarias para interactuar con periféricos BLE sin necesidad de conocer los detalles de bajo nivel del protocolo de transporte, ofreciendo una API orientada a objetos clara y bien estructurada.

El framework opera bajo el modelo **Central-Periférico** del estándar BLE. Una aplicación puede actuar como **Central** (descubre y se conecta a periféricos que publican servicios) o como **Periférico** (publica servicios y responde a solicitudes de centrales). Esta dualidad permite crear desde aplicaciones que leen datos de un sensor cardíaco hasta sistemas de comunicación entre dispositivos Apple de forma completamente descentralizada.

CoreBluetooth es la opción indicada cuando necesitas comunicarte con hardware BLE externo — wearables, sensores IoT, dispositivos médicos, cerraduras inteligentes, beacons, o cualquier accesorio que implemente el estándar GATT (Generic Attribute Profile). Si tu proyecto requiere transferir pequeñas cantidades de datos de forma eficiente y con bajo consumo energético, CoreBluetooth es el framework nativo que Apple proporciona para este propósito.

## Casos de uso principales

- **Dispositivos de salud y fitness**: Conexión con pulseras de actividad, monitores de frecuencia cardíaca, glucómetros, oxímetros de pulso y básculas inteligentes que transmiten datos de salud mediante perfiles BLE estandarizados.

- **Domótica e IoT**: Control de luces inteligentes, termostatos, cerraduras electrónicas y sensores ambientales (temperatura, humedad, calidad del aire) desde una aplicación móvil.

- **Localización y proximidad con beacons**: Detección de beacons BLE para experiencias contextuales en museos, tiendas minoristas, estadios deportivos o sistemas de navegación en interiores.

- **Transferencia de datos entre dispositivos Apple**: Comunicación peer-to-peer entre iPhones, iPads o Macs para compartir información sin necesidad de conexión a Internet, útil en aplicaciones colaborativas o juegos multijugador locales.

- **Periféricos de entrada personalizados**: Integración con mandos de juego BLE, teclados especializados, lectores de códigos de barras portátiles o instrumentos musicales MIDI inalámbricos.

- **Firmware y configuración de hardware**: Aplicaciones companion que permiten actualizar el firmware (OTA/DFU), configurar parámetros o diagnosticar el estado de dispositivos electrónicos embebidos mediante BLE.

## Instalación y configuración

### Agregar el framework al proyecto

CoreBluetooth viene incluido de forma nativa en el SDK de iOS, por lo que **no requiere instalación mediante gestores de paquetes**. Solo necesitas importar el módulo en los archivos donde lo utilices:

```swift
import CoreBluetooth
```

### Permisos en Info.plist

Desde iOS 13, Apple exige declarar el propósito del uso de Bluetooth. Debes agregar las siguientes claves en tu archivo `Info.plist`:

```xml
<!-- Obligatorio: describe por qué la app usa Bluetooth -->
<key>NSBluetoothAlwaysUsageDescription</key>
<string>Esta aplicación necesita Bluetooth para conectarse con tu dispositivo de salud y sincronizar tus datos de actividad.</string>

<!-- Requerido solo si soportas iOS 12 o anterior -->
<key>NSBluetoothPeripheralUsageDescription</key>
<string>Esta aplicación necesita acceder a periféricos Bluetooth para leer datos de sensores.</string>
```

### Capability de Background Mode (opcional)

Si necesitas que la comunicación BLE continúe cuando la app está en segundo plano, activa el **Background Mode** en las capabilities del target:

1. Selecciona tu target en Xcode → pestaña **Signing & Capabilities**.
2. Pulsa **+ Capability** y añade **Background Modes**.
3. Marca las opciones según tu necesidad:
   - **Uses Bluetooth LE accessories** (rol Central en background).
   - **Acts as a Bluetooth LE accessory** (rol Periférico en background).

En tu `Info.plist` esto se refleja como:

```xml
<key>UIBackgroundModes</key>
<array>
    <string>bluetooth-central</string>
    <string>bluetooth-peripheral</string>
</array>
```

### Requisitos mínimos

| Plataforma | Versión mínima |
|-----------|---------------|
| iOS       | 5.0 (BLE básico), 13.0+ (recomendado) |
| macOS     | 10.9          |
| watchOS   | 2.0           |
| tvOS      | 9.0           |

## Conceptos clave

### 1. Central y Periférico

Son los dos roles fundamentales en BLE. El **Central** (`CBCentralManager`) es quien escanea, descubre y se conecta a periféricos. El **Periférico** (`CBPeripheralManager`) es quien publica servicios y espera conexiones. Tu app puede adoptar uno o ambos roles simultáneamente.

### 2. Servicio (CBService)

Un servicio es una colección de datos y comportamientos asociados que describe una funcionalidad específica de un periférico. Se identifica mediante un **UUID**. Por ejemplo, el servicio de frecuencia cardíaca tiene el UUID estándar `0x180D`. Un periférico puede ofrecer múltiples servicios.

### 3. Característica (CBCharacteristic)

Cada servicio contiene una o más características, que son los valores de datos concretos. Una característica tiene propiedades que definen cómo puede interactuarse con ella: **lectura** (`.read`), **escritura** (`.write`, `.writeWithoutResponse`) y **notificación** (`.notify`, `.indicate`). El servicio de frecuencia cardíaca, por ejemplo, tiene la característica "Heart Rate Measurement" con UUID `0x2A37`.

### 4. UUID (CBUUID)

Cada servicio y característica se identifica con un UUID. Los perfiles BLE estandarizados por el Bluetooth SIG usan UUIDs de **16 bits** (como `"180D"`). Los servicios y características personalizados usan UUIDs de **128 bits** (como `"E621E1F8-C36C-495A-93FC-0C247A3E6E5F"`).

### 5. Descriptores (CBDescriptor)

Los descriptores proporcionan metadatos adicionales sobre una característica, como su descripción legible por humanos o el formato de los datos. El descriptor más usado es el **Client Characteristic Configuration Descriptor (CCCD)**, que habilita o deshabilita las notificaciones.

### 6. Estado de restauración (State Restoration)

CoreBluetooth soporta **restauración de estado**: si el sistema termina tu app mientras está en segundo plano, puede relanzarla y restaurar los objetos `CBCentralManager` o `CBPeripheralManager` con sus conexiones activas. Esto es crítico para apps que mantienen conexiones BLE prolongadas.

## Ejemplo básico

Este ejemplo muestra cómo crear un Central Manager, verificar el estado de Bluetooth y escanear periféricos cercanos:

```swift
import CoreBluetooth

/// Clase básica que demuestra el escaneo de periféricos BLE
class BluetoothScanner: NSObject, CBCentralManagerDelegate {
    
    // El Central Manager es el punto de entrada para operaciones BLE como Central
    private var centralManager: CBCentralManager!
    
    override init() {
        super.init()
        // Inicializar el Central Manager con self como delegado
        // queue: nil indica que los callbacks se ejecutarán en la cola principal
        centralManager = CBCentralManager(delegate: self, queue: nil)
    }
    
    // MARK: - CBCentralManagerDelegate
    
    /// Se llama cada vez que el estado del Central Manager cambia
    /// Este es el PRIMER método que se invoca tras la inicialización
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        switch central.state {
        case .poweredOn:
            print("✅ Bluetooth está encendido y disponible")
            // Solo podemos escanear cuando el estado es .poweredOn
            iniciarEscaneo()
            
        case .poweredOff:
            print("⚠️ Bluetooth está apagado. Solicita al usuario que lo encienda.")
            
        case .unauthorized:
            print("🚫 La app no tiene permisos para usar Bluetooth")
            
        case .unsupported:
            print("❌ Este dispositivo no soporta Bluetooth Low Energy")
            
        case .resetting:
            print("🔄 El sistema Bluetooth se está reiniciando")
            
        case .unknown:
            print("❓ Estado desconocido del Bluetooth")
            
        @unknown default:
            print("Estado no contemplado")
        }
    }
    
    /// Inicia el escaneo de periféricos BLE
    private func iniciarEscaneo() {
        // nil en serviceUUIDs = escanear TODOS los periféricos visibles
        // En producción, SIEMPRE filtra por UUIDs de servicio específicos
        centralManager.scanForPeripherals(
            withServices: nil,
            options: [CBCentralManagerScanOptionAllowDuplicatesKey: false]
        )
        print("🔍 Escaneando periféricos BLE...")
    }
    
    /// Se llama cada vez que se descubre un periférico durante el escaneo
    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String: Any],
        rssi RSSI: NSNumber
    ) {
        let nombre = peripheral.name ?? "Sin nombre"
        print("📱 Periférico descubierto: \(nombre) | RSSI: \(RSSI) dBm")
        print("   UUID: \(peripheral.identifier)")
        print("   Datos de anuncio: \(advertisementData)")
    }
    
    /// Detiene el escaneo para ahorrar batería
    func detenerEscaneo() {
        centralManager.stopScan()
        print("🛑 Escaneo detenido")
    }
}
```

## Ejemplo intermedio

Este ejemplo muestra un flujo completo: escanear, conectar, descubrir servicios, leer una característica y recibir notificaciones de un sensor de frecuencia cardíaca:

```swift
import CoreBluetooth

/// UUIDs estándar del perfil de frecuencia cardíaca (Heart Rate Profile)
enum HeartRateUUIDs {
    static let servicio = CBUUID(string: "180D")
    static let medicion = CBUUID(string: "2A37")
    static let posicionSensor = CBUUID(string: "2A38")
}

/// Gestor completo de conexión con un monitor de frecuencia cardíaca BLE
class HeartRateManager: NSObject {
    
    private var centralManager: CBCentralManager!
    
    /// Referencia fuerte al periférico conectado (IMPORTANTE: debe mantenerse)
    private var sensorConectado: CBPeripheral?
    
    /// Closure para notificar nuevas lecturas de frecuencia cardíaca
    var onHeartRateUpdate: ((Int) -> Void)?
    
    /// Closure para notificar cambios en el estado de conexión
    var onConnectionStateChange: ((ConnectionState) -> Void)?
    
    enum ConnectionState {
        case desconectado
        case escaneando
        case conectando
        case conectado
        case error(String)
    }
    
    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: .global(qos: .userInitiated))
    }
    
    /// Inicia la búsqueda de sensores de frecuencia cardíaca
    func buscarSensor() {
        guard centralManager.state == .poweredOn else {
            onConnectionStateChange?(.error("Bluetooth no disponible"))
            return
        }
        
        onConnectionStateChange?(.escaneando)
        
        // Filtrar SOLO por periféricos que anuncien el servicio de Heart Rate
        centralManager.scanForPeripherals(
            withServices: [HeartRateUUIDs.servicio],
            options: nil
        )
        
        // Timeout de seguridad: detener el escaneo tras 15 segundos
        DispatchQueue.global().asyncAfter(deadline: .now() + 15) { [weak self] in
            guard let self = self, self.sensorConectado == nil else { return }
            self.centralManager.stopScan()
            self.onConnectionStateChange?(.error("No se encontró ningún sensor"))
        }
    }
    
    /// Desconecta el sensor actual
    func desconectar() {
        guard let periferico = sensorConectado else { return }
        centralManager.cancelPeripheralConnection(periferico)
    }
    
    // MARK: - Parseo de datos de frecuencia cardíaca
    
    /// Interpreta los bytes raw de la característica Heart Rate Measurement
    /// según la especificación Bluetooth SIG
    private func parsearFrecuenciaCardiaca(desde data: Data) -> Int {
        let bytes = [UInt8](data)
        guard !bytes.isEmpty else { return 0 }
        
        // El primer byte contiene flags; el bit 0 indica el formato:
        // 0 = valor en UInt8 (1 byte), 1 = valor en UInt16 (2 bytes)
        let formatoUInt16 = (bytes[0] & 0x01) != 0
        
        if formatoUInt16 && bytes.count >= 3 {
            return Int(UInt16(bytes[1]) | (UInt16(bytes[2]) << 8))
        } else if bytes.count >= 2 {
            return Int(bytes[1])
        }
        
        return 0
    }
}

// MARK: - CBCentralManagerDelegate

extension HeartRateManager: CBCentralManagerDelegate {
    
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if central.state != .poweredOn {
            onConnectionStateChange?(.error("Bluetooth no está disponible"))
        }
    }
    
    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String: Any],
        rssi RSSI: NSNumber
    ) {
        print("Sensor encontrado: \(peripheral.name ?? "Desconocido") RSSI: \(RSSI)")
        
        // Detener escaneo al encontrar el primer sensor
        centralManager.stopScan()
        
        // ⚠️ CRÍTICO: Mantener una referencia fuerte al periférico
        // Si no lo haces, ARC lo libera y la conexión falla silenciosamente
        sensorConectado = peripheral
        
        onConnectionStateChange?(.conectando)
        centralManager.connect(peripheral, options: nil)
    }
    
    func centralManager(
        _ central: CBCentralManager,
        didConnect peripheral: CBPeripheral
    ) {
        print("✅ Conectado a \(peripheral.name ?? "sensor")")
        onConnectionStateChange?(.conectado)
        
        // Asignar delegado del periférico para recibir datos
        peripheral.delegate = self
        