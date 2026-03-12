---
sidebar_position: 1
title: Demo Widget
---

# Demo Widget: Construye tu primer Widget para iOS paso a paso

## ¿Qué es un Widget en iOS?

Los **Widgets** son extensiones de tu aplicación que muestran contenido relevante y actualizado directamente en la pantalla de inicio (Home Screen), la pantalla de bloqueo (Lock Screen) o en el StandBy de los dispositivos Apple. Fueron introducidos con su arquitectura actual en **iOS 14** a través del framework **WidgetKit** y utilizan **SwiftUI** como única tecnología de interfaz.

A diferencia de las vistas tradicionales de una app, los Widgets no son interactivos en tiempo real (aunque a partir de iOS 17 soportan interactividad básica con `AppIntents`). Su propósito es ofrecer **información de un vistazo** — glanceable content — sin necesidad de abrir la aplicación completa.

## ¿Por qué es importante para un dev iOS en LATAM?

En Latinoamérica, los Widgets representan una oportunidad enorme por varias razones:

1. **Visibilidad constante**: En mercados donde la competencia por la atención del usuario es feroz, tener presencia permanente en la pantalla de inicio es una ventaja competitiva brutal. Si desarrollas apps de fintech (Nubank, Mercado Pago, Ualá), delivery o noticias, un Widget puede ser el diferenciador que retenga usuarios.

2. **Requisito del mercado laboral**: Las empresas tecnológicas de la región — desde startups en Ciudad de México y Bogotá hasta unicornios en São Paulo y Buenos Aires — buscan desarrolladores que dominen extensiones de app. Saber construir Widgets ya no es opcional en entrevistas técnicas.

3. **Bajo costo de implementación, alto impacto**: Un Widget bien diseñado puede incrementar significativamente el engagement sin requerir una inversión enorme de tiempo. Es una de las mejores relaciones esfuerzo-resultado en el ecosistema iOS.

4. **Conectividad variable**: En muchas zonas de LATAM la conexión a internet es inestable. Los Widgets permiten mostrar datos cacheados sin que el usuario necesite abrir la app y esperar una carga completa.

## Arquitectura de un Widget

Antes de escribir código, entendamos los componentes fundamentales:

```
┌─────────────────────────────────────────────┐
│                 Widget Bundle                │
│  ┌────────────────────────────────────────┐  │
│  │          Widget Configuration          │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │           TimelineProvider       │  │  │
│  │  │  • placeholder()                 │  │  │
│  │  │  • getSnapshot()                 │  │  │
│  │  │  • getTimeline()                 │  │  │
│  │  └──────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │           TimelineEntry          │  │  │
│  │  │  • date: Date                    │  │  │
│  │  │  • datos personalizados          │  │  │
│  │  └──────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │         EntryView (SwiftUI)      │  │  │
│  │  │  • Vista para cada Entry         │  │  │
│  │  └──────────────────────────────────┘  │  │
│  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

- **`TimelineProvider`**: El cerebro del Widget. Decide **qué datos** mostrar y **cuándo** actualizarlos.
- **`TimelineEntry`**: Un "snapshot" de datos en un momento específico del tiempo.
- **`EntryView`**: La vista SwiftUI que renderiza cada entry.
- **`Widget Configuration`**: Define el tipo de Widget (estático o configurable por el usuario).

## Demo práctica: Widget de tipo de cambio USD/MXN

Vamos a construir un Widget que muestre el tipo de cambio del dólar estadounidense al peso mexicano. Este es un caso de uso extremadamente relevante en LATAM, donde millones de personas monitorean el tipo de cambio diariamente.

### Paso 1: Crear el target del Widget

En Xcode:

1. Ve a **File → New → Target**
2. Selecciona **Widget Extension**
3. Nómbralo `CurrencyWidget`
4. **Desmarca** "Include Configuration App Intent" si quieres empezar con un Widget estático (lo mantendremos simple)
5. Haz clic en **Finish**

### Paso 2: Definir el modelo de datos (TimelineEntry)

```swift
import WidgetKit
import Foundation

struct CurrencyEntry: TimelineEntry {
    let date: Date
    let exchangeRate: Double
    let previousRate: Double
    let currencyPair: String
    let isPlaceholder: Bool
    
