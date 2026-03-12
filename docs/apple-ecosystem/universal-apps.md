---
sidebar_position: 1
title: Universal Apps
---

# Universal Apps: Una App, Todo el Ecosistema Apple

## ¿Qué son las Universal Apps?

Las **Universal Apps** (también conocidas como aplicaciones universales) son aplicaciones diseñadas para ejecutarse de forma nativa en **múltiples dispositivos del ecosistema Apple** — iPhone, iPad, Mac, Apple Watch y Apple TV — desde un único proyecto y, en muchos casos, compartiendo gran parte del código base.

Este concepto ha evolucionado significativamente. Originalmente, "Universal App" se refería simplemente a una app que funcionaba tanto en iPhone como en iPad. Hoy, con la llegada de **SwiftUI**, **Mac Catalyst**, **Apple Silicon** y la convergencia de plataformas, el término abarca todo el ecosistema.

```
┌─────────────────────────────────────────────┐
│              CÓDIGO COMPARTIDO              │
│         (Modelos, Lógica, ViewModels)       │
├──────────┬──────────┬──────────┬────────────┤
│  iPhone  │   iPad   │   Mac    │ Apple Watch│
│   (iOS)  │ (iPadOS) │ (macOS)  │  (watchOS) │
└──────────┴──────────┴──────────┴────────────┘
```

## ¿Por qué es crucial para desarrolladores en LATAM?

### 1. Maximizar el retorno de inversión
En Latinoamérica, muchos desarrolladores trabajan como freelancers, en startups con recursos limitados o en agencias pequeñas. Construir **una sola app que llegue a todos los dispositivos** reduce drásticamente los costos de desarrollo y mantenimiento.

### 2. Diferenciación profesional
El mercado de trabajo remoto para LATAM ha crecido exponencialmente. Empresas en EE.UU., Canadá y Europa buscan desarrolladores que dominen **todo el ecosistema**, no solo iOS. Saber construir Universal Apps te posiciona como un profesional más completo y mejor remunerado.

### 3. Mayor alcance de usuarios
Una app universal aparece en la App Store de **todos los dispositivos compatibles**, lo que multiplica tu visibilidad orgánica sin esfuerzo adicional de marketing.

### 4. Preparación para visionOS
Con Apple Vision Pro expandiéndose gradualmente, las apps universales bien diseñadas con SwiftUI están listas para ejecutarse en este nuevo dispositivo con ajustes mínimos.

## Arquitectura de una Universal App moderna

### La clave: Separación de responsabilidades

La base de una Universal App exitosa es una arquitectura que separe claramente la **lógica de negocio** de la **interfaz de usuario**.

```swift
// MARK: - Capa de Modelo (compartida entre TODAS las plataformas)

struct Producto: Identifiable, Codable {
    let id: UUID
    let nombre: String
    let precio: Double
    let categoria: String
    let disponible: Bool
    
    var precioFormateado: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.locale = Locale(identifier: "es_MX") // Localización para LATAM
        return formatter.string(from: NSNumber(value: precio)) ?? "$\(precio)"
    }
}
```

```swift
// MARK: - ViewModel compartido (toda la lógica de negocio)

import SwiftUI

@MainActor
class ProductosViewModel: ObservableObject {
    @Published var productos: [Producto] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var terminoBusqueda = ""
    
    var productosFiltrados: [Producto] {
        if terminoBusqueda.isEmpty {
            return productos
        }
        return productos.filter { producto in
            producto.nombre.localizedCaseInsensitiveContains(terminoBusqueda)
        }
    }
    
    private let servicio: ProductoServicioProtocol
    
    init(servicio: ProductoServicioProtocol = ProductoServicio()) {
        self.servicio = servicio
    }
    
    func cargarProductos() async {
        isLoading = true
        errorMessage = nil
        
        do {
            productos = try await servicio.obtenerProductos()
        } catch {
            errorMessage = "Error al cargar productos: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
    
    func toggleDisponibilidad(de producto: Producto) async {
        do {
            try await servicio.actualizarDisponibilidad(productoId: producto.id)
            await cargarProductos()
        } catch {
            errorMessage = "No se pudo actualizar el producto"
        }
    }
}
```

