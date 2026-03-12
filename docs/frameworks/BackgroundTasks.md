---
sidebar_position: 1
title: BackgroundTasks
---

# BackgroundTasks

## ¿Qué es BackgroundTasks?

**BackgroundTasks** es un framework de Apple introducido en iOS 13 que permite a las aplicaciones programar y ejecutar trabajo en segundo plano de manera eficiente y respetuosa con los recursos del sistema. Este framework reemplaza y mejora los mecanismos anteriores de ejecución en background, proporcionando una API moderna y declarativa para registrar, programar y gestionar tareas que deben ejecutarse cuando la aplicación no está en primer plano.

El framework se basa en dos tipos fundamentales de tareas: las **tareas de actualización de la aplicación** (`BGAppRefreshTask`) y las **tareas de procesamiento** (`BGProcessingTask`). Las primeras están diseñadas para operaciones breves como la obtención de contenido nuevo, mientras que las segundas permiten trabajos más intensivos como el mantenimiento de bases de datos, el entrenamiento de modelos de Machine Learning o la sincronización masiva de datos.

BackgroundTasks es esencial cuando necesitas que tu aplicación realice trabajo significativo sin intervención del usuario, manteniendo el contenido actualizado y la experiencia fluida. El sistema operativo administra inteligentemente cuándo se ejecutan estas tareas, considerando factores como el nivel de batería, la conectividad de red, si el dispositivo está cargando y los patrones de uso del usuario, lo que garantiza un equilibrio óptimo entre funcionalidad y eficiencia energética.

## Casos de uso principales

- **Sincronización de datos con servidor**: Mantener sincronizados los datos locales con una API remota, como descargar nuevos mensajes de correo, actualizar catálogos de productos o sincronizar cambios pendientes en aplicaciones colaborativas.

- **Mantenimiento de base de datos**: Ejecutar operaciones de limpieza, compactación, migración o indexación de bases de datos locales (Core Data, SQLite, Realm) durante períodos de inactividad del dispositivo.

- **Descarga de contenido anticipado**: Pre-descargar artículos, episodios de podcasts, mapas offline o recursos multimedia para que estén disponibles cuando el usuario abra la aplicación.

- **Procesamiento de Machine Learning**: Entrenar o actualizar modelos de Core ML con datos recopilados localmente, aprovechando los períodos en que el dispositivo está conectado a la corriente eléctrica.

- **Envío de analíticas y logs**: Agrupar y enviar eventos de analítica, registros de errores o métricas de rendimiento al servidor, optimizando el uso de red mediante el envío por lotes.

- **Generación de reportes o exportaciones**: Crear informes PDF, exportar datos a formatos específicos o procesar imágenes/vídeos en segundo plano sin afectar la experiencia del usuario.

## Instalación y configuración

### 1. Importar el framework

BackgroundTasks está incluido en el SDK de iOS y no requiere dependencias externas:

```swift
import BackgroundTasks
```

### 2. Habilitar Background Modes

En Xcode, navega a tu target → **Signing & Capabilities** → **+ Capability** → **Background Modes** y activa:

- ✅ **Background fetch** (para `BGAppRefreshTask`)
- ✅ **Background processing** (para `BGProcessingTask`)

### 3. Registrar identificadores en Info.plist

Añade la clave `BGTaskSchedulerPermittedIdentifiers` en tu archivo `Info.plist` con los identificadores únicos de tus tareas:

```xml
<key>BGTaskSchedulerPermittedIdentifiers</key>
<array>
    <string>com.miapp.refresh</string>
    <string>com.miapp.db-cleanup</string>
    <string>com.miapp.sync</string>
</array>
```

> **Importante**: Cada identificador debe seguir la convención de nomenclatura de dominio inverso y coincidir exactamente con los identificadores que utilices al registrar y programar las tareas en tu código.

### 4. Compatibilidad

| Plataforma | Versión mínima |
|------------|---------------|
| iOS        | 13.0+         |
| iPadOS     | 13.0+         |
| Mac Catalyst | 13.0+      |
| tvOS       | 13.0+         |
| watchOS    | _(No disponible)_ |

## Conceptos clave

### BGTaskScheduler

Es el objeto singleton central del framework. Actúa como el coordinador entre tu aplicación y el sistema operativo. A través de él registras los manejadores de tus tareas y envías las solicitudes de programación. Solo existe una instancia accesible mediante `BGTaskScheduler.shared`.

### BGAppRefreshTask

