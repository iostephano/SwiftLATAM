---
sidebar_position: 1
title: SwiftData
---

# SwiftData

## ¿Qué es SwiftData?

SwiftData es el framework moderno de persistencia de datos desarrollado por Apple, presentado en la WWDC 2023. Fue diseñado como el sucesor natural de Core Data, ofreciendo una API declarativa construida íntegramente con Swift que aprovecha al máximo las características del lenguaje, como las macros, los tipos de datos nativos y la concurrencia estructurada. Su objetivo principal es simplificar drásticamente el almacenamiento, la consulta y la gestión de datos en aplicaciones iOS, macOS, watchOS, tvOS y visionOS.

A diferencia de Core Data, donde era necesario crear modelos de datos mediante un editor visual (`.xcdatamodeld`), definir entidades manualmente y gestionar contextos complejos, SwiftData permite definir los modelos directamente en código Swift usando la macro `@Model`. Esto elimina la necesidad de archivos de configuración separados, reduce la superficie de errores y proporciona autocompletado e inferencia de tipos en tiempo de compilación. SwiftData se encarga internamente de la serialización, el esquema de la base de datos, las migraciones y la sincronización con iCloud a través de CloudKit.

SwiftData es ideal cuando necesitas persistencia local robusta en tu aplicación, ya sea para almacenar preferencias complejas del usuario, cachear datos provenientes de una API, gestionar contenido generado por el usuario o construir aplicaciones completamente offline-first. Su integración nativa con SwiftUI lo convierte en la opción más natural y productiva para proyectos nuevos que utilicen el stack moderno de Apple.

## Casos de uso principales

- **Aplicaciones de notas y tareas**: Almacenar, editar y organizar notas, tareas o recordatorios con relaciones jerárquicas (carpetas, etiquetas, subtareas) de forma completamente local y sincronizada con iCloud.

- **Catálogos y listas de contenido**: Gestionar colecciones de libros, recetas, películas, contactos o cualquier tipo de entidad con capacidad de búsqueda, filtrado y ordenamiento avanzado.

- **Caché de datos de API**: Persistir respuestas de servicios web para ofrecer experiencia offline, reducir consumo de red y mejorar los tiempos de carga percibidos por el usuario.

- **Aplicaciones de seguimiento personal**: Registros de hábitos, ejercicio, finanzas personales o diarios donde el usuario genera datos continuamente que necesitan persistirse y consultarse históricamente.

- **Gestión de borradores y estado de la aplicación**: Guardar el progreso del usuario en formularios largos, flujos de edición o configuraciones complejas que deben sobrevivir al cierre de la aplicación.

- **Aplicaciones colaborativas con sincronización**: Aprovechar la integración transparente con CloudKit para sincronizar datos entre dispositivos del mismo usuario sin escribir código de red.

## Instalación y configuración

### Requisitos del sistema

SwiftData está disponible a partir de las siguientes versiones mínimas:

| Plataforma | Versión mínima |
|------------|----------------|
| iOS        | 17.0           |
| macOS      | 14.0 (Sonoma)  |
| watchOS    | 10.0           |
| tvOS       | 17.0           |
| visionOS   | 1.0            |

### Agregar SwiftData al proyecto

SwiftData viene integrado en el SDK de Apple, por lo que **no necesitas agregar ninguna dependencia externa** mediante Swift Package Manager, CocoaPods ni Carthage. Basta con importar el módulo.

```swift
import SwiftData
```

### Configuración en el punto de entrada de la aplicación

Para que SwiftData funcione correctamente con SwiftUI, debes configurar el contenedor de modelos en el punto de entrada de tu app:

```swift
import SwiftUI
import SwiftData

@main
struct MiAplicacionApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        // Registra los modelos que SwiftData debe gestionar
        .modelContainer(for: [Tarea.self, Categoria.self])
    }
}
```

### Permisos en Info.plist

SwiftData **no requiere permisos especiales** en `Info.plist` para persistencia local. Sin embargo, si deseas habilitar la sincronización con iCloud a través de CloudKit, necesitarás:

1. Activar la capability **iCloud** en el target de tu proyecto.
2. Marcar la opción **CloudKit** dentro de la capability.
3. Crear o seleccionar un contenedor de CloudKit (por ejemplo, `iCloud.com.tuempresa.tuapp`).

No se requiere configuración adicional en `Info.plist` para el almacenamiento local estándar.

## Conceptos clave

### 1. `@Model` — La macro de definición de modelos

La macro `@Model` transforma una clase Swift ordinaria en un modelo persistente. SwiftData genera automáticamente la conformidad con el protocolo `PersistentModel`, la observabilidad y el mapeo al esquema de almacenamiento.

