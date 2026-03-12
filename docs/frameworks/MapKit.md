---
sidebar_position: 1
title: MapKit
---

# MapKit

## ¿Qué es MapKit?

MapKit es el framework nativo de Apple que permite integrar mapas interactivos directamente en aplicaciones iOS, macOS, tvOS y watchOS. Proporciona una interfaz completa para mostrar mapas, satelitales o híbridos, además de permitir la interacción del usuario mediante gestos como zoom, desplazamiento y rotación. MapKit utiliza los datos cartográficos de Apple Maps, lo que garantiza información actualizada y de alta calidad sin necesidad de servicios de terceros.

Este framework va mucho más allá de simplemente mostrar un mapa. Ofrece capacidades avanzadas como la búsqueda de puntos de interés, el cálculo de rutas (driving, walking, transit), la geocodificación directa e inversa, la adición de anotaciones y overlays personalizados, y la detección de la ubicación del usuario en tiempo real. Con la llegada de SwiftUI, MapKit ha evolucionado significativamente, ofreciendo APIs declarativas modernas que simplifican enormemente la integración de mapas.

MapKit es la elección ideal cuando necesitas mostrar información geoespacial en tu aplicación sin depender de SDKs externos como Google Maps. Es especialmente potente en el ecosistema Apple gracias a su integración nativa con Core Location, Combine y SwiftUI, lo que permite construir experiencias de mapas fluidas y con un rendimiento excelente, respetando la privacidad del usuario con las políticas de Apple.

## Casos de uso principales

- **Aplicaciones de delivery y logística**: Mostrar la ubicación en tiempo real de repartidores, trazar rutas de entrega y calcular tiempos estimados de llegada entre múltiples puntos.

- **Apps de turismo y viajes**: Presentar puntos de interés cercanos, museos, restaurantes y atracciones turísticas con anotaciones personalizadas y categorización por tipo.

- **Plataformas inmobiliarias**: Visualizar propiedades disponibles en un mapa, permitiendo a los usuarios explorar zonas geográficas y filtrar resultados según su ubicación.

- **Aplicaciones de fitness y deportes**: Trazar rutas de running, ciclismo o senderismo sobre el mapa, mostrando métricas como distancia, elevación y velocidad en cada segmento.

- **Redes sociales geolocalizadas**: Permitir a los usuarios etiquetar ubicaciones en publicaciones, descubrir contenido cercano y visualizar actividad social en zonas específicas.

- **Servicios de emergencia y salud**: Localizar hospitales, farmacias o estaciones de bomberos más cercanas, calcular la ruta más rápida y mostrar áreas de cobertura de servicios.

## Instalación y configuración

### Agregar MapKit al proyecto

MapKit viene incluido en el SDK de iOS, por lo que no necesitas instalar dependencias externas. Solo debes asegurarte de habilitar la capability correspondiente:

1. Abre tu proyecto en Xcode.
2. Selecciona el **target** de tu aplicación.
3. Ve a la pestaña **Signing & Capabilities**.
4. Haz clic en **+ Capability** y busca **Maps**.
5. Activa los modos que necesites (Standard, Driving, Transit, etc.).

### Permisos en Info.plist

Si necesitas acceder a la ubicación del usuario (muy común al usar MapKit), debes agregar las claves de privacidad correspondientes en tu archivo `Info.plist`:

```xml
<!-- Permiso para usar la ubicación mientras la app está en uso -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>Necesitamos tu ubicación para mostrarte lugares cercanos en el mapa.</string>

<!-- Permiso para usar la ubicación en todo momento (si aplica) -->
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>Necesitamos tu ubicación para enviarte notificaciones de lugares cercanos.</string>
```

### Imports necesarios

```swift
import MapKit       // Framework principal de mapas
import CoreLocation // Para servicios de ubicación y geocodificación
```

## Conceptos clave

### 1. MKMapView / Map (SwiftUI)

Es el componente visual principal que renderiza el mapa en pantalla. En UIKit se utiliza `MKMapView` como una vista que se agrega a la jerarquía. En SwiftUI (iOS 17+), se utiliza la estructura `Map` con una API completamente declarativa que acepta marcadores, anotaciones y overlays como contenido.

### 2. Anotaciones (MKAnnotation / Marker)

Las anotaciones representan puntos específicos en el mapa. Cada anotación tiene una coordenada geográfica (`CLLocationCoordinate2D`), un título y un subtítulo. Son el mecanismo principal para señalar ubicaciones de interés. En SwiftUI moderno se usan `Marker` y `Annotation` directamente dentro del `Map`.

