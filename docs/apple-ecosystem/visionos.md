---
sidebar_position: 1
title: Visionos
---

# visionOS: Desarrollo para Apple Vision Pro

## ¿Qué es visionOS?

visionOS es el sistema operativo de Apple diseñado específicamente para **Apple Vision Pro**, su dispositivo de computación espacial. Lanzado en 2024, representa una nueva dimensión en el ecosistema Apple donde las aplicaciones ya no están confinadas a una pantalla plana, sino que coexisten en el **espacio tridimensional** que rodea al usuario.

Para un desarrollador iOS, visionOS no es un territorio completamente desconocido. Apple diseñó deliberadamente este sistema para que la transición desde iOS y iPadOS fuera lo más natural posible. Si ya dominas **SwiftUI**, tienes el 70% del camino recorrido.

## ¿Por qué debería importarte como dev iOS en LATAM?

Quizás pienses: *"Apple Vision Pro ni siquiera se vende en mi país"*. Es una objeción válida, pero considera lo siguiente:

1. **El mercado remoto es tu mercado real.** La mayoría de los desarrolladores en Latinoamérica trabajan para empresas en EE.UU., Europa o clientes internacionales. Las empresas que ya adoptan Vision Pro **buscan talento que domine visionOS**.

2. **Ventana de oportunidad única.** Estamos en la fase temprana de adopción. Así como quienes dominaron iOS en 2008 construyeron carreras extraordinarias, posicionarte ahora en computación espacial te da una ventaja competitiva brutal.

3. **Diferenciación salarial.** Los desarrolladores con experiencia en visionOS pueden negociar tarifas significativamente superiores. La oferta de talento es mínima y la demanda crece.

4. **Reutilización de conocimientos.** Todo lo que aprendas — SwiftUI, RealityKit, ARKit — es transferible a iOS y iPadOS. No estás apostando a un solo caballo.

## Arquitectura de una app en visionOS

visionOS introduce tres tipos de experiencias inmersivas:

| Tipo | Descripción | Caso de uso |
|------|-------------|-------------|
| **Window** | Ventanas 2D flotantes en el espacio | Apps de productividad, lectores, dashboards |
| **Volume** | Contenedores 3D con contenido tridimensional | Visualización de modelos, juegos de mesa |
| **Full Space** | Experiencia inmersiva que ocupa todo el entorno | Simulaciones, entretenimiento, capacitación |

### La jerarquía fundamental

```
App
├── WindowGroup (ventanas 2D)
├── WindowGroup + .volumetric (volúmenes 3D)
└── ImmersiveSpace (espacios inmersivos)
```

## Tu primera app para visionOS

### Paso 1: Configuración del entorno

Necesitas:
- **Xcode 15.2+** (idealmente Xcode 16)
- **macOS Sonoma 14.0+**
- El simulador de visionOS (se descarga desde Xcode → Settings → Platforms)

> 💡 **No necesitas un Apple Vision Pro físico para empezar.** El simulador es sorprendentemente funcional para desarrollo y pruebas iniciales.

### Paso 2: Crear el proyecto

En Xcode, selecciona **File → New → Project → visionOS → App**. Elige:
- **Initial Scene**: Window
- **Immersive Space**: Mixed (para empezar)
- **Immersive Style**: Mixed

### Paso 3: La estructura básica

```swift
import SwiftUI

@main
struct MiAppVisionOS: App {
    var body: some Scene {
        // Ventana principal 2D
        WindowGroup {
            ContentView()
        }

        // Espacio inmersivo bajo demanda
        ImmersiveSpace(id: "espacioInmersivo") {
            ImmersiveView()
        }
    }
}
```

```swift
import SwiftUI

struct ContentView: View {
    @Environment(\.openImmersiveSpace) var openImmersiveSpace
    @Environment(\.dismissImmersiveSpace) var dismissImmersiveSpace
    @State private var espacioAbierto = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Text("🇲🇽 Mi Primera App Espacial")
                    .font(.extraLargeTitle)

                Text("Bienvenido a la computación espacial")
                    .font(.title2)
                    .foregroundStyle(.secondary)

                Toggle("Experiencia inmersiva", isOn: $espacioAbierto)
                    .toggleStyle(.button)
                    .padding()
            }
            .padding(48)
            .onChange(of: espacioAbierto) { _, nuevoValor in
                Task {
                    if nuevoValor {
                        await openImmersiveSpace(id: "espacioInmersivo")
                    } else {
                        await dismissImmersiveSpace()
                    }
                }
            }
        }
    }
}
```

