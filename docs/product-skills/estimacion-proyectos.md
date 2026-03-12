---
sidebar_position: 1
title: Estimacion Proyectos
---

# Estimación de Proyectos en Desarrollo iOS

## ¿Qué es la estimación de proyectos?

La estimación de proyectos es el proceso de **predecir el esfuerzo, tiempo y recursos necesarios** para completar una tarea, funcionalidad o proyecto completo de software. No se trata de adivinar: es una habilidad técnica y humana que se desarrolla con práctica, datos históricos y comunicación honesta.

Para un desarrollador iOS, estimar correctamente significa la diferencia entre entregar un proyecto exitoso o caer en un ciclo interminable de "ya casi está listo" que destruye la confianza del cliente, del equipo y, eventualmente, tu reputación profesional.

## ¿Por qué es crítico para un dev iOS en LATAM?

En el contexto latinoamericano, la estimación cobra una importancia particular:

- **Trabajo remoto con equipos internacionales**: Muchos devs iOS en LATAM trabajan para empresas de EE.UU., Canadá o Europa. Una mala estimación no solo retrasa el proyecto, genera desconfianza cultural y puede costarte el contrato.
- **Freelance y consultorías**: Si cobras por proyecto (no por hora), una estimación deficiente significa trabajar gratis durante semanas.
- **Startups con recursos limitados**: En el ecosistema emprendedor latinoamericano, cada sprint cuenta. No hay presupuesto para "recalcular" constantemente.
- **Crecimiento profesional**: Los devs que estiman bien ascienden más rápido. Punto. Los tech leads y engineering managers son, ante todo, personas que entienden la relación entre esfuerzo y entrega.

## Las técnicas fundamentales de estimación

### 1. Estimación por analogía (comparación histórica)

Compara la tarea actual con algo que ya hayas construido antes.

```swift
// Ejemplo: Ya construiste una pantalla de login con Firebase Auth
// que te tomó 3 días. Ahora te piden login con Sign in with Apple.

struct EstimacionPorAnalogia {
    let tareaAnterior = "Login con Firebase Auth"
    let tiempoReal: Double = 3.0 // días
    
    let tareaNueva = "Login con Sign in with Apple"
    
    func estimar() -> Double {
        // Sign in with Apple es más sencillo que Firebase Auth manual,
        // pero nunca lo has implementado antes.
        let factorComplejidad = 0.7  // Menos complejo técnicamente
        let factorIncertidumbre = 1.4 // Nunca lo has hecho
        
        return tiempoReal * factorComplejidad * factorIncertidumbre
        // Resultado: 2.94 días ≈ 3 días
    }
}
```

### 2. Planning Poker (estimación en equipo)

Cada miembro del equipo asigna un valor de complejidad usando la secuencia de Fibonacci (1, 2, 3, 5, 8, 13, 21). Si hay discrepancia grande, se discute y se vuelve a votar.

```swift
enum StoryPoints: Int, CaseIterable {
    case trivial = 1
    case simple = 2
    case moderado = 3
    case complejo = 5
    case muyComplejo = 8
    case epico = 13
    case descomponer = 21 // Si llegas aquí, divide la tarea
}

struct HistoriaDeUsuario {
    let titulo: String
    let descripcion: String
    var votaciones: [String: StoryPoints] = [:]
    
    var hayConsenso: Bool {
        guard let min = votaciones.values.map(\.rawValue).min(),
              let max = votaciones.values.map(\.rawValue).max() else {
            return false
        }
        // Si la diferencia es mayor a un nivel de Fibonacci, no hay consenso
        return max <= min * 2
    }
    
    var estimacionFinal: StoryPoints? {
        guard hayConsenso else { return nil }
        let promedio = votaciones.values.map(\.rawValue).reduce(0, +) 
                       / votaciones.count
        // Redondear al Fibonacci más cercano hacia arriba (ser conservador)
        return StoryPoints.allCases.first { $0.rawValue >= promedio }
    }
}

// Uso en la práctica
var historia = HistoriaDeUsuario(
    titulo: "Implementar caché de imágenes offline",
    descripcion: "Las imágenes del catálogo deben estar disponibles sin conexión"
)

historia.votaciones = [
    "Ana (Senior)": .complejo,      // 5
    "Carlos (Mid)": .muyComplejo,   // 8
    "Diana (Junior)": .epico        // 13
]

// No hay consenso → Diana probablemente no conoce NSCache/SDWebImage
// Se discute, Diana aprende que hay librerías, revota con 5
// Consenso: 5 story points
```