```swift
@Model
class Tarea {
    var titulo: String
    var completada: Bool
    var fechaCreacion: Date

    init(titulo: String, completada: Bool = false) {
        self.titulo = titulo
        self.completada = completada
        self.fechaCreacion = .now
    }
}
```

### 2. `ModelContainer` — El contenedor de almacenamiento

El `ModelContainer` es responsable de crear y gestionar el almacenamiento subyacente (base de datos SQLite por defecto). Define qué modelos se persisten y con qué configuración (en memoria, en disco, con CloudKit, etc.).

```swift
// Contenedor básico en disco
let container = try ModelContainer(for: Tarea.self)

// Contenedor en memoria (útil para tests y previews)
let config = ModelConfiguration(isStoredInMemoryOnly: true)
let container = try ModelContainer(for: Tarea.self, configurations: config)
```

### 3. `ModelContext` — El contexto de trabajo

El `ModelContext` es el espacio de trabajo donde insertas, modificas, eliminas y consultas objetos. Actúa como intermediario entre tus objetos en memoria y el almacenamiento persistente. En SwiftUI se inyecta automáticamente a través del environment.

```swift
@Environment(\.modelContext) private var contexto
```

### 4. `@Query` — Consultas declarativas

La propiedad envolvente `@Query` permite definir consultas reactivas directamente en las vistas de SwiftUI. Los resultados se actualizan automáticamente cuando los datos subyacentes cambian.

```swift
@Query(sort: \Tarea.fechaCreacion, order: .reverse)
private var tareas: [Tarea]
```

### 5. `@Relationship` — Relaciones entre modelos

SwiftData infiere automáticamente las relaciones a partir de las propiedades de tipo modelo, pero puedes personalizarlas con la macro `@Relationship` para definir reglas de eliminación en cascada, relaciones inversas y más.

```swift
@Model
class Categoria {
    var nombre: String

    @Relationship(deleteRule: .cascade, inverse: \Tarea.categoria)
    var tareas: [Tarea]

    init(nombre: String, tareas: [Tarea] = []) {
        self.nombre = nombre
        self.tareas = tareas
    }
}
```

### 6. `#Predicate` — Filtros con seguridad de tipos

La macro `#Predicate` permite construir filtros de consulta que se verifican en tiempo de compilación, eliminando los errores típicos de los `NSPredicate` basados en cadenas de texto.

```swift
let soloIncompletas = #Predicate<Tarea> { tarea in
    tarea.completada == false
}
```

## Ejemplo básico

Este ejemplo muestra cómo definir un modelo simple y realizar operaciones CRUD fundamentales:

```swift
import SwiftData
import SwiftUI

// MARK: - Modelo de datos
// La macro @Model convierte esta clase en una entidad persistente
@Model
class Nota {
    var titulo: String
    var contenido: String
    var fechaCreacion: Date

    init(titulo: String, contenido: String) {
        self.titulo = titulo
        self.contenido = contenido
        self.fechaCreacion = .now
    }
}

// MARK: - Vista principal con listado
struct ListaNotasView: View {
    // @Query obtiene automáticamente todas las notas ordenadas por fecha
    @Query(sort: \Nota.fechaCreacion, order: .reverse)
    private var notas: [Nota]

    // El contexto se inyecta automáticamente desde el modelContainer
    @Environment(\.modelContext) private var contexto

    var body: some View {
        NavigationStack {
            List {
                ForEach(notas) { nota in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(nota.titulo)
                            .font(.headline)
                        Text(nota.contenido)
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .lineLimit(2)
                    }
                }
                .onDelete(perform: eliminarNotas)
            }
            .navigationTitle("Mis Notas")
            .toolbar {
                Button("Agregar", systemImage: "plus") {
                    agregarNota()
                }
            }
        }
    }

    // MARK: - Insertar una nueva nota
    private func agregarNota() {
        let nueva = Nota(
            titulo: "Nueva nota",
            contenido: "Escribe aquí tu contenido..."
        )
        // Insertar el objeto en el contexto lo persiste automáticamente
        contexto.insert(nueva)
    }

    // MARK: - Eliminar notas seleccionadas
    private func eliminarNotas(en offsets: IndexSet) {
        for index in offsets {
            // Eliminar el objeto del contexto lo remueve del almacenamiento
            contexto.delete(notas[index])
        }
    }
}
```

## Ejemplo intermedio

Este ejemplo muestra un caso de uso real con relaciones entre modelos, filtros dinámicos y formularios de edición:

