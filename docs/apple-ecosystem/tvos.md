---
sidebar_position: 1
title: Tvos
---

# tvOS: Desarrollo para Apple TV

## ¿Qué es tvOS?

tvOS es el sistema operativo que impulsa el **Apple TV**, diseñado específicamente para experiencias en la pantalla grande del salón. Basado en iOS, comparte gran parte de sus frameworks y APIs, pero introduce paradigmas de interacción únicos centrados en el **Siri Remote**, el enfoque (*focus engine*) y la experiencia visual inmersiva a distancia.

Desde su lanzamiento en 2015, tvOS ha evolucionado para soportar contenido HDR, Dolby Atmos, juegos con controladores, y más recientemente, integración con SharePlay y continuidad entre dispositivos Apple.

## ¿Por qué es importante para un desarrollador iOS en LATAM?

### Oportunidad de mercado subestimada

Mientras la mayoría de los desarrolladores en Latinoamérica se concentran exclusivamente en iOS y, en menor medida, en macOS, tvOS representa un **nicho con muy poca competencia**. Esto se traduce en:

- **Menor saturación en la App Store de tvOS**: Tu app tiene mayor visibilidad orgánica.
- **Clientes enterprise dispuestos a pagar**: Hoteles, gimnasios, restaurantes, salas de espera médicas y aerolíneas buscan soluciones personalizadas para pantallas grandes.
- **Reutilización masiva de código**: Si ya dominas UIKit o SwiftUI, el 70-80% de tu conocimiento se transfiere directamente.
- **Diferenciación profesional**: En entrevistas y portafolios, demostrar experiencia multiplataforma dentro del ecosistema Apple te posiciona como un profesional de nivel senior.

### Casos de uso reales en LATAM

- **Plataformas de streaming regionales** (Claro Video, Blim, ViX) que necesitan apps nativas para Apple TV.
- **Apps de fitness y bienestar** para gimnasios y centros deportivos.
- **Cartelería digital** (*digital signage*) en comercios y restaurantes.
- **Apps educativas** para escuelas y universidades que usan Apple TV en aulas.
- **Juegos casuales** optimizados para la pantalla del televisor.

## Arquitectura y conceptos fundamentales

### El Focus Engine

A diferencia de iOS donde el usuario toca directamente la pantalla, en tvOS la navegación se basa en un sistema de **enfoque (focus)**. El usuario desliza el dedo sobre el Siri Remote y el sistema determina qué elemento de la interfaz recibe el foco.

```swift
import SwiftUI

struct ContentView: View {
    @FocusState private var selectedButton: String?
    
    var body: some View {
        HStack(spacing: 40) {
            MenuButton(title: "Películas", id: "movies", selectedButton: $selectedButton)
            MenuButton(title: "Series", id: "series", selectedButton: $selectedButton)
            MenuButton(title: "En Vivo", id: "live", selectedButton: $selectedButton)
            MenuButton(title: "Mi Lista", id: "mylist", selectedButton: $selectedButton)
        }
        .padding(60)
    }
}

struct MenuButton: View {
    let title: String
    let id: String
    @FocusState.Binding var selectedButton: String?
    
    var body: some View {
        Button(action: {
            print("Seleccionado: \(title)")
        }) {
            Text(title)
                .font(.title2)
                .fontWeight(.semibold)
                .padding(.horizontal, 40)
                .padding(.vertical, 20)
        }
        .focused($selectedButton, equals: id)
        .scaleEffect(selectedButton == id ? 1.15 : 1.0)
        .animation(.easeInOut(duration: 0.2), value: selectedButton)
    }
}
```

### Diferencias clave con iOS

| Característica | iOS | tvOS |
|---|---|---|
| **Interacción** | Táctil directa | Remoto + Focus Engine |
| **Tamaño de pantalla** | 4.7" - 6.7" | 40" - 85"+ |
| **Distancia del usuario** | 30-40 cm | 2-5 metros |
| **Almacenamiento de apps** | Hasta 4 GB+ | Máximo 4 GB (con recursos bajo demanda) |
| **Web browsing** | WebKit completo | No disponible |
| **Persistencia local** | Ilimitada (relativa) | Limitada, puede purgarse |

## Creando tu primera app para tvOS

### Paso 1: Configurar el proyecto

En Xcode, selecciona **File → New → Project → tvOS → App**. Puedes elegir entre SwiftUI y UIKit como interfaz.