Observa cómo **el código es prácticamente idéntico al de una app SwiftUI para iOS**. Las diferencias principales son los modificadores específicos de visionOS y las APIs de espacios inmersivos.

### Paso 4: Agregar contenido 3D con RealityKit

Aquí es donde la magia sucede. visionOS usa **RealityKit** como motor de renderizado 3D:

```swift
import SwiftUI
import RealityKit

struct ImmersiveView: View {
    var body: some View {
        RealityView { content in
            // Crear una esfera
            let esfera = MeshResource.generateSphere(radius: 0.1)
            let material = SimpleMaterial(
                color: .blue,
                roughness: 0.2,
                isMetallic: true
            )
            let entidadEsfera = ModelEntity(
                mesh: esfera,
                materials: [material]
            )

            // Posicionar a 1.5 metros frente al usuario
            entidadEsfera.position = SIMD3<Float>(0, 1.5, -1.5)

            // Habilitar interacción
            entidadEsfera.components.set(
                InputTargetComponent(allowedInputTypes: .indirect)
            )
            entidadEsfera.generateCollisionShapes(recursive: true)

            content.add(entidadEsfera)
        }
        .gesture(
            TapGesture()
                .targetedToAnyEntity()
                .onEnded { valor in
                    // Animar la entidad al tocarla
                    let entidad = valor.entity
                    let desplazamiento = entidad.position.y + 0.2
                    entidad.move(
                        to: Transform(
                            translation: SIMD3<Float>(
                                entidad.position.x,
                                desplazamiento,
                                entidad.position.z
                            )
                        ),
                        relativeTo: nil,
                        duration: 0.5
                    )
                }
        )
    }
}
```

### Paso 5: Ventanas volumétricas

Las ventanas volumétricas permiten mostrar contenido 3D sin necesidad de un espacio inmersivo completo:

```swift
import SwiftUI
import RealityKit

@main
struct AppVolumetrica: App {
    var body: some Scene {
        WindowGroup(id: "volumen-principal") {
            VistaVolumetrica()
        }
        .windowStyle(.volumetric)
        .defaultSize(width: 0.5, height: 0.5, depth: 0.5, in: .meters)
    }
}

struct VistaVolumetrica: View {
    @State private var angulo: Angle = .zero

    var body: some View {
        RealityView { content in
            if let modelo = try? await ModelEntity(
                named: "MiModelo3D" // Archivo .usdz en el bundle
            ) {
                modelo.scale = SIMD3<Float>(repeating: 0.01)
                content.add(modelo)
            }
        }
        .rotation3DEffect(angulo, axis: .y)
        .gesture(
            DragGesture()
                .onChanged { valor in
                    angulo = .degrees(valor.translation.width)
                }
        )
    }
}
```

## Ornamentos: UI contextual única de visionOS

Los **ornamentos** son elementos de interfaz que flotan alrededor de las ventanas, una capacidad exclusiva de visionOS:

```swift
struct ContentView: View {
    @State private var herramientaSeleccionada: Herramienta = .pincel

    var body: some View {
        LienzoView(herramienta: herramientaSeleccionada)
            .ornament(
                visibility: .visible,
                attachmentAnchor: .scene(.bottom)
            ) {
                HStack(spacing: 16) {
                    ForEach(Herramienta.allCases, id: \.self) { herramienta in
                        Button {
                            herramientaSeleccionada = herramienta
                        } label: {
                            Image(systemName: herramienta.icono)
                                .font(.title)
                        }
                        .buttonStyle(.borderless)
                        .padding(8)
                        .background(
                            herramientaSeleccionada == herramienta
                                ? .blue.opacity(0.3)
                                : .clear,
                            in: .capsule
                        )
                    }
                }
                .padding(16)
                .glassBackgroundEffect()
            }
    }
}

enum Herramienta: CaseIterable {
    case pincel, borrador, selector, texto

    var icono: String {
        switch self {
        case .pincel: return "paintbrush.fill"
        case .borrador: return "eraser.fill"
        case .selector: return "eyedropper"
        case .texto: return "textformat"
        }
    }
}
```

## Interacciones en visionOS

El modelo de interacción es radicalmente diferente al táctil. En visionOS, el usuario interactúa mediante:

### Mirada + Pellizco (Look and Pinch)