```swift
import SwiftData
import SwiftUI

// MARK: - Modelos con relaciones

@Model
class Proyecto {
    var nombre: String
    var descripcion: String
    var color: String // Almacenamos el nombre del color como String
    var fechaCreacion: Date

    // Relación uno-a-muchos: un proyecto tiene múltiples tareas
    // Si se elimina el proyecto, se eliminan todas sus tareas
    @Relationship(deleteRule: .cascade, inverse: \Tarea.proyecto)
    var tareas: [Tarea]

    // Propiedad computada para obtener el progreso del proyecto
    var progreso: Double {
        guard !tareas.isEmpty else { return 0 }
        let completadas = tareas.filter(\.completada).count
        return Double(completadas) / Double(tareas.count)
    }

    init(nombre: String, descripcion: String = "", color: String = "blue") {
        self.nombre = nombre
        self.descripcion = descripcion
        self.color = color
        self.fechaCreacion = .now
        self.tareas = []
    }
}

@Model
class Tarea {
    var titulo: String
    var completada: Bool
    var prioridad: Int // 1 = baja, 2 = media, 3 = alta
    var fechaLimite: Date?
    var fechaCreacion: Date

    // Relación inversa hacia el proyecto
    var proyecto: Proyecto?

    init(
        titulo: String,
        prioridad: Int = 2,
        fechaLimite: Date? = nil,
        proyecto: Proyecto? = nil
    ) {
        self.titulo = titulo
        self.completada = false
        self.prioridad = prioridad
        self.fechaLimite = fechaLimite
        self.fechaCreacion = .now
        self.proyecto = proyecto
    }
}

// MARK: - Vista de lista de proyectos

struct ProyectosView: View {
    @Query(sort: \Proyecto.fechaCreacion, order: .reverse)
    private var proyectos: [Proyecto]

    @Environment(\.modelContext) private var contexto
    @State private var mostrarFormulario = false

    var body: some View {
        NavigationStack {
            List {
                ForEach(proyectos) { proyecto in
                    NavigationLink(destination: DetallePoryectoView(proyecto: proyecto)) {
                        HStack {
                            // Indicador de color del proyecto
                            Circle()
                                .fill(Color(proyecto.color))
                                .frame(width: 12, height: 12)

                            VStack(alignment: .leading) {
                                Text(proyecto.nombre)
                                    .font(.headline)
                                Text("\(proyecto.tareas.count) tareas")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }

                            Spacer()

                            // Indicador visual de progreso
                            ProgressView(value: proyecto.progreso)
                                .frame(width: 60)
                        }
                    }
                }
                .onDelete { offsets in
                    offsets.forEach { contexto.delete(proyectos[$0]) }
                }
            }
            .navigationTitle("Proyectos")
            .toolbar {
                Button("Nuevo", systemImage: "plus") {
                    mostrarFormulario = true
                }
            }
            .sheet(isPresented: $mostrarFormulario) {
                NuevoProyectoView()
            }
        }
    }
}

// MARK: - Vista de detalle con filtro dinámico de tareas

struct DetallePoryectoView: View {
    @Bindable var proyecto: Proyecto
    @Environment(\.modelContext) private var contexto
    @State private var nuevoTitulo = ""
    @State private var filtro: FiltroTarea = .todas

    enum FiltroTarea: String, CaseIterable {
        case todas = "Todas"
        case pendientes = "Pendientes"
        case completadas = "Completadas"
    }

    // Filtramos las tareas del proyecto según el filtro seleccionado
    var tareasFiltradas: [Tarea] {
        switch filtro {
        case .todas:
            return proyecto.tareas.sorted { $0.prioridad > $1.prioridad }
        case .pendientes:
            return proyecto.tareas
                .filter { !$0.completada }
                .sorted { $0.prioridad > $1.prioridad }
        case .completadas:
            return proyecto.tareas
                .filter { $0.completada }
                .sorted { $0.fechaCreacion > $1.fechaCreacion }
        }
    }

    var body: some View {
        List {
            // Sección para agregar nueva tarea rápidamente
            Section {
                HStack {
                    TextField("Nueva tarea...", text: $nuevoTitulo)
                    Button("Agregar", systemImage: "plus.circle.fill") {
                        guard !nuevoTitulo.trimmingCharacters(in: .whitespaces).isEmpty else { return }
                        let tarea = Tarea(titulo: nuevoTitulo, proyecto: proyecto)
                        contexto.insert(tarea)
                        nuevoTitulo = ""
                    }
                    .disabled(nuevoTitulo.trimmingCharacters(in: .whitespaces).isEmpty)
                }
            }

            // Selector de filtro
            Section {
                Picker("Filt