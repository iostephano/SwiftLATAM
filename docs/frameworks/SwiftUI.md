---
sidebar_position: 1
title: SwiftUI
---

# SwiftUI

## ¿Qué es SwiftUI?

SwiftUI es el framework declarativo de Apple para construir interfaces de usuario en todas las plataformas del ecosistema Apple: iOS, iPadOS, macOS, watchOS, tvOS y visionOS. Introducido en la WWDC 2019, SwiftUI representa un cambio de paradigma fundamental respecto a UIKit y AppKit, ya que permite describir **qué** debe mostrar la interfaz en lugar de **cómo** debe construirse paso a paso. Esto se traduce en código más conciso, legible y menos propenso a errores.

El framework se basa en un sistema reactivo donde la interfaz se actualiza automáticamente cuando cambian los datos subyacentes, eliminando la necesidad de sincronizar manualmente el estado de la aplicación con la vista. SwiftUI aprovecha las características modernas de Swift como los *property wrappers*, los *result builders* y los protocolos con tipos asociados para ofrecer una API expresiva y fuertemente tipada que el compilador puede verificar en tiempo de compilación.

SwiftUI es ideal tanto para proyectos nuevos como para la modernización progresiva de aplicaciones existentes, gracias a su interoperabilidad bidireccional con UIKit y AppKit. Apple continúa invirtiendo activamente en su desarrollo, añadiendo componentes nuevos y mejorando el rendimiento en cada versión de sus sistemas operativos. Hoy en día, es la opción recomendada por Apple para iniciar cualquier proyecto nuevo.

## Casos de uso principales

- **Aplicaciones multiplataforma**: SwiftUI permite compartir la mayor parte del código de interfaz entre iOS, macOS, watchOS y tvOS, adaptando automáticamente los componentes al idioma visual de cada plataforma. Un mismo `NavigationStack` se comporta de forma nativa en iPhone y iPad sin modificaciones.

- **Prototipado rápido y desarrollo iterativo**: Gracias a las *previews* en tiempo real de Xcode, los desarrolladores pueden visualizar cambios instantáneamente sin compilar ni ejecutar la aplicación en un simulador. Esto acelera drásticamente el ciclo de diseño e implementación.

- **Aplicaciones con interfaces reactivas y dinámicas**: Paneles de control, dashboards financieros, aplicaciones de fitness con datos en tiempo real y cualquier escenario donde el estado cambie frecuentemente se beneficia enormemente del sistema reactivo de SwiftUI.

- **Widgets y extensiones del sistema**: Los Widgets de iOS y macOS, las complicaciones de watchOS, las Live Activities y los App Intents se construyen exclusivamente con SwiftUI. No existe alternativa en UIKit para estos componentes.

- **Aplicaciones para visionOS**: El desarrollo de aplicaciones para Apple Vision Pro requiere SwiftUI como base fundamental, combinado con RealityKit para experiencias inmersivas en realidad mixta.

- **Modernización progresiva de apps existentes en UIKit**: Mediante `UIHostingController` y `UIViewRepresentable`, es posible integrar vistas de SwiftUI dentro de proyectos UIKit y viceversa, permitiendo una migración gradual y controlada.

## Instalación y configuración

SwiftUI viene integrado de forma nativa en el SDK de Apple, por lo que **no requiere instalación adicional** ni gestores de dependencias. Está disponible desde:

| Plataforma | Versión mínima |
|------------|---------------|
| iOS        | 13.0          |
| macOS      | 10.15 (Catalina) |
| watchOS    | 6.0           |
| tvOS       | 13.0          |
| visionOS   | 1.0           |

> **Nota importante**: Aunque el soporte técnico comienza en iOS 13, muchas APIs esenciales como `LazyVGrid`, `@StateObject`, `task {}` y `NavigationStack` requieren versiones posteriores. Para proyectos nuevos en 2024-2025, se recomienda **iOS 17+** como *deployment target* para aprovechar al máximo las capacidades del framework.

### Crear un proyecto nuevo con SwiftUI

1. Abre **Xcode 15** o superior.
2. Selecciona **File → New → Project**.
3. Elige la plantilla **App** bajo la sección de la plataforma deseada.
4. En la configuración del proyecto, selecciona **SwiftUI** como *Interface* y **SwiftUI App** como *Life Cycle*.

### Import necesario

En cualquier archivo donde utilices componentes de SwiftUI, incluye el import correspondiente:

```swift
import SwiftUI
```

### Permisos en Info.plist

SwiftUI en sí mismo no requiere permisos especiales. Sin embargo, los permisos siguen siendo necesarios cuando se accede a recursos del sistema (cámara, ubicación, etc.) a través de otros frameworks utilizados dentro de vistas SwiftUI. Por ejemplo:

```xml
<!-- Solo si tu app SwiftUI usa la cámara -->
<key>NSCameraUsageDescription</key>
<string>Necesitamos acceso a la cámara para escanear documentos</string>

<!-- Solo si tu app SwiftUI usa la ubicación -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>Necesitamos tu ubicación para mostrarte lugares cercanos</string>
```

### Estructura del punto de entrada

```swift
import SwiftUI

@main
struct MiAplicacionApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

## Conceptos clave

### 1. Vistas como estructuras (`View` protocol)

En SwiftUI, cada componente visual es una estructura (`struct`) que conforma el protocolo `View`. Este protocolo requiere una única propiedad computada: `body`, que devuelve otra vista. Esta composición recursiva es el fundamento de todo el framework. Las vistas son **tipos de valor** (value types), lo que significa que son ligeras, inmutables por defecto y fáciles de comparar. SwiftUI utiliza esta característica para determinar eficientemente qué partes de la interfaz necesitan re-renderizarse.

```swift
struct SaludoView: View {
    var body: some View {
        Text("¡Hola, mundo!")
    }
}
```

### 2. Gestión de estado (`@State`, `@Binding`, `@Observable`)

El estado es el motor de SwiftUI. Cuando una propiedad marcada con un *property wrapper* de estado cambia, SwiftUI recalcula automáticamente las vistas que dependen de ella. La jerarquía principal es:

- **`@State`**: Estado local privado de una vista. Ideal para valores simples como booleanos, strings o números que solo necesita esa vista.
- **`@Binding`**: Referencia de lectura/escritura al estado de una vista padre. Permite que vistas hijas modifiquen datos que no les pertenecen.
- **`@Observable` (iOS 17+)**: Macro que convierte una clase en observable. Reemplaza a `ObservableObject` y `@Published`, simplificando enormemente el código.
- **`@Environment`**: Acceso a valores compartidos a través de la jerarquía de vistas, como el *color scheme*, la localización o dependencias inyectadas.

### 3. Composición declarativa y *View Builders*

SwiftUI utiliza *result builders* (anteriormente *function builders*) para permitir una sintaxis declarativa donde simplemente se listan las vistas hijas dentro de un closure. Los contenedores como `VStack`, `HStack`, `ZStack`, `List` y `ScrollView` organizan estas vistas siguiendo diferentes estrategias de layout:

```swift
VStack(alignment: .leading, spacing: 12) {
    Text("Título")
    Text("Subtítulo")
    Image(systemName: "star.fill")
}
```

### 4. Modificadores de vista (*View Modifiers*)

Los modificadores son métodos que se encadenan a una vista para transformar su apariencia o comportamiento. Cada modificador devuelve una **nueva vista envuelta**, lo que hace que el orden sea significativo. Un `.padding()` antes de `.background()` produce un resultado visual diferente a invertir el orden.

```swift
Text("Destacado")
    .font(.headline)
    .foregroundStyle(.white)
    .padding()
    .background(.blue, in: .capsule)
```

### 5. Sistema de navegación

Desde iOS 16, SwiftUI introduce `NavigationStack` con navegación basada en datos (*data-driven navigation*). En lugar de empujar vistas directamente, se mantiene un array de valores que representan la ruta de navegación. Esto permite deep linking, restauración de estado y un control programático completo:

```swift
@State private var path = NavigationPath()

NavigationStack(path: $path) {
    List(items) { item in
        NavigationLink(value: item) {
            Text(item.nombre)
        }
    }
    .navigationDestination(for: Item.self) { item in
        DetalleView(item: item)
    }
}
```

### 6. Ciclo de vida y efectos secundarios

SwiftUI proporciona modificadores para ejecutar código en momentos específicos del ciclo de vida de una vista: `.onAppear`, `.onDisappear`, `.task` (para trabajo asíncrono) y `.onChange(of:)` (para reaccionar a cambios de valores). El modificador `.task` es especialmente poderoso porque cancela automáticamente la tarea asíncrona cuando la vista desaparece.

## Ejemplo básico

```swift
import SwiftUI

/// Vista simple que muestra un contador con botones para incrementar y decrementar.
/// Demuestra el uso de @State para gestión de estado local.
struct ContadorView: View {
    // Estado local: SwiftUI observa cambios y re-renderiza automáticamente
    @State private var contador: Int = 0
    
