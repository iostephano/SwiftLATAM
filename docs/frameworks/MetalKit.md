---
sidebar_position: 1
title: MetalKit
---

# MetalKit

## ¿Qué es MetalKit?

MetalKit es un framework de Apple que simplifica enormemente el desarrollo de aplicaciones que utilizan **Metal**, la API de gráficos y computación de bajo nivel. Mientras que Metal proporciona acceso directo a la GPU para renderizado 3D, procesamiento de imágenes y computación paralela, MetalKit actúa como una capa de conveniencia que reduce significativamente el código repetitivo (boilerplate) necesario para poner en marcha una pipeline gráfica funcional.

El framework proporciona tres pilares fundamentales: **MTKView**, una vista especializada que gestiona automáticamente el ciclo de renderizado y la cadena de intercambio (swap chain); **MTKTextureLoader**, un cargador de texturas que soporta múltiples formatos de imagen y los convierte en texturas Metal listas para usar; y **MTKMesh/MTKModelIO**, utilidades para cargar modelos 3D complejos directamente desde archivos compatibles con Model I/O. Estos componentes eliminan cientos de líneas de configuración manual que serían necesarias trabajando exclusivamente con Metal.

MetalKit está disponible en **iOS 9+, macOS 10.11+, tvOS 9+ y visionOS 1.0+**, y es la opción recomendada por Apple siempre que se necesite renderizado personalizado con Metal. Es ideal tanto para desarrolladores que están comenzando con gráficos de bajo nivel como para equipos experimentados que buscan acelerar el tiempo de desarrollo sin sacrificar el control granular que Metal ofrece.

## Casos de uso principales

- **Renderizado 3D en tiempo real**: Creación de escenas tridimensionales con iluminación, sombras y materiales personalizados. MetalKit gestiona el ciclo de renderizado y la presentación de fotogramas, permitiendo al desarrollador concentrarse en la lógica de la escena.

- **Procesamiento de imágenes y filtros personalizados**: Aplicación de filtros y efectos visuales mediante compute shaders de Metal. MTKTextureLoader facilita la carga de imágenes origen y MTKView muestra el resultado procesado en tiempo real.

- **Videojuegos y motores gráficos**: Desarrollo de juegos 2D y 3D con control total sobre la pipeline de renderizado. MetalKit proporciona la infraestructura de visualización mientras Metal permite optimizaciones específicas para cada tipo de juego.

- **Visualización científica y de datos**: Representación gráfica de conjuntos de datos masivos aprovechando la potencia de la GPU. Gráficos interactivos con millones de puntos de datos renderizados a 60 FPS o más.

- **Realidad aumentada personalizada**: Integración con ARKit para renderizar contenido 3D personalizado sobre la cámara del dispositivo, reemplazando SceneKit o RealityKit cuando se necesita control total del pipeline gráfico.

- **Procesamiento de vídeo en tiempo real**: Aplicación de efectos y transformaciones a fotogramas de vídeo en tiempo real, combinando AVFoundation para la captura con MetalKit para el procesamiento y la visualización.

## Instalación y configuración

### Agregar MetalKit al proyecto

MetalKit viene incluido en el SDK de Apple, por lo que **no requiere dependencias externas**. Solo necesitas importar el framework:

```swift
import MetalKit
import Metal // Generalmente necesario junto a MetalKit
```

### Configuración en Xcode

1. **Verificar el target**: Asegúrate de que tu proyecto apunta a un dispositivo compatible (iOS 9+, macOS 10.11+). **El simulador de iOS tiene soporte limitado para Metal a partir de Xcode 11+**, pero el rendimiento difiere significativamente del hardware real.

2. **Linking automático**: En proyectos modernos con Xcode 15+, el linking de MetalKit es automático al usar `import MetalKit`. Si trabajas con proyectos legacy, ve a **Build Phases > Link Binary With Libraries** y añade `MetalKit.framework` y `Metal.framework`.

3. **Archivos de shaders**: Crea un archivo con extensión `.metal` para tus funciones de shader. Xcode los compilará automáticamente en una biblioteca Metal (`default.metallib`) durante el build.

```
MiProyecto/
├── Sources/
│   ├── Renderer.swift
│   ├── GameViewController.swift
│   └── Shaders.metal        // ← Archivo de shaders
├── Resources/
│   ├── Assets.xcassets
│   └── Models/              // ← Modelos 3D opcionales
└── Info.plist
```

### Permisos en Info.plist

MetalKit **no requiere permisos especiales** en Info.plist. Sin embargo, si combinas Metal con la cámara (por ejemplo, para AR o procesamiento de vídeo), necesitarás:

```xml
<key>NSCameraUsageDescription</key>
<string>Se necesita acceso a la cámara para procesamiento de vídeo en tiempo real</string>
```

