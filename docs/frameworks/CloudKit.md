---
sidebar_position: 1
title: CloudKit
---

# CloudKit

## ¿Qué es CloudKit?

CloudKit es el framework de Apple que proporciona una infraestructura de almacenamiento y sincronización de datos en la nube basada en iCloud. Permite a los desarrolladores almacenar datos estructurados (registros), archivos (assets) y datos clave-valor directamente en los servidores de Apple, sin necesidad de configurar ni mantener un backend propio. CloudKit actúa como un puente entre tu aplicación y iCloud, gestionando la autenticación del usuario de forma transparente a través de su Apple ID.

Este framework es especialmente útil cuando necesitas sincronizar datos entre múltiples dispositivos de un mismo usuario, compartir información entre distintos usuarios, o simplemente almacenar datos en la nube sin depender de servicios de terceros como Firebase o AWS. CloudKit ofrece una capa gratuita generosa que escala automáticamente con el número de usuarios de tu aplicación, lo que lo convierte en una opción económica y robusta para la mayoría de aplicaciones iOS, macOS, watchOS y tvOS.

Desde su introducción en iOS 8, CloudKit ha evolucionado significativamente. Con la llegada de `CKSyncEngine` en iOS 17, la sincronización automática de datos se ha simplificado enormemente. Además, CloudKit se integra de forma nativa con `NSPersistentCloudKitContainer` de Core Data y con SwiftData, permitiendo sincronización transparente de modelos de datos locales con la nube.

## Casos de uso principales

- **Sincronización entre dispositivos**: Mantener notas, preferencias, listas de tareas o cualquier dato del usuario sincronizado entre su iPhone, iPad, Mac y Apple Watch. El usuario edita en un dispositivo y ve los cambios reflejados instantáneamente en los demás.

- **Aplicaciones colaborativas**: Compartir registros entre distintos usuarios mediante zonas compartidas (`CKShare`). Ideal para aplicaciones de listas compartidas, proyectos en equipo o álbumes familiares donde múltiples personas necesitan leer y escribir datos.

- **Almacenamiento de contenido generado por el usuario**: Guardar fotos, documentos, grabaciones de audio u otros archivos pesados como `CKAsset`, aprovechando la infraestructura de iCloud sin costes adicionales de almacenamiento en servidores propios.

- **Base de datos pública para la aplicación**: Utilizar la base de datos pública de CloudKit como backend ligero para almacenar contenido accesible por todos los usuarios, como catálogos de productos, puntos de interés o noticias de la aplicación.

- **Notificaciones push basadas en datos**: Configurar suscripciones que envían notificaciones push automáticas cuando los datos cambian en el servidor, sin necesidad de configurar APNs manualmente ni mantener un servicio de push propio.

- **Respaldo y restauración de datos**: Ofrecer al usuario la seguridad de que sus datos persisten incluso si cambia de dispositivo o reinstala la aplicación, ya que los datos se recuperan automáticamente desde iCloud.

## Instalación y configuración

### 1. Habilitar CloudKit en el proyecto

En Xcode, selecciona tu target principal y ve a la pestaña **Signing & Capabilities**:

1. Haz clic en **+ Capability**.
2. Añade **iCloud**.
3. Marca la casilla **CloudKit**.
4. Selecciona o crea un **container** (por ejemplo, `iCloud.com.tuempresa.tuapp`).

### 2. Verificar el entitlement

Xcode genera automáticamente el archivo de entitlements. Verifica que contenga:

```xml
<key>com.apple.developer.icloud-container-identifiers</key>
<array>
    <string>iCloud.com.tuempresa.tuapp</string>
</array>
<key>com.apple.developer.icloud-services</key>
<array>
    <string>CloudKit</string>
</array>
```

### 3. Configurar el esquema en CloudKit Dashboard