### 3. Overlays (MKOverlay)

Los overlays permiten dibujar formas geométricas sobre el mapa: polilíneas para rutas, polígonos para áreas, y círculos para radios de cobertura. Son fundamentales para representar rutas de navegación, zonas geofencing o áreas de interés.

### 4. Geocodificación (CLGeocoder)

La geocodificación es el proceso de convertir direcciones legibles (como "Paseo de la Reforma 505, CDMX") en coordenadas geográficas (latitud/longitud) y viceversa. `CLGeocoder` proporciona esta funcionalidad y es esencial para búsquedas de direcciones.

### 5. MKDirections

Este componente permite calcular rutas entre dos o más puntos, proporcionando información detallada como distancia, tiempo estimado, instrucciones paso a paso y la polilínea de la ruta para dibujarla sobre el mapa.

### 6. MKLocalSearch

Permite realizar búsquedas de puntos de interés y negocios cercanos utilizando los datos de Apple Maps. Es extremadamente útil para implementar funcionalidades tipo "buscar restaurantes cerca de mí" sin necesidad de APIs externas.

## Ejemplo básico

```swift
import SwiftUI
import MapKit

/// Vista básica que muestra un mapa centrado en Ciudad de México
/// con un marcador en el Ángel de la Independencia.
struct MapaBasicoView: View {
    
    // Posición inicial de la cámara del mapa
    @State private var posicionCamara: MapCameraPosition = .region(
        MKCoordinateRegion(
            center: CLLocationCoordinate2D(
                latitude: 19.4270,
                longitude: -99.1677
            ),
            span: MKCoordinateSpan(
                latitudeDelta: 0.01,
                longitudeDelta: 0.01
            )
        )
    )
    
    var body: some View {
        // Map con un marcador simple usando la API de iOS 17+
        Map(position: $posicionCamara) {
            // Marcador en el Ángel de la Independencia
            Marker(
                "Ángel de la Independencia",
                systemImage: "star.fill",
                coordinate: CLLocationCoordinate2D(
                    latitude: 19.4270,
                    longitude: -99.1677
                )
            )
            .tint(.orange)
        }
        .mapStyle(.standard(elevation: .realistic))
        .mapControls {
            MapCompass()        // Brújula
            MapScaleView()     // Escala
            MapUserLocationButton() // Botón de ubicación del usuario
        }
    }
}

#Preview {
    MapaBasicoView()
}
```

## Ejemplo intermedio