### Compatibilidad con SwiftUI

Para usar MTKView en SwiftUI, necesitarás envolver la vista mediante `UIViewRepresentable` (iOS) o `NSViewRepresentable` (macOS):

```swift
import SwiftUI
import MetalKit

struct MetalView: UIViewRepresentable {
    func makeUIView(context: Context) -> MTKView {
        let mtkView = MTKView()
        // Configuración inicial
        return mtkView
    }

    func updateUIView(_ uiView: MTKView, context: Context) {}
}
```

## Conceptos clave

### 1. MTKView — La vista de renderizado

`MTKView` es una subclase de `UIView` (iOS) / `NSView` (macOS) diseñada específicamente para mostrar contenido renderizado con Metal. Gestiona automáticamente los **drawables** (buffers de presentación), el **depth/stencil buffer** y el ciclo de renderizado. Puede funcionar en modo continuo (ideal para juegos) o bajo demanda (ideal para interfaces que solo cambian ante interacciones).

```swift
let mtkView = MTKView(frame: .zero, device: MTLCreateSystemDefaultDevice())
mtkView.preferredFramesPerSecond = 60
mtkView.colorPixelFormat = .bgra8Unorm
mtkView.depthStencilPixelFormat = .depth32Float
mtkView.clearColor = MTLClearColor(red: 0.0, green: 0.0, blue: 0.0, alpha: 1.0)
```

### 2. MTKViewDelegate — El protocolo de renderizado

El protocolo `MTKViewDelegate` define dos métodos esenciales: `draw(in:)`, que se invoca en cada fotograma para ejecutar los comandos de renderizado, y `mtkView(_:drawableSizeWillChange:)`, que notifica cambios en el tamaño de la vista (rotación de dispositivo, redimensionamiento de ventana). Este patrón de delegado separa limpiamente la lógica de renderizado de la vista.

### 3. MTKTextureLoader — Carga de texturas simplificada

`MTKTextureLoader` convierte imágenes desde múltiples fuentes (archivos, URLs, `CGImage`, `MDLTexture`, assets del catálogo) en objetos `MTLTexture` listos para usar en shaders. Soporta carga **síncrona y asíncrona**, generación automática de mipmaps y diversas opciones de formato y orientación.

### 4. MTKMesh — Geometría desde Model I/O

`MTKMesh` actúa como puente entre el framework Model I/O (`ModelIO`) y Metal. Permite cargar modelos 3D desde formatos como `.obj`, `.usdz` o `.abc`, y los convierte automáticamente en vertex buffers compatibles con Metal, incluyendo información de submallas y descriptores de atributos.

### 5. Pipeline de renderizado (Render Pipeline)

Aunque no es exclusivo de MetalKit, comprender la pipeline es esencial. Se configura mediante `MTLRenderPipelineDescriptor`, donde se especifican las funciones de vértice y fragmento compiladas desde archivos `.metal`. MetalKit simplifica la obtención del descriptor del pixel format y otros parámetros directamente desde `MTKView`.

### 6. Command Queue y Command Buffers

El `MTLCommandQueue` es la cola donde se encolan los buffers de comandos (`MTLCommandBuffer`). Cada fotograma típicamente crea un command buffer, codifica comandos de renderizado mediante un `MTLRenderCommandEncoder`, y finalmente presenta el drawable. MetalKit se encarga de proporcionar el drawable actual a través de `currentDrawable` y el descriptor de pase de renderizado mediante `currentRenderPassDescriptor`.

## Ejemplo básico

Este ejemplo muestra cómo configurar una `MTKView` para limpiar la pantalla con un color que cambia dinámicamente:

```swift
import UIKit
import MetalKit

// MARK: - ViewController con MTKView básico
class BasicMetalViewController: UIViewController {

    // Referencia al dispositivo Metal (GPU)
    private var metalDevice: MTLDevice!

    // Cola de comandos para enviar trabajo a la GPU
    private var commandQueue: MTLCommandQueue!

    // La vista MetalKit que muestra el contenido renderizado
    private var mtkView: MTKView!

    // Contador para animar el color de fondo
    private var time: Float = 0.0

    override func viewDidLoad() {
        super.viewDidLoad()
        configurarMetal()
    }

    private func configurarMetal() {
        // 1. Obtener referencia al dispositivo Metal (GPU por defecto)
        guard let device = MTLCreateSystemDefaultDevice() else {
            fatalError("Metal no está disponible en este dispositivo")
        }
        metalDevice = device

        // 2. Crear la cola de comandos
        guard let queue = device.makeCommandQueue() else {
            fatalError("No se pudo crear la cola de comandos")
        }
        commandQueue = queue

        // 3. Configurar la MTKView
        mtkView = MTKView(frame: view.bounds, device: device)
        mtkView.autoresizingMask = [.flexibleWidth, .flexibleHeight]

        // Formato de color de los píxeles de salida
        mtkView.colorPixelFormat = .bgra8Unorm

        // 60 fotogramas por segundo
        mtkView.preferredFramesPerSecond = 60

        // Asignar el delegado para recibir callbacks de renderizado
        mtkView.delegate = self

        // 4. Añadir la vista a la jerarquía
        view.addSubview(mtkView)
    }
}

// MARK: - MTKViewDelegate
extension BasicMetalViewController: MTKViewDelegate {

    /// Se llama cuando cambia el tamaño de la vista (ej: rotación)
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
        print("Nuevo tamaño del drawable: \(size)")
    }

    /// Se llama en cada fotograma para dibujar contenido
    func draw(in view: MTKView) {
        // Incrementar el tiempo para la animación
        time += 1.0 / Float(view.preferredFramesPerSecond)

        // Calcular un color que oscile suavemente
        let rojo = Double(sin(time) * 0.5 + 0.5)
        let verde = Double(cos(time * 0.7) * 0.5 + 0.5)
        let azul = Double(sin(time * 1.3) * 0.5 + 0.5)

        // Establecer el color de limpieza de la vista
        view.clearColor = MTLClearColor(
            red: rojo,
            green: verde,
            blue: azul,
            alpha: 1.0
        )

        // Obtener el descriptor del pase de renderizado actual
        guard let renderPassDescriptor = view.currentRenderPassDescriptor,
              let commandBuffer = commandQueue.makeCommandBuffer(),
              let renderEncoder = commandBuffer.makeRenderCommandEncoder(
                  descriptor: renderPassDescriptor
              ) else {
            return
        }

        // En este ejemplo básico, solo limpiamos la pantalla con el color
        // No dibujamos geometría adicional
        renderEncoder.endEncoding()

        // Presentar el drawable en pantalla
        if let drawable = view.currentDrawable {
            commandBuffer.present(drawable)
        }

        // Enviar el buffer de comandos a la GPU
        commandBuffer.commit()
    }
}
```

## Ejemplo intermedio

Este ejemplo renderiza un triángulo con colores por vértice, incluyendo la configuración completa de la pipeline de renderizado:

**Shaders.metal** — Archivo de funciones de shader:

```metal
#include <metal_stdlib>
using namespace metal;

// Estructura que recibe datos del vertex buffer
struct VertexIn {
    float3 position [[attribute(0)]];
    float4 color    [[attribute(1)]];
};

// Estructura que pasa datos del vertex shader al fragment shader
struct VertexOut {
    float4 position [[position]];
    float4 color;
};

// Uniforms: datos que cambian por fotograma (ej: tiempo de animación)
struct Uniforms {
    float time;
    float2 resolution;
};

// MARK: - Vertex Shader
vertex VertexOut vertexShader(
    VertexIn in [[stage_in]],
    constant Uniforms &uniforms [[buffer(1)]]
) {
    VertexOut out;

    // Aplicar una rotación sutil basada en el tiempo
    float angle = uniforms.time * 0.5;
    float cosA = cos(angle);
    float sinA = sin(angle);

    float3 rotatedPos = float3(
        in.position.x * cosA - in.position.y * sinA,
        in.position.x * sinA + in.position.y * cosA,
        in.position.z
    );

    out.position = float4(rotatedPos, 1.0);
    out.color = in.color;

    return out;
}

// MARK: - Fragment Shader
fragment float4 fragmentShader(VertexOut in [[stage_in]]) {
    return in.color;
}
```

**TriangleRenderer.swift** — Renderer completo:

```swift
import MetalKit

// MARK: - Estructura de vértice (debe coincidir con el shader)
struct Vertex {
    var position: SIMD3<Float>  // Posición XYZ
    var color: SIMD4<Float>     // Color RGBA
}

// MARK: - Uniforms enviados a la GPU cada fotograma
struct Uniforms {
    var time: Float
    var resolution: SIMD2<Float>
}

// MARK: - Renderer del triángulo
class TriangleRenderer: NSObject {

    private let device: MTLDevice
    private let commandQueue: MTLCommandQueue
    private var pipelineState: MTLRenderPipelineState!
    private var vertexBuffer: MTLBuffer!
    private var time: Float = 0.0

    // Definición de los vértices del triángulo con colores
    private let vertices: [Vertex] = [
        // Vértice superior - Rojo
        Vertex(position: SIMD3<Float>(0.0,  0.75, 0.0),
               color: SIMD4<Float>(1.0, 0.2, 0.2, 1.0)),

        // Vértice inferior izquierdo - Verde
        Vertex(position: SIMD3<Float>(-0.75, -0.75, 0.0),
               color: SIMD4<Float>(0.2, 1.0, 0.2, 1.0)),

        // Vértice