```swift
// MARK: - Protocolo del servicio (facilita testing)

protocol ProductoServicioProtocol {
    func obtenerProductos() async throws -> [Producto]
    func actualizarDisponibilidad(productoId: UUID) async throws
}

class ProductoServicio: ProductoServicioProtocol {
    private let baseURL = "https://api.mitienda.com/v1"
    
    func obtenerProductos() async throws -> [Producto] {
        guard let url = URL(string: "\(baseURL)/productos") else {
            throw URLError(.badURL)
        }
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([Producto].self, from: data)
    }
    
    func actualizarDisponibilidad(productoId: UUID) async throws {
        guard let url = URL(string: "\(baseURL)/productos/\(productoId)/toggle") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "PATCH"
        let _ = try await URLSession.shared.data(for: request)
    }
}
```

## Interfaces adaptativas con SwiftUI

Aquí es donde ocurre la magia. SwiftUI nos permite crear interfaces que se **adaptan automáticamente** a cada plataforma.

### Vista principal con NavigationSplitView

```swift
// MARK: - Vista principal adaptativa

struct ContentView: View {
    @StateObject private var viewModel = ProductosViewModel()
    @State private var productoSeleccionado: Producto?
    @State private var columnVisibility: NavigationSplitViewVisibility = .all
    
    var body: some View {
        NavigationSplitView(columnVisibility: $columnVisibility) {
            // SIDEBAR - Lista de productos
            ProductosListaView(
                viewModel: viewModel,
                seleccion: $productoSeleccionado
            )
        } detail: {
            // DETAIL - Detalle del producto
            if let producto = productoSeleccionado {
                ProductoDetalleView(
                    producto: producto,
                    viewModel: viewModel
                )
            } else {
                ContentUnavailableView(
                    "Selecciona un producto",
                    systemImage: "cube.box",
                    description: Text("Elige un producto de la lista para ver sus detalles")
                )
            }
        }
        .task {
            await viewModel.cargarProductos()
        }
    }
}
```

> **Nota:** `NavigationSplitView` muestra automáticamente una barra lateral en iPad y Mac, mientras que en iPhone presenta una navegación tipo stack tradicional. ¡Sin código condicional!

### Lista de productos

```swift
struct ProductosListaView: View {
    @ObservedObject var viewModel: ProductosViewModel
    @Binding var seleccion: Producto?
    
    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Cargando productos...")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = viewModel.errorMessage {
                ContentUnavailableView {
                    Label("Error", systemImage: "exclamationmark.triangle")
                } description: {
                    Text(error)
                } actions: {
                    Button("Reintentar") {
                        Task { await viewModel.cargarProductos() }
                    }
                    .buttonStyle(.borderedProminent)
                }
            } else {
                List(viewModel.productosFiltrados, selection: $seleccion) { producto in
                    ProductoFilaView(producto: producto)
                        .tag(producto)
                }
                .searchable(
                    text: $viewModel.terminoBusqueda,
                    prompt: "Buscar productos..."
                )
            }
        }
        .navigationTitle("Productos")
        #if os(iOS)
        .refreshable {
            await viewModel.cargarProductos()
        }
        #endif
    }
}
```

### Fila de producto con diseño adaptativo

```swift
struct ProductoFilaView: View {
    let producto: Producto
    
    // Detectar la plataforma para ajustes sutiles
    #if os(watchOS)
    private let tamañoIcono: CGFloat = 24
    #else
    private let tamañoIcono: CGFloat = 44
    #endif
    
    var body: some View {
        HStack(spacing: 12) {
            // Icono de categoría
            Image(systemName: iconoParaCategoria(producto.categoria))
                .font(.title2)
                .frame(width: tamañoIcono, height: tamañoIcono)
                .background(Color.accentColor.opacity(0.1))
                .clipShape(RoundedRectangle(cornerRadius: 8))
            
            VStack(alignment: .leading, spacing: 4) {
                Text(producto.nombre)
                    .font(.headline)
                    .lineLimit(1)
                
                Text(producto.precioFormateado)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            
            Spacer()
            
            // Indicador de disponibilidad
            Circle()
                .fill(producto.disponible ? .green : .red)
                .frame(width: 10, height: 10)
        }
        .padding(.vertical, 4)
        #if os(macOS)
        .padding(.horizontal, 4)
        #endif
    }
    
    private func iconoParaCategoria(_ categoria: String) -> String {
        switch categoria.lowercased() {
        case "electrónica": return "desktopcomputer"
        case "ropa": return "tshirt"
        case "alimentos": return "cart"
        case "hogar": return "house"
        default: return "cube.box"
        }
    }
}
```