    var difference: Double {
        exchangeRate - previousRate
    }
    
    var isRateUp: Bool {
        difference > 0
    }
    
    var formattedRate: String {
        String(format: "%.4f", exchangeRate)
    }
    
    var formattedDifference: String {
        let sign = isRateUp ? "+" : ""
        return "\(sign)\(String(format: "%.4f", difference))"
    }
    
    static var placeholder: CurrencyEntry {
        CurrencyEntry(
            date: .now,
            exchangeRate: 17.1520,
            previousRate: 17.0890,
            currencyPair: "USD/MXN",
            isPlaceholder: true
        )
    }
    
    static var sample: CurrencyEntry {
        CurrencyEntry(
            date: .now,
            exchangeRate: 17.2345,
            previousRate: 17.1890,
            currencyPair: "USD/MXN",
            isPlaceholder: false
        )
    }
}
```

### Paso 3: Implementar el TimelineProvider

```swift
import WidgetKit

struct CurrencyTimelineProvider: TimelineProvider {
    
    // Se muestra mientras el Widget carga por primera vez
    func placeholder(in context: Context) -> CurrencyEntry {
        CurrencyEntry.placeholder
    }
    
    // Se muestra en la galería de Widgets y en transiciones
    func getSnapshot(
        in context: Context,
        completion: @escaping (CurrencyEntry) -> Void
    ) {
        if context.isPreview {
            completion(CurrencyEntry.sample)
            return
        }
        
        fetchExchangeRate { entry in
            completion(entry)
        }
    }
    
    // Define la línea temporal completa de actualizaciones
    func getTimeline(
        in context: Context,
        completion: @escaping (Timeline<CurrencyEntry>) -> Void
    ) {
        fetchExchangeRate { entry in
            // Actualizar cada 30 minutos
            let nextUpdate = Calendar.current.date(
                byAdding: .minute,
                value: 30,
                to: entry.date
            )!
            
            let timeline = Timeline(
                entries: [entry],
                policy: .after(nextUpdate)
            )
            completion(timeline)
        }
    }
    
    // MARK: - Networking
    
    private func fetchExchangeRate(
        completion: @escaping (CurrencyEntry) -> Void
    ) {
        // En producción, aquí harías una llamada real a una API
        // como Banxico, Fixer.io o ExchangeRate-API
        
        guard let url = URL(
            string: "https://api.exchangerate-api.com/v4/latest/USD"
        ) else {
            completion(CurrencyEntry.sample)
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            guard
                let data = data,
                error == nil,
                let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                let rates = json["rates"] as? [String: Double],
                let mxnRate = rates["MXN"]
            else {
                completion(CurrencyEntry.sample)
                return
            }
            
            // Simulamos el rate anterior con un valor guardado en UserDefaults
            let sharedDefaults = UserDefaults(
                suiteName: "group.com.tuapp.currencywidget"
            )
            let previousRate = sharedDefaults?.double(forKey: "previousMXNRate") ?? mxnRate
            
            // Guardamos el rate actual para la próxima comparación
            sharedDefaults?.set(mxnRate, forKey: "previousMXNRate")
            
            let entry = CurrencyEntry(
                date: .now,
                exchangeRate: mxnRate,
                previousRate: previousRate,
                currencyPair: "USD/MXN",
                isPlaceholder: false
            )
            
            completion(entry)
        }.resume()
    }
}
```

> ⚠️ **Nota importante**: Para compartir datos entre tu app principal y el Widget, necesitas configurar un **App Group** en ambos targets. Ve a **Signing & Capabilities → App Groups** y agrega un grupo como `group.com.tuapp.currencywidget`.

### Paso 4: Diseñar la vista del Widget

```swift
import SwiftUI
import WidgetKit

struct CurrencyWidgetEntryView: View {
    var entry: CurrencyEntry
    
    @Environment(\.widgetFamily) var widgetFamily
    
    var body: some View {
        switch widgetFamily {
        case .systemSmall:
            smallWidget
        case .systemMedium:
            mediumWidget
        default:
            smallWidget
        }
    }
    
    // MARK: - Small Widget
    