Representa una tarea de actualización breve. El sistema le asigna aproximadamente **30 segundos** de tiempo de ejecución. Está optimizada para operaciones ligeras como consultar un endpoint API, verificar si hay contenido nuevo o actualizar un widget. El sistema aprende los patrones de uso del usuario y programa estas tareas justo antes de los momentos en que es probable que abra la aplicación.

### BGProcessingTask

Representa una tarea de procesamiento intensivo. Puede ejecutarse durante **varios minutos** (el tiempo exacto lo determina el sistema). Está diseñada para operaciones pesadas y puede configurarse para requerir conectividad de red o que el dispositivo esté conectado a corriente eléctrica. Generalmente se ejecuta durante la noche o en períodos prolongados de inactividad.

### BGTaskRequest (y sus subclases)

Las solicitudes (`BGAppRefreshTaskRequest` y `BGProcessingTaskRequest`) son los objetos que defines para indicar al sistema qué tarea deseas programar y bajo qué condiciones. Incluyen propiedades como `earliestBeginDate` para especificar la fecha más temprana a partir de la cual el sistema puede ejecutar la tarea.

### Ciclo de vida de una tarea

El flujo completo sigue estos pasos: **Registro** del manejador al iniciar la app → **Programación** de la solicitud (generalmente al pasar a background) → **Ejecución** por el sistema cuando las condiciones son favorables → **Finalización** marcando la tarea como completada. Es fundamental reprogramar la tarea dentro del manejador si deseas que se repita.

### Expiración y cancelación

Cada tarea tiene una propiedad `expirationHandler` que el sistema invoca cuando el tiempo asignado está a punto de agotarse. Es **crítico** manejar este evento correctamente, deteniendo cualquier trabajo en curso y marcando la tarea como completada para evitar que el sistema penalice tu aplicación reduciendo la frecuencia de ejecución futura.

## Ejemplo básico

```swift
import UIKit
import BackgroundTasks

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    
    // Identificador único para nuestra tarea de refresco
    static let refreshTaskIdentifier = "com.miapp.refresh"
    
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        
        // PASO 1: Registrar el manejador de la tarea
        // Esto debe hacerse ANTES de que finalice el lanzamiento de la app
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: Self.refreshTaskIdentifier,
            using: nil // nil = cola principal
        ) { task in
            // Este closure se ejecuta cuando el sistema lanza la tarea
            self.handleAppRefresh(task: task as! BGAppRefreshTask)
        }
        
        return true
    }
    
    func applicationDidEnterBackground(_ application: UIApplication) {
        // PASO 2: Programar la tarea cuando la app pasa a segundo plano
        scheduleAppRefresh()
    }
    
    // PASO 3: Definir la lógica de programación
    func scheduleAppRefresh() {
        let request = BGAppRefreshTaskRequest(
            identifier: Self.refreshTaskIdentifier
        )
        // No ejecutar antes de 15 minutos desde ahora
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
        
        do {
            try BGTaskScheduler.shared.submit(request)
            print("✅ Tarea de refresco programada correctamente")
        } catch {
            print("❌ Error al programar tarea: \(error.localizedDescription)")
        }
    }
    
    // PASO 4: Implementar el manejador de la tarea
    func handleAppRefresh(task: BGAppRefreshTask) {
        // Reprogramar para la próxima ejecución
        scheduleAppRefresh()
        
        // Configurar el handler de expiración
        task.expirationHandler = {
            // Cancelar cualquier trabajo pendiente
            print("⏰ La tarea de refresco ha expirado")
            task.setTaskCompleted(success: false)
        }
        
        // Realizar el trabajo de actualización
        fetchLatestData { success in
            task.setTaskCompleted(success: success)
            print(success ? "✅ Refresco completado" : "❌ Refresco fallido")
        }
    }
    
    // Simulación de obtención de datos
    func fetchLatestData(completion: @escaping (Bool) -> Void) {
        // Aquí iría la llamada real a tu API
        DispatchQueue.global().asyncAfter(deadline: .now() + 2) {
            completion(true)
        }
    }
}
```

## Ejemplo intermedio