    var body: some View {
        VStack(spacing: 24) {
            // Título descriptivo
            Text("Contador Simple")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            // Muestra el valor actual del contador con estilo dinámico
            Text("\(contador)")
                .font(.system(size: 72, weight: .bold, design: .rounded))
                .foregroundStyle(contador >= 0 ? .blue : .red)
                .contentTransition(.numericText()) // Animación al cambiar números
            
            // Controles horizontales
            HStack(spacing: 32) {
                // Botón para decrementar
                Button {
                    withAnimation(.snappy) {
                        contador -= 1
                    }
                } label: {
                    Image(systemName: "minus.circle.fill")
                        .font(.system(size: 44))
                        .foregroundStyle(.red)
                }
                
                // Botón para reiniciar
                Button("Reiniciar") {
                    withAnimation(.snappy) {
                        contador = 0
                    }
                }
                .buttonStyle(.bordered)
                .disabled(contador == 0)
                
                // Botón para incrementar
                Button {
                    withAnimation(.snappy) {
                        contador += 1
                    }
                } label: {
                    Image(systemName: "plus.circle.fill")
                        .font(.system(size: 44))
                        .foregroundStyle(.green)
                }
            }
        }
        .padding()
    }
}

// Preview para visualización en Xcode
#Preview {
    ContadorView()
}
```

## Ejemplo intermedio

```swift
import SwiftUI

// MARK: - Modelo de datos

/// Representa una tarea pendiente en la lista
struct Tarea: Identifiable, Hashable {
    let id = UUID()
    var titulo: String
    var descripcion: String
    var completada: Bool = false
    var prioridad: Prioridad
    let fechaCreacion: Date = .now
    
    enum Prioridad: String, CaseIterable, Identifiable {
        case baja = "Baja"
        case media = "Media"
        case alta = "Alta"
        
        var id: String { rawValue }
        
        var color: Color {
            switch self {
            case .baja: .green
            case .media: .orange
            case .alta: .red
            }
        }
        
        var icono: String {
            switch self {
            case .baja: "arrow.down.circle"
            case .media: "equal.circle"
            case .alta: "exclamationmark.circle"
            }
        }
    }
}

// MARK: - Vista principal: Lista de tareas

/// Vista principal que muestra una lista de tareas con capacidad de agregar,
/// completar y eliminar tareas. Demuestra @State, @Binding, List, sheet y
/// animaciones.
struct ListaTareasView: View {
    @State private var tareas: [Tarea] = [
        Tarea(titulo: "Comprar víveres", descripcion: "Leche, pan, frutas", prioridad: .media),
        Tarea(titulo: "Revisar pull requests", descripcion: "PRs pendientes del sprint", prioridad: .alta),
        Tarea(titulo: "Leer documentación SwiftUI", descripcion: "Nuevas APIs de iOS 18", prioridad: .baja)
    ]
    @State private var mostrarFormulario = false
    @State private var busqueda = ""
    
    /// Filtra tareas según el texto de búsqueda
    private var tareasFiltradas: [Tarea] {
        if busqueda.isEmpty {
            return tareas
        }
        return tareas.filter {
            $0.titulo.localizedCaseInsensitiveContains(busqueda) ||
            $0.descripcion.localizedCaseInsensitiveContains(busqueda)
        }
    }
    
    /// Calcula el progreso de tareas completadas
    private var progreso: Double {
        guard !tareas.isEmpty else { return 0 }
        return Double(tareas.filter(\.completada).count) / Double(tareas.count)
    }
    
    var body: some View {
        NavigationStack {
            List {
                // Sección de progreso
                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Progreso general")
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                            Spacer()
                            Text("\(Int(progreso * 100))%")
                                .font(.subheadline.bold())
                                .foregroundStyle(.blue)
                        }
                        
                        ProgressView(value: progreso)
                            .tint(progreso == 1.0 ? .green : .blue)
                            .animation(.smooth, value: progreso)
                    }
                    .padding(.vertical, 4)
                }
                
                // Sección de tareas pendientes
                Section("Pendientes (\(tareasFiltradas.filter { !$0.completada }.count))") {
                    ForEach($tareas) { $tarea in
                        if !tarea.completada && coincideConBusqueda(tarea) {
                            FilaTareaView(tarea: $tarea)
                        }
                    }
                    .onDelete { indexSet in
                        withAnimation {
                            tareas.remove(atOffsets: indexSet)
                        }
                    }
                }
                
                // Sección de tareas completadas
                Section("Completadas (\(tareasFiltradas.filter(\.completada).count))") {
                    ForEach($tareas) { $tarea in
                        if tarea.completada && coincideConBusqueda(tarea) {
                            FilaTareaView(tarea: $tarea)
                        }
                    }
                    .onDelete { indexSet in
                        withAnimation {
                            tareas.remove(atOffsets: indexSet)