---
sidebar_position: 1
title: CoreData
---

# CoreData

## ¿Qué es CoreData?

CoreData es el framework de persistencia de datos nativo de Apple que permite modelar, gestionar y almacenar datos de manera estructurada en aplicaciones iOS, macOS, watchOS y tvOS. No es simplemente una base de datos: es un **grafo de objetos gestionado** que se encarga de la vida útil de los objetos, sus relaciones, la validación de datos y la persistencia en disco. Internamente puede utilizar SQLite, almacenamiento binario o incluso almacenamiento en memoria como backend, pero abstrae toda esa complejidad para que el desarrollador trabaje directamente con objetos Swift.

CoreData resulta especialmente potente cuando necesitas manejar grandes volúmenes de datos estructurados con relaciones complejas, realizar búsquedas eficientes, mantener un historial de cambios o sincronizar datos entre dispositivos mediante CloudKit. Su integración profunda con SwiftUI y Combine lo convierte en la opción preferida para aplicaciones que requieren persistencia local robusta sin depender de librerías de terceros.

¿Cuándo usar CoreData? Cuando tu aplicación necesita almacenar datos estructurados que persistan entre sesiones, cuando los datos tienen relaciones entre sí (por ejemplo, un usuario tiene muchos pedidos, cada pedido tiene muchos productos), cuando necesitas realizar consultas complejas con filtros y ordenación, o cuando quieres aprovechar la sincronización automática con iCloud a través de `NSPersistentCloudKitContainer`. Si solo necesitas guardar preferencias simples, `UserDefaults` o `SwiftData` (a partir de iOS 17) podrían ser alternativas más sencillas.

## Casos de uso principales

- **Aplicaciones de gestión de tareas y notas**: Almacenar tareas, listas, etiquetas y sus relaciones. CoreData permite consultas rápidas para filtrar por estado, fecha o categoría, además de soportar deshacer/rehacer de forma nativa.

- **Aplicaciones de comercio electrónico**: Gestionar catálogos de productos, carritos de compra, historiales de pedidos y perfiles de usuario con relaciones complejas entre entidades. La capacidad de realizar *fetches* con predicados permite búsquedas eficientes incluso con miles de registros.

- **Aplicaciones con modo offline**: Almacenar datos descargados de una API REST para que la aplicación funcione sin conexión a internet. CoreData actúa como caché inteligente, permitiendo sincronizar cambios cuando se recupera la conectividad.

- **Aplicaciones de salud y fitness**: Registrar entrenamientos, métricas corporales, planes alimenticios y progreso a lo largo del tiempo. Las *fetch requests* con agregaciones permiten generar estadísticas y reportes históricos.

- **Aplicaciones colaborativas con sincronización iCloud**: Mediante `NSPersistentCloudKitContainer`, CoreData sincroniza datos automáticamente entre todos los dispositivos del usuario sin necesidad de configurar un backend propio.

- **Aplicaciones de contenido multimedia**: Gestionar bibliotecas de fotos, música o vídeos con metadatos, álbumes, playlists y etiquetas, aprovechando las relaciones *many-to-many* y el *faulting* para cargar datos bajo demanda.

## Instalación y configuración

### Agregar CoreData al proyecto

CoreData viene incluido en el SDK de Apple, por lo que **no necesitas instalar ninguna dependencia externa**. Tienes dos formas de configurarlo:

**Opción 1: Al crear el proyecto**
Al crear un nuevo proyecto en Xcode, marca la casilla **"Use Core Data"** en el asistente de creación. Esto generará automáticamente el archivo `.xcdatamodeld` y el código de configuración del stack en tu `App` o `AppDelegate`.

**Opción 2: Agregar manualmente a un proyecto existente**

1. Crea un nuevo archivo de tipo **Data Model** (`File > New > File > Data Model`) que generará un archivo `.xcdatamodeld`.
2. Configura el stack de CoreData en tu código.

### Import necesario

```swift
import CoreData
```

### Permisos en Info.plist

CoreData **no requiere permisos especiales** en `Info.plist` para almacenamiento local. Sin embargo, si usas `NSPersistentCloudKitContainer` para sincronización con iCloud, necesitarás:

1. Activar la capability **iCloud** con **CloudKit** en tu target.
2. Activar la capability **Background Modes** > **Remote notifications**.
3. Configurar un contenedor de CloudKit en el portal de desarrollador de Apple.

### Archivo del modelo de datos (.xcdatamodeld)

Este archivo es el editor visual donde defines tus **entidades** (tablas), **atributos** (columnas) y **relaciones**. Xcode proporciona un editor gráfico intuitivo para diseñar tu esquema de datos sin escribir código.

## Conceptos clave

### 1. NSManagedObjectModel