```swift
import Foundation
import BackgroundTasks
import CoreData

/// Servicio encargado de gestionar todas las tareas en segundo plano de la aplicación.
/// Centraliza el registro, programación y manejo de BGAppRefreshTask y BGProcessingTask.
final class BackgroundTaskService {
    
    // MARK: - Identificadores de tareas
    
    enum TaskIdentifier {
        static let contentRefresh = "com.miapp.content.refresh"
        static let databaseCleanup = "com.miapp.database.cleanup"
        static let dataSync = "com.miapp.data.sync"
    }
    
    // MARK: - Singleton
    
    static let shared = BackgroundTaskService()
    private init() {}
    
    // MARK: - Propiedades
    
    /// Referencia al contexto de Core Data para operaciones de base de datos
    var persistentContainer: NSPersistentContainer?
    
    /// Tarea de red activa que podemos cancelar si el tiempo expira
    private var currentSyncTask: URLSessionDataTask?
    
    // MARK: - Registro de tareas
    
    /// Registra todos los manejadores de tareas en segundo plano.
    /// DEBE llamarse durante `didFinishLaunchingWithOptions`, antes de que retorne.
    func registerAllTasks() {
        
        // Tarea de refresco de contenido (breve, ~30 segundos)
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: TaskIdentifier.contentRefresh,
            using: nil
        ) { [weak self] task in
            guard let refreshTask = task as? BGAppRefreshTask else { return }
            self?.handleContentRefresh(task: refreshTask)
        }
        
        // Tarea de limpieza de base de datos (larga, requiere carga)
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: TaskIdentifier.databaseCleanup,
            using: nil
        ) { [weak self] task in
            guard let processingTask = task as? BGProcessingTask else { return }
            self?.handleDatabaseCleanup(task: processingTask)
        }
        
        // Tarea de sincronización de datos (larga, requiere red)
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: TaskIdentifier.dataSync,
            using: nil
        ) { [weak self] task in
            guard let processingTask = task as? BGProcessingTask else { return }
            self?.handleDataSync(task: processingTask)
        }
        
        print("📋 Todas las tareas en segundo plano registradas")
    }
    
    // MARK: - Programación de tareas
    
    /// Programa la tarea de refresco de contenido.
    /// Se recomienda llamar al pasar a segundo plano.
    func scheduleContentRefresh() {
        let request = BGAppRefreshTaskRequest(
            identifier: TaskIdentifier.contentRefresh
        )
        request.earliestBeginDate = Date(timeIntervalSinceNow: 30 * 60) // 30 min
        
        submitRequest(request)
    }
    
    /// Programa la limpieza nocturna de base de datos.
    /// Requiere que el dispositivo esté conectado a la corriente.
    func scheduleDatabaseCleanup() {
        let request = BGProcessingTaskRequest(
            identifier: TaskIdentifier.databaseCleanup
        )
        request.earliestBeginDate = Date(timeIntervalSinceNow: 2 * 60 * 60) // 2 horas
        request.requiresExternalPower = true // Solo cuando está cargando
        request.requiresNetworkConnectivity = false
        
        submitRequest(request)
    }
    
    /// Programa la sincronización completa de datos con el servidor.
    /// Requiere conectividad de red.
    func scheduleDataSync() {
        let request = BGProcessingTaskRequest(
            identifier: TaskIdentifier.dataSync
        )
        request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 60) // 1 hora
        request.requiresExternalPower = false
        request.requiresNetworkConnectivity = true // Requiere internet
        
        submitRequest(request)
    }
    
    /// Programa todas las tareas. Útil al entrar en segundo plano.
    func scheduleAllTasks() {
        scheduleContentRefresh()
        scheduleDatabaseCleanup()
        scheduleDataSync()
    }
    
    // MARK: - Manejadores de tareas
    
    private func handleContentRefresh(task: BGAppRefreshTask) {
        // Reprogramar para la siguiente ejecución
        scheduleContentRefresh()
        
        // Crear una operación de red para obtener contenido nuevo
        let url = URL(string: "https://api.miapp.com/content/latest")!
        let dataTask = URLSession.shared.dataTask(with: url) { data, response, error in
            
            guard let data = data,
                  let httpResponse = response as? HTTPURLResponse,
                  httpResponse.statusCode == 200 else {
                task.setTaskCompleted(success: false)
                return
            }
            
            // Procesar los datos recibidos
            self.processContentUpdate(data: data) { success in
                task.setTaskCompleted(success: success)
            }
        }
        
        // Manejar la expiración cancelando la petición de red
        task.expirationHandler = {
            dataTask.cancel()
            task.setTaskCompleted(success: false)
        }
        
        dataTask.resume()
    }
    
    private func handleDatabaseCleanup(task: BGProcessingTask) {
        // Reprogramar para la próxima limpieza
        scheduleDatabaseCleanup()
        
        guard let container = persistentContainer else {
            task.setTaskCompleted(success: false)
            return
        }
        
        let context = container.newBackgroundContext()
        
        // Variable para controlar la cancelación
        var isCancelled = false
        
        task.expirationHandler = {
            isCancelled = true
            context.perform {
                // Descartar cambios no guardados si expira
                context.rollback()
            }
            task.setTask