    private var smallWidget: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header
            HStack {
                Image(systemName: "dollarsign.circle.fill")
                    .font(.title3)
                    .foregroundStyle(.green)
                
                Text(entry.currencyPair)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.secondary)
            }
            
            Spacer()
            
            // Tipo de cambio principal
            Text("$\(entry.formattedRate)")
                .font(.system(.title, design: .rounded))
                .fontWeight(.bold)
                .minimumScaleFactor(0.7)
                .lineLimit(1)
                .redacted(reason: entry.isPlaceholder ? .placeholder : [])
            
            // Diferencia
            HStack(spacing: 4) {
                Image(systemName: entry.isRateUp ? "arrow.up.right" : "arrow.down.right")
                    .font(.caption2)
                
                Text(entry.formattedDifference)
                    .font(.caption)
                    .fontWeight(.medium)
            }
            .foregroundStyle(entry.isRateUp ? .red : .green)
            .redacted(reason: entry.isPlaceholder ? .placeholder : [])
            
            // Última actualización
            Text(entry.date, style: .time)
                .font(.caption2)
                .foregroundStyle(.tertiary)
        }
        .padding()
        .containerBackground(.fill.tertiary, for: .widget)
    }
    
    // MARK: - Medium Widget
    
    private var mediumWidget: some View {
        HStack {
            smallWidget
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 12) {
                Text("Tipo de Cambio")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.secondary)
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Label("Anterior", systemImage: "clock.arrow.circlepath")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                    
                    Text("$\(String(format: "%.4f", entry.previousRate))")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundStyle(.secondary)
                }
                
                VStack(alignment: .trailing, spacing: 4) {
                    Label("Variación", systemImage: "chart.line.uptrend.xyaxis")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                    
                    Text(entry.formattedDifference)
                        .font(.subheadline)
                        .fontWeight(.bold)
                        .foregroundStyle(entry.isRateUp ? .red : .green)
                }
            }
            .padding()
        }
        .containerBackground(.fill.tertiary, for: .widget)
    }
}
```

### Paso 5: Configurar el Widget y el Bundle

```swift
import WidgetKit
import SwiftUI

struct CurrencyWidget: Widget {
    let kind: String = "CurrencyWidget"
    
    var body: some WidgetConfiguration {
        StaticConfiguration(
            kind: kind,
            provider: CurrencyTimelineProvider()
        ) { entry in
            CurrencyWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Tipo de Cambio")
        .description("Monitorea el tipo de cambio USD/MXN en tiempo real desde tu pantalla de inicio.")
        .supportedFamilies([.systemSmall, .systemMedium])
        .contentMarginsDisabled()
    }
}

// MARK: - Widget Bundle (si tienes múltiples widgets)

@main
struct CurrencyWidgetBundle: WidgetBundle {
    var body: some Widget {
        CurrencyWidget()
        // Aquí podrías agregar más widgets:
        // CurrencyWidgetLockScreen()
    }
}
```

### Paso 6: Agregar previsualizaciones

```swift
#Preview(as: .systemSmall) {
    CurrencyWidget()
} timeline: {
    CurrencyEntry.sample
    CurrencyEntry(
        date: .now,
        exchangeRate: 17.3456,
        previousRate: 17.2345,
        currencyPair: "USD/MXN",
        isPlaceholder: false
    )
}

#Preview(as: .systemMedium) {
    CurrencyWidget()
} timeline: {
    CurrencyEntry.sample
}
```

## Paso 7: Forzar actualizaciones desde la app principal

Cuando el usuario realiza una acción en tu app que debería reflejarse en el Widget, puedes forzar una actualización:

```swift
import WidgetKit

class ExchangeRateViewModel: ObservableObject {
    
    func refreshRate() async {
        // ... lógica de actualización de datos ...
        
        // Notificar al Widget que debe actualizarse
        WidgetCenter.shared.reloadTimelines(ofKind: "CurrencyWidget")
    }
    
    func reloadAllWidgets() {
        WidgetCenter.shared.reloadAllTimelines()
    }
    
    /// Verifica qué widgets tiene instalados el usuario
    func checkInstalledWidgets() {
        WidgetCenter.shared.getCurrentConfigurations { result in
            switch result {
            case .success(let configurations):
                for config in configurations {
                    print("Widget instalado: \(config.kind), familia: \(config.family)")
                }