Es la representación en memoria de tu esquema de datos (el archivo `.xcdatamodeld` compilado). Define las entidades, sus atributos, relaciones y reglas de validación. Piensa en él como el **plano arquitectónico** de tu base de datos.

### 2. NSPersistentStoreCoordinator y NSPersistentContainer

El `NSPersistentStoreCoordinator` actúa como puente entre el modelo de objetos y el almacenamiento físico en disco. En la práctica moderna, usamos `NSPersistentContainer` (o `NSPersistentCloudKitContainer`), que encapsula toda la configuración del stack de CoreData en un solo objeto fácil de configurar: modelo, coordinador y contexto principal.

### 3. NSManagedObjectContext

Es el **espacio de trabajo** donde creas, lees, actualizas y eliminas objetos. Funciona como un *scratchpad* temporal: los cambios no se persisten hasta que llamas a `save()`. Puedes tener múltiples contextos (uno principal para la UI y otros en segundo plano para operaciones pesadas) que se sincronizan entre sí.

### 4. NSManagedObject

Es la clase base de todos los objetos gestionados por CoreData. Cada instancia representa una fila en tu almacén de datos. Xcode puede generar automáticamente subclases tipadas (por ejemplo, `Tarea`, `Proyecto`) con propiedades que corresponden a los atributos definidos en el modelo.

### 5. NSFetchRequest

Es el mecanismo para recuperar datos del almacén. Permite especificar **predicados** (filtros con `NSPredicate`), **ordenación** (`NSSortDescriptor`), **límites** de resultados y **estrategias de carga** (por lotes, con *faulting*, etc.). En SwiftUI, el property wrapper `@FetchRequest` simplifica enormemente este proceso.

### 6. Faulting (carga diferida)

CoreData implementa un sistema inteligente de carga diferida llamado *faulting*. Cuando realizas un *fetch*, los objetos devueltos son inicialmente **faults** (marcadores de posición vacíos) que solo cargan sus datos reales cuando accedes a una propiedad específica. Esto optimiza dramáticamente el uso de memoria en colecciones grandes.

## Ejemplo básico

```swift
import CoreData

// MARK: - Configuración mínima del stack de CoreData

/// Clase encargada de gestionar el stack completo de CoreData.
/// Se implementa como singleton para acceso global.
class PersistenceController {

    // Singleton para acceder desde cualquier parte de la app
    static let shared = PersistenceController()

    // NSPersistentContainer encapsula todo el stack de CoreData
    let container: NSPersistentContainer

    init(inMemory: Bool = false) {
        // "MiModelo" debe coincidir con el nombre del archivo .xcdatamodeld
        container = NSPersistentContainer(name: "MiModelo")

        // Almacenamiento en memoria útil para tests y previews
        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }

        // Cargar los almacenes persistentes
        container.loadPersistentStores { descripcion, error in
            if let error = error as NSError? {
                // En producción, manejar este error adecuadamente
                fatalError("Error al cargar CoreData: \(error), \(error.userInfo)")
            }
        }

        // Fusionar automáticamente los cambios de contextos en segundo plano
        container.viewContext.automaticallyMergesChangesFromParent = true
    }

    // MARK: - Operación CRUD básica: Crear una tarea

    /// Crea una nueva tarea y la guarda en CoreData
    func crearTarea(titulo: String, completada: Bool = false) {
        let contexto = container.viewContext

        // Crear una nueva instancia de la entidad "Tarea"
        let nuevaTarea = NSEntityDescription.insertNewObject(
            forEntityName: "Tarea",
            into: contexto
        )

        // Asignar valores a los atributos
        nuevaTarea.setValue(titulo, forKey: "titulo")
        nuevaTarea.setValue(completada, forKey: "completada")
        nuevaTarea.setValue(Date(), forKey: "fechaCreacion")
        nuevaTarea.setValue(UUID(), forKey: "id")

        // Persistir los cambios en disco
        guardarContexto()
    }

    // MARK: - Operación CRUD básica: Leer tareas

    /// Obtiene todas las tareas ordenadas por fecha de creación
    func obtenerTareas() -> [NSManagedObject] {
        let contexto = container.viewContext
        let solicitud = NSFetchRequest<NSManagedObject>(entityName: "Tarea")

        // Ordenar por fecha de creación descendente (más recientes primero)
        solicitud.sortDescriptors = [
            NSSortDescriptor(key: "fechaCreacion", ascending: false)
        ]

        do {
            return try contexto.fetch(solicitud)
        } catch {
            print("Error al obtener tareas: \(error)")
            return []
        }
    }

    // MARK: - Operación CRUD básica: Eliminar una tarea

    /// Elimina un objeto gestionado del contexto
    func eliminarTarea(_ tarea: NSManagedObject) {
        container.viewContext.delete(tarea)
        guardarContexto()
    }

    // MARK: - Guardar contexto

    /// Persiste los cambios pendientes del contexto principal
    func guardarContexto() {
        let contexto = container.viewContext

        // Solo guardar si hay cambios pendientes
        guard contexto.hasChanges else { return }

        do {
            try contexto.save()
        } catch {
            let nsError = error as NSError
            print("Error al guardar contexto: \(nsError), \(nsError.userInfo)")
        }
    }
}
```