```swift
struct InteraccionesView: View {
    @State private var posicion: CGPoint = .zero

    var body: some View {
        RealityView { content in
            // Configurar escena
        }
        .gesture(
            // Gesto de arrastre con mirada + pellizco
            DragGesture()
                .targetedToAnyEntity()
                .onChanged { valor in
                    valor.entity.position.x = Float(
                        valor.location3D.x
                    )
                    valor.entity.position.y = Float(
                        valor.location3D.y
                    )
                }
        )
        .gesture(
            // Gesto de zoom con dos manos
            MagnifyGesture()
                .targetedToAnyEntity()
                .onChanged { valor in
                    let escala = Float(valor.magnification)
                    valor.entity.scale = SIMD3<Float>(
                        repeating: escala
                    )
                }
        )
    }
}
```

### Hover Effects

En visionOS, los elementos responden visualmente cuando el usuario **mira** hacia ellos:

```swift
struct TarjetaEspacial: View {
    var titulo: String
    var descripcion: String

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(titulo)
                .font(.title2)
                .fontWeight(.bold)

            Text(descripcion)
                .font(.body)
                .foregroundStyle(.secondary)
        }
        .padding(24)
        .frame(width: 320)
        .background(.ultraThinMaterial)
        .clipShape(.rect(cornerRadius: 20))
        .hoverEffect(.highlight) // Efecto visual al mirar
    }
}
```

## Portabilidad: de iOS a visionOS

Una de las mayores ventajas es que **muchas apps iOS funcionan en visionOS sin cambios**. Apple ofrece tres niveles de adopción:

### Nivel 1: Compatible (sin cambios)

Tu app iOS existente corre automáticamente como una ventana plana en visionOS.

### Nivel 2: Diseñada para visionOS (cambios menores)

```swift
struct AdaptableView: View {
    var body: some View {
        List {
            ForEach(productos) { producto in
                FilaProducto(producto: producto)
            }
        }
        #if os(visionOS)
        .listStyle(.plain)
        .frame(minWidth: 400, minHeight: 600)
        #else
        .listStyle(.insetGrouped)
        #endif
    }
}
```

### Nivel 3: Nativa visionOS (experiencia completa)

Aprovecha volumenes, espacios inmersivos y todas las capacidades espaciales que cubrimos anteriormente.

## Arquitectura recomendada para apps multiplatforma

```swift
// Modelo compartido entre iOS, iPadOS y visionOS
@Observable
class ModeloProducto {
    var productos: [Producto] = []
    var seleccionado: Producto?
    var estaCargando = false

    func cargarProductos() async throws {
        estaCargando = true
        defer { estaCargando = false }

        productos = try await ServicioAPI.shared.obtenerProductos()
    }
}

// Vista que adapta su presentación por plataforma
struct CatalogoView: View {
    @State private var modelo = ModeloProducto()

    var body: some View {
        Group {
            #if os(visionOS)
            CatalogoEspacialView(modelo: modelo)
            #elseif os(iOS)
            CatalogoiOSView(modelo: modelo)
            #endif
        }
        .task {
            try? await modelo.cargarProductos()
        }
    }
}

// Solo para visionOS: vista 3D del producto
#if os(visionOS)
struct CatalogoEspacialView: View {
    var modelo: ModeloProducto

    var body: some View {
        HStack {
            // Panel de lista
            List(modelo.productos, selection: $modelo.seleccionado) {
                producto in
                Text(producto.nombre)
            }
            .frame(width: 300)

            // Visualización 3D del producto seleccionado
            if let producto = modelo.seleccionado {
                Model3D(named: producto.modelo3DName) { fase in
                    switch fase {
                    case .success(let modelo):
                        modelo
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(depth: 200)
                    case .failure:
                        Text("Error al cargar modelo")
                    case .empty:
                        ProgressView()
                    @unknown default:
                        EmptyView()
                    }
                }
            }
        }
    }
}
#endif
```

## Reality Composer Pro

**Reality Composer Pro** es la herramienta de Xcode para crear escenas 3D para visionOS. Es tu equivalente a Interface Builder, pero para contenido espacial.

### Flujo de trabajo típico

1. **Importar modelos** `.usdz` o `.reality`
2. **Componer la escena** visualmente en el editor 3D
3. **Agregar comportamientos** y físicas
4. **Cargar la escena** desde código:

```swift
import RealityKit

struct EscenaRealityView: View {
    var body: some View {
        RealityView