Accede a [CloudKit Console](https://icloud.developer.apple.com/) para definir tus tipos de registros (Record Types), índices y permisos de seguridad. También puedes dejar que CloudKit cree los esquemas automáticamente en el entorno de desarrollo al guardar registros por primera vez.

### 4. Import necesario

```swift
import CloudKit
```

Para integraciones con Core Data:

```swift
import CoreData // NSPersistentCloudKitContainer
import CloudKit
```

### 5. Permisos y consideraciones de Info.plist

CloudKit **no requiere permisos explícitos** en `Info.plist` ya que utiliza la cuenta de iCloud del dispositivo. Sin embargo, si usas notificaciones push con suscripciones, necesitarás añadir la capability de **Push Notifications**. También es recomendable verificar el estado de la cuenta:

```swift
CKContainer.default().accountStatus { status, error in
    switch status {
    case .available:
        print("iCloud disponible")
    case .noAccount:
        print("El usuario no ha iniciado sesión en iCloud")
    case .restricted:
        print("Acceso a iCloud restringido")
    case .couldNotDetermine:
        print("No se pudo determinar el estado")
    case .temporarilyUnavailable:
        print("iCloud temporalmente no disponible")
    @unknown default:
        break
    }
}
```

## Conceptos clave

### CKContainer

El contenedor es el nivel más alto de organización en CloudKit. Cada aplicación tiene al menos un contenedor por defecto (`CKContainer.default()`), y puede acceder a contenedores adicionales. Un contenedor encapsula las bases de datos y gestiona la identidad del usuario. Piensa en él como el "servidor" de tu aplicación.

### Bases de datos (CKDatabase)

Cada contenedor tiene tres bases de datos:

- **Pública** (`publicCloudDatabase`): Accesible por todos los usuarios. Ideal para contenido compartido globalmente. Los datos cuentan contra la cuota de almacenamiento del desarrollador.
- **Privada** (`privateCloudDatabase`): Solo accesible por el usuario autenticado. Los datos cuentan contra la cuota de iCloud del usuario.
- **Compartida** (`sharedCloudDatabase`): Contiene registros que otros usuarios han compartido con el usuario actual mediante `CKShare`.

### CKRecord

Es la unidad fundamental de datos en CloudKit, similar a una fila en una base de datos o un documento en un almacén NoSQL. Cada registro tiene un `recordType` (equivalente a una tabla), un `recordID` único, y pares clave-valor para almacenar datos (strings, números, fechas, ubicaciones, referencias a otros registros, y assets).

### CKRecordZone

Las zonas son subdivisiones dentro de una base de datos. La base de datos pública solo tiene la zona por defecto, pero en la base de datos privada puedes crear zonas personalizadas. Las zonas personalizadas son necesarias para habilitar sincronización atómica con `CKFetchRecordZoneChangesOperation` y para compartir datos con `CKShare`.

### CKSubscription

Las suscripciones permiten que el servidor notifique a tu aplicación cuando ocurren cambios. Existen tres tipos principales:

- **Query subscriptions**: Se disparan cuando un registro que coincide con un predicado es creado, modificado o eliminado.
- **RecordZone subscriptions**: Notifican sobre cualquier cambio en una zona específica.
- **Database subscriptions**: Notifican sobre cambios en toda una base de datos.

### CKOperation

CloudKit ofrece dos APIs: la API de conveniencia (métodos simples en `CKDatabase`) y las operaciones (`CKOperation`). Las operaciones heredan de `Operation` y ofrecen mayor control: prioridad, dependencias, procesamiento por lotes, calidad de servicio (QoS) y cancelación. Para código de producción, se recomienda usar operaciones.

## Ejemplo básico

```swift
import CloudKit

// MARK: - Guardar y recuperar un registro simple en CloudKit

/// Este ejemplo muestra cómo crear, guardar y consultar un registro
/// en la base de datos privada del usuario.

func guardarNota(titulo: String, contenido: String) async throws -> CKRecord {
    // 1. Obtener referencia al contenedor y la base de datos privada
    let container = CKContainer.default()
    let database = container.privateCloudDatabase
    
    // 2. Crear un nuevo registro de tipo "Nota"
    let record = CKRecord(recordType: "Nota")
    record["titulo"] = titulo as CKRecordValue
    record["contenido"] = contenido as CKRecordValue
    record["fechaCreacion"] = Date() as CKRecordValue
    record["esFavorita"] = false as CKRecordValue
    
    // 3. Guardar el registro en iCloud (API async/await de iOS 15+)
    let registroGuardado = try await database.save(record)
    print("Nota guardada con ID: \(registroGuardado.recordID.recordName)")
    
    return registroGuardado
}

func obtenerTodasLasNotas() async throws -> [CKRecord] {
    let database = CKContainer.default().privateCloudDatabase
    
    // 4. Crear una consulta con predicado (todas las notas)
    let query = CKQuery(recordType: "Nota", predicate: NSPredicate(value: true))
    
    // 5. Ordenar por fecha de creación descendente
    query.sortDescriptors = [NSSortDescriptor(key: "fechaCreacion", ascending: false)]
    
    // 6. Ejecutar la consulta
    let (resultados, _) = try await database.records(matching: query)
    
    // 7. Extraer los registros exitosos
    let notas = resultados.compactMap { _, result in
        try? result.get()
    }
    
    print("Se encontraron \(notas.count) notas")
    return notas
}

func eliminarNota(recordID: CKRecord.ID) async throws {
    let database = CKContainer.default().privateCloudDatabase
    
    // 8. Eliminar el registro por su ID
    try await database.deleteRecord(withID: recordID)
    print("Nota eliminada correctamente")
}
```

## Ejemplo intermedio

```swift
import CloudKit
import Foundation

// MARK: - Servicio CloudKit completo con manejo de errores y assets

/// Servicio que gestiona recetas de cocina con imágenes en CloudKit.
/// Demuestra el uso de CKAsset, consultas con filtros, modificación
/// de registros y manejo robusto de errores.

final class RecetaCloudKitService {
    
    // MARK: - Propiedades
    
    private let container: CKContainer
    private let database: CKDatabase
    private let zoneName = "RecetasZone"
    private lazy var customZone = CKRecordZone(zoneName: zoneName)
    
    // MARK: - Inicialización
    
    init(containerIdentifier: String? = nil) {
        if let identifier = containerIdentifier {
            self.container = CKContainer(identifier: identifier)
        } else {
            self.container = CKContainer.default()
        }
        self.database = container.privateCloudDatabase
    }
    
    // MARK: - Configuración de zona personalizada
    
    /// Crea la zona personalizada si no existe.
    /// Las zonas personalizadas permiten sincronización incremental.
    func configurarZona() async throws {
        do {
            _ = try await database.save(customZone)
            print("Zona '\(zoneName)' creada exitosamente")
        } catch let error as CKError where error.code == .serverRejectedRequest {
            // La zona ya existe, no es un error real
            print("La zona ya existía previamente")
        }
    }
    
    // MARK: - Modelo de datos
    
    struct Receta {
        let id: CKRecord.ID?
        let nombre: String
        let ingredientes: [String]
        let instrucciones: String
        let tiempoMinutos: Int
        let dificultad: String // "fácil", "media", "difícil"
        let imagenURL: URL?
        
        /// Convierte la receta en un CKRecord para guardar en CloudKit
        func toCKRecord(zoneID: CKRecordZone.ID) -> CKRecord {
            let recordID = id ?? CKRecord.ID(
                recordName: UUID().uuidString,
                zoneID: zoneID
            )
            let record = CKRecord(recordType: "Receta", recordID: recordID)
            
            record["nombre"] = nombre as CKRecordValue
            record["ingredientes"] = ingredientes as CKRecordValue
            record["instrucciones"] = instrucciones as CKRecordValue
            record["tiempoMinutos"] = tiempoMinutos as CKRecordValue
            record["dificultad"] = dificultad as CKRecordValue
            
            // Adjuntar imagen como CKAsset si existe
            if let url = imagenURL {
                record["imagen"] = CKAsset(fileURL: url)
            }
            
            return record
        }
        
        /// Crea una Receta a partir de un CKRecord recibido de CloudKit
        static func fromCKRecord(_ record: CKRecord) -> Receta? {
            guard let nombre = record["nombre"] as? String,
                  let instrucciones = record["instrucciones"] as? String else {
                return nil
            }
            
            return Receta(
                id: record.recordID,
                nombre: nombre,
                ingredientes: record["ingredientes"] as? [String] ?? [],
                instrucciones: instrucciones,
                tiempoMinutos: record["tiempoMinutos"] as? Int ?? 0,
                dificultad: record["dificultad"] as? String ?? "media",
                imagenURL: (record["imagen"] as? CKAsset)?.fileURL
            )
        }
    }
    
    // MARK: - Operaciones CRUD
    
    /// Guarda una receta nueva o actualiza una existente
    func guardarReceta(_ receta: Receta) async throws -> Receta {
        let record = receta.toCKRecord(zoneID: customZone.zoneID)
        let savedRecord = try await database.save(record)
        
        guard let recetaGuardada = Receta.fromCKRecord(savedRecord) else {
            throw CloudKitServiceError.errorDeConversion
        }
        return recetaGuardada
    }
    
    /// Busca recetas por dificultad con límite de resultados
    func buscarRecetas(
        dificultad: String,
        limite: Int = 20
    ) async throws -> [Receta] {
        let predicate = NSPredicate(format: "dificultad == %@", dificultad)
        let query = CKQuery(recordType: "Receta", predicate: predicate)
        query.sortDescriptors = [
            NSSortDescriptor(key: "nombre", ascending: true)
        ]
        
        // Usar la API moderna con zona personalizada
        let (results, _) = try await database.records(
            matching: query,
            inZoneWith: customZone.zoneID,
            desiredKeys: ["nombre", "ingredientes", "tiempoMinutos", "dificultad"],
            resultsLimit: limite
        )
        
        return results.compactMap { _, result in
            guard let record = try? result.get() else { return nil }
            return Receta.fromCKRecord(record)
        }
    }
    
    /// Busca recetas que contengan un ingrediente específico