## Ejemplo intermedio

```swift
import CoreData
import Foundation

// MARK: - Subclases generadas de NSManagedObject (tipado seguro)
// Normalmente Xcode genera estas clases automáticamente desde el .xcdatamodeld
// Aquí las definimos manualmente para mayor claridad

/// Entidad Proyecto: contiene múltiples tareas
@objc(Proyecto)
public class Proyecto: NSManagedObject, Identifiable {
    @NSManaged public var id: UUID
    @NSManaged public var nombre: String
    @NSManaged public var descripcionTexto: String?
    @NSManaged public var fechaCreacion: Date
    @NSManaged public var color: String
    @NSManaged public var tareas: NSSet? // Relación uno-a-muchos con Tarea
}

// MARK: - Extensión para manejar la relación con Tareas
extension Proyecto {
    /// Tareas convertidas a un array ordenado por fecha
    var tareasOrdenadas: [Tarea] {
        let conjunto = tareas as? Set<Tarea> ?? []
        return conjunto.sorted { $0.fechaCreacion > $1.fechaCreacion }
    }

    /// Número total de tareas completadas
    var tareasCompletadas: Int {
        tareasOrdenadas.filter { $0.completada }.count
    }

    /// Porcentaje de progreso del proyecto (0.0 a 1.0)
    var progreso: Double {
        guard !tareasOrdenadas.isEmpty else { return 0 }
        return Double(tareasCompletadas) / Double(tareasOrdenadas.count)
    }
}

/// Entidad Tarea: pertenece a un Proyecto
@objc(Tarea)
public class Tarea: NSManagedObject, Identifiable {
    @NSManaged public var id: UUID
    @NSManaged public var titulo: String
    @NSManaged public var completada: Bool
    @NSManaged public var fechaCreacion: Date
    @NSManaged public var fechaLimite: Date?
    @NSManaged public var prioridad: Int16 // 0: baja, 1: media, 2: alta
    @NSManaged public var proyecto: Proyecto? // Relación inversa
}

// MARK: - Enum de prioridad para mayor legibilidad
extension Tarea {
    enum Prioridad: Int16, CaseIterable {
        case baja = 0
        case media = 1
        case alta = 2

        var etiqueta: String {
            switch self {
            case .baja: return "Baja"
            case .media: return "Media"
            case .alta: return "Alta"
            }
        }

        var icono: String {
            switch self {
            case .baja: return "arrow.down.circle"
            case .media: return "equal.circle"
            case .alta: return "exclamationmark.circle.fill"
            }
        }
    }

    var nivelPrioridad: Prioridad {
        Prioridad(rawValue: prioridad) ?? .media
    }
}

// MARK: - Servicio de datos con operaciones avanzadas

/// Servicio que encapsula todas las operaciones de CoreData
/// con soporte para operaciones en segundo plano
class CoreDataService {

    private let container: NSPersistentContainer

    /// Contexto principal para operaciones en el hilo de la UI
    var contextoVista: NSManagedObjectContext {
        container.viewContext
    }

    init(container: NSPersistentContainer) {
        self.container = container
        // Política de fusión: los cambios del almacén tienen prioridad
        contextoVista.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        contextoVista.automaticallyMergesChangesFromParent = true
    }

    // MARK: - Crear proyecto con tareas iniciales

    /// Crea un proyecto con un conjunto de tareas iniciales de forma atómica
    func crearProyecto(
        nombre: String,
        descripcion: String?,
        color: String,
        tareasIniciales: [(titulo: String, prioridad: Tarea.Prioridad)]
    ) throws -> Proyecto {
        let contexto = contextoVista

        // Crear el proyecto
        let proyecto = Proyecto(context: contexto)
        proyecto.id = UUID()
        proyecto.nombre = nombre
        proyecto.descripcionTexto = descripcion
        proyecto.fechaCreacion = Date()
        proyecto.color = color

        // Crear las tareas asociadas al proyecto
        for (indice, datosTarea) in tareasIniciales.enumerated() {
            let tarea = Tarea(context: contexto)
            tarea.id = UUID()
            tarea.titulo = datosTarea.titulo
            tarea.completada = false