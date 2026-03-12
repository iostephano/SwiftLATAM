---
sidebar_position: 1
title: CoreLocation
---

# CoreLocation

## ¿Qué es CoreLocation?

CoreLocation es el framework de Apple que proporciona servicios de localización geográfica y orientación del dispositivo. Permite a las aplicaciones determinar la ubicación actual del usuario, monitorear cambios de posición, detectar la entrada y salida de regiones geográficas definidas (geofencing), y obtener datos del rumbo (heading) del dispositivo. Funciona combinando datos de GPS, Wi-Fi, Bluetooth, redes celulares y el barómetro del dispositivo para ofrecer la ubicación más precisa posible según el contexto.

Este framework es fundamental para cualquier aplicación que necesite interactuar con la posición física del usuario. Desde aplicaciones de navegación hasta servicios de entrega, pasando por redes sociales basadas en proximidad o apps de fitness que rastrean rutas, CoreLocation actúa como la capa base que alimenta todas estas funcionalidades. Apple ha diseñado el framework con un fuerte énfasis en la privacidad del usuario, requiriendo permisos explícitos y ofreciendo diferentes niveles de precisión.

A partir de iOS 14, Apple introdujo cambios significativos en el manejo de permisos, incluyendo la ubicación aproximada y el permiso temporal de ubicación precisa. Con iOS 15 y posteriores, se han añadido mejoras como el uso de `CLLocationManager` con `async/await`, haciendo que su integración con Swift moderno sea más natural y limpia. Comprender CoreLocation en profundidad es esencial para cualquier desarrollador iOS que aspire a crear experiencias de usuario enriquecidas y contextualmente relevantes.

## Casos de uso principales

- **Navegación y mapas**: Mostrar la ubicación del usuario en un mapa, calcular rutas y proporcionar indicaciones paso a paso en tiempo real.
- **Geofencing (geovallas)**: Detectar automáticamente cuándo un usuario entra o sale de una zona geográfica definida, útil para notificaciones contextuales, ofertas en tiendas o control de asistencia.
- **Aplicaciones de fitness y salud**: Rastrear recorridos de carrera, ciclismo o caminata, calculando distancias, velocidades y elevación durante la actividad física.
- **Servicios de entrega y logística**: Permitir el seguimiento en tiempo real de repartidores o flotas de vehículos, optimizando rutas y tiempos de entrega.
- **Contenido basado en ubicación**: Mostrar información relevante según la posición del usuario, como restaurantes cercanos, puntos de interés turístico o condiciones meteorológicas locales.
- **Aplicaciones de seguridad y emergencias**: Enviar la ubicación precisa del usuario a servicios de emergencia o contactos de confianza en situaciones de riesgo.

## Instalación y configuración

### Agregar el framework al proyecto

CoreLocation viene incluido de forma nativa en el SDK de iOS, por lo que no necesitas instalar ninguna dependencia externa. Simplemente importa el módulo en los archivos donde lo necesites:

```swift
import CoreLocation
```

Si usas **SwiftUI**, también puedes necesitar:

```swift
import MapKit // Si combinas ubicación con mapas
```

### Configuración de permisos en Info.plist

CoreLocation **requiere obligatoriamente** declarar las razones por las que tu app necesita acceso a la ubicación. Debes añadir las claves correspondientes en el archivo `Info.plist`:

```xml
<!-- Permiso para usar ubicación mientras la app está en primer plano -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>Necesitamos tu ubicación para mostrarte lugares cercanos.</string>

<!-- Permiso para usar ubicación en todo momento (primer plano y fondo) -->
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>Necesitamos tu ubicación para enviarte alertas cuando estés cerca de tus lugares favoritos.</string>
```

### Habilitar capacidades en segundo plano (si aplica)

Si tu aplicación necesita recibir actualizaciones de ubicación en segundo plano, debes habilitar **Background Modes** en la pestaña **Signing & Capabilities** de tu target:

1. Ve a tu proyecto en Xcode → target de tu app.
2. Pestaña **Signing & Capabilities**.
3. Agrega **Background Modes**.
4. Marca la casilla **Location updates**.

Esto añadirá automáticamente al `Info.plist`:

```xml
<key>UIBackgroundModes</key>
<array>
    <string>location</string>
</array>
```

## Conceptos clave

### 1. CLLocationManager

Es la clase central del framework. Actúa como el punto de entrada para solicitar permisos, iniciar y detener actualizaciones de ubicación, configurar la precisión deseada y gestionar el monitoreo de regiones. Cada instancia de `CLLocationManager` se configura con propiedades como `desiredAccuracy`, `distanceFilter` y `activityType` para optimizar el consumo de batería según las necesidades de la aplicación.