### 3. Desglose por componentes (Work Breakdown Structure)

Esta es la técnica más confiable para proyectos iOS completos. Descompones cada pantalla y funcionalidad en sus componentes reales.

```swift
struct DesglosePantalla {
    let nombre: String
    var componentes: [Componente]
    
    struct Componente {
        let nombre: String
        let estimacionOptimista: Double  // horas
        let estimacionProbable: Double   // horas
        let estimacionPesimista: Double  // horas
        
        // Fórmula PERT (Program Evaluation and Review Technique)
        var estimacionPERT: Double {
            (estimacionOptimista + 4 * estimacionProbable + estimacionPesimista) / 6
        }
        
        // Desviación estándar para medir incertidumbre
        var desviacionEstandar: Double {
            (estimacionPesimista - estimacionOptimista) / 6
        }
    }
    
    var totalHoras: Double {
        componentes.reduce(0) { $0 + $1.estimacionPERT }
    }
    
    var incertidumbreTotal: Double {
        let varianzaTotal = componentes.reduce(0) { 
            $0 + pow($1.desviacionEstandar, 2) 
        }
        return sqrt(varianzaTotal)
    }
    
    var rangoEstimacion: (minimo: Double, maximo: Double) {
        // Intervalo de confianza del 95% (±2 desviaciones estándar)
        (totalHoras - 2 * incertidumbreTotal, 
         totalHoras + 2 * incertidumbreTotal)
    }
}

// Ejemplo real: Pantalla de perfil de usuario
let pantallaPerfil = DesglosePantalla(
    nombre: "Perfil de Usuario",
    componentes: [
        .init(nombre: "UI/Layout (SwiftUI)",
              estimacionOptimista: 4, estimacionProbable: 6, estimacionPesimista: 12),
        .init(nombre: "API Service (GET /profile)",
              estimacionOptimista: 2, estimacionProbable: 3, estimacionPesimista: 6),
        .init(nombre: "Edición de foto (ImagePicker + Crop)",
              estimacionOptimista: 3, estimacionProbable: 6, estimacionPesimista: 14),
        .init(nombre: "Validación de formulario",
              estimacionOptimista: 2, estimacionProbable: 3, estimacionPesimista: 5),
        .init(nombre: "Unit Tests",
              estimacionOptimista: 2, estimacionProbable: 4, estimacionPesimista: 6),
        .init(nombre: "UI Tests",
              estimacionOptimista: 1, estimacionProbable: 2, estimacionPesimista: 4),
    ]
)

let rango = pantallaPerfil.rangoEstimacion
print("Estimación: \(pantallaPerfil.totalHoras) horas")
print("Rango (95% confianza): \(rango.minimo) - \(rango.maximo) horas")
// Estimación: ~24 horas
// Rango: ~18 - ~30 horas
```

## Los multiplicadores ocultos que todo dev iOS ignora

La estimación técnica pura es solo una parte. Estos factores multiplican tu estimación real:

```swift
struct MultiplicadoresReales {
    // Factores que la mayoría olvida incluir
    let codeReview = 1.15           // +15% por revisiones de código
    let reuniones = 1.10            // +10% por dailies, plannings, retros
    let bugFixing = 1.20            // +20% por bugs encontrados en QA
    let appStoreReview = 1.05       // +5% por posibles rechazos de App Store
    let comunicacionRemota = 1.10   // +10% si el equipo está distribuido
    let documentacion = 1.05        // +5% por documentar decisiones
    let configCI_CD = 1.08          // +8% por pipelines, certificates, provisioning
    
    var multiplicadorTotal: Double {
        codeReview * reuniones * bugFixing * appStoreReview *
        comunicacionRemota * documentacion * configCI_CD
    }
    // Resultado: ~1.93x → ¡Casi el doble de la estimación técnica pura!
    
    func estimacionRealista(horasTecnicas: Double) -> Double {
        horasTecnicas * multiplicadorTotal
    }
}

let multiplicadores = MultiplicadoresReales()
let horasTecnicas = 24.0 // Del ejemplo anterior
let horasReales = multiplicadores.estimacionRealista(horasTecnicas: horasTecnicas)
print("Horas técnicas: \(horasTecnicas)")
print("Horas reales: \(horasReales)")
// Horas técnicas: 24.0
// Horas reales: ~46.3 horas ≈ 6 días laborales
```

## La "Regla del Developer iOS en LATAM"

Después de años de experiencia en equipos latinoamericanos, esta regla informal funciona sorprendentemente bien:

```swift
struct ReglaEstimacionPragmatica {
    
    enum NivelExperiencia {
        case junior    // < 2 años
        case mid       // 2-5 años
        case senior    // 5+ años
    }
    
    /// Tu primera estimación instintiva, multiplicada por un factor de experiencia
    static func estimar(
        instinto: Double,
        experiencia: NivelExperiencia,
        tecnologiaNueva: Bool
    ) -> (minimo: Double, maximo: Double) {
        
        let factorExperiencia: Double = switch experiencia {
        case .junior: 3.0   // Los juniors subestiman 3x
        case .mid:    2.0   // Los mid subestiman 2x
        case .senior: 1.5   // Los seniors subestiman 1.5x
        }
        
        let factorTecnologia = tecnologiaNueva ? 1.5 : 1.0
        
        let estimacion = instinto * factorExperiencia * factorTecnologia
        
        return (
            minimo: estimacion * 0.8,
            maximo: estimacion * 1.3
        )
    }
}

// "Creo que me toma 2 días" - dice un dev mid usando SwiftData por primera vez
let resultado = ReglaEstimacionPragmatica.estimar(
    instinto: 2.0,
    experiencia: .mid,
    tecnologiaNueva: true
)
print("Rango realista: \(resultado.minimo) - \(resultado.maximo) días")
// Rango realista: 4.8 - 7.8 días
// (Sí, probablemente sea una semana completa)
```

## Anatomía de una estimación profesional para un proyecto iOS

Veamos cómo estructurar una estimación completa que puedas presentar a un cliente o product manager:

```swift
struct EstimacionProyectoiOS {
    let nombreProyecto: String
    let modulos: [Modulo]
    
    struct Modulo {
        let nombre: String
        let historias: [Historia]
        
        struct Historia {
            let titulo: String
            let storyPoints: Int
            let diasEstimados: Double
            let riesgos: [String]
            let dependencias: [String]
        }
        
        var totalDias: Double {
            historias.reduce(0) { $0 + $1.diasEstimados }
        }
    }
    
    var resumen: String {
        let totalDias = modulos.reduce(0) { $0 + $1.totalDias }
        let diasConBuffer = totalDias * 1.2 // 20% buffer de contingencia
        let semanasLaborales = ceil(diasConBuffer / 5)
        
        return """
        📱 Proyecto: \(nombreProyecto)
        ═══════════════════════════════════
        
        \(modulos.map { modulo in
            """
            📦 \(modulo.nombre): \(modulo.totalDias) días
            \(modulo.historias.map { "   → \($0.titulo): \($0.diasEstimados)d" }.joined(separator: "\n"))
            """
        }.joined(separator: "\n\n"))
        
        ───────────────────────────────────
        Subtotal técnico:     \(totalDias) días
        Buffer contingencia:  \(diasConBuffer - totalDias) días (20%)
        ───────────────────────────────────
        TOTAL ESTIMADO:       \(diasConBuffer) días (~\(Int(semanasLaborales)) semanas)
        
        ⚠️  Esta estimación asume:
        • Diseños finalizados antes de iniciar desarrollo
        • API documentada y funcional
        • 1 desarrollador iOS dedicado al 100%
        • Feedback de QA en máximo 24 horas
        """
    }
}

// Ejemplo: App de delivery para restaurante local
let proyecto = EstimacionProyectoiOS(
    nombreProyecto: "FoodExpress iOS",
    modulos: [
        .init(nombre: "Autenticación", historias: [
            .init(titulo: "Login email/password", storyPoints: 3, diasEstimados: 2,
                  riesgos: ["Cambios en flujo de Firebase"], dependencias: ["Backend auth"]),
            .init(titulo: "Sign in with Apple", storyPoints: 3, diasEstimados: 2,
                  riesgos: ["Configuración certificates"], dependencias: ["Apple Developer Account"]),
            .init(titulo: "Onboarding screens", storyPoints: 2, diasEstimados: 1.5,
                  riesgos: [], dependencias: ["Diseños finales"]),
        ]),
        .init(nombre: "Catálogo", historias: [
            .init(titulo: "Lista de restaurantes", storyPoints: 5, diasEstimados: 3,
                  riesgos: ["Paginación compleja"], dependencias: ["API /restaurants"]),
            .init(titulo: "Detalle de restaurante", storyPoints: 3, diasEstimados: 2,
                  riesgos: [], dependencias: ["API /restaurant/:id"]),
            .init(titulo: "Menú con categorías", storyPoints: 5, diasEstimados: 3,
                  riesg