```swift
import SwiftUI
import MapKit

// MARK: - Modelo de lugar

/// Representa un punto de interés en el mapa
struct LugarInteres: Identifiable {
    let id = UUID()
    let nombre: String
    let descripcion: String
    let coordenada: CLLocationCoordinate2D
    let categoria: Categoria
    
    enum Categoria: String, CaseIterable {
        case museo = "Museo"
        case restaurante = "Restaurante"
        case parque = "Parque"
        
        var icono: String {
            switch self {
            case .museo: return "building.columns.fill"
            case .restaurante: return "fork.knife"
            case .parque: return "leaf.fill"
            }
        }
        
        var color: Color {
            switch self {
            case .museo: return .purple
            case .restaurante: return .red
            case .parque: return .green
            }
        }
    }
}

// MARK: - Vista principal del mapa con múltiples funcionalidades

struct MapaIntermedioView: View {
    
    @State private var posicionCamara: MapCameraPosition = .region(
        MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 19.4326, longitude: -99.1332),
            span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
        )
    )
    
    @State private var lugarSeleccionado: LugarInteres?
    @State private var categoriaFiltro: LugarInteres.Categoria?
    @State private var textoBusqueda: String = ""
    @State private var resultadosBusqueda: [MKMapItem] = []
    @State private var mostrarDetalle: Bool = false
    
    // Datos de ejemplo: lugares de interés en CDMX
    let lugares: [LugarInteres] = [
        LugarInteres(
            nombre: "Museo Nacional de Antropología",
            descripcion: "Uno de los museos más importantes de América Latina.",
            coordenada: CLLocationCoordinate2D(latitude: 19.4260, longitude: -99.1862),
            categoria: .museo
        ),
        LugarInteres(
            nombre: "Museo Frida Kahlo",
            descripcion: "La icónica Casa Azul donde vivió Frida Kahlo.",
            coordenada: CLLocationCoordinate2D(latitude: 19.3551, longitude: -99.1626),
            categoria: .museo
        ),
        LugarInteres(
            nombre: "Pujol",
            descripcion: "Restaurante de alta cocina mexicana contemporánea.",
            coordenada: CLLocationCoordinate2D(latitude: 19.4330, longitude: -99.1920),
            categoria: .restaurante
        ),
        LugarInteres(
            nombre: "Bosque de Chapultepec",
            descripcion: "El parque urbano más grande de Latinoamérica.",
            coordenada: CLLocationCoordinate2D(latitude: 19.4204, longitude: -99.1893),
            categoria: .parque
        ),
        LugarInteres(
            nombre: "Contramar",
            descripcion: "Restaurante emblemático de mariscos en la Roma.",
            coordenada: CLLocationCoordinate2D(latitude: 19.4175, longitude: -99.1712),
            categoria: .restaurante
        )
    ]
    
    /// Lugares filtrados según la categoría seleccionada
    var lugaresFiltrados: [LugarInteres] {
        guard let filtro = categoriaFiltro else { return lugares }
        return lugares.filter { $0.categoria == filtro }
    }
    
    var body: some View {
        NavigationStack {
            ZStack(alignment: .bottom) {
                // Mapa principal con marcadores y resultados de búsqueda
                Map(position: $posicionCamara, selection: .constant(nil)) {
                    // Marcadores de lugares de interés filtrados
                    ForEach(lugaresFiltrados) { lugar in
                        Annotation(lugar.nombre, coordinate: lugar.coordenada) {
                            Button {
                                lugarSeleccionado = lugar
                                mostrarDetalle = true
                            } label: {
                                VStack(spacing: 2) {
                                    Image(systemName: lugar.categoria.icono)
                                        .font(.title2)
                                        .foregroundStyle(.white)
                                        .padding(8)
                                        .background(lugar.categoria.color)
                                        .clipShape(Circle())
                                        .shadow(radius: 3)
                                    
                                    Text(lugar.nombre)
                                        .font(.caption2)
                                        .fontWeight(.semibold)
                                        .lineLimit(1)
                                }
                            }
                        }
                    }
                    
                    // Marcadores de resultados de búsqueda local
                    ForEach(resultadosBusqueda, id: \.self) { item in
                        if let nombre = item.name {
                            Marker(nombre, coordinate: item.placemark.coordinate)
                                .tint(.blue)
                        }
                    }
                }
                .mapStyle(.standard(pointsOfInterest: .excludingAll))
                .mapControls {
                    MapCompass()
                    MapScaleView()
                }
                
                // Panel de filtros por categoría
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 10) {
                        // Botón para mostrar todos
                        BotonFiltro(
                            titulo: "Todos",
                            icono: "map",
                            color: .blue,
                            activo: categoriaFiltro == nil
                        ) {
                            categoriaFiltro = nil
                        }
                        
                        // Botón por cada categoría
                        ForEach(LugarInteres.Categoria.allCases, id: \.self) { cat in
                            BotonFiltro(
                                titulo: cat.rawValue,
                                icono: cat.icono,
                                color: cat.color,
                                activo: categoriaFiltro == cat
                            ) {
                                categoriaFiltro = cat
                            }
                        }
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical, 10)
                .background(.ultraThinMaterial)
            }
            .navigationTitle("Explorar CDMX")
            .navigationBarTitleDisplayMode(.inline)
            .searchable(text: $textoBusqueda, prompt: "Buscar lugares...")
            .onSubmit(of: .search) {
                buscarLugares()
            }
            .sheet(isPresented: $mostrarDetalle) {
                if let lugar = lugarSeleccionado {
                    DetalleLugarView(lugar: lugar)
                        .presentationDetents([.medium])
                }
            }
        }
    }
    
    /// Realiza una búsqueda local usando MKLocalSearch
    private func buscarLugares() {
        let request = MKLocalSearch.Request()
        request.naturalLanguageQuery = textoBusqueda
        request.region = MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 19.4326, longitude: -99.1332),
            span: MKCoordinateSpan(latitudeDelta: 0.1, longitudeDelta: 0.1)
        )
        
        let search = MKLocalSearch(request: request)
        search.start { response, error in
            guard let response = response, error == nil else {
                print("Error en búsqueda: \(error?.localizedDescription ?? "Desconocido")")
                return
            }
            resultadosBusqueda = response.mapItems
        }
    }
}

// MARK: - Componente reutilizable de botón de filtro

struct BotonFiltro: View {
    let titulo: String
    