### 2. Niveles de autorización

CoreLocation trabaja con varios estados de autorización definidos en `CLAuthorizationStatus`:

- **`.notDetermined`**: El usuario aún no ha tomado una decisión.
- **`.restricted`**: El acceso está restringido (por ejemplo, controles parentales).
- **`.denied`**: El usuario ha denegado explícitamente el acceso.
- **`.authorizedWhenInUse`**: La app puede acceder a la ubicación solo en primer plano.
- **`.authorizedAlways`**: La app puede acceder a la ubicación en todo momento.

### 3. CLLocation

Objeto que encapsula los datos de una ubicación concreta: coordenadas (latitud/longitud), altitud, precisión horizontal y vertical, velocidad, rumbo y timestamp. Es el resultado principal que recibes de las actualizaciones de ubicación.

### 4. Geofencing con CLCircularRegion

Permite definir regiones circulares en el mapa. El sistema notifica a tu app cuando el dispositivo entra o sale de estas regiones, incluso si la app no está en ejecución. Hay un límite máximo de 20 regiones monitoreadas simultáneamente por app.

### 5. Precisión aproximada vs. precisa

Desde iOS 14, los usuarios pueden otorgar **ubicación aproximada** (un área de varios kilómetros) en lugar de la ubicación precisa. Tu app debe ser capaz de funcionar con ambos niveles de precisión y puede solicitar temporalmente precisión completa cuando sea necesario mediante `requestTemporaryFullAccuracyAuthorization(withPurposeKey:)`.

### 6. CLGeocoder

Clase que permite convertir coordenadas en direcciones legibles (geocodificación inversa) y direcciones de texto en coordenadas (geocodificación directa). Es fundamental para mostrar información comprensible al usuario a partir de datos de latitud y longitud.

## Ejemplo básico

```swift
import CoreLocation

/// Clase simple que obtiene la ubicación actual del usuario.
/// Ideal para entender los fundamentos de CLLocationManager.
class BasicLocationService: NSObject, CLLocationManagerDelegate {
    
    // MARK: - Propiedades
    
    /// El manager es el punto de entrada principal para servicios de ubicación
    private let locationManager = CLLocationManager()
    
    // MARK: - Inicialización
    
    override init() {
        super.init()
        configurarLocationManager()
    }
    
    // MARK: - Configuración
    
    private func configurarLocationManager() {
        // Asignamos el delegado para recibir callbacks
        locationManager.delegate = self
        
        // Precisión de ~100 metros, buen balance entre precisión y batería
        locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        
        // Solo notificar cambios mayores a 50 metros
        locationManager.distanceFilter = 50.0
    }
    
    /// Solicita permiso al usuario y comienza a obtener ubicación
    func solicitarUbicacion() {
        // Primero solicitamos permiso (muestra el diálogo del sistema)
        locationManager.requestWhenInUseAuthorization()
    }
    
    // MARK: - CLLocationManagerDelegate
    
    /// Se invoca cada vez que cambia el estado de autorización
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        switch manager.authorizationStatus {
        case .notDetermined:
            print("⏳ Esperando decisión del usuario...")
            
        case .authorizedWhenInUse, .authorizedAlways:
            print("✅ Permiso concedido. Obteniendo ubicación...")
            // Solicita una sola lectura de ubicación
            manager.requestLocation()
            
        case .denied:
            print("❌ Permiso denegado. Guía al usuario a Configuración.")
            
        case .restricted:
            print("🔒 Acceso restringido por políticas del dispositivo.")
            
        @unknown default:
            print("⚠️ Estado de autorización desconocido.")
        }
    }
    
    /// Se invoca cuando se reciben nuevas ubicaciones
    func locationManager(
        _ manager: CLLocationManager,
        didUpdateLocations locations: [CLLocation]
    ) {
        // Tomamos la ubicación más reciente
        guard let ubicacion = locations.last else { return }
        
        print("📍 Ubicación obtenida:")
        print("   Latitud: \(ubicacion.coordinate.latitude)")
        print("   Longitud: \(ubicacion.coordinate.longitude)")
        print("   Precisión: ±\(ubicacion.horizontalAccuracy) metros")
        print("   Velocidad: \(ubicacion.speed) m/s")
        print("   Timestamp: \(ubicacion.timestamp)")
    }
    
    /// Se invoca cuando ocurre un error al obtener la ubicación
    func locationManager(
        _ manager: CLLocationManager,
        didFailWithError error: Error
    ) {
        if let clError = error as? CLError {
            switch clError.code {
            case .denied:
                print("❌ El usuario denegó el acceso a la ubicación.")
            case .locationUnknown:
                print("⚠️ Ubicación temporalmente no disponible. Reintentando...")
            default:
                print("❌ Error de ubicación: \(clError.localizedDescription)")
            }
        }
    }
}
```