### Vista de detalle con layouts adaptativos

```swift
struct ProductoDetalleView: View {
    let producto: Producto
    @ObservedObject var viewModel: ProductosViewModel
    @Environment(\.horizontalSizeClass) var sizeClass
    
    var body: some View {
        ScrollView {
            // ViewThatFits elige automáticamente el mejor layout
            ViewThatFits(in: .horizontal) {
                // Layout horizontal para pantallas amplias (iPad, Mac)
                layoutHorizontal
                // Layout vertical para pantallas estrechas (iPhone)
                layoutVertical
            }
            .padding()
        }
        .navigationTitle(producto.nombre)
        #if os(macOS)
        .frame(minWidth: 400)
        #endif
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task {
                        await viewModel.toggleDisponibilidad(de: producto)
                    }
                } label: {
                    Label(
                        producto.disponible ? "Desactivar" : "Activar",
                        systemImage: producto.disponible ? "eye.slash" : "eye"
                    )
                }
            }
            
            #if os(macOS)
            ToolbarItem(placement: .automatic) {
                ShareLink(
                    item: producto.nombre,
                    subject: Text("Mira este producto"),
                    message: Text("\(producto.nombre) - \(producto.precioFormateado)")
                )
            }
            #endif
        }
    }
    
    // MARK: - Layouts
    
    private var layoutHorizontal: some View {
        HStack(alignment: .top, spacing: 32) {
            imagenProducto
                .frame(width: 300, height: 300)
            
            informacionProducto
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(minWidth: 600)
    }
    
    private var layoutVertical: some View {
        VStack(spacing: 20) {
            imagenProducto
                .frame(maxWidth: .infinity)
                .frame(height: 250)
            
            informacionProducto
        }
    }
    
    private var imagenProducto: some View {
        RoundedRectangle(cornerRadius: 16)
            .fill(
                LinearGradient(
                    colors: [.blue.opacity(0.3), .purple.opacity(0.3)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .overlay {
                Image(systemName: "cube.box.fill")
                    .font(.system(size: 64))
                    .foregroundStyle(.secondary)
            }
    }
    
    private var informacionProducto: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(producto.nombre)
                .font(.largeTitle)
                .bold()
            
            Text(producto.precioFormateado)
                .font(.title)
                .foregroundStyle(.green)
            
            Divider()
            
            Label(
                producto.disponible ? "Disponible" : "No disponible",
                systemImage: producto.disponible ? "checkmark.circle.fill" : "xmark.circle.fill"
            )
            .font(.title3)
            .foregroundStyle(producto.disponible ? .green : .red)
            
            Label(producto.categoria, systemImage: "tag")
                .font(.title3)
                .foregroundStyle(.secondary)
            
            Divider()
            
            // Botón de acción principal
            Button {
                Task {
                    await viewModel.toggleDisponibilidad(de: producto)
                }
            } label: {
                Text(producto.disponible ? "Marcar como no disponible" : "Marcar como disponible")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .tint(producto.disponible ? .red : .green)
        }
    }
}
```

## Configuración del proyecto en Xcode

### Paso 1: Crear el proyecto como Multiplatform

Al crear un nuevo proyecto en Xcode, selecciona **"Multiplatform App"** en lugar de "iOS App". Esto configura automáticamente targets para iOS, macOS y otros.

### Paso 2: Estructura de carpetas recomendada

```
MiAppUniversal/
├── Shared/                    # Código compartido entre TODAS las plataformas
│   ├── Models/
│   │   └── Producto.swift
│   ├── ViewModels/
│   │   └── ProductosViewModel.swift
│   ├── Services/
│   │   └── ProductoServicio.swift
│   └── Views/
│       ├── ContentView.swift
│       ├── ProductosListaView.swift
│       ├── ProductoFilaView.swift
│       └── ProductoDetalleView.swift
│
├── iOS/                       # Código EXCLUSIVO de iOS
│   ├── iOSSpecificView.swift
│   └── Info.plist
│
├── macOS/