```swift
// App.swift - Punto de entrada de una app tvOS con SwiftUI
import SwiftUI

@main
struct MiAppTVApp: App {
    var body: some Scene {
        WindowGroup {
            MainTabView()
        }
    }
}
```

### Paso 2: Navegación con TabView

La navegación principal en tvOS generalmente usa un `TabView` en la parte superior, similar a las apps nativas de Apple:

```swift
struct MainTabView: View {
    var body: some View {
        TabView {
            HomeView()
                .tabItem {
                    Label("Inicio", systemImage: "house.fill")
                }
            
            SearchView()
                .tabItem {
                    Label("Buscar", systemImage: "magnifyingglass")
                }
            
            FavoritesView()
                .tabItem {
                    Label("Favoritos", systemImage: "heart.fill")
                }
            
            SettingsView()
                .tabItem {
                    Label("Ajustes", systemImage: "gear")
                }
        }
    }
}
```

### Paso 3: Construir una grilla de contenido

Las apps de streaming y contenido en tvOS suelen presentar una grilla horizontal con pósters que responden al foco:

```swift
struct HomeView: View {
    let categories = ["Tendencias", "Acción", "Comedia", "Drama", "Documentales"]
    
    var body: some View {
        ScrollView(.vertical) {
            LazyVStack(alignment: .leading, spacing: 50) {
                ForEach(categories, id: \.self) { category in
                    CategoryRow(title: category)
                }
            }
            .padding(60)
        }
    }
}

struct CategoryRow: View {
    let title: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text(title)
                .font(.title3)
                .fontWeight(.bold)
                .foregroundColor(.secondary)
            
            ScrollView(.horizontal, showsIndicators: false) {
                LazyHStack(spacing: 40) {
                    ForEach(0..<10) { index in
                        ContentCard(index: index)
                    }
                }
            }
        }
    }
}

struct ContentCard: View {
    let index: Int
    @Environment(\.isFocused) var isFocused
    
    var body: some View {
        Button(action: {
            print("Reproducir contenido \(index)")
        }) {
            VStack(alignment: .leading, spacing: 12) {
                RoundedRectangle(cornerRadius: 12)
                    .fill(
                        LinearGradient(
                            colors: [.blue, .purple],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 300, height: 170)
                    .overlay(
                        Image(systemName: "play.circle.fill")
                            .font(.system(size: 44))
                            .foregroundColor(.white.opacity(0.8))
                    )
                
                Text("Título \(index + 1)")
                    .font(.caption)
                    .foregroundColor(.primary)
                    .lineLimit(1)
            }
        }
        .buttonStyle(.card)
    }
}
```

### Paso 4: Reproducción de video con AVKit

La reproducción multimedia es el corazón de muchas apps tvOS:

```swift
import SwiftUI
import AVKit

struct PlayerView: View {
    let videoURL: URL
    @StateObject private var playerViewModel = PlayerViewModel()
    
    var body: some View {
        VideoPlayer(player: playerViewModel.player)
            .onAppear {
                playerViewModel.setupPlayer(with: videoURL)
            }
            .onDisappear {
                playerViewModel.cleanup()
            }
            .ignoresSafeArea()
    }
}

class PlayerViewModel: ObservableObject {
    @Published var player: AVPlayer?
    
    func setupPlayer(with url: URL) {
        let playerItem = AVPlayerItem(url: url)
        player = AVPlayer(playerItem: playerItem)
        
        // Configurar metadatos para la interfaz nativa de tvOS
        let titleMetadata = AVMutableMetadataItem()
        titleMetadata.identifier = .commonIdentifierTitle
        titleMetadata.value = "Mi Película" as NSString
        titleMetadata.extendedLanguageTag = "es"
        
        let descriptionMetadata = AVMutableMetadataItem()
        descriptionMetadata.identifier = .commonIdentifierDescription
        descriptionMetadata.value = "Una descripción increíble de la película" as NSString
        descriptionMetadata.extendedLanguageTag = "es"
        
        playerItem.externalMetadata = [titleMetadata, descriptionMetadata]
        
        player?.play()
    }
    
    func cleanup() {
        player?.pause()
        player = nil
    }
}
```

## Top Shelf Extension

Una de las características más distintivas de tvOS es el **Top Shelf**, esa área prominente en la parte superior de la pantalla de inicio cuando tu app está en la fila superior. Puedes personalizarla para mostrar contenido destacado:

```swift
import TVServices

class ContentProvider: TVTopShelfContentProvider {
    
    override func loadTopShelfContent() async -> TVTopShelfContent? {
        // Crear elementos para el Top Shelf
        var items: [TVTopShelfSectionedItem] = []
        
        let featuredContent = [
            ("Película Destacada", "https://tu-servidor.com/poster1.jpg"),
            ("Serie Popular", "https://tu-servidor.com/poster2.jpg"),
            ("Documental Nuevo", "https://tu-servidor.com/poster3.jpg")
        ]
        
        for (index, content) in featuredContent.enumerated() {
            let item = TVTopShelfSectionedItem(identifier: "item_\(index)")
            item.title = content.0
            
            // URL que abrirá un deeplink en tu app
            item.playAction = TVTopShelfAction(url: URL(string: "miapp://play/\(index)")!)
            item.displayAction = TVTopShelfAction(url: URL(string: "miapp://detail/\(index)")!)
            
            if let imageURL = URL(string: content.1) {
                item.setImageURL(imageURL, for: .screenScale1x)
            }
            
            items.append(item)
        }
        
        let section = TVTopShelfItemCollection(items: items)
        section.title = "Contenido Destacado"
        
        return TVTopShelfSectionedContent(sections: [section])
    }
}
```

## Trabajando con el Siri Remote

El Siri Remote tiene gestos específicos que puedes capturar para crear experiencias interactivas, especialmente útiles en juegos o apps de navegación avanzada:

```swift
import SwiftUI
import GameController

struct GameView: View {
    @State private var playerPosition = CGPoint(x: 960, y: 540)
    @State private var score = 0
    
    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            
            Circle()
                .fill(.blue)
                .frame(width: 60, height: 60)
                .position(playerPosition)
            
            VStack {
                HStack {
                    Text("Puntuación: \(score)")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                    Spacer()
                }
                Spacer()
            }
        }
        .onAppear {
            setupGameController()
        }
        .onPlayPauseCommand {
            // El usuario presionó Play/Pause en el remote
            print("Juego pausado/reanudado")
        }
        .onMoveCommand { direction in
            withAnimation(.easeOut(duration: 0.15)) {
                switch direction {
                case .up:
                    playerPosition.y -= 30
                case .down:
                    playerPosition.y += 30
                case .left:
                    playerPosition.x -= 30
                case .right:
                    playerPosition.x += 30
                @unknown default:
                    break
                }
            }
        }
    }
    
    private func setupGameController() {
        NotificationCenter.default.addObserver(
            forName: .GCControllerDidConnect,
            object: nil,
            queue: .main
        ) { notification in
            guard let controller = notification.object as? GCController else { return }
            
            if let microGamepad = controller.microGamepad {
                // Siri Remote como controlador
                microGamepad.dpad.valueChangedHandler = { _, xValue, yValue in
                    print("Dirección: x=\(xValue), y=\(yValue)")
                }
            }
            
            if let extendedGamepad = controller.extendedGamepad {
                // Controlador de juegos Bluetooth externo
                extendedGamepad.buttonA.pressedChangedHandler = { _, _, pressed in
                    if pressed {
                        print("Botón A presionado")
                    }
                }
            }
        }
        
        GCController.startWirelessControllerDiscovery()
    }
}
```

## Networking y persistencia en tvOS

### Consideraciones importantes de almacenamiento

tvOS **no garantiza la persistencia de datos locales**. El sistema puede purgar el almacenamiento de tu app en cualquier momento. Por esto, debes diseñar tu arquitectura asumiendo que los datos locales son temporales:

```swift
import Foundation

class TVDataManager {
    static let shared = TVDataManager()
    
    private let defaults = UserDefaults.standard
    private let cacheDirectory: URL? = {
        FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first
    }()
    
    // MARK: - Datos críticos → CloudKit o servidor remoto
    
    func saveUserPreferences(_ preferences: UserPreferences) async throws {
        // Siempre sincronizar con la nube
        try await CloudSyncService.shared.upload(preferences)
        
        // Cachear localmente para acceso rápido
        let data = try JSONEncoder().encode(preferences)
        defaults.set(data, forKey: "cached_preferences")
    }
    
    func loadUserPreferences() async -> UserPreferences {
        // Intentar cache local primero
        if let cachedData = defaults.data(forKey: "cached_preferences"),
           let cached = try? JSONDecoder().decode(UserPreferences.self, from: cachedData) {
            
            // Refrescar desde la nube en background
            Task {
                if let remote = try? await CloudSyncService.shared.fetchPreferences() {
                    await MainActor.run {
                        self.updateLocalCache(remote)
                    }
                }
            }
            
            return cached
        }
        
        //