---
sidebar_position: 1
title: Metal
---

# Metal

## ¿Qué es Metal?

Metal es el framework de bajo nivel de Apple diseñado para proporcionar acceso casi directo a la unidad de procesamiento gráfico (GPU) de los dispositivos Apple. Lanzado en 2014, Metal permite a los desarrolladores ejecutar cálculos gráficos y de propósito general con una eficiencia extraordinaria, eliminando gran parte de la sobrecarga que frameworks de nivel superior introducen. Es el equivalente de Apple a Vulkan (Khronos Group) o DirectX 12 (Microsoft), pero optimizado específicamente para el hardware de iPhone, iPad, Mac, Apple TV y Apple Vision Pro.

Metal sirve como la base sobre la que se construyen muchas tecnologías de Apple, incluyendo Core Animation, Core Image, SceneKit, RealityKit y hasta el propio compositor de ventanas del sistema operativo. Cuando un desarrollador necesita el máximo rendimiento gráfico —ya sea para renderizar escenas 3D complejas, aplicar filtros de imagen en tiempo real, entrenar modelos de machine learning o procesar datos masivos en paralelo— Metal es la herramienta indicada.

Deberías considerar usar Metal directamente cuando los frameworks de alto nivel no satisfacen tus necesidades de rendimiento, cuando necesitas control granular sobre el pipeline de renderizado, cuando quieres implementar shaders personalizados o cuando tu aplicación requiere cómputo en GPU (GPGPU). Si bien la curva de aprendizaje es pronunciada comparada con SceneKit o SpriteKit, las ganancias en rendimiento y flexibilidad son significativas.

## Casos de uso principales

- **Motores de renderizado 3D personalizados**: Construir pipelines de renderizado completos con control total sobre vértices, fragmentos, iluminación y post-procesamiento. Ideal para juegos AAA o visualizaciones arquitectónicas.

- **Procesamiento de imagen y video en tiempo real**: Aplicar filtros, efectos y transformaciones a imágenes o flujos de video con latencia mínima. Aplicaciones de cámara, editores de foto/video y apps de realidad aumentada se benefician enormemente.

- **Cómputo de propósito general (GPGPU)**: Ejecutar algoritmos paralelos masivos como simulaciones de partículas, simulaciones físicas, procesamiento de señales, criptografía o cualquier tarea que se beneficie de paralelismo masivo.

- **Machine Learning e inferencia**: Metal Performance Shaders (MPS) y el backend de Core ML usan Metal para acelerar operaciones de redes neuronales. También puedes escribir kernels de cómputo personalizados para operaciones ML especializadas.

- **Visualización científica y de datos**: Renderizar millones de puntos de datos, gráficos volumétricos, simulaciones de fluidos o cualquier visualización que requiera procesamiento intensivo de geometría y fragmentos.

- **Efectos de post-procesamiento y shaders artísticos**: Implementar bloom, depth of field, screen-space ambient occlusion (SSAO), ray marching y otros efectos que requieren shaders de fragmentos personalizados.

## Instalación y configuración

Metal viene incluido como framework del sistema en todas las plataformas Apple, por lo que **no necesitas instalarlo mediante gestores de paquetes**. Sin embargo, hay varios pasos de configuración importantes:

### Requisitos del proyecto

```
Plataforma mínima: iOS 8.0 / macOS 10.11 / tvOS 9.0 / visionOS 1.0
Lenguaje: Swift 5+ / Objective-C
Hardware: Cualquier dispositivo con GPU Apple (A7 o posterior, cualquier Apple Silicon)
```

### Imports necesarios

```swift
import Metal          // API principal: dispositivos, colas de comandos, buffers, pipelines
import MetalKit       // Utilidades: MTKView, carga de texturas, carga de modelos
import MetalPerformanceShaders // Operaciones optimizadas: convoluciones, resize, redes neuronales
import simd           // Tipos matemáticos: matrices, vectores (se importa implícitamente)
```

### Configuración en Xcode

1. **Crear el proyecto** seleccionando la plantilla adecuada (Game o App).
2. En **Build Settings**, verificar que `METAL_LIBRARY_OUTPUT_DIR` esté configurado (normalmente lo está por defecto).
3. Los archivos de shader (`.metal`) se agregan directamente al target y se compilan automáticamente en un `default.metallib`.
4. Para **macOS con Catalyst**, asegúrate de que el entitlement de GPU esté habilitado si tu app corre en sandbox.

### Info.plist (si aplica)

En la mayoría de los casos no se necesitan permisos especiales en `Info.plist`. Sin embargo, para aplicaciones macOS que necesiten acceder a GPUs externas:

```xml
<key>GPUEjectPolicy</key>
<string>relaunch</string>
<key>GPUSelectionPolicy</key>
<string>preferRemovable</string>
```