## Ejemplo intermedio

```swift
import CoreLocation
import Combine

/// Servicio de ubicación reactivo que publica actualizaciones
/// usando Combine. Incluye geocodificación inversa y geofencing.
class LocationService: NSObject, ObservableObject {
    
    // MARK: - Propiedades publicadas (para SwiftUI)
    
    @Published var ubicacionActual: CLLocation?
    @Published var direccionActual: String = "Obteniendo dirección..."
    @Published var estadoAutorizacion: CLAuthorizationStatus = .notDetermined
    @Published var error: LocationError?
    @Published var dentroDeRegion: Bool = false
    
    // MARK: - Propiedades privadas
    
    private let locationManager = CLLocationManager()
    private let geocoder = CLGeocoder()
    
    /// Errores personalizados para un manejo más limpio
    enum LocationError: LocalizedError {
        case permisoDenegado
        case ubicacionNoDisponible
        case geocodificacionFallida(String)
        case regionNoSoportada
        
        var errorDescription: String? {
            switch self {
            case .permisoDenegado:
                return "El acceso a la ubicación ha sido denegado."
            case .ubicacionNoDisponible:
                return "No se pudo determinar la ubicación actual."
            case .geocodificacionFallida(let detalle):
                return "Error al obtener la dirección: \(detalle)"
            case .regionNoSoportada:
                return "El monitoreo de regiones no está disponible."
            }
        }
    }
    
    // MARK: - Inicialización
    
    override init() {
        super.init()
        configurar()
    }
    
    private func configurar() {
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.distanceFilter = 10 // Actualizar cada 10 metros
        locationManager.activityType = .fitness // Optimiza para actividad física
        locationManager.allowsBackgroundLocationUpdates = false
        locationManager.pausesLocationUpdatesAutomatically = true
    }
    
    // MARK: - API Pública
    
    /// Solicita permiso y comienza el rastreo continuo
    func iniciarRastreo() {
        locationManager.requestWhenInUseAuthorization()
    }
    
    /// Detiene las actualizaciones de ubicación
    func detenerRastreo() {
        locationManager.stopUpdatingLocation()
        print("🛑 Rastreo de ubicación detenido.")
    }
    
    /// Configura una geovalla circular alrededor de un punto
    func configurarGeovalla(
        centro: CLLocationCoordinate2D,
        radio: CLLocationDistance,
        identificador: String
    ) {
        // Verificar que el dispositivo soporte monitoreo de regiones
        guard CLLocationManager.isMonitoringAvailable(
            for: CLCircularRegion.self
        ) else {
            self.error = .regionNoSoportada
            return
        }
        
        // Crear la región circular (máximo 20 simultáneas)
        let region = CLCircularRegion(
            center: centro,
            radius: min(radio, locationManager.maximumRegionMonitoringDistance),
            identifier: identificador
        )
        
        // Configurar qué eventos nos interesan
        region.notifyOnEntry = true
        region.notifyOnExit = true
        
        // Iniciar monitoreo
        locationManager.startMonitoring(for: region)
        print("🔔 Geovalla configurada: \(identificador) (radio: \(radio)m)")
    }
    
    /// Realiza geocodificación inversa para obtener la dirección legible
    func obtenerDireccion(de ubicacion: CLLocation) {
        // Cancelar geocodificaciones previas pendientes
        geocoder.cancelGeocode()
        
        geocoder.reverseGeocodeLocation(ubicacion) { [weak self] placemarks, error in
            guard let self = self else { return }
            
            if let error = error {
                self.error = .geocodificacionFallida(error.localizedDescription)
                return
            }
            
            guard let placemark = placemarks?.first else {
                self.direccionActual = "Dirección desconocida"
                return
            }
            
            // Construir una dirección legible a partir del placemark
            let componentes = [
                placemark.thoroughfare,        // Calle
                placemark.subThoroughfare,     // Número
                placemark.locality,            // Ciudad
                placemark.administrativeArea,  // Estado/Provincia
                placemark.country              // País
            ].compactMap { $0 }
            
            DispatchQueue.main.async {
                self.direccionActual = componentes.joined(separator: ", ")
            }
        }
    }
    
    /// Calcula la distancia entre la ubicación actual y un punto destino
    func distanciaHasta(destino: CLLocationCoordinate2D) -> CLLocationDistance? {
        guard let ubicacion = ubicacionActual else { return nil }
        let puntoDestino = CLLocation(
            latitude: destino.latitude,
            longitude: destino.longitude
        )
        return ubicacion.distance(from: puntoDestino)