### Archivo de shader básico (`Shaders.metal`)

```metal
#include <metal_stdlib>
using namespace metal;

// Este archivo se compila automáticamente al agregarlo al target
vertex float4 vertex_main(uint vertexID [[vertex_id]]) {
    return float4(0.0, 0.0, 0.0, 1.0);
}

fragment half4 fragment_main() {
    return half4(1.0, 0.0, 0.0, 1.0);
}
```

## Conceptos clave

### 1. MTLDevice — El punto de entrada

`MTLDevice` representa la GPU física. Es el objeto raíz desde el cual creas todos los demás recursos de Metal: buffers, texturas, pipelines y colas de comandos. En iOS solo hay un dispositivo disponible; en macOS puede haber varios (GPU integrada, discreta, externa).

```swift
guard let device = MTLCreateSystemDefaultDevice() else {
    fatalError("Metal no está soportado en este dispositivo")
}
```

### 2. Command Queue y Command Buffers — El sistema de envío

Metal usa un modelo de envío basado en colas. Un **MTLCommandQueue** es una cola serie de larga duración que persiste durante toda la vida de la aplicación. Los **MTLCommandBuffer** son objetos efímeros que agrupan un conjunto de comandos codificados para enviarlos a la GPU como una unidad atómica.

### 3. Encoders — La codificación de trabajo

Los **encoders** escriben comandos dentro de un command buffer. Existen tres tipos principales:
- **MTLRenderCommandEncoder**: Para operaciones de renderizado (dibujar geometría).
- **MTLComputeCommandEncoder**: Para operaciones de cómputo general (kernels/shaders de cómputo).
- **MTLBlitCommandEncoder**: Para operaciones de copia y transferencia de datos entre recursos.

### 4. Pipeline State — La configuración del pipeline

Un **MTLRenderPipelineState** o **MTLComputePipelineState** es un objeto precompilado e inmutable que define cómo la GPU procesará los datos. Incluye las funciones de shader, formatos de píxel, configuración de blending, etc. Crear pipelines es costoso, por lo que deben crearse una vez y reutilizarse.

### 5. Buffers y Texturas — Los recursos de datos

**MTLBuffer** almacena datos arbitrarios (vértices, índices, uniformes, datos de cómputo). **MTLTexture** almacena datos de imagen en formatos específicos. Ambos residen en memoria accesible por la GPU y, en plataformas con memoria unificada (Apple Silicon), también por la CPU sin necesidad de copias explícitas.

### 6. Render Pass Descriptor — La descripción del destino

Un **MTLRenderPassDescriptor** describe los attachments de color, profundidad y stencil donde se renderizará. Define acciones de carga (load) y almacenamiento (store) que determinan si el contenido previo se conserva, se limpia o se descarta, lo cual tiene un impacto significativo en el rendimiento.

## Ejemplo básico

Este ejemplo muestra la configuración mínima para renderizar un triángulo de colores usando Metal y MetalKit:

```swift
import MetalKit

/// Renderer básico que dibuja un triángulo de colores en pantalla.
/// Demuestra la configuración mínima del pipeline de Metal.
class TrianguloBasicoRenderer: NSObject, MTKViewDelegate {
    
    // MARK: - Propiedades fundamentales de Metal
    
    /// Referencia a la GPU
    private let device: MTLDevice
    
    /// Cola de comandos para enviar trabajo a la GPU
    private let commandQueue: MTLCommandQueue
    
    /// Estado del pipeline de renderizado (precompilado e inmutable)
    private let pipelineState: MTLRenderPipelineState
    
    // MARK: - Datos de geometría
    
    /// Buffer con los vértices del triángulo (posición + color)
    private let vertexBuffer: MTLBuffer
    
    /// Estructura que define un vértice con posición y color
    struct Vertice {
        var posicion: SIMD2<Float>   // x, y
        var color: SIMD4<Float>      // r, g, b, a
    }
    
    // MARK: - Inicialización
    
    init?(mtkView: MTKView) {
        // 1. Obtener referencia al dispositivo GPU
        guard let device = mtkView.device else {
            print("Error: La MTKView no tiene un dispositivo Metal asignado")
            return nil
        }
        self.device = device
        
        // 2. Crear la cola de comandos (una por aplicación normalmente)
        guard let queue = device.makeCommandQueue() else {
            print("Error: No se pudo crear la cola de comandos")
            return nil
        }
        self.commandQueue = queue
        
        // 3. Definir los vértices del triángulo
        let vertices: [Vertice] = [
            Vertice(posicion: SIMD2( 0.0,  0.5), color: SIMD4(1, 0, 0, 1)), // Arriba - Rojo
            Vertice(posicion: SIMD2(-0.5, -0.5), color: SIMD4(0, 1, 0, 1)), // Izquierda - Verde
            Vertice(posicion: SIMD2( 0.5, -0.5), color: SIMD4(0, 0, 1, 1))  // Derecha - Azul
        ]
        
        // 4. Crear buffer de vértices en memoria de GPU
        guard let buffer = device.makeBuffer(
            bytes: vertices,
            length: MemoryLayout<Vertice>.stride * vertices.count,
            options: .storageModeShared  // Memoria compartida CPU/GPU (Apple Silicon)
        ) else {
            print("Error: No se pudo crear el buffer de vértices")
            return nil
        }
        self.vertexBuffer = buffer
        
        // 5. Configurar el pipeline de renderizado
        let library = device.makeDefaultLibrary()! // Carga Shaders.metal compilado
        
        let descriptor = MTLRenderPipelineDescriptor()
        descriptor.vertexFunction = library.makeFunction(name: "vertice_basico")
        descriptor.fragmentFunction = library.makeFunction(name: "fragmento_basico")
        descriptor.colorAttachments[0].pixelFormat = mtkView.colorPixelFormat
        
        do {
            self.pipelineState = try device.makeRenderPipelineState(descriptor: descriptor)
        } catch {
            print("Error creando pipeline: \(error)")
            return nil
        }
        
        super.init()
    }
    
    // MARK: - MTKViewDelegate
    
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
        // Se llama cuando cambia el tamaño de la vista (rotación, resize)
    }
    
    func draw(in view: MTKView) {
        // 6. Obtener el render pass descriptor (describe el framebuffer destino)
        guard let renderPassDescriptor = view.currentRenderPassDescriptor,
              let drawable = view.currentDrawable else { return }
        
        // Color de fondo negro
        renderPassDescriptor.colorAttachments[0].clearColor = MTLClearColor(
            red: 0.0, green: 0.0, blue: 0.0, alpha: 1.0
        )
        
        // 7. Crear command buffer para este frame
        guard let commandBuffer = commandQueue.makeCommandBuffer() else { return }
        
        // 8. Crear encoder de renderizado
        guard let encoder = commandBuffer.makeRenderCommandEncoder(
            descriptor: renderPassDescriptor
        ) else { return }
        
        // 9. Configurar el encoder y dibujar
        encoder.setRenderPipelineState(pipelineState)
        encoder.setVertexBuffer(vertexBuffer, offset: 0, index: 0)
        encoder.drawPrimitives(type: .triangle, vertexStart: 0, vertexCount: 3)
        
        // 10. Finalizar codificación, presentar y enviar
        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }
}
```

Y los shaders correspondientes en un archivo `Shaders.metal`:

```metal
#include <metal_stdlib>
using namespace metal;

/// Estructura del vértice que coincide con la definición en Swift
struct VertexIn {
    float2 posicion [[attribute(0)]];
    float4 color    [[attribute(1)]];
};

/// Datos interpolados que pasan del vertex shader al fragment shader
struct VertexOut {
    float4 posicion [[position]];  // Posición en clip space
    float4 color;                   // Color interpolado
};

/// Estructura que coincide con el layout de memoria de Swift
struct Vertice {
    packed_float2 posicion;
    packed_float4 color;
};

/// Vertex shader: transforma posiciones y pasa colores
vertex VertexOut vertice_basico(
    uint vertexID [[vertex_id]],
    const device Vertice* vertices [[buffer(0)]]
) {
    VertexOut out;
    out.posicion = float4(vertices[vertexID].posicion, 0.0, 1.0);
    out.color = vertices[vertexID].color;
    return out;
}

/// Fragment shader: retorna el color interpolado por vértice
fragment half4 fragmento_basico(VertexOut in [[stage_in]]) {
    return half4(in.color);
}
```

## Ejemplo intermedio

Este ejemplo muestra cómo renderizar un cubo 3D con rotación animada, usando matrices de transformación, buffer de uniformes y depth testing:

```swift
import MetalKit
import simd

/// Renderer que dibuja un cubo 3D rotando con iluminación básica.
/// Demuestra: matrices MVP, depth buffer, uniform buffers y animación.
class Cubo3DRenderer: NSObject, MTKViewDelegate {
    
    // MARK: - Tipos compartidos con los shaders
    
    /// Uniformes que se envían a la GPU cada frame
    struct Uniformes {
        var matrizModelo: float4x4
        var matrizVista: float4x4
        var matrizProyeccion: float4x4
        var colorLuz: SIMD3<Float>
        var direccionLuz: SIMD3<Float>
    }
    
    /// Vértice con posición, normal y color
    struct VerticeCompleto {
        var posicion: SIMD3<Float>
        var normal: SIMD3<Float>
        var color: SIMD4<Float